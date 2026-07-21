import asyncio
from pathlib import Path
from types import SimpleNamespace

from app.ai import SourceReference, TutorResponseOutput
from app.config import Settings
from app.db import connect
from app.tutor import send_tutor_message
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


def test_demo_tutor_stays_grounded_and_persists_conversation(tmp_path: Path) -> None:
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
            assert tutor["messages"] == []
            assert tutor["boundaries"] == {
                "active_concept_only": True,
                "can_change_route": False,
                "can_search": False,
                "creates_agent_decision": False,
            }
            assert len(tutor["quick_actions"]) == 6

            checked = await client.post(
                f"/api/sessions/{session_id}/tutor/messages",
                json={
                    "message": "Check my understanding",
                    "quick_action": "check_understanding",
                    "thread_version": tutor["thread"]["version"],
                },
            )
            assert checked.status_code == 200
            tutor = checked.json()
            assert tutor["generation"] == {
                "mode": "demo",
                "model": "deterministic-demo-tutor-v1",
                "internet_search_performed": False,
            }
            assert [message["role"] for message in tutor["messages"]] == ["user", "tutor"]
            reply = tutor["messages"][-1]
            assert reply["source_origin"] == "uploaded"
            assert reply["source_refs"]
            assert reply["source_ref_details"][0]["source_origin"] == "uploaded"
            assert reply["guidance_level"] == 7
            assert reply["checking_question"]
            assert "recommendation" not in reply
            assert "next_action" not in reply

            confused = await client.post(
                f"/api/sessions/{session_id}/tutor/messages",
                json={
                    "message": "I am still confused about the combination step.",
                    "quick_action": None,
                    "thread_version": tutor["thread"]["version"],
                },
            )
            assert confused.status_code == 200
            tutor = confused.json()
            assert tutor["messages"][-1]["confusion_signal"]
            assert tutor["messages"][-1]["prerequisite_gap_signal"] is None

            restored = await client.get(f"/api/sessions/{session_id}/tutor/messages")
            assert restored.status_code == 200
            assert len(restored.json()["messages"]) == 4
            assert restored.json()["thread"]["version"] == tutor["thread"]["version"]

    asyncio.run(scenario())


def test_demo_tutor_labels_ai_example_and_covered_prerequisite(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            focus = await prepare_focus(client)
            session_id = focus["session"]["id"]
            tutor = (
                await client.post(
                    f"/api/sessions/{session_id}/tutor/open",
                    json={"version": focus["session"]["version"]},
                )
            ).json()
            example = await client.post(
                f"/api/sessions/{session_id}/tutor/messages",
                json={
                    "message": "Give a concrete example",
                    "quick_action": "concrete_example",
                    "thread_version": tutor["thread"]["version"],
                },
            )
            assert example.status_code == 200
            tutor = example.json()
            assert tutor["messages"][-1]["source_origin"] == "ai_supplement"
            assert tutor["messages"][-1]["message"].startswith("AI supplemental example:")

            prerequisite = await client.post(
                f"/api/sessions/{session_id}/tutor/messages",
                json={
                    "message": "What is the dot product doing here?",
                    "thread_version": tutor["thread"]["version"],
                },
            )
            assert prerequisite.status_code == 200
            reply = prerequisite.json()["messages"][-1]
            assert reply["prerequisite_gap_signal"] is None
            assert reply["source_ref_details"][0]["filename"] == "matrix_prerequisite.md"

    asyncio.run(scenario())


def test_tutor_pause_close_reopen_and_version_guards(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            focus = await prepare_focus(client)
            session_id = focus["session"]["id"]
            tutor = (
                await client.post(
                    f"/api/sessions/{session_id}/tutor/open",
                    json={"version": focus["session"]["version"]},
                )
            ).json()
            stale = await client.post(
                f"/api/sessions/{session_id}/tutor/messages",
                json={
                    "message": "Give only a hint",
                    "quick_action": "hint_only",
                    "thread_version": tutor["thread"]["version"] + 1,
                },
            )
            assert stale.status_code == 409
            assert stale.json()["error_code"] == "tutor_version_conflict"

            paused = await client.post(
                f"/api/sessions/{session_id}/pause",
                json={"version": tutor["session"]["version"]},
            )
            assert paused.status_code == 200
            blocked = await client.post(
                f"/api/sessions/{session_id}/tutor/messages",
                json={
                    "message": "Explain more simply",
                    "quick_action": "simplify",
                    "thread_version": tutor["thread"]["version"],
                },
            )
            assert blocked.status_code == 409
            assert blocked.json()["error_code"] == "session_paused"
            resumed = await client.post(
                f"/api/sessions/{session_id}/resume",
                json={"version": paused.json()["session"]["version"]},
            )
            assert resumed.status_code == 200

            closed = await client.post(
                f"/api/sessions/{session_id}/tutor/close",
                json={"thread_version": tutor["thread"]["version"]},
            )
            assert closed.status_code == 200
            focus_after_close = closed.json()
            assert focus_after_close["session"]["tutor_open"] is False

            reopened = await client.post(
                f"/api/sessions/{session_id}/tutor/open",
                json={"version": focus_after_close["session"]["version"]},
            )
            assert reopened.status_code == 200
            assert reopened.json()["thread"]["id"] == tutor["thread"]["id"]
            assert reopened.json()["thread"]["version"] > tutor["thread"]["version"]

    asyncio.run(scenario())


def test_real_tutor_uses_structured_gpt56_path_without_tools(tmp_path: Path) -> None:
    captured = {}

    class FakeResponses:
        def __init__(self, source_ref):
            self.source_ref = source_ref

        def parse(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                status="completed",
                id="resp_tutor_test",
                output_parsed=TutorResponseOutput(
                    message="Compare relevance first, then combine value information using those weights.",
                    guidance_level=3,
                    checking_question="What happens after comparison?",
                    source_origin="uploaded",
                    source_refs=[self.source_ref],
                    confusion_signal=None,
                    prerequisite_gap_signal=None,
                ),
            )

    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            focus = await prepare_focus(client)
            session_id = focus["session"]["id"]
            tutor = (
                await client.post(
                    f"/api/sessions/{session_id}/tutor/open",
                    json={"version": focus["session"]["version"]},
                )
            ).json()
            source_ref = SourceReference.model_validate(tutor["context"]["concept"]["source_refs"][0])
            with connect(app.state.settings.database_path) as connection:
                workspace_id = str(
                    connection.execute(
                        "SELECT workspace_id FROM learning_sessions WHERE id = ?",
                        (session_id,),
                    ).fetchone()["workspace_id"]
                )
            real_settings = Settings(
                mode="real",
                database_path=app.state.settings.database_path,
                upload_dir=app.state.settings.upload_dir,
                openai_api_key="test-key",
                openai_model="gpt-5.6",
            )
            result = send_tutor_message(
                real_settings,
                workspace_id,
                session_id,
                "I understand comparison, but what happens next?",
                None,
                tutor["thread"]["version"],
                client_factory=lambda _settings: SimpleNamespace(responses=FakeResponses(source_ref)),
            )
            assert result["generation"]["mode"] == "real"
            assert result["messages"][-1]["source_origin"] == "uploaded"

    asyncio.run(scenario())
    assert captured["model"] == "gpt-5.6"
    assert captured["text_format"] is TutorResponseOutput
    assert captured["store"] is False
    assert "tools" not in captured
