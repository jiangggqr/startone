import asyncio
from pathlib import Path
import uuid

import httpx

from app.config import AppMode, Settings
from app.db import connect, initialize_database
from app.main import create_app


def build_app(tmp_path: Path, mode: AppMode = "demo"):
    settings = Settings(
        mode=mode,
        database_path=tmp_path / "test.sqlite3",
        upload_dir=tmp_path / "uploads",
    )
    return create_app(settings)


async def request(app, path: str) -> httpx.Response:
    async with app.router.lifespan_context(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.get(path)


def test_health_initializes_versioned_database(tmp_path: Path) -> None:
    response = asyncio.run(request(build_app(tmp_path), "/api/health"))

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "mode": "demo",
        "database": "ready",
        "schema_version": 11,
        "version": "1.0.0",
    }
    assert response.headers["cache-control"] == "no-store"
    assert (tmp_path / "test.sqlite3").exists()


def test_health_does_not_create_or_touch_anonymous_workspace(tmp_path: Path) -> None:
    database_path = tmp_path / "health.sqlite3"
    app = create_app(Settings(
        mode="demo",
        database_path=database_path,
        upload_dir=tmp_path / "uploads",
    ))

    async def scenario() -> list[httpx.Response]:
        async with app.router.lifespan_context(app):
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                return [await client.get("/api/health") for _ in range(3)]

    responses = asyncio.run(scenario())

    assert all(response.status_code == 200 for response in responses)
    assert all("set-cookie" not in response.headers for response in responses)
    with connect(database_path) as connection:
        workspace_count = connection.execute("SELECT COUNT(*) FROM workspaces").fetchone()[0]
    assert workspace_count == 0


def test_homepage_serves_accessible_app_shell(tmp_path: Path) -> None:
    response = asyncio.run(request(build_app(tmp_path), "/"))

    assert response.status_code == 200
    assert 'lang="en"' in response.text
    assert 'id="main-content"' in response.text
    assert "StartOne" in response.text
    assert "Start with one clear step. Keep going until it sticks." in response.text
    assert "Upload material and start learning" in response.text
    assert "AI and technical learning first" in response.text
    assert "Build my map and start" in response.text
    assert "Start one focused step" in response.text
    assert 'id="start-action-view"' not in response.text
    assert "Verifiable preview" not in response.text
    assert "Suggested outcome" not in response.text
    assert "Recommended route" not in response.text
    assert "Practice boundary" not in response.text
    assert "Structured feedback" not in response.text
    assert "Evidence is ready for one planning decision" not in response.text
    assert 'id="activity-sources"' not in response.text
    assert 'id="evidence-ready-list"' not in response.text
    assert 'id="focus-more-panel"' not in response.text
    assert "Choose another path" not in response.text
    assert "Start one-question Quiz" not in response.text
    assert "Check this concept" in response.text
    assert "3 quick questions" in response.text
    assert "Explain it yourself" in response.text
    assert "Where this idea fits" in response.text
    assert "Memory anchor" in response.text
    assert 'id="agent-view"' not in response.text
    assert 'id="coverage-view"' not in response.text
    assert "Demo mode" not in response.text
    assert "Enter a topic only" not in response.text
    assert 'id="setup-view"' not in response.text
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["permissions-policy"].startswith("camera=()")
    assert response.headers["cross-origin-opener-policy"] == "same-origin"
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
    assert "object-src 'none'" in response.headers["content-security-policy"]


def test_public_workspace_session_quota_is_enforced(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = create_app(Settings(
            mode="demo",
            database_path=tmp_path / "quota.sqlite3",
            upload_dir=tmp_path / "uploads",
            max_sessions_per_workspace=1,
        ))
        async with app.router.lifespan_context(app):
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                first = await client.post("/api/sessions")
                second = await client.post("/api/sessions")

        assert first.status_code == 201
        assert second.status_code == 429
        assert second.json()["error_code"] == "workspace_session_quota_reached"
        assert second.json()["saved_state"] == "Your existing sessions and sources are unchanged."

    asyncio.run(scenario())


def test_restart_closes_interrupted_ai_activity(tmp_path: Path) -> None:
    database_path = tmp_path / "recovery.sqlite3"
    settings = Settings(
        mode="demo",
        database_path=database_path,
        upload_dir=tmp_path / "uploads",
    )

    async def create_running_activity() -> str:
        app = create_app(settings)
        async with app.router.lifespan_context(app):
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                session = (await client.post("/api/sessions")).json()["session"]
        activity_id = str(uuid.uuid4())
        with connect(database_path) as connection:
            row = connection.execute(
                "SELECT workspace_id FROM learning_sessions WHERE id = ?",
                (session["id"],),
            ).fetchone()
            connection.execute(
                """
                INSERT INTO ai_activity_logs(
                    id, workspace_id, session_id, operation, generation_mode, model, status
                ) VALUES (?, ?, ?, 'source_coverage', 'demo', 'deterministic-demo-v1', 'running')
                """,
                (activity_id, row["workspace_id"], session["id"]),
            )
        return activity_id

    activity_id = asyncio.run(create_running_activity())
    initialize_database(database_path)

    with connect(database_path) as connection:
        activity = connection.execute(
            "SELECT status, error_code, completed_at FROM ai_activity_logs WHERE id = ?",
            (activity_id,),
        ).fetchone()
    assert activity["status"] == "failed"
    assert activity["error_code"] == "operation_interrupted"
    assert activity["completed_at"] is not None
