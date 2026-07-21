import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from types import SimpleNamespace

import httpx

from app.ai import (
    CoveredConcept,
    ConceptEdge,
    ConceptOutput,
    KnowledgeMapOutput,
    SourceCoverageOutput,
    SourceReference,
    StartActionOutput,
    model_gateway_error_for_exception,
)
from app.config import Settings
from app.learning import _normalize_map_structure, _resolve_source_reference_aliases, _source_context
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


async def build_learning_path(client: httpx.AsyncClient, session: dict, *, allow_search: bool = True) -> dict:
    response = await client.post(
        f"/api/sessions/{session['id']}/learning-path",
        json={
            "version": session["version"],
            "search_permission": allow_search,
        },
    )
    assert response.status_code == 200
    return response.json()


def test_material_builds_an_automatic_learning_path_without_user_setup(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            session = await create_session(client)
            loaded = await client.post(f"/api/sessions/{session['id']}/demo-materials")
            assert loaded.status_code == 201
            session = (await client.get(f"/api/sessions/{session['id']}")).json()["session"]

            response = await client.post(
                f"/api/sessions/{session['id']}/learning-path",
                json={"version": session["version"]},
            )
            assert response.status_code == 200
            body = response.json()
            assert body["coverage"]["coverage"]["covered_concepts"]
            assert body["path"]["knowledge_map"]["concepts"]
            assert body["path"]["knowledge_map"]["recommended_route"]

            prepared = (await client.get(f"/api/sessions/{session['id']}")).json()["session"]
            assert prepared["setup_completed"] is True
            assert prepared["name"] == body["path"]["knowledge_map"]["map_title"]
            assert prepared["goal"] == f"Understand and explain {prepared['name']}."

    asyncio.run(scenario())


def test_learning_path_can_report_coverage_before_building_the_map(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            session = await create_session(client)
            await client.post(f"/api/sessions/{session['id']}/demo-materials")
            session = (await client.get(f"/api/sessions/{session['id']}")).json()["session"]

            coverage = await client.post(
                f"/api/sessions/{session['id']}/learning-path",
                json={"version": session["version"], "stage": "coverage"},
            )
            assert coverage.status_code == 200
            assert coverage.json()["coverage"]["coverage"]["covered_concepts"]
            assert coverage.json()["path"] is None
            assert (await client.get(f"/api/sessions/{session['id']}/path")).status_code == 404

            path = await client.post(f"/api/sessions/{session['id']}/path")
            assert path.status_code == 200
            assert path.json()["knowledge_map"]["concepts"]

    asyncio.run(scenario())


def test_long_source_context_samples_the_whole_document() -> None:
    chunks = [
        {
            "id": f"chunk-{index}",
            "source_id": "source-1",
            "filename": "long.pdf",
            "source_origin": "uploaded",
            "heading_path": "",
            "page_number": index,
            "start_line": None,
            "end_line": None,
            "text": f"Page {index} " + ("content " * 300),
        }
        for index in range(1, 73)
    ]

    context = _source_context(chunks)

    assert "page: 1" in context
    assert "page: 72" in context
    assert len(context) < 24_000
    assert context.count("<source_excerpt>") == 20


def test_model_reference_aliases_resolve_to_saved_source_ids() -> None:
    chunks = [
        {
            "id": "real-chunk-id",
            "source_id": "real-source-id",
            "filename": "notes.md",
            "source_origin": "uploaded",
            "heading_path": "Topic",
            "page_number": None,
            "start_line": 1,
            "end_line": 2,
            "text": "A grounded topic.",
        }
    ]
    output = SourceCoverageOutput(
        covered_concepts=[
            CoveredConcept(
                concept_key="topic",
                title="Topic",
                coverage_summary="A grounded topic.",
                source_refs=[SourceReference(source_id="source_1", chunk_id="chunk_1")],
            )
        ],
        source_gaps=[],
        ignored_sections=[],
        source_refs=[SourceReference(source_id="source_1", chunk_id="chunk_1")],
    )

    resolved = _resolve_source_reference_aliases(output, chunks)

    assert resolved.covered_concepts[0].source_refs[0] == SourceReference(
        source_id="real-source-id",
        chunk_id="real-chunk-id",
    )
    assert "real-source-id" not in _source_context(chunks)


def test_map_structure_normalization_removes_invalid_prerequisites() -> None:
    reference = SourceReference(source_id="source", chunk_id="chunk")
    output = KnowledgeMapOutput(
        map_title="Topic",
        concepts=[
            ConceptOutput(
                concept_key="foundation",
                title="Foundation",
                plain_definition="The foundation.",
                role_in_map="First.",
                prerequisite_keys=["missing"],
                estimated_minutes=2,
                source_refs=[reference],
            ),
            ConceptOutput(
                concept_key="application",
                title="Application",
                plain_definition="The application.",
                role_in_map="Second.",
                prerequisite_keys=["foundation", "missing"],
                estimated_minutes=2,
                source_refs=[reference],
            ),
        ],
        edges=[
            ConceptEdge(
                from_concept_key="missing",
                to_concept_key="application",
                relationship="prepares for",
            )
        ],
        recommended_route=["application", "foundation"],
        start_action=StartActionOutput(
            title="Start",
            instruction="Write one sentence.",
            estimated_seconds=60,
            completion_condition="One sentence is written.",
            why_this_first="It provides a starting signal.",
        ),
        source_gaps=[],
    )

    normalized = _normalize_map_structure(output)

    assert normalized.recommended_route == ["foundation", "application"]
    assert normalized.concepts[0].prerequisite_keys == []
    assert normalized.concepts[1].prerequisite_keys == ["foundation"]
    assert normalized.edges == []


def test_timeout_error_is_specific_and_recoverable() -> None:
    class APITimeoutError(Exception):
        pass

    error = model_gateway_error_for_exception(APITimeoutError())

    assert error.error_code == "openai_timeout"
    assert "longer than expected" in error.user_message
    assert "saved" in error.user_message


def test_automatic_coverage_map_adjust_and_confirm(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            session = await create_session(client)
            demo = await client.post(f"/api/sessions/{session['id']}/demo-materials")
            assert demo.status_code == 201
            assert demo.json()["created_count"] == 2

            session = (await client.get(f"/api/sessions/{session['id']}")).json()["session"]
            generated = await build_learning_path(client, session)
            coverage = generated["coverage"]
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

            path = generated["path"]
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


def test_controlled_search_demo_loads_only_the_gap_source(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            session = await create_session(client)
            response = await client.post(
                f"/api/sessions/{session['id']}/demo-materials?scenario=controlled_search"
            )
            assert response.status_code == 201
            body = response.json()
            assert body["created_count"] == 1
            assert body["scenario"] == "controlled_search"
            assert [source["filename"] for source in body["sources"]] == [
                "transformer_notes.md"
            ]

            session = (await client.get(f"/api/sessions/{session['id']}")).json()["session"]
            coverage = (await build_learning_path(client, session))["coverage"]
            gap_descriptions = [gap["description"] for gap in coverage["source_gaps"]]
            assert any("dot product" in description for description in gap_descriptions)

    asyncio.run(scenario())


def test_automatic_learning_path_uses_optimistic_version(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            session = await create_session(client)
            await client.post(f"/api/sessions/{session['id']}/demo-materials")
            current = (await client.get(f"/api/sessions/{session['id']}")).json()["session"]
            await build_learning_path(client, current)
            conflict = await client.post(
                f"/api/sessions/{session['id']}/learning-path",
                json={"version": current["version"]},
            )
            assert conflict.status_code == 409
            assert conflict.json()["error_code"] == "session_version_conflict"

    asyncio.run(scenario())


def test_invalid_automatic_path_request_uses_product_error_envelope(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            session = await create_session(client)
            response = await client.post(
                f"/api/sessions/{session['id']}/learning-path",
                json={},
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
            response = await client.post(
                f"/api/sessions/{session['id']}/learning-path",
                json={"version": session["version"]},
            )
            assert response.status_code == 503
            assert response.json()["error_code"] == "openai_key_missing"
            assert "saved" in response.json()["saved_state"].lower()

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
            response = await client.post(
                f"/api/sessions/{session['id']}/learning-path",
                json={"version": session["version"]},
            )
            assert response.status_code == 422
            assert response.json()["error_code"] == "source_reference_invalid"
            missing = await client.get(f"/api/sessions/{session['id']}/coverage")
            assert missing.status_code == 404

    asyncio.run(scenario())
