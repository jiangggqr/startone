import asyncio
from pathlib import Path

from tests.test_learning_path import app_client, build_learning_path, create_session, make_app


async def prepare_start_action(client, *, demo_scenario: str = "standard"):
    session = await create_session(client)
    await client.post(
        f"/api/sessions/{session['id']}/demo-materials?scenario={demo_scenario}"
    )
    session = (await client.get(f"/api/sessions/{session['id']}")).json()["session"]
    await build_learning_path(client, session)
    await client.post(f"/api/sessions/{session['id']}/path/confirm")
    return (await client.get(f"/api/sessions/{session['id']}")).json()["session"]


def test_versioned_drafts_preserve_both_conflict_copies(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            session = await prepare_start_action(client)
            first = await client.put(
                f"/api/sessions/{session['id']}/drafts/start_action",
                json={"content": "It compares tokens.", "hint_depth": 0, "version": 0},
            )
            assert first.status_code == 200
            assert first.json()["draft"]["server_version"] == 1

            conflict = await client.put(
                f"/api/sessions/{session['id']}/drafts/start_action",
                json={"content": "It compares and combines token information.", "hint_depth": 0, "version": 0},
            )
            assert conflict.status_code == 409
            body = conflict.json()
            assert body["error_code"] == "draft_version_conflict"
            assert body["details"]["server_draft"]["content"] == "It compares tokens."
            assert body["details"]["local_draft"]["content"] == "It compares and combines token information."

            resolved = await client.post(
                f"/api/sessions/{session['id']}/draft-conflicts/start_action/resolve",
                json={
                    "choice": "local",
                    "local_content": "It compares and combines token information.",
                    "server_version": 1,
                    "hint_depth": 0,
                },
            )
            assert resolved.status_code == 200
            assert resolved.json()["draft"]["server_version"] == 2
            assert resolved.json()["draft"]["content"].endswith("information.")

    asyncio.run(scenario())


def test_start_focus_pause_resume_and_refresh_recovery(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            session = await prepare_start_action(client)
            draft = await client.put(
                f"/api/sessions/{session['id']}/drafts/start_action",
                json={
                    "content": "Self-attention compares related positions and brings their information together.",
                    "hint_depth": 0,
                    "version": 0,
                },
            )
            assert draft.status_code == 200
            started = await client.post(
                f"/api/sessions/{session['id']}/start-action/complete",
                json={"version": session["version"]},
            )
            assert started.status_code == 200
            focus = started.json()
            assert focus["session"]["state"] == "learning_concept"
            assert focus["active_concept"]["concept_key"] == "self_attention"
            assert focus["progress"] == {"current": 2, "total": 5, "completed": 1}
            assert focus["source_policy"] == {
                "primary_origin": "uploaded",
                "internet_search_performed": False,
            }
            assert focus["active_concept"]["source_ref_details"][0]["source_origin"] == "uploaded"

            note = await client.put(
                f"/api/sessions/{session['id']}/drafts/focus_note",
                json={"content": "I want to clarify the weighted combination.", "hint_depth": 0, "version": 0},
            )
            assert note.status_code == 200

            paused = await client.post(
                f"/api/sessions/{session['id']}/pause",
                json={"version": focus["session"]["version"]},
            )
            assert paused.status_code == 200
            paused_session = paused.json()["session"]
            assert paused_session["is_paused"] is True
            assert paused_session["resume_state"] == "learning_concept"
            blocked = await client.put(
                f"/api/sessions/{session['id']}/drafts/focus_note",
                json={"content": "A mutation while paused", "hint_depth": 0, "version": 1},
            )
            assert blocked.status_code == 409
            assert blocked.json()["error_code"] == "session_paused"

            resumed = await client.post(
                f"/api/sessions/{session['id']}/resume",
                json={"version": paused_session["version"]},
            )
            assert resumed.status_code == 200
            assert resumed.json()["session"]["is_paused"] is False
            restored = await client.get(f"/api/sessions/{session['id']}/focus")
            assert restored.status_code == 200
            restored_body = restored.json()
            assert restored_body["drafts"]["start_action"]["content"].startswith("Self-attention")
            assert restored_body["drafts"]["focus_note"]["content"].endswith("combination.")
            assert restored_body["restart_action"].startswith("Resume Self-attention")

    asyncio.run(scenario())


def test_start_action_requires_a_saved_checkable_answer(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            session = await prepare_start_action(client)
            response = await client.post(
                f"/api/sessions/{session['id']}/start-action/complete",
                json={"version": session["version"]},
            )
            assert response.status_code == 422
            assert response.json()["error_code"] == "start_action_incomplete"

    asyncio.run(scenario())
