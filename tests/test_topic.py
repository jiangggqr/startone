import asyncio
import sqlite3
from pathlib import Path
from types import SimpleNamespace

from app.ai import TopicSectionOutput, TopicSourceOutput
from app.db import connect, initialize_database
from tests.test_learning_path import app_client, create_session, make_app, save_setup


def test_demo_topic_fallback_stays_ai_supplemental_through_practice(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            session = await create_session(client)
            created = await client.post(
                f"/api/sessions/{session['id']}/topic-source",
                json={"topic": "Self-attention"},
            )
            assert created.status_code == 201
            body = created.json()
            assert body["source"]["source_origin"] == "ai_supplement"
            assert body["generation"] == {
                "mode": "demo",
                "model": "deterministic-demo-topic-v1",
            }
            assert body["source_policy"] == {
                "source_origin": "ai_supplement",
                "uploaded_material_present": False,
                "internet_search_performed": False,
            }

            detail = await client.get(f"/api/sources/{body['source']['id']}")
            assert detail.status_code == 200
            assert detail.json()["source"]["source_origin"] == "ai_supplement"
            assert "Fixed Demo AI supplemental fixture" in detail.json()["source"]["chunks"][0]["text"]

            current = (await client.get(f"/api/sessions/{session['id']}")).json()["session"]
            current = await save_setup(client, current)
            coverage = (await client.post(f"/api/sessions/{session['id']}/coverage")).json()
            assert {item["source_origin"] for item in coverage["source_ref_details"]} == {"ai_supplement"}
            path = (await client.post(f"/api/sessions/{session['id']}/path")).json()
            assert {item["source_origin"] for item in path["source_ref_details"]} == {"ai_supplement"}
            await client.post(f"/api/sessions/{session['id']}/path/confirm")
            saved = await client.put(
                f"/api/sessions/{session['id']}/drafts/start_action",
                json={"content": "It compares positions and combines relevant information.", "hint_depth": 0, "version": 0},
            )
            assert saved.status_code == 200
            start_session = (await client.get(f"/api/sessions/{session['id']}")).json()["session"]
            focused = await client.post(
                f"/api/sessions/{session['id']}/start-action/complete",
                json={"version": start_session["version"]},
            )
            assert focused.status_code == 200
            focus = focused.json()
            assert focus["source_policy"]["primary_origin"] == "ai_supplement"
            assert {item["source_origin"] for item in focus["active_concept"]["source_ref_details"]} == {"ai_supplement"}
            quiz = await client.post(
                f"/api/sessions/{session['id']}/activities",
                json={"type": "quiz", "version": focus["session"]["version"]},
            )
            assert quiz.status_code == 201
            assert quiz.json()["activity"]["source_origin"] == "ai_supplement"

            activity = await client.get("/api/ai-activity")
            topic_log = next(item for item in activity.json()["activities"] if item["operation"] == "generate_topic_source")
            assert topic_log["generation_mode"] == "demo"
            assert topic_log["status"] == "completed"

    asyncio.run(scenario())


def test_demo_topic_fallback_rejects_non_fixture_topic_without_saving_source(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            session = await create_session(client)
            response = await client.post(
                f"/api/sessions/{session['id']}/topic-source",
                json={"topic": "Quantum field theory"},
            )
            assert response.status_code == 422
            assert response.json()["error_code"] == "demo_topic_unavailable"
            sources = await client.get(f"/api/sessions/{session['id']}/sources")
            assert sources.json()["sources"] == []

    asyncio.run(scenario())


def test_real_topic_fallback_uses_structured_server_call_without_tools(tmp_path: Path) -> None:
    captured = {}

    class FakeResponses:
        def parse(self, **kwargs):
            captured.update(kwargs)
            output = TopicSourceOutput(
                title="Bayes' theorem",
                overview="Bayes' theorem updates a prior probability after new evidence is observed in a defined probability model.",
                sections=[
                    TopicSectionOutput(
                        heading="Prior and likelihood",
                        explanation="The prior represents the starting belief, while the likelihood describes how compatible the observed evidence is with each hypothesis.",
                    ),
                    TopicSectionOutput(
                        heading="Posterior",
                        explanation="The posterior combines prior belief and evidence, then normalizes the result so the updated possibilities form a probability distribution.",
                    ),
                ],
                verification_note="Verify assumptions and consequential uses with a trusted course source.",
            )
            return SimpleNamespace(status="completed", output_parsed=output, id="resp_topic")

    def factory(_settings):
        return SimpleNamespace(responses=FakeResponses())

    async def scenario() -> None:
        app = make_app(tmp_path, mode="real", key="test-key", factory=factory)
        async with app_client(app) as client:
            session = await create_session(client)
            response = await client.post(
                f"/api/sessions/{session['id']}/topic-source",
                json={"topic": "Bayes' theorem"},
            )
            assert response.status_code == 201
            assert response.json()["source"]["source_origin"] == "ai_supplement"
            assert captured["model"] == "gpt-5.6"
            assert captured["store"] is False
            assert "tools" not in captured
            assert captured["text_format"] is TopicSourceOutput
            assert "<untrusted_topic>Bayes' theorem</untrusted_topic>" in captured["input"][1]["content"]

    asyncio.run(scenario())


def test_schema_10_migrates_existing_sources_without_losing_child_rows(tmp_path: Path) -> None:
    database_path = tmp_path / "old.sqlite3"
    connection = sqlite3.connect(database_path)
    connection.executescript(
        """
        PRAGMA foreign_keys = ON;
        CREATE TABLE schema_migrations(version INTEGER PRIMARY KEY, applied_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE workspaces(id TEXT PRIMARY KEY);
        CREATE TABLE learning_sessions(id TEXT PRIMARY KEY, workspace_id TEXT REFERENCES workspaces(id) ON DELETE CASCADE);
        CREATE TABLE source_blobs(id TEXT PRIMARY KEY, workspace_id TEXT REFERENCES workspaces(id), checksum TEXT, storage_path TEXT, byte_size INTEGER);
        CREATE TABLE source_documents(
            id TEXT PRIMARY KEY,
            workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
            session_id TEXT NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
            blob_id TEXT NOT NULL REFERENCES source_blobs(id),
            filename TEXT NOT NULL,
            media_type TEXT NOT NULL,
            media_kind TEXT NOT NULL CHECK(media_kind IN ('pdf', 'markdown', 'text', 'pasted')),
            source_origin TEXT NOT NULL DEFAULT 'uploaded' CHECK(source_origin = 'uploaded'),
            parse_status TEXT NOT NULL,
            page_count INTEGER,
            line_count INTEGER,
            error_code TEXT,
            error_message TEXT,
            version INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX idx_sources_session_created ON source_documents(session_id, created_at);
        CREATE TABLE source_chunks(
            id TEXT PRIMARY KEY,
            source_id TEXT NOT NULL REFERENCES source_documents(id) ON DELETE CASCADE,
            heading_path TEXT, page_number INTEGER, page_chunk_index INTEGER,
            paragraph_number INTEGER, start_line INTEGER, end_line INTEGER,
            start_char INTEGER NOT NULL, end_char INTEGER NOT NULL,
            text TEXT NOT NULL, search_text TEXT NOT NULL, checksum TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        INSERT INTO schema_migrations(version) VALUES (1),(2),(3),(4),(5),(6),(7),(8),(9);
        INSERT INTO workspaces(id) VALUES ('workspace');
        INSERT INTO learning_sessions(id, workspace_id) VALUES ('session', 'workspace');
        INSERT INTO source_blobs(id, workspace_id, checksum, storage_path, byte_size)
            VALUES ('blob', 'workspace', 'sum', '/tmp/old', 4);
        INSERT INTO source_documents(id, workspace_id, session_id, blob_id, filename, media_type, media_kind, parse_status)
            VALUES ('source', 'workspace', 'session', 'blob', 'notes.md', 'text/markdown', 'markdown', 'success');
        INSERT INTO source_chunks(id, source_id, start_char, end_char, text, search_text, checksum)
            VALUES ('chunk', 'source', 0, 4, 'text', 'text', 'sum');
        """
    )
    connection.close()

    initialize_database(database_path)
    with connect(database_path) as migrated:
        assert migrated.execute("SELECT source_origin FROM source_documents WHERE id = 'source'").fetchone()[0] == "uploaded"
        assert migrated.execute("SELECT source_id FROM source_chunks WHERE id = 'chunk'").fetchone()[0] == "source"
        assert migrated.execute("PRAGMA foreign_key_check").fetchall() == []
        migrated.execute("UPDATE source_documents SET source_origin = 'ai_supplement' WHERE id = 'source'")

