import asyncio
from contextlib import asynccontextmanager
from io import BytesIO
from pathlib import Path
import sqlite3

import httpx
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

from app.config import Settings
from app.db import connect, initialize_database
from app.main import create_app


def make_app(tmp_path: Path):
    return create_app(
        Settings(
            mode="demo",
            database_path=tmp_path / "test.sqlite3",
            upload_dir=tmp_path / "uploads",
            max_file_bytes=1024 * 1024,
            max_files=5,
        )
    )


@asynccontextmanager
async def app_client(app):
    async with app.router.lifespan_context(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            yield client


async def create_session(client: httpx.AsyncClient) -> str:
    response = await client.post("/api/sessions")
    assert response.status_code == 201
    return response.json()["session"]["id"]


def text_pdf(*, blank_second_page: bool = False) -> bytes:
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    font_reference = writer._add_object(font)
    page[NameObject("/Resources")] = DictionaryObject(
        {NameObject("/Font"): DictionaryObject({NameObject("/F1"): font_reference})}
    )
    stream = DecodedStreamObject()
    stream.set_data(b"BT /F1 12 Tf 72 720 Td (Attention appears on page one.) Tj ET")
    page[NameObject("/Contents")] = writer._add_object(stream)
    if blank_second_page:
        writer.add_blank_page(width=612, height=792)
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def blank_pdf() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def test_markdown_upload_has_real_lines_and_stable_chunks(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            session_id = await create_session(client)
            material = "# Attention\n\nContext first.\n\n## Values\n\nValues are combined.\n"
            response = await client.post(
                f"/api/sessions/{session_id}/sources",
                files={"files": ("notes.md", material.encode(), "text/markdown")},
            )
            assert response.status_code == 202
            source_id = response.json()["accepted"][0]["id"]

            detail = (await client.get(f"/api/sources/{source_id}")).json()["source"]
            assert detail["parse_status"] == "success"
            assert detail["line_count"] == 7
            assert detail["source_origin"] == "uploaded"
            assert detail["chunks"][0]["heading_path"] == "Attention"
            assert detail["chunks"][0]["start_line"] == 1
            assert detail["chunks"][0]["end_line"] == 3
            first_ids = [chunk["id"] for chunk in detail["chunks"]]

            retry = await client.post(f"/api/sources/{source_id}/retry")
            assert retry.status_code == 202
            retried = (await client.get(f"/api/sources/{source_id}")).json()["source"]
            assert [chunk["id"] for chunk in retried["chunks"]] == first_ids

            search = await client.get(
                f"/api/sessions/{session_id}/source-search",
                params={"q": "combined values"},
            )
            assert search.status_code == 200
            assert search.json()["results"][0]["source_id"] == source_id

    asyncio.run(scenario())


def test_mixed_upload_reports_partial_success(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            session_id = await create_session(client)
            response = await client.post(
                f"/api/sessions/{session_id}/sources",
                files=[
                    ("files", ("valid.txt", b"A useful paragraph.", "text/plain")),
                    ("files", ("malware.exe", b"not allowed", "application/octet-stream")),
                ],
            )
            body = response.json()
            assert response.status_code == 202
            assert body["status"] == "partial_success"
            assert len(body["accepted"]) == 1
            assert body["rejected"][0]["error_code"] == "unsupported_file_type"

            sources = (await client.get(f"/api/sessions/{session_id}/sources")).json()["sources"]
            assert len(sources) == 1
            assert sources[0]["parse_status"] == "success"

    asyncio.run(scenario())


def test_public_workspace_source_quota_is_enforced(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = create_app(Settings(
            mode="demo",
            database_path=tmp_path / "quota.sqlite3",
            upload_dir=tmp_path / "uploads",
            max_sources_per_workspace=1,
        ))
        async with app_client(app) as client:
            session_id = await create_session(client)
            first = await client.post(
                f"/api/sessions/{session_id}/pasted-sources",
                json={"title": "First source", "text": "A grounded learning note."},
            )
            second = await client.post(
                f"/api/sessions/{session_id}/pasted-sources",
                json={"title": "Second source", "text": "Another grounded note."},
            )

        assert first.status_code == 202
        assert second.status_code == 429
        assert second.json()["error_code"] == "workspace_source_quota_reached"
        assert "existing sessions" in second.json()["saved_state"]

    asyncio.run(scenario())


def test_pasted_text_uses_paragraph_locations(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            session_id = await create_session(client)
            response = await client.post(
                f"/api/sessions/{session_id}/pasted-sources",
                json={"title": "Seminar notes", "text": "First point.\n\nSecond point."},
            )
            source_id = response.json()["source"]["id"]
            source = (await client.get(f"/api/sources/{source_id}")).json()["source"]
            assert source["media_kind"] == "pasted"
            assert [chunk["paragraph_number"] for chunk in source["chunks"]] == [1, 2]
            assert source["chunks"][1]["start_char"] == 14

    asyncio.run(scenario())


def test_pdf_uses_real_pages_and_reports_blank_pages(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            session_id = await create_session(client)
            response = await client.post(
                f"/api/sessions/{session_id}/sources",
                files={"files": ("lesson.pdf", text_pdf(blank_second_page=True), "application/pdf")},
            )
            source_id = response.json()["accepted"][0]["id"]
            source = (await client.get(f"/api/sources/{source_id}")).json()["source"]
            assert source["parse_status"] == "partial_success"
            assert source["page_count"] == 2
            assert source["error_code"] == "pages_without_text"
            assert source["chunks"][0]["page_number"] == 1
            assert "Attention appears" in source["chunks"][0]["text"]

    asyncio.run(scenario())


def test_scanned_pdf_has_recoverable_parse_error(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            session_id = await create_session(client)
            response = await client.post(
                f"/api/sessions/{session_id}/sources",
                files={"files": ("scan.pdf", blank_pdf(), "application/pdf")},
            )
            source_id = response.json()["accepted"][0]["id"]
            source = (await client.get(f"/api/sources/{source_id}")).json()["source"]
            assert source["parse_status"] == "error"
            assert source["error_code"] == "no_extractable_text"
            assert "selectable text" in source["error_message"]
            assert source["chunk_count"] == 0

    asyncio.run(scenario())


def test_workspace_cookie_isolates_sources(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app.router.lifespan_context(app):
            transport = httpx.ASGITransport(app=app)
            async with (
                httpx.AsyncClient(transport=transport, base_url="http://testserver") as owner,
                httpx.AsyncClient(transport=transport, base_url="http://testserver") as outsider,
            ):
                workspace_response = await owner.get("/api/health")
                set_cookie = workspace_response.headers["set-cookie"]
                assert "HttpOnly" in set_cookie
                assert "SameSite=lax" in set_cookie
                session_id = await create_session(owner)
                response = await owner.post(
                    f"/api/sessions/{session_id}/sources",
                    files={"files": ("private.txt", b"Private learning material.", "text/plain")},
                )
                source_id = response.json()["accepted"][0]["id"]

                denied = await outsider.get(f"/api/sources/{source_id}")
                assert denied.status_code == 404
                assert denied.json()["error_code"] == "source_not_found"
                assert (await outsider.get("/api/sessions")).json()["sessions"] == []

    asyncio.run(scenario())


def test_delete_last_source_removes_blob_file(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            session_id = await create_session(client)
            response = await client.post(
                f"/api/sessions/{session_id}/sources",
                files={"files": ("delete.txt", b"Delete this source.", "text/plain")},
            )
            source_id = response.json()["accepted"][0]["id"]
            assert list((tmp_path / "uploads").rglob("*.bin"))
            deleted = await client.delete(f"/api/sources/{source_id}")
            assert deleted.status_code == 204
            assert list((tmp_path / "uploads").rglob("*.bin")) == []

    asyncio.run(scenario())


def test_source_location_report_is_owned_and_exported(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app.router.lifespan_context(app):
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as owner:
                session_id = await create_session(owner)
                uploaded = await owner.post(
                    f"/api/sessions/{session_id}/sources",
                    files={"files": ("notes.md", b"# Topic\n\nGrounded text.", "text/markdown")},
                )
                source_id = uploaded.json()["accepted"][0]["id"]
                detail = (await owner.get(f"/api/sources/{source_id}")).json()["source"]
                chunk_id = detail["chunks"][0]["id"]
                report = await owner.post(
                    f"/api/sources/{source_id}/chunks/{chunk_id}/reports",
                    json={"reason": "location_incorrect", "note": "The heading boundary looks wrong."},
                )
                assert report.status_code == 201
                assert report.json()["report"]["status"] == "open"
                exported = (await owner.get("/api/export?format=json")).json()
                assert exported["source_reference_reports"][0]["chunk_id"] == chunk_id

            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as stranger:
                denied = await stranger.post(
                    f"/api/sources/{source_id}/chunks/{chunk_id}/reports",
                    json={"reason": "other", "note": "Should not be visible."},
                )
                assert denied.status_code == 404
                assert "filename" not in denied.text

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
