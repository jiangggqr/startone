"""Run an explicit, isolated GPT-5.6 smoke flow without printing credentials or content."""

from __future__ import annotations

import asyncio
from dataclasses import replace
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any

import httpx

SCRIPT_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPT_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_PROJECT_ROOT))

from app.config import PROJECT_ROOT, Settings
from app.main import create_app


def _require_live_opt_in(settings: Settings) -> None:
    if os.getenv("STARTFRAME_RUN_LIVE_SMOKE") != "1":
        raise RuntimeError("Set STARTFRAME_RUN_LIVE_SMOKE=1 to authorize real API usage.")
    if settings.mode != "real":
        raise RuntimeError("STARTFRAME_MODE must be real for the live smoke test.")
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured in the server environment.")


def _body(response: httpx.Response, label: str, expected: set[int]) -> dict[str, Any]:
    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError(f"{label} returned a non-JSON response ({response.status_code}).") from exc
    if response.status_code not in expected:
        code = payload.get("error_code", "unknown_error")
        message = payload.get("user_message", "No safe user message was returned.")
        raise RuntimeError(f"{label} failed ({response.status_code}, {code}): {message}")
    print(f"PASS {label}")
    return payload


async def _run() -> None:
    configured = Settings.from_env()
    _require_live_opt_in(configured)

    with tempfile.TemporaryDirectory(prefix="startframe-live-smoke-") as temp_dir:
        temp_root = Path(temp_dir)
        settings = replace(
            configured,
            database_path=temp_root / "smoke.sqlite3",
            upload_dir=temp_root / "uploads",
            secure_cookies=False,
        )
        app = create_app(settings)
        async with app.router.lifespan_context(app):
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://startframe-smoke.local",
                timeout=180,
            ) as client:
                health = _body(await client.get("/api/health"), "health", {200})
                if health["mode"] != "real" or health["version"] != "1.0.0":
                    raise RuntimeError("The live service did not start in the expected release mode.")

                created = _body(await client.post("/api/sessions"), "session creation", {201})
                session = created["session"]
                session_id = session["id"]

                sample_paths = [
                    PROJECT_ROOT / "sample_data" / "transformer_notes.md",
                    PROJECT_ROOT / "sample_data" / "matrix_prerequisite.md",
                ]
                files = [
                    ("files", (path.name, path.read_bytes(), "text/markdown"))
                    for path in sample_paths
                ]
                _body(
                    await client.post(f"/api/sessions/{session_id}/sources", files=files),
                    "grounded source ingestion",
                    {202},
                )
                current = _body(
                    await client.get(f"/api/sessions/{session_id}"),
                    "source-ready session",
                    {200},
                )["session"]
                prepared = None
                for generation_attempt in range(3):
                    response = await client.post(
                        f"/api/sessions/{session_id}/learning-path",
                        json={
                            "version": current["version"],
                            "show_timer": False,
                        },
                    )
                    if response.status_code == 200:
                        prepared = _body(
                            response,
                            "automatic GPT-5.6 learning path",
                            {200},
                        )
                        break
                    payload = response.json()
                    if (
                        generation_attempt < 2
                        and payload.get("error_code") == "source_reference_invalid"
                    ):
                        continue
                    _body(response, "automatic GPT-5.6 learning path", {200})
                if prepared is None:
                    raise RuntimeError("GPT-5.6 learning path retries were exhausted.")
                coverage = prepared["coverage"]
                if coverage["generation"]["model"] != settings.openai_model:
                    raise RuntimeError("Coverage did not report the configured GPT-5.6 model.")

                path = prepared["path"]
                if path["generation"]["model"] != settings.openai_model:
                    raise RuntimeError("Knowledge map did not report the configured GPT-5.6 model.")
                _body(
                    await client.post(f"/api/sessions/{session_id}/path/confirm"),
                    "path confirmation",
                    {200},
                )
                current = _body(
                    await client.get(f"/api/sessions/{session_id}"),
                    "confirmed session",
                    {200},
                )["session"]
                _body(
                    await client.put(
                        f"/api/sessions/{session_id}/drafts/start_action",
                        json={
                            "content": "Self-attention compares positions and combines relevant value information.",
                            "hint_depth": 0,
                            "version": 0,
                        },
                    ),
                    "start-action save",
                    {200},
                )
                focus = _body(
                    await client.post(
                        f"/api/sessions/{session_id}/start-action/complete",
                        json={"version": current["version"]},
                    ),
                    "focus entry",
                    {200},
                )

                tutor = _body(
                    await client.post(
                        f"/api/sessions/{session_id}/tutor/open",
                        json={"version": focus["session"]["version"]},
                    ),
                    "Tutor open",
                    {200},
                )
                tutor = _body(
                    await client.post(
                        f"/api/sessions/{session_id}/tutor/messages",
                        json={
                            "message": "Check whether I understand how attention combines information.",
                            "quick_action": "check_understanding",
                            "thread_version": tutor["thread"]["version"],
                        },
                    ),
                    "GPT-5.6 Tutor response",
                    {200},
                )
                closed = _body(
                    await client.post(
                        f"/api/sessions/{session_id}/tutor/close",
                        json={"thread_version": tutor["thread"]["version"]},
                    ),
                    "Tutor close boundary",
                    {200},
                )

                activity = _body(
                    await client.post(
                        f"/api/sessions/{session_id}/activities",
                        json={"type": "quiz", "version": closed["session"]["version"]},
                    ),
                    "GPT-5.6 Quiz generation",
                    {201},
                )
                answers = {
                    question["id"]: question["options"][0]["id"]
                    for question in activity["quiz"]["questions"]
                }
                _body(
                    await client.put(
                        f"/api/sessions/{session_id}/drafts/quiz",
                        json={
                            "content": json.dumps(answers, sort_keys=True),
                            "hint_depth": 0,
                            "version": 0,
                        },
                    ),
                    "Quiz answer save",
                    {200},
                )
                attempt = _body(
                    await client.post(
                        f"/api/activities/{activity['activity']['id']}/attempts",
                        json={"version": activity["activity"]["version"], "elapsed_seconds": 32},
                    ),
                    "Quiz submission",
                    {201},
                )
                feedback = _body(
                    await client.post(
                        f"/api/attempts/{attempt['submission']['id']}/feedback"
                    ),
                    "GPT-5.6 structured feedback",
                    {201},
                )
                evidence = feedback["evidence"]
                forbidden = {"next_action", "recommendation", "should_continue", "search_needed"}
                if forbidden.intersection(evidence):
                    raise RuntimeError("LearningEvidence contains a forbidden recommendation field.")
                completed = _body(
                    await client.post(
                        f"/api/feedback/{feedback['feedback']['id']}/complete",
                        json={"version": feedback["session"]["version"]},
                    ),
                    "evidence boundary",
                    {200},
                )
                decision = _body(
                    await client.post(f"/api/sessions/{session_id}/agent-decisions"),
                    "GPT-5.6 bounded Agent decision",
                    {201},
                )
                if decision["boundaries"]["exactly_one_recommended_action"] is not True:
                    raise RuntimeError("The Agent did not preserve the exactly-one action boundary.")
                if decision["boundaries"]["learning_performance_basis"] != "LearningEvidence only":
                    raise RuntimeError("The Agent used an invalid learning-performance basis.")
                if completed["session"]["state"] != "evidence_ready":
                    raise RuntimeError("Feedback did not finish at the evidence-ready boundary.")

                print("LIVE SMOKE PASSED: real GPT-5.6 core flow and product boundaries are valid.")


if __name__ == "__main__":
    asyncio.run(_run())
