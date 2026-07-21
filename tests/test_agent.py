import asyncio
import json
from pathlib import Path
from types import SimpleNamespace

from app.agent import create_agent_decision
from app.config import Settings
from app.db import connect
from tests.test_activities import prepare_focus, quiz_answer_payload
from tests.test_learning_path import app_client, make_app


async def complete_quiz_evidence(client, focus: dict, *, correct: bool) -> dict:
    session_id = focus["session"]["id"]
    created = await client.post(
        f"/api/sessions/{session_id}/activities",
        json={"type": "quiz", "version": focus["session"]["version"]},
    )
    assert created.status_code == 201
    activity = created.json()
    option = quiz_answer_payload(activity, correct=correct)
    saved = await client.put(
        f"/api/sessions/{session_id}/drafts/quiz",
        json={
            "content": option,
            "hint_depth": 0,
            "version": activity["draft"]["server_version"] if activity["draft"] else 0,
        },
    )
    assert saved.status_code == 200
    submitted = await client.post(
        f"/api/activities/{activity['activity']['id']}/attempts",
        json={"version": activity["activity"]["version"], "elapsed_seconds": 34},
    )
    assert submitted.status_code == 201
    feedback = await client.post(
        f"/api/attempts/{submitted.json()['submission']['id']}/feedback"
    )
    assert feedback.status_code == 201
    completed = await client.post(
        f"/api/feedback/{feedback.json()['feedback']['id']}/complete",
        json={"version": feedback.json()["session"]["version"]},
    )
    assert completed.status_code == 200
    return completed.json()


def test_agent_selects_one_action_and_applies_validated_progression(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            focus = await prepare_focus(client)
            evidence = await complete_quiz_evidence(client, focus, correct=True)
            session_id = evidence["session"]["id"]

            # Time pressure must not end a route while a validated next concept exists.
            with connect(app.state.settings.database_path) as connection:
                connection.execute(
                    "UPDATE learning_sessions SET remaining_seconds = 60 WHERE id = ?",
                    (session_id,),
                )

            proposed = await client.post(f"/api/sessions/{session_id}/agent-decisions")
            assert proposed.status_code == 201
            body = proposed.json()
            assert body["decision"]["action"] == "continue_next"
            assert body["decision"]["status"] == "proposed"
            assert body["session"]["state"] == "agent_decision"
            assert body["boundaries"]["learning_performance_basis"] == "LearningEvidence only"
            assert body["boundaries"]["exactly_one_recommended_action"] is True
            assert body["boundaries"]["more_material_requested"] is False
            assert all(item["action"] != "continue_next" for item in body["allowed_alternatives"])

            repeated = await client.post(f"/api/sessions/{session_id}/agent-decisions")
            assert repeated.status_code == 201
            assert repeated.json()["decision"]["id"] == body["decision"]["id"]

            accepted = await client.post(
                f"/api/agent-decisions/{body['decision']['id']}/accept",
                json={"version": body["session"]["version"]},
            )
            assert accepted.status_code == 200
            result = accepted.json()
            assert result["decision"]["status"] == "accepted"
            assert result["execution"]["destination"] == "focus"
            assert result["execution"]["session"]["state"] == "learning_concept"
            assert result["execution"]["session"]["active_concept_id"] != focus["active_concept"]["id"]

            with connect(app.state.settings.database_path) as connection:
                rows = connection.execute(
                    "SELECT action, status FROM agent_decisions WHERE session_id = ?",
                    (session_id,),
                ).fetchall()
                assert [tuple(row) for row in rows] == [("continue_next", "accepted")]

    asyncio.run(scenario())


def test_agent_finishes_only_after_the_final_concept_is_mastered(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            current_focus = await prepare_focus(client)
            session_id = current_focus["session"]["id"]
            path = (await client.get(f"/api/sessions/{session_id}/path")).json()
            route = path["knowledge_map"]["recommended_route"]
            route_length = len(route)
            active_index = route.index(current_focus["active_concept"]["concept_key"])
            remaining_length = route_length - active_index

            for concept_index in range(remaining_length):
                evidence = await complete_quiz_evidence(client, current_focus, correct=True)
                decision = (
                    await client.post(f"/api/sessions/{session_id}/agent-decisions")
                ).json()
                expected_action = "finish_session" if concept_index == remaining_length - 1 else "continue_next"
                assert decision["decision"]["action"] == expected_action
                accepted = await client.post(
                    f"/api/agent-decisions/{decision['decision']['id']}/accept",
                    json={"version": decision["session"]["version"]},
                )
                assert accepted.status_code == 200
                current_focus = accepted.json()["execution"]

            assert current_focus["destination"] == "session_summary"
            summary = await client.get(f"/api/sessions/{session_id}/summary")
            assert summary.status_code == 200
            assert summary.json()["summary"]["still_to_review"] == []
            assert len(summary.json()["summary"]["completed_concepts"]) == route_length

    asyncio.run(scenario())


def test_agent_override_is_penalty_free_and_invalid_paths_are_rejected(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            focus = await prepare_focus(client)
            evidence = await complete_quiz_evidence(client, focus, correct=False)
            session_id = evidence["session"]["id"]
            proposed = (await client.post(f"/api/sessions/{session_id}/agent-decisions")).json()
            assert proposed["decision"]["action"] == "retry_current"

            invalid = await client.post(
                f"/api/agent-decisions/{proposed['decision']['id']}/override",
                json={
                    "action": "continue_next",
                    "reason": "Skip ahead",
                    "version": proposed["session"]["version"],
                },
            )
            assert invalid.status_code == 422
            assert invalid.json()["error_code"] == "agent_override_not_allowed"

            material_request_without_gap = await client.post(
                f"/api/agent-decisions/{proposed['decision']['id']}/override",
                json={
                    "action": "request_more_material",
                    "reason": "Ask for more material anyway",
                    "version": proposed["session"]["version"],
                },
            )
            assert material_request_without_gap.status_code == 422
            assert material_request_without_gap.json()["error_code"] == "agent_override_not_allowed"

            switched = await client.post(
                f"/api/agent-decisions/{proposed['decision']['id']}/override",
                json={
                    "action": "switch_activity",
                    "reason": "Use another retrieval format.",
                    "version": proposed["session"]["version"],
                },
            )
            assert switched.status_code == 200
            result = switched.json()
            assert result["decision"]["status"] == "overridden"
            assert result["decision"]["selected_action"] == "switch_activity"
            assert result["boundaries"]["user_override_penalty"] is False
            assert result["execution"]["destination"] == "activity"

    asyncio.run(scenario())


def test_agent_inserts_and_returns_from_a_linked_prerequisite(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            focus = await prepare_focus(client)
            evidence = await complete_quiz_evidence(client, focus, correct=False)
            session_id = evidence["session"]["id"]
            with connect(app.state.settings.database_path) as connection:
                connection.execute(
                    "UPDATE concepts SET status = 'planned' WHERE session_id = ? AND concept_key = 'transformer_goal'",
                    (session_id,),
                )
                connection.execute(
                    "UPDATE learning_evidence SET source_gap_signal = ? WHERE session_id = ?",
                    ("The learner needs the linked transformer goal prerequisite.", session_id),
                )

            proposed = (await client.post(f"/api/sessions/{session_id}/agent-decisions")).json()
            assert proposed["decision"]["action"] == "insert_prerequisite"
            original_id = proposed["decision"]["concept_id"]
            accepted = await client.post(
                f"/api/agent-decisions/{proposed['decision']['id']}/accept",
                json={"version": proposed["session"]["version"]},
            )
            assert accepted.status_code == 200
            detour_session = accepted.json()["execution"]["session"]
            assert detour_session["active_concept_id"] != original_id

            detour_focus_response = await client.get(f"/api/sessions/{session_id}/focus")
            assert detour_focus_response.status_code == 200
            detour_evidence = await complete_quiz_evidence(
                client, detour_focus_response.json(), correct=True
            )
            return_decision = (await client.post(f"/api/sessions/{session_id}/agent-decisions")).json()
            assert return_decision["decision"]["action"] == "continue_next"
            assert return_decision["decision"]["target_concept_id"] == original_id
            returned = await client.post(
                f"/api/agent-decisions/{return_decision['decision']['id']}/accept",
                json={"version": return_decision["session"]["version"]},
            )
            assert returned.status_code == 200
            assert returned.json()["execution"]["session"]["active_concept_id"] == original_id
            with connect(app.state.settings.database_path) as connection:
                detour = connection.execute(
                    "SELECT status FROM learning_detours WHERE session_id = ?",
                    (session_id,),
                ).fetchone()
                assert detour["status"] == "returned"

    asyncio.run(scenario())


def test_more_material_is_requested_only_after_a_validated_gap_and_local_support(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            focus = await prepare_focus(client)
            session_id = focus["session"]["id"]
            opened = await client.post(
                f"/api/sessions/{session_id}/tutor/open",
                json={"version": focus["session"]["version"]},
            )
            tutor = opened.json()
            replied = await client.post(
                f"/api/sessions/{session_id}/tutor/messages",
                json={
                    "message": "What is a dot product? The notes do not define it.",
                    "quick_action": None,
                    "thread_version": tutor["thread"]["version"],
                },
            )
            closed = await client.post(
                f"/api/sessions/{session_id}/tutor/close",
                json={"thread_version": replied.json()["thread"]["version"]},
            )
            evidence = await complete_quiz_evidence(client, closed.json(), correct=False)
            assert len(evidence["learning_evidence"]) == 2
            with connect(app.state.settings.database_path) as connection:
                connection.execute(
                    """
                    UPDATE learning_evidence SET source_gap_signal = ?
                    WHERE session_id = ? AND activity_type = 'tutor_check'
                    """,
                    (
                        "The source does not explain why score variance grows with key dimension.",
                        session_id,
                    ),
                )

            proposed = await client.post(f"/api/sessions/{session_id}/agent-decisions")
            assert proposed.status_code == 201
            body = proposed.json()
            assert body["decision"]["action"] == "request_more_material"
            assert body["decision"]["required_tool"] == "open_material_upload"
            assert body["boundaries"]["more_material_requested"] is True
            accepted = await client.post(
                f"/api/agent-decisions/{body['decision']['id']}/accept",
                json={"version": body["session"]["version"]},
            )
            assert accepted.status_code == 200
            execution = accepted.json()["execution"]
            assert execution["destination"] == "material_upload"
            assert "variance scaling" in execution["requested_material"]
            assert execution["session"]["state"] == "learning_concept"

    asyncio.run(scenario())


def test_real_agent_forces_one_strict_gpt56_function_call(tmp_path: Path) -> None:
    captured: dict = {}

    class FakeResponses:
        def create(self, **kwargs):
            captured.update(kwargs)
            context = json.loads(kwargs["input"])
            item = context["allowed_actions"]["continue_next"]
            arguments = json.dumps({
                "action": "continue_next",
                "reason_for_user": "The latest check is mastered with no blocking misconception.",
                "estimated_minutes": item["estimated_minutes"],
                "target_concept_id": item["target_concept_id"],
                "return_to_concept_id": item["return_to_concept_id"],
                "required_tool": item["required_tool"],
                "confidence": 0.88,
            })
            call = SimpleNamespace(
                type="function_call",
                name="select_next_learning_action",
                arguments=arguments,
            )
            return SimpleNamespace(status="completed", output=[call], id="resp_agent")

    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            focus = await prepare_focus(client)
            evidence = await complete_quiz_evidence(client, focus, correct=True)
            with connect(app.state.settings.database_path) as connection:
                workspace_id = connection.execute(
                    "SELECT workspace_id FROM learning_sessions WHERE id = ?",
                    (evidence["session"]["id"],),
                ).fetchone()["workspace_id"]
            settings = Settings(
                mode="real",
                database_path=app.state.settings.database_path,
                upload_dir=app.state.settings.upload_dir,
                openai_api_key="test-key",
                openai_model="gpt-5.6",
            )
            result = create_agent_decision(
                settings,
                str(workspace_id),
                evidence["session"]["id"],
                client_factory=lambda _settings: SimpleNamespace(responses=FakeResponses()),
            )
            assert result["decision"]["action"] == "continue_next"
            assert result["generation"]["mode"] == "real"

    asyncio.run(scenario())
    assert captured["model"] == "gpt-5.6"
    assert captured["store"] is False
    assert captured["parallel_tool_calls"] is False
    assert captured["tool_choice"] == {
        "type": "function",
        "name": "select_next_learning_action",
    }
    tool = captured["tools"][0]
    assert tool["strict"] is True
    assert tool["parameters"]["additionalProperties"] is False
    assert set(tool["parameters"]["required"]) == set(tool["parameters"]["properties"])
