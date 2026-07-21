import asyncio
import json
from pathlib import Path
from types import SimpleNamespace

from app.activities import create_activity
from app.ai import (
    QuizActivityOutput,
    QuizOptionExplanationOutput,
    QuizOptionOutput,
    SourceReference,
)
from app.config import Settings
from app.db import connect
from tests.test_focus_workspace import prepare_start_action
from tests.test_learning_path import app_client, make_app


async def prepare_focus(client):
    session = await prepare_start_action(client)
    saved = await client.put(
        f"/api/sessions/{session['id']}/drafts/start_action",
        json={
            "content": "Self-attention compares positions and combines relevant value information.",
            "hint_depth": 0,
            "version": 0,
        },
    )
    assert saved.status_code == 200
    started = await client.post(
        f"/api/sessions/{session['id']}/start-action/complete",
        json={"version": session["version"]},
    )
    assert started.status_code == 200
    return started.json()


def test_quiz_hides_answer_and_restores_draft_hints_pause_and_attempt(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            focus = await prepare_focus(client)
            session_id = focus["session"]["id"]
            created = await client.post(
                f"/api/sessions/{session_id}/activities",
                json={"type": "quiz", "version": focus["session"]["version"]},
            )
            assert created.status_code == 201
            quiz = created.json()
            activity_id = quiz["activity"]["id"]
            assert quiz["session"]["state"] == "practicing"
            assert len(quiz["quiz"]["options"]) == 4
            assert quiz["hints"] == {
                "depth": 0,
                "total": 3,
                "revealed": [],
                "can_reveal_more": True,
            }
            serialized = json.dumps(quiz)
            assert "correct_option_id" not in serialized
            assert "misconception_tag" not in serialized
            assert "explanation_by_option" not in serialized
            assert quiz["boundaries"]["creates_learning_evidence"] is False
            assert quiz["boundaries"]["creates_agent_decision"] is False
            assert quiz["generation"]["internet_search_performed"] is False

            selected_id = quiz["quiz"]["options"][1]["id"]
            saved = await client.put(
                f"/api/sessions/{session_id}/drafts/quiz",
                json={"content": selected_id, "hint_depth": 0, "version": 0},
            )
            assert saved.status_code == 200
            assert saved.json()["draft"]["activity_id"] == activity_id

            hinted = await client.post(
                f"/api/activities/{activity_id}/hints/next",
                json={"version": quiz["activity"]["version"]},
            )
            assert hinted.status_code == 200
            hint_body = hinted.json()
            assert hint_body["hints"]["depth"] == 1
            assert len(hint_body["hints"]["revealed"]) == 1
            assert hint_body["draft"]["content"] == selected_id
            assert hint_body["draft"]["hint_depth"] == 1
            stale_hint = await client.post(
                f"/api/activities/{activity_id}/hints/next",
                json={"version": quiz["activity"]["version"]},
            )
            assert stale_hint.status_code == 409
            assert stale_hint.json()["error_code"] == "activity_version_conflict"

            paused = await client.post(
                f"/api/sessions/{session_id}/pause",
                json={"version": hint_body["session"]["version"]},
            )
            assert paused.status_code == 200
            assert paused.json()["session"]["resume_state"] == "practicing"
            blocked = await client.post(
                f"/api/activities/{activity_id}/hints/next",
                json={"version": hint_body["activity"]["version"]},
            )
            assert blocked.status_code == 409
            assert blocked.json()["error_code"] == "session_paused"

            resumed = await client.post(
                f"/api/sessions/{session_id}/resume",
                json={"version": paused.json()["session"]["version"]},
            )
            assert resumed.status_code == 200
            restored = await client.get(f"/api/activities/{activity_id}")
            assert restored.status_code == 200
            assert restored.json()["draft"]["content"] == selected_id
            assert restored.json()["hints"]["depth"] == 1

            submitted = await client.post(
                f"/api/activities/{activity_id}/attempts",
                json={"version": hint_body["activity"]["version"], "elapsed_seconds": 47},
            )
            assert submitted.status_code == 201
            submission = submitted.json()
            assert submission["activity"]["status"] == "submitted"
            assert submission["submission"]["answer_received"] is True
            assert submission["submission"]["hint_depth"] == 1
            assert submission["submission"]["feedback_ready"] is False
            assert "correct_option_id" not in json.dumps(submission)

            closed = await client.post(
                f"/api/activities/{activity_id}/close",
                json={"version": submission["session"]["version"]},
            )
            assert closed.status_code == 200
            assert closed.json()["session"]["state"] == "learning_concept"
            with connect(app.state.settings.database_path) as connection:
                attempt = connection.execute(
                    "SELECT * FROM attempts WHERE activity_id = ?",
                    (activity_id,),
                ).fetchone()
                assert attempt["selected_option_id"] == selected_id
                assert attempt["raw_answer"] is None
                event = connection.execute(
                    "SELECT detail_json FROM session_events WHERE event_type = 'activity_submitted'"
                ).fetchone()
                detail = json.loads(event["detail_json"])
                assert detail["learning_evidence_created"] is False
                assert detail["agent_decision_created"] is False

    asyncio.run(scenario())


def test_free_recall_keeps_evaluation_key_server_side_and_detects_conflict(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            focus = await prepare_focus(client)
            session_id = focus["session"]["id"]
            created = await client.post(
                f"/api/sessions/{session_id}/activities",
                json={"type": "recall", "version": focus["session"]["version"]},
            )
            assert created.status_code == 201
            recall = created.json()
            activity_id = recall["activity"]["id"]
            assert "expected_key_points" not in json.dumps(recall)
            assert "misconception_patterns" not in json.dumps(recall)
            assert recall["activity"]["source_origin"] == "uploaded"
            assert recall["activity"]["source_ref_details"]

            first = await client.put(
                f"/api/sessions/{session_id}/drafts/recall",
                json={
                    "content": "It compares positions, creates relevance weights, and combines value information.",
                    "hint_depth": 0,
                    "version": 0,
                },
            )
            assert first.status_code == 200
            conflict = await client.put(
                f"/api/sessions/{session_id}/drafts/recall",
                json={"content": "A different local answer", "hint_depth": 0, "version": 0},
            )
            assert conflict.status_code == 409
            assert conflict.json()["details"]["server_draft"]["content"].startswith("It compares")
            restored = await client.get(f"/api/activities/{activity_id}")
            assert restored.json()["draft"]["content"].startswith("It compares")

    asyncio.run(scenario())


def test_real_quiz_uses_gpt56_strict_schema_without_tools(tmp_path: Path) -> None:
    captured: dict = {}

    class FakeResponses:
        def __init__(self, source_ref: SourceReference):
            self.source_ref = source_ref

        def parse(self, **kwargs):
            captured.update(kwargs)
            output = QuizActivityOutput(
                question="What happens after relevance scores are computed?",
                options=[
                    QuizOptionOutput(id="a", text="Delete every token.", misconception_tag="deletion"),
                    QuizOptionOutput(id="b", text="Combine value information by weight.", misconception_tag="correct"),
                    QuizOptionOutput(id="c", text="Reorder the input.", misconception_tag="reordering"),
                ],
                correct_option_id="b",
                explanation_by_option=[
                    QuizOptionExplanationOutput(option_id="a", explanation="Weights do not delete every token."),
                    QuizOptionExplanationOutput(option_id="b", explanation="This matches the source."),
                    QuizOptionExplanationOutput(option_id="c", explanation="Attention does not reorder the input."),
                ],
                hint_levels=["Think about values.", "Scores become weights.", "Weighted value combination."],
                source_origin="uploaded",
                source_refs=[self.source_ref],
            )
            return SimpleNamespace(status="completed", output_parsed=output, id="resp_activity")

    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            focus = await prepare_focus(client)
            session_id = focus["session"]["id"]
            source_ref = SourceReference.model_validate(focus["active_concept"]["source_refs"][0])
            with connect(app.state.settings.database_path) as connection:
                workspace_id = str(
                    connection.execute(
                        "SELECT workspace_id FROM learning_sessions WHERE id = ?",
                        (session_id,),
                    ).fetchone()["workspace_id"]
                )
            settings = Settings(
                mode="real",
                database_path=app.state.settings.database_path,
                upload_dir=app.state.settings.upload_dir,
                openai_api_key="test-key",
                openai_model="gpt-5.6",
            )
            result = create_activity(
                settings,
                workspace_id,
                session_id,
                "quiz",
                focus["session"]["version"],
                client_factory=lambda _settings: SimpleNamespace(responses=FakeResponses(source_ref)),
            )
            assert result["generation"]["mode"] == "real"

    asyncio.run(scenario())
    assert captured["model"] == "gpt-5.6"
    assert captured["text_format"] is QuizActivityOutput
    assert captured["store"] is False
    assert "tools" not in captured
