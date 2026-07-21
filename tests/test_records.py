import asyncio
import json
from pathlib import Path

from app.db import connect
from tests.test_activities import prepare_focus
from tests.test_learning_path import app_client, create_session, make_app


def test_session_copy_shares_blob_until_last_session_is_deleted(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            session = await create_session(client)
            loaded = await client.post(f"/api/sessions/{session['id']}/demo-materials")
            assert loaded.status_code == 201
            with connect(app.state.settings.database_path) as connection:
                blob_rows = connection.execute(
                    "SELECT id, storage_path FROM source_blobs ORDER BY id"
                ).fetchall()
                original_blob_ids = {row["id"] for row in blob_rows}
                original_paths = [Path(row["storage_path"]) for row in blob_rows]
            assert len(original_blob_ids) == 2
            assert all(path.exists() for path in original_paths)

            copied = await client.post(f"/api/sessions/{session['id']}/copy")
            assert copied.status_code == 201
            copied_session = copied.json()["session"]
            assert copied_session["name"].startswith("Copy of")
            assert copied_session["source_count"] == 2
            with connect(app.state.settings.database_path) as connection:
                assert connection.execute("SELECT COUNT(*) AS count FROM source_blobs").fetchone()["count"] == 2
                assert connection.execute("SELECT COUNT(*) AS count FROM source_documents").fetchone()["count"] == 4

            deleted_original = await client.delete(f"/api/sessions/{session['id']}")
            assert deleted_original.status_code == 200
            assert deleted_original.json()["removed_unreferenced_blobs"] == 0
            assert all(path.exists() for path in original_paths)

            deleted_copy = await client.delete(f"/api/sessions/{copied_session['id']}")
            assert deleted_copy.status_code == 200
            assert deleted_copy.json()["removed_unreferenced_blobs"] == 2
            assert deleted_copy.json()["file_cleanup_complete"] is True
            assert all(not path.exists() for path in original_paths)

    asyncio.run(scenario())


def test_export_ai_activity_summary_and_workspace_delete(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            focus = await prepare_focus(client)
            session_id = focus["session"]["id"]

            summary = await client.get(f"/api/sessions/{session_id}/summary")
            assert summary.status_code == 200
            summary_body = summary.json()["summary"]
            assert summary_body["current_concept"] == "Self-attention"
            assert summary_body["restart_action"].startswith("For two minutes")
            assert summary_body["penalty_for_stopping"] is False

            activity_log = await client.get("/api/ai-activity")
            assert activity_log.status_code == 200
            assert {item["operation"] for item in activity_log.json()["activities"]} >= {
                "source_coverage",
                "knowledge_map",
            }
            assert all("response_id" not in item for item in activity_log.json()["activities"])

            exported = await client.get("/api/export?format=json")
            assert exported.status_code == 200
            assert "attachment" in exported.headers["content-disposition"]
            assert exported.headers["cache-control"] == "no-store"
            data = exported.json()
            assert data["sessions"][0]["id"] == session_id
            assert data["source_chunks"]
            serialized = json.dumps(data).lower()
            assert "storage_path" not in serialized
            assert "response_id" not in serialized
            assert "openai_api_key" not in serialized
            assert "correct_option_id" not in serialized

            markdown = await client.get("/api/export?format=markdown")
            assert markdown.status_code == 200
            assert markdown.text.startswith("# StartFrame Agent learning record")
            assert "## Understand self-attention" in markdown.text

            with connect(app.state.settings.database_path) as connection:
                paths = [
                    Path(row["storage_path"])
                    for row in connection.execute("SELECT storage_path FROM source_blobs").fetchall()
                ]
            deleted = await client.delete("/api/user-data")
            assert deleted.status_code == 200
            assert deleted.json()["deleted_sessions"] == 1
            assert deleted.json()["file_cleanup_complete"] is True
            assert all(not path.exists() for path in paths)
            sessions = await client.get("/api/sessions")
            assert sessions.status_code == 200
            assert sessions.json()["sessions"] == []

    asyncio.run(scenario())
