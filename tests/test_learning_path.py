import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from types import SimpleNamespace

import httpx

from app.ai import CoveredConcept, SourceCoverageOutput, SourceReference
from app.config import Settings
from app.main import create_app


def make_app(tmp_path: Path, *, mode: str = "demo", key: str | None = None, factory=None):
    settings = Settings(
        mode=mode,  # type: ignore[arg-type]
        database_path=tmp_path / "test.sqlite3",
        upload_dir=tmp_path / "uploads",
        openai_api_key=key,
    )
    return create_app(settings, ai_client_factory=factory)


@asynccontextmanager
async def app_client(app):
    async with app.router.lifespan_context(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            yield client


async def create_session(client: httpx.AsyncClient) -> dict:
    response = await client.post("/api/sessions")
    assert response.status_code == 201
    return response.json()["session"]


async def save_setup(client: httpx.AsyncClient, session: dict) -> dict:
    response = await client.patch(
        f"/api/sessions/{session['id']}",
        json={
            "goal": "Understand self-attention in a focused study session",
            "prior_knowledge": "Basic machine learning",
            "available_minutes": 25,
            "energy_level": "medium",
            "current_question": "How do attention scores change a token representation?",
            "support_preferences": ["direct_explanation", "define_terms", "short_steps"],
            "show_timer": False,
            "search_permission": True,
            "version": session["version"],
        },
    )
    assert response.status_code == 200
    return response.json()["session"]


def test_demo_setup_coverage_map_adjust_and_confirm(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            session = await create_session(client)
            demo = await client.post(f"/api/sessions/{session['id']}/demo-materials")
            assert demo.status_code == 201
            assert demo.json()["created_count"] == 2

            session = (await client.get(f"/api/sessions/{session['id']}")).json()["session"]
            session = await save_setup(client, session)
            assert session["language"] == "English"
            assert session["setup_completed"] is True

            coverage_response = await client.post(f"/api/sessions/{session['id']}/coverage")
            assert coverage_response.status_code == 200
            coverage = coverage_response.json()
            assert [item["title"] for item in coverage["coverage"]["covered_concepts"]] == [
                "Transformer goal",
                "Self-attention",
                "Query, Key, and Value",
                "Scaled dot-product attention",
                "Positional information",
            ]
            assert coverage["generation"] == {
                "mode": "demo",
                "model": "deterministic-demo-v1",
                "internet_search_performed": False,
            }
            assert all(gap["status"] == "candidate" for gap in coverage["source_gaps"])
            assert all(detail["source_origin"] == "uploaded" for detail in coverage["source_ref_details"])

            path_response = await client.post(f"/api/sessions/{session['id']}/path")
            assert path_response.status_code == 200
            path = path_response.json()
            expected_route = [
                "transformer_goal",
                "self_attention",
                "qkv",
                "scaled_dot_product",
                "positional_information",
            ]
            assert path["knowledge_map"]["recommended_route"] == expected_route
            assert 60 <= path["knowledge_map"]["start_action"]["estimated_seconds"] <= 120
            assert path["confirmed"] is False

            adjusted = await client.patch(
                f"/api/sessions/{session['id']}/path",
                json={"route_concept_keys": expected_route[:3]},
            )
            assert adjusted.status_code == 200
            assert adjusted.json()["knowledge_map"]["recommended_route"] == expected_route[:3]

            invalid_route = await client.patch(
                f"/api/sessions/{session['id']}/path",
                json={"route_concept_keys": ["transformer_goal", "scaled_dot_product"]},
            )
            assert invalid_route.status_code == 400
            assert invalid_route.json()["error_code"] == "invalid_learning_route_prerequisite"

            confirmed = await client.post(f"/api/sessions/{session['id']}/path/confirm")
            assert confirmed.status_code == 200
            assert confirmed.json()["confirmed"] is True
            final_session = (await client.get(f"/api/sessions/{session['id']}")).json()["session"]
            assert final_session["state"] == "start_action"

    asyncio.run(scenario())


def test_setup_uses_optimistic_version(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            session = await create_session(client)
            await save_setup(client, session)
            conflict = await client.patch(
                f"/api/sessions/{session['id']}",
                json={
                    "goal": "A changed goal that remains in the browser",
                    "prior_knowledge": "Beginner",
                    "available_minutes": 15,
                    "energy_level": "low",
                    "support_preferences": [],
                    "show_timer": False,
                    "search_permission": False,
                    "version": session["version"],
                },
            )
            assert conflict.status_code == 409
            assert conflict.json()["error_code"] == "session_version_conflict"

    asyncio.run(scenario())


def test_invalid_setup_uses_product_error_envelope(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            session = await create_session(client)
            response = await client.patch(
                f"/api/sessions/{session['id']}",
                json={"goal": "No"},
            )
            assert response.status_code == 422
            body = response.json()
            assert body["error_code"] == "request_validation_failed"
            assert body["recoverable"] is True
            assert body["field_errors"]
            assert "input" not in body

    asyncio.run(scenario())


def test_real_mode_without_key_fails_explicitly(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path, mode="real")
        async with app_client(app) as client:
            session = await create_session(client)
            upload = await client.post(
                f"/api/sessions/{session['id']}/sources",
                files={"files": ("notes.md", b"# Topic\n\nA grounded idea.", "text/markdown")},
            )
            assert upload.status_code == 202
            session = (await client.get(f"/api/sessions/{session['id']}")).json()["session"]
            await save_setup(client, session)
            response = await client.post(f"/api/sessions/{session['id']}/coverage")
            assert response.status_code == 503
            assert response.json()["error_code"] == "openai_key_missing"
            assert "sources are saved" in response.json()["user_message"]

    asyncio.run(scenario())


def test_invalid_model_source_reference_is_never_persisted(tmp_path: Path) -> None:
    class FakeResponses:
        def parse(self, **kwargs):
            output = SourceCoverageOutput(
                covered_concepts=[
                    CoveredConcept(
                        concept_key="topic",
                        title="Topic",
                        coverage_summary="A generated summary.",
                        source_refs=[SourceReference(source_id="missing", chunk_id="missing")],
                    )
                ],
                source_gaps=[],
                ignored_sections=[],
                source_refs=[SourceReference(source_id="missing", chunk_id="missing")],
            )
            return SimpleNamespace(status="completed", output_parsed=output, id="resp_test")

    def factory(_settings):
        return SimpleNamespace(responses=FakeResponses())

    async def scenario() -> None:
        app = make_app(tmp_path, mode="real", key="test-key", factory=factory)
        async with app_client(app) as client:
            session = await create_session(client)
            await client.post(
                f"/api/sessions/{session['id']}/sources",
                files={"files": ("notes.md", b"# Topic\n\nA grounded idea.", "text/markdown")},
            )
            session = (await client.get(f"/api/sessions/{session['id']}")).json()["session"]
            await save_setup(client, session)
            response = await client.post(f"/api/sessions/{session['id']}/coverage")
            assert response.status_code == 422
            assert response.json()["error_code"] == "source_reference_invalid"
            missing = await client.get(f"/api/sessions/{session['id']}/coverage")
            assert missing.status_code == 404

    asyncio.run(scenario())
