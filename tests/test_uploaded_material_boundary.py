import asyncio
import json
from pathlib import Path

from app.db import _rewrite_legacy_material_boundary, connect
from tests.test_learning_path import app_client, make_app


def test_product_exposes_no_external_search_api_or_storage(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            openapi = (await client.get("/openapi.json")).json()
            paths = openapi["paths"]
            assert not any("source-search" in path for path in paths)
            assert not any("search-requests" in path for path in paths)
            assert not any("external-sources" in path for path in paths)
            assert "web_search" not in json.dumps(openapi)

            assert (await client.get("/api/sessions/missing/source-search")).status_code == 404
            assert (await client.post("/api/search-requests/missing/confirm")).status_code == 404
            assert (await client.post("/api/external-sources/missing/select")).status_code == 404

        with connect(app.state.settings.database_path) as connection:
            tables = {
                row["name"]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
            assert "search_requests" not in tables
            assert "external_sources" not in tables
            assert "concept_external_sources" not in tables

    asyncio.run(scenario())


def test_legacy_gap_and_agent_json_is_rewritten_for_more_uploads() -> None:
    legacy = {
        "source_gaps": [{"suggested_query_scope": "A short prerequisite note"}],
        "action_metadata": {
            "request_search": {
                "required_tool": "request_search",
            }
        },
    }

    assert _rewrite_legacy_material_boundary(legacy) == {
        "source_gaps": [{"requested_material": "A short prerequisite note"}],
        "action_metadata": {
            "request_more_material": {
                "required_tool": "open_material_upload",
            }
        },
    }
