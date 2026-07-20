import asyncio
from pathlib import Path

import httpx

from app.config import AppMode, Settings
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
        "schema_version": 2,
        "version": "0.2.0",
    }
    assert (tmp_path / "test.sqlite3").exists()


def test_homepage_serves_accessible_app_shell(tmp_path: Path) -> None:
    response = asyncio.run(request(build_app(tmp_path), "/"))

    assert response.status_code == 200
    assert 'lang="en"' in response.text
    assert 'id="main-content"' in response.text
    assert "Demo mode" in response.text
    assert "Upload material and start a session" in response.text
    assert response.headers["x-content-type-options"] == "nosniff"
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
