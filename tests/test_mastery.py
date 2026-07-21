import asyncio
import json
from pathlib import Path
from types import SimpleNamespace

from app.ai import FeedbackOutput, RemedialActivityOutput, SourceReference
from app.config import Settings
from app.db import connect
from app.mastery import create_remedial_activity, generate_feedback
from tests.test_activities import prepare_focus, quiz_answer_payload
from tests.test_learning_path import app_client, make_app


async def _submit_quiz(client, *, choose_correct: bool = False):
    focus = await prepare_focus(client)
    session_id = focus["session"]["id"]
    created = await client.post(
        f"/api/sessions/{session_id}/activities",
        json={"type": "quiz", "version": focus["session"]["version"]},
    )
    body = created.json()
    option = quiz_answer_payload(body, correct=choose_correct)
    saved = await client.put(
        f"/api/sessions/{session_id}/drafts/quiz",
        json={"content": option, "hint_depth": 0, "version": 0},
    )
    assert saved.status_code == 200
    submitted = await client.post(
        f"/api/activities/{body['activity']['id']}/attempts",
        json={"version": body["activity"]["version"], "elapsed_seconds": 31},
    )
    assert submitted.status_code == 201
    return submitted.json()


def test_feedback_records_factual_evidence_and_runs_local_remediation(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            submitted = await _submit_quiz(client)
            attempt_id = submitted["submission"]["id"]
            prepared = await client.post(f"/api/attempts/{attempt_id}/feedback")
            assert prepared.status_code == 201
            feedback = prepared.json()
            repeated = await client.post(f"/api/attempts/{attempt_id}/feedback")
            assert repeated.status_code == 201
            assert repeated.json()["feedback"]["id"] == feedback["feedback"]["id"]
            assert feedback["session"]["state"] == "feedback_shown"
            assert feedback["feedback"]["mastered_points"] == []
            assert feedback["feedback"]["missing_or_unclear_points"]
            assert feedback["feedback"]["compact_correction"]
            assert feedback["feedback"]["encouragement"]
            assert feedback["feedback"]["next_micro_action"]
            quiz_result = feedback["feedback"]["quiz_result"]
            assert quiz_result["is_correct"] is False
            assert quiz_result["correct_count"] == 0
            assert quiz_result["total_questions"] == 3
            assert len(quiz_result["questions"]) == 3
            assert all(question["selected_option_text"] for question in quiz_result["questions"])
            assert all(question["correct_option_text"] for question in quiz_result["questions"])
            assert all(question["explanation"] for question in quiz_result["questions"])
            assert feedback["remediation"]["available"] is True
            assert feedback["remediation"]["recommended_strategy"] == "smaller_question"
            assert feedback["boundaries"]["agent_decision_created"] is False
            assert feedback["generation"]["internet_search_performed"] is False

            evidence = feedback["evidence"]
            assert evidence["activity_type"] == "quiz"
            assert evidence["outcome"] == "needs_support"
            serialized_evidence = json.dumps(evidence)
            for forbidden in ("next_action", "recommendation", "should_continue", "search_needed"):
                assert forbidden not in serialized_evidence

            remedial = await client.post(
                f"/api/feedback/{feedback['feedback']['id']}/remedial-activity",
                json={"version": feedback["session"]["version"]},
            )
            assert remedial.status_code == 201
            activity = remedial.json()
            assert activity["session"]["state"] == "remedial_practice"
            assert activity["activity"]["type"] == "remedial"
            assert activity["remedial"]["strategy"] == "smaller_question"
            assert "expected_key_points" not in json.dumps(activity)

            draft = activity["draft"]
            saved_remedial = await client.put(
                f"/api/sessions/{activity['session']['id']}/drafts/remedial",
                json={
                    "content": "I do not know yet.",
                    "hint_depth": 0,
                    "version": draft["server_version"],
                },
            )
            assert saved_remedial.status_code == 200
            submitted_remedial = await client.post(
                f"/api/activities/{activity['activity']['id']}/attempts",
                json={"version": activity["activity"]["version"], "elapsed_seconds": 22},
            )
            assert submitted_remedial.status_code == 201
            remedial_feedback_response = await client.post(
                f"/api/attempts/{submitted_remedial.json()['submission']['id']}/feedback"
            )
            assert remedial_feedback_response.status_code == 201
            remedial_feedback = remedial_feedback_response.json()
            assert remedial_feedback["evidence"]["activity_type"] == "remedial"
            assert remedial_feedback["evidence"]["remedial_result"] == "not_improved"
            assert remedial_feedback["remediation"]["recommended_strategy"] == "concrete_example"

            completed = await client.post(
                f"/api/feedback/{remedial_feedback['feedback']['id']}/complete",
                json={"version": remedial_feedback["session"]["version"]},
            )
            assert completed.status_code == 200
            evidence_body = completed.json()
            assert evidence_body["session"]["state"] == "evidence_ready"
            assert len(evidence_body["learning_evidence"]) == 2
            assert evidence_body["boundaries"]["contains_recommendations"] is False

            with connect(app.state.settings.database_path) as connection:
                columns = {
                    row["name"] for row in connection.execute("PRAGMA table_info(learning_evidence)")
                }
                for forbidden in ("next_action", "recommendation", "should_continue", "search_needed"):
                    assert forbidden not in columns

    asyncio.run(scenario())


def test_real_feedback_uses_gpt56_typed_output_without_tools(tmp_path: Path) -> None:
    captured: dict = {}
    captured_remedial: dict = {}

    class FakeResponses:
        def __init__(self, source_ref: SourceReference):
            self.source_ref = source_ref

        def parse(self, **kwargs):
            captured.update(kwargs)
            output = FeedbackOutput(
                mastered_points=[],
                missing_or_unclear_points=["The relevance weights control value combination."],
                misconceptions=["The answer treats attention as deletion."],
                compact_correction="Attention weights scale and combine value information.",
                next_micro_action="Answer one smaller question about weighted value combination.",
                encouragement="You made a checkable choice that identifies one precise misconception.",
                source_origin="uploaded",
                source_refs=[self.source_ref],
            )
            return SimpleNamespace(status="completed", output_parsed=output, id="resp_feedback")

    class FakeRemedialResponses:
        def __init__(self, source_ref: SourceReference):
            self.source_ref = source_ref

        def parse(self, **kwargs):
            captured_remedial.update(kwargs)
            output = RemedialActivityOutput(
                strategy="smaller_question",
                title="One smaller attention step",
                prompt="What do relevance weights control?",
                completion_condition="Write one short sentence.",
                expected_key_points=["They control how value information is combined."],
                misconception_patterns=["They delete every lower-weight position."],
                hint_levels=["Think about values.", "Scores become weights.", "Weights control contribution."],
                source_origin="uploaded",
                source_refs=[self.source_ref],
            )
            return SimpleNamespace(status="completed", output_parsed=output, id="resp_remedial")

    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            submitted = await _submit_quiz(client)
            attempt_id = submitted["submission"]["id"]
            with connect(app.state.settings.database_path) as connection:
                row = connection.execute(
                    """
                    SELECT at.workspace_id, a.source_refs_json
                    FROM attempts at JOIN activities a ON a.id = at.activity_id
                    WHERE at.id = ?
                    """,
                    (attempt_id,),
                ).fetchone()
            source_ref = SourceReference.model_validate(json.loads(row["source_refs_json"])[0])
            settings = Settings(
                mode="real",
                database_path=app.state.settings.database_path,
                upload_dir=app.state.settings.upload_dir,
                openai_api_key="test-key",
                openai_model="gpt-5.6",
            )
            result = generate_feedback(
                settings,
                str(row["workspace_id"]),
                attempt_id,
                client_factory=lambda _settings: SimpleNamespace(responses=FakeResponses(source_ref)),
            )
            assert result["generation"]["mode"] == "real"
            remedial = create_remedial_activity(
                settings,
                str(row["workspace_id"]),
                result["feedback"]["id"],
                result["session"]["version"],
                client_factory=lambda _settings: SimpleNamespace(responses=FakeRemedialResponses(source_ref)),
            )
            assert remedial["activity"]["type"] == "remedial"
            assert remedial["remedial"]["strategy"] == "smaller_question"

    asyncio.run(scenario())
    assert captured["model"] == "gpt-5.6"
    assert captured["text_format"] is FeedbackOutput
    assert captured["store"] is False
    assert "tools" not in captured
    assert captured_remedial["model"] == "gpt-5.6"
    assert captured_remedial["text_format"] is RemedialActivityOutput
    assert captured_remedial["store"] is False
    assert "tools" not in captured_remedial


def test_tutor_close_records_observation_without_recommendation(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            focus = await prepare_focus(client)
            session_id = focus["session"]["id"]
            opened = await client.post(
                f"/api/sessions/{session_id}/tutor/open",
                json={"version": focus["session"]["version"]},
            )
            assert opened.status_code == 200
            tutor = opened.json()
            replied = await client.post(
                f"/api/sessions/{session_id}/tutor/messages",
                json={
                    "message": "I do not understand the comparison step.",
                    "quick_action": None,
                    "thread_version": tutor["thread"]["version"],
                },
            )
            assert replied.status_code == 200
            thread = replied.json()["thread"]
            closed = await client.post(
                f"/api/sessions/{session_id}/tutor/close",
                json={"thread_version": thread["version"]},
            )
            assert closed.status_code == 200
            evidence_response = await client.get(f"/api/sessions/{session_id}/evidence")
            assert evidence_response.status_code == 200
            evidence = evidence_response.json()["learning_evidence"]
            assert len(evidence) == 1
            assert evidence[0]["activity_type"] == "tutor_check"
            assert evidence[0]["outcome"] == "unresolved"
            assert evidence[0]["tutor_confusion_signals"] == [
                "User explicitly reported that part of the active concept remains unclear."
            ]
            assert "recommend" not in json.dumps(evidence).lower()

    asyncio.run(scenario())
