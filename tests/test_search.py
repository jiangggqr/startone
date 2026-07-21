import asyncio
from pathlib import Path
from types import SimpleNamespace

from app.config import Settings
from app.db import connect
from app.search import execute_search_request
from tests.test_activities import prepare_focus
from tests.test_agent import complete_quiz_evidence
from tests.test_learning_path import app_client, make_app


async def prepare_search_confirmation(client, database_path: Path) -> dict:
    focus = await prepare_focus(client, demo_scenario="controlled_search")
    session_id = focus["session"]["id"]
    opened = await client.post(
        f"/api/sessions/{session_id}/tutor/open",
        json={"version": focus["session"]["version"]},
    )
    tutor = opened.json()
    replied = await client.post(
        f"/api/sessions/{session_id}/tutor/messages",
        json={
            "message": "What is a dot product? The uploaded notes use it but do not define it.",
            "quick_action": None,
            "thread_version": tutor["thread"]["version"],
        },
    )
    closed = await client.post(
        f"/api/sessions/{session_id}/tutor/close",
        json={"thread_version": replied.json()["thread"]["version"]},
    )
    evidence_before_quiz = (
        await client.get(f"/api/sessions/{session_id}/evidence")
    ).json()["learning_evidence"]
    assert evidence_before_quiz[0]["source_gap_signal"] == (
        "The uploaded material does not define the named dot-product prerequisite."
    )
    await complete_quiz_evidence(client, closed.json(), correct=False)
    decision = (await client.post(f"/api/sessions/{session_id}/agent-decisions")).json()
    assert decision["decision"]["action"] == "request_search"
    accepted = await client.post(
        f"/api/agent-decisions/{decision['decision']['id']}/accept",
        json={"version": decision["session"]["version"]},
    )
    assert accepted.status_code == 200
    request = await client.post(f"/api/sessions/{session_id}/search-requests")
    assert request.status_code == 201
    return request.json()


def test_demo_search_revalidates_four_gates_and_attaches_one_cited_source(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            request = await prepare_search_confirmation(client, app.state.settings.database_path)
            request_id = request["search_request"]["id"]
            assert request["gates"] == {
                "session_permission": True,
                "named_gap_validated": True,
                "agent_requested_search": True,
                "user_confirmed_this_scope": False,
            }
            assert request["generation"]["internet_search_performed"] is False
            assert request["external_sources"] == []

            blocked = await client.post(
                f"/api/search-requests/{request_id}/execute",
                json={
                    "session_version": request["session"]["version"],
                    "request_version": request["search_request"]["version"],
                },
            )
            assert blocked.status_code == 409
            assert blocked.json()["error_code"] == "search_gate_failed"

            confirmed = await client.post(
                f"/api/search-requests/{request_id}/confirm",
                json={
                    "confirmed": True,
                    "session_version": request["session"]["version"],
                    "request_version": request["search_request"]["version"],
                },
            )
            assert confirmed.status_code == 200
            confirmed_body = confirmed.json()
            assert confirmed_body["gates"]["user_confirmed_this_scope"] is True

            searched = await client.post(
                f"/api/search-requests/{request_id}/execute",
                json={
                    "session_version": confirmed_body["session"]["version"],
                    "request_version": confirmed_body["search_request"]["version"],
                },
            )
            assert searched.status_code == 200
            results = searched.json()
            assert results["session"]["state"] == "search_results"
            assert results["generation"]["internet_search_performed"] is True
            assert len(results["external_sources"]) == 3
            assert all(item["source_origin"] == "external" for item in results["external_sources"])
            assert all(item["canonical_url"].startswith("https://") for item in results["external_sources"])

            selected = await client.post(
                f"/api/external-sources/{results['external_sources'][0]['id']}/select",
                json={"version": results["session"]["version"]},
            )
            assert selected.status_code == 200
            assert selected.json()["session"]["state"] == "learning_concept"
            focus = (await client.get(f"/api/sessions/{results['session']['id']}/focus")).json()
            assert len(focus["external_supplements"]) == 1
            assert focus["external_supplements"][0]["source_origin"] == "external"
            assert focus["source_policy"]["primary_origin"] == "uploaded"

    asyncio.run(scenario())


def test_declining_confirmation_never_calls_or_persists_external_search(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            request = await prepare_search_confirmation(client, app.state.settings.database_path)
            declined = await client.post(
                f"/api/search-requests/{request['search_request']['id']}/confirm",
                json={
                    "confirmed": False,
                    "session_version": request["session"]["version"],
                    "request_version": request["search_request"]["version"],
                },
            )
            assert declined.status_code == 200
            assert declined.json()["session"]["state"] == "learning_concept"
            assert declined.json()["search_request"]["search_status"] == "cancelled"
            assert declined.json()["generation"]["internet_search_performed"] is False
            with connect(app.state.settings.database_path) as connection:
                assert connection.execute("SELECT COUNT(*) AS count FROM external_sources").fetchone()["count"] == 0

    asyncio.run(scenario())


def test_real_search_uses_required_gpt56_web_search_and_only_cited_https_results(tmp_path: Path) -> None:
    captured: dict = {}
    cited_text = "A scaled dot product controls large scores before softmax."

    class FakeResponses:
        def create(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                status="completed",
                id="resp_search",
                output=[
                    SimpleNamespace(
                        type="web_search_call",
                            action=SimpleNamespace(
                            sources=[
                                {
                                    "url": "https://example.edu/attention#scaling",
                                    "title": "Attention scaling",
                                },
                                {
                                    "url": "https://uncited.example/reference",
                                    "title": "Consulted but not cited",
                                },
                            ]
                        ),
                    ),
                    SimpleNamespace(
                        type="message",
                        content=[SimpleNamespace(
                            type="output_text",
                            text=cited_text,
                            annotations=[
                                {
                                    "type": "url_citation",
                                    "start_index": 0,
                                    "end_index": len(cited_text),
                                    "url": "https://example.edu/attention#scaling",
                                    "title": "Attention scaling",
                                },
                                {
                                    "type": "url_citation",
                                    "start_index": 0,
                                    "end_index": len(cited_text),
                                    "url": "http://127.0.0.1/private",
                                    "title": "Rejected non-public URL",
                                },
                            ],
                        )],
                    ),
                ],
            )

    async def scenario() -> None:
        app = make_app(tmp_path)
        async with app_client(app) as client:
            request = await prepare_search_confirmation(client, app.state.settings.database_path)
            confirmed = (await client.post(
                f"/api/search-requests/{request['search_request']['id']}/confirm",
                json={
                    "confirmed": True,
                    "session_version": request["session"]["version"],
                    "request_version": request["search_request"]["version"],
                },
            )).json()
            with connect(app.state.settings.database_path) as connection:
                workspace_id = connection.execute(
                    "SELECT workspace_id FROM learning_sessions WHERE id = ?",
                    (request["session"]["id"],),
                ).fetchone()["workspace_id"]
            settings = Settings(
                mode="real",
                database_path=app.state.settings.database_path,
                upload_dir=app.state.settings.upload_dir,
                openai_api_key="test-key",
                openai_model="gpt-5.6",
            )
            result = execute_search_request(
                settings,
                str(workspace_id),
                confirmed["search_request"]["id"],
                confirmed["session"]["version"],
                confirmed["search_request"]["version"],
                client_factory=lambda _settings: SimpleNamespace(responses=FakeResponses()),
            )
            assert len(result["external_sources"]) == 1
            assert result["external_sources"][0]["canonical_url"] == "https://example.edu/attention"
            assert result["external_sources"][0]["citation_excerpt"] == cited_text

    asyncio.run(scenario())
    assert captured["model"] == "gpt-5.6"
    assert captured["tools"] == [{"type": "web_search", "external_web_access": True}]
    assert captured["tool_choice"] == "required"
    assert captured["include"] == ["web_search_call.action.sources"]
    assert captured["store"] is False
    assert captured["safety_identifier"]
