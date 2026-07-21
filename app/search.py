"""Four-gate external search, citations, selection, and recovery."""

from __future__ import annotations

from datetime import UTC, datetime
import ipaddress
import json
from pathlib import Path
import re
from typing import Any, Callable
from urllib.parse import urlsplit, urlunsplit
import uuid

from app.config import Settings
from app.db import connect
from app.sources import SourceError, get_session


DEMO_SEARCH_MODEL = "deterministic-demo-search-v1"


def get_or_create_search_request(
    settings: Settings,
    workspace_id: str,
    session_id: str,
) -> dict[str, Any]:
    """Create one confirmation record for the accepted Agent search request."""

    session = get_session(settings.database_path, workspace_id, session_id)
    if session.get("is_paused"):
        raise SourceError(
            "session_paused",
            "Resume the session before reviewing the search request.",
            status_code=409,
            saved_state="The named gap and Agent decision remain saved.",
        )
    if session["state"] not in {"search_confirmation", "search_running", "search_results"}:
        raise SourceError(
            "search_confirmation_not_available",
            "The Planning Agent has not requested an external search at this step.",
            status_code=409,
            saved_state="Your current learning state is unchanged.",
        )
    with connect(settings.database_path) as connection:
        decision = connection.execute(
            """
            SELECT * FROM agent_decisions
            WHERE workspace_id = ? AND session_id = ?
              AND status IN ('accepted', 'overridden')
              AND COALESCE(selected_action, action) = 'request_search'
            ORDER BY resolved_at DESC, rowid DESC LIMIT 1
            """,
            (workspace_id, session_id),
        ).fetchone()
        if not decision:
            raise SourceError(
                "agent_search_request_missing",
                "A resolved Planning Agent search request is required before confirmation.",
                status_code=409,
            )
        existing = connection.execute(
            "SELECT id FROM search_requests WHERE agent_decision_id = ? AND workspace_id = ?",
            (decision["id"], workspace_id),
        ).fetchone()
        if existing:
            return get_search_request(settings.database_path, workspace_id, str(existing["id"]))

        snapshot = json.loads(str(decision["evidence_snapshot_json"]))
        selected = str(decision["selected_action"] or decision["action"])
        metadata = snapshot.get("action_metadata", {}).get(selected, {})
        gap_id = metadata.get("source_gap_id")
        gap = connection.execute(
            """
            SELECT * FROM source_gaps
            WHERE id = ? AND workspace_id = ? AND session_id = ? AND status = 'validated'
            """,
            (gap_id, workspace_id, session_id),
        ).fetchone()
        if not gap:
            raise SourceError(
                "validated_source_gap_missing",
                "The named source gap is no longer validated, so search cannot be confirmed.",
                status_code=409,
                saved_state="No external request has run.",
            )
        request_id = str(uuid.uuid4())
        connection.execute(
            """
            INSERT INTO search_requests(
                id, workspace_id, session_id, concept_id, source_gap_id,
                agent_decision_id, query_scope, reason_for_user,
                permission_snapshot, generation_mode, model
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request_id,
                workspace_id,
                session_id,
                decision["concept_id"],
                gap["id"],
                decision["id"],
                gap["suggested_query_scope"],
                decision["reason_for_user"],
                int(bool(session.get("search_permission"))),
                settings.mode,
                DEMO_SEARCH_MODEL if settings.mode == "demo" else settings.openai_model,
            ),
        )
        _record_event(
            connection,
            workspace_id,
            session_id,
            "search_confirmation_created",
            {
                "search_request_id": request_id,
                "source_gap_id": gap["id"],
                "internet_search_performed": False,
            },
        )
    return get_search_request(settings.database_path, workspace_id, request_id)


def get_search_request(
    database_path: Path,
    workspace_id: str,
    request_id: str,
) -> dict[str, Any]:
    with connect(database_path) as connection:
        row = connection.execute(
            """
            SELECT r.*, g.description AS gap_description, g.why_needed AS gap_why_needed,
                   g.evidence AS gap_evidence, g.status AS gap_status,
                   c.title AS concept_title, s.search_permission, s.state AS session_state,
                   d.status AS decision_status,
                   COALESCE(d.selected_action, d.action) AS decision_action
            FROM search_requests r
            JOIN source_gaps g ON g.id = r.source_gap_id
            JOIN concepts c ON c.id = r.concept_id
            JOIN learning_sessions s ON s.id = r.session_id
            JOIN agent_decisions d ON d.id = r.agent_decision_id
            WHERE r.id = ? AND r.workspace_id = ? AND s.workspace_id = ?
            """,
            (request_id, workspace_id, workspace_id),
        ).fetchone()
        if not row:
            raise SourceError(
                "search_request_not_found",
                "This search request is not available in the current workspace.",
                status_code=404,
            )
        sources = connection.execute(
            """
            SELECT * FROM external_sources
            WHERE search_request_id = ? AND workspace_id = ?
            ORDER BY rank, created_at
            """,
            (request_id, workspace_id),
        ).fetchall()
    session = get_session(database_path, workspace_id, str(row["session_id"]))
    performed = row["executed_at"] is not None
    return {
        "search_request": _public_request(dict(row)),
        "source_gap": {
            "id": row["source_gap_id"],
            "description": row["gap_description"],
            "why_needed": row["gap_why_needed"],
            "evidence": row["gap_evidence"],
            "status": row["gap_status"],
        },
        "concept": {"id": row["concept_id"], "title": row["concept_title"]},
        "gates": {
            "session_permission": bool(row["search_permission"]),
            "named_gap_validated": row["gap_status"] == "validated",
            "agent_requested_search": (
                row["decision_status"] in {"accepted", "overridden"}
                and row["decision_action"] == "request_search"
            ),
            "user_confirmed_this_scope": row["confirmation_status"] == "confirmed",
        },
        "external_sources": [_public_external_source(dict(source)) for source in sources],
        "session": _public_session(session),
        "generation": {
            "mode": row["generation_mode"],
            "model": row["model"],
            "internet_search_performed": performed,
        },
    }


def get_latest_search_request(
    settings: Settings,
    workspace_id: str,
    session_id: str,
) -> dict[str, Any]:
    # Resolve by the latest accepted Agent decision, not merely the latest old
    # request. This lets a later evidence boundary create a fresh confirmation.
    return get_or_create_search_request(settings, workspace_id, session_id)


def confirm_search_request(
    database_path: Path,
    workspace_id: str,
    request_id: str,
    confirmed: bool,
    expected_session_version: int,
    expected_request_version: int,
) -> dict[str, Any]:
    with connect(database_path) as connection:
        row, session = _owned_request_and_session(connection, workspace_id, request_id)
        _require_versions(row, session, expected_request_version, expected_session_version)
        if session["is_paused"]:
            raise SourceError("session_paused", "Resume the session before confirming search.", status_code=409)
        if session["state"] != "search_confirmation" or row["search_status"] != "pending":
            raise SourceError(
                "search_confirmation_already_resolved",
                "This search confirmation has already been resolved.",
                status_code=409,
                saved_state="The saved search state is unchanged.",
            )
        if confirmed:
            connection.execute(
                """
                UPDATE search_requests SET confirmation_status = 'confirmed',
                    version = version + 1, confirmed_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (request_id,),
            )
            event = "search_confirmed"
        else:
            connection.execute(
                """
                UPDATE search_requests SET confirmation_status = 'declined',
                    search_status = 'cancelled', version = version + 1,
                    confirmed_at = CURRENT_TIMESTAMP, completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (request_id,),
            )
            connection.execute(
                """
                UPDATE learning_sessions SET state = 'learning_concept',
                    version = version + 1, last_saved_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND workspace_id = ?
                """,
                (row["session_id"], workspace_id),
            )
            event = "search_declined"
        _record_event(
            connection,
            workspace_id,
            str(row["session_id"]),
            event,
            {"search_request_id": request_id, "internet_search_performed": False},
        )
    return get_search_request(database_path, workspace_id, request_id)


def execute_search_request(
    settings: Settings,
    workspace_id: str,
    request_id: str,
    expected_session_version: int,
    expected_request_version: int,
    *,
    client_factory: Callable[[Settings], Any] | None = None,
) -> dict[str, Any]:
    """Revalidate all four gates, then perform the only allowed web-search call."""

    with connect(settings.database_path) as connection:
        row, session = _owned_request_and_session(connection, workspace_id, request_id)
        if row["search_status"] == "completed":
            return get_search_request(settings.database_path, workspace_id, request_id)
        _require_versions(row, session, expected_request_version, expected_session_version)
        gate = _revalidate_execution_gates(connection, workspace_id, dict(row), dict(session))
        connection.execute(
            """
            UPDATE search_requests SET search_status = 'running', version = version + 1,
                executed_at = CURRENT_TIMESTAMP, error_code = NULL WHERE id = ?
            """,
            (request_id,),
        )
        connection.execute(
            """
            UPDATE learning_sessions SET state = 'search_running', version = version + 1,
                last_saved_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND workspace_id = ?
            """,
            (row["session_id"], workspace_id),
        )
        _record_event(
            connection,
            workspace_id,
            str(row["session_id"]),
            "external_search_started",
            {"search_request_id": request_id, "source_gap_id": row["source_gap_id"]},
        )

    try:
        if settings.mode == "demo":
            candidates = _demo_candidates(str(row["query_scope"]), str(gate["description"]))
            response_id = None
        else:
            candidates, response_id = _real_search(
                settings,
                workspace_id,
                str(row["query_scope"]),
                str(gate["description"]),
                client_factory=client_factory,
            )
        if not candidates:
            raise SourceError(
                "external_search_no_results",
                "No reliable public source was found for this exact gap.",
                status_code=503,
                saved_state="Your learning progress is saved; continue with uploaded material or try again later.",
            )
        _persist_search_results(settings, workspace_id, dict(row), candidates, response_id)
    except SourceError as exc:
        _persist_search_failure(settings.database_path, workspace_id, dict(row), exc.error_code)
        raise
    except Exception as exc:
        _persist_search_failure(settings.database_path, workspace_id, dict(row), "external_search_failed")
        raise SourceError(
            "external_search_failed",
            "External search is temporarily unavailable.",
            status_code=503,
            saved_state="Your learning progress is saved; continue with uploaded material or try again later.",
        ) from exc
    return get_search_request(settings.database_path, workspace_id, request_id)


def select_external_source(
    database_path: Path,
    workspace_id: str,
    source_id: str,
    expected_session_version: int,
) -> dict[str, Any]:
    with connect(database_path) as connection:
        source = connection.execute(
            """
            SELECT e.*, r.session_id AS request_session_id, r.search_status
            FROM external_sources e JOIN search_requests r ON r.id = e.search_request_id
            WHERE e.id = ? AND e.workspace_id = ?
            """,
            (source_id, workspace_id),
        ).fetchone()
        if not source:
            raise SourceError("external_source_not_found", "This external source is unavailable.", status_code=404)
        session = connection.execute(
            "SELECT * FROM learning_sessions WHERE id = ? AND workspace_id = ?",
            (source["session_id"], workspace_id),
        ).fetchone()
        if not session or int(session["version"]) != expected_session_version:
            raise SourceError(
                "session_version_conflict",
                "This source-selection step changed in another page. Reload the saved results.",
                status_code=409,
            )
        if session["state"] != "search_results" or source["search_status"] != "completed":
            raise SourceError("external_source_selection_unavailable", "Search results are not active.", status_code=409)
        if source["status"] not in {"candidate", "selected"}:
            raise SourceError("external_source_selection_unavailable", "This source is no longer selectable.", status_code=409)
        connection.execute(
            "UPDATE external_sources SET status = 'ignored' WHERE search_request_id = ? AND status = 'candidate'",
            (source["search_request_id"],),
        )
        connection.execute(
            "UPDATE external_sources SET status = 'selected', selected_at = CURRENT_TIMESTAMP WHERE id = ?",
            (source_id,),
        )
        connection.execute(
            "INSERT OR IGNORE INTO concept_external_sources(concept_id, external_source_id) VALUES (?, ?)",
            (source["concept_id"], source_id),
        )
        connection.execute(
            "UPDATE source_gaps SET status = 'resolved', resolved_at = CURRENT_TIMESTAMP WHERE id = ?",
            (source["source_gap_id"],),
        )
        connection.execute(
            """
            UPDATE learning_sessions SET state = 'learning_concept', version = version + 1,
                last_saved_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND workspace_id = ?
            """,
            (source["session_id"], workspace_id),
        )
        _record_event(
            connection,
            workspace_id,
            str(source["session_id"]),
            "external_source_selected",
            {"external_source_id": source_id, "source_gap_id": source["source_gap_id"]},
        )
    return {
        "selected_source": get_external_source(database_path, workspace_id, source_id),
        "session": _public_session(get_session(database_path, workspace_id, str(source["session_id"]))),
    }


def ignore_search_results(
    database_path: Path,
    workspace_id: str,
    request_id: str,
    expected_session_version: int,
) -> dict[str, Any]:
    with connect(database_path) as connection:
        row, session = _owned_request_and_session(connection, workspace_id, request_id)
        if int(session["version"]) != expected_session_version:
            raise SourceError("session_version_conflict", "Reload the saved search results.", status_code=409)
        if session["state"] != "search_results" or row["search_status"] != "completed":
            raise SourceError("search_results_not_active", "These search results are no longer active.", status_code=409)
        connection.execute(
            "UPDATE external_sources SET status = 'ignored' WHERE search_request_id = ? AND status = 'candidate'",
            (request_id,),
        )
        connection.execute(
            "UPDATE search_requests SET search_status = 'ignored', version = version + 1, completed_at = CURRENT_TIMESTAMP WHERE id = ?",
            (request_id,),
        )
        connection.execute(
            """
            UPDATE learning_sessions SET state = 'learning_concept', version = version + 1,
                last_saved_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND workspace_id = ?
            """,
            (row["session_id"], workspace_id),
        )
        _record_event(
            connection,
            workspace_id,
            str(row["session_id"]),
            "external_search_ignored",
            {"search_request_id": request_id, "penalty": False},
        )
    return {"session": _public_session(get_session(database_path, workspace_id, str(row["session_id"])))}


def cancel_running_search(
    database_path: Path,
    workspace_id: str,
    request_id: str,
    expected_session_version: int,
    expected_request_version: int,
) -> dict[str, Any]:
    """Recover a stranded running state after a client or process interruption."""

    with connect(database_path) as connection:
        row, session = _owned_request_and_session(connection, workspace_id, request_id)
        _require_versions(row, session, expected_request_version, expected_session_version)
        if session["state"] != "search_running" or row["search_status"] != "running":
            raise SourceError("search_not_running", "This search is no longer running.", status_code=409)
        connection.execute(
            """
            UPDATE search_requests SET search_status = 'cancelled', error_code = 'search_cancelled_by_user',
                version = version + 1, completed_at = CURRENT_TIMESTAMP WHERE id = ?
            """,
            (request_id,),
        )
        connection.execute(
            """
            UPDATE learning_sessions SET state = 'learning_concept', version = version + 1,
                last_saved_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND workspace_id = ?
            """,
            (row["session_id"], workspace_id),
        )
        _record_event(
            connection,
            workspace_id,
            str(row["session_id"]),
            "external_search_cancelled",
            {"search_request_id": request_id, "progress_preserved": True},
        )
    return {"session": _public_session(get_session(database_path, workspace_id, str(row["session_id"])))}


def get_external_source(database_path: Path, workspace_id: str, source_id: str) -> dict[str, Any]:
    with connect(database_path) as connection:
        row = connection.execute(
            "SELECT * FROM external_sources WHERE id = ? AND workspace_id = ?",
            (source_id, workspace_id),
        ).fetchone()
    if not row:
        raise SourceError("external_source_not_found", "This external source is unavailable.", status_code=404)
    return _public_external_source(dict(row))


def selected_sources_for_concept(
    database_path: Path, workspace_id: str, session_id: str, concept_id: str
) -> list[dict[str, Any]]:
    with connect(database_path) as connection:
        rows = connection.execute(
            """
            SELECT e.* FROM external_sources e
            JOIN concept_external_sources x ON x.external_source_id = e.id
            WHERE e.workspace_id = ? AND e.session_id = ? AND x.concept_id = ?
              AND e.status = 'selected'
            ORDER BY x.attached_at, e.rank
            """,
            (workspace_id, session_id, concept_id),
        ).fetchall()
    return [_public_external_source(dict(row)) for row in rows]


def _revalidate_execution_gates(connection, workspace_id: str, row: dict[str, Any], session: dict[str, Any]):
    if session["is_paused"]:
        raise SourceError("session_paused", "Resume the session before running search.", status_code=409)
    if session["state"] != "search_confirmation" or row["search_status"] != "pending":
        raise SourceError("search_execution_unavailable", "This search is not ready to run.", status_code=409)
    gap = connection.execute(
        "SELECT * FROM source_gaps WHERE id = ? AND workspace_id = ? AND session_id = ?",
        (row["source_gap_id"], workspace_id, row["session_id"]),
    ).fetchone()
    decision = connection.execute(
        "SELECT * FROM agent_decisions WHERE id = ? AND workspace_id = ?",
        (row["agent_decision_id"], workspace_id),
    ).fetchone()
    gates = {
        "permission": bool(session["search_permission"]) and bool(row["permission_snapshot"]),
        "gap": bool(gap and gap["status"] == "validated"),
        "agent": bool(
            decision
            and decision["status"] in {"accepted", "overridden"}
            and str(decision["selected_action"] or decision["action"]) == "request_search"
        ),
        "confirmation": row["confirmation_status"] == "confirmed",
    }
    if not all(gates.values()):
        raise SourceError(
            "search_gate_failed",
            "External search was blocked because one of the four required gates is no longer valid.",
            status_code=409,
            saved_state="No external request has run; your learning progress is saved.",
            details={"gates": gates},
        )
    return gap


def _real_search(
    settings: Settings,
    workspace_id: str,
    query_scope: str,
    gap_description: str,
    *,
    client_factory: Callable[[Settings], Any] | None,
) -> tuple[list[dict[str, str]], str | None]:
    if not settings.openai_api_key:
        raise SourceError(
            "openai_key_missing",
            "Live search needs a server-side OpenAI API key. The named gap and learning progress are saved.",
            status_code=503,
            saved_state="No external request was completed.",
        )
    if client_factory:
        client = client_factory(settings)
    else:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key, timeout=settings.openai_timeout_seconds)
    prompt = (
        "Perform one narrow educational web search for this named gap. "
        "Return at most three short, distinct, beginner-appropriate findings from publicly accessible, "
        "credible sources. Cite every finding inline. Do not provide uncited URLs.\n\n"
        f"Named gap: {gap_description}\nConfirmed query scope: {query_scope}"
    )
    response = client.responses.create(
        model=settings.openai_model,
        reasoning={"effort": "low"},
        tools=[{"type": "web_search", "external_web_access": True}],
        tool_choice="required",
        include=["web_search_call.action.sources"],
        input=prompt,
        store=False,
        safety_identifier=_safety_identifier(workspace_id),
    )
    if _value(response, "status") not in {None, "completed"}:
        raise SourceError(
            "external_search_incomplete",
            "External search did not complete.",
            status_code=503,
            saved_state="Your learning progress and confirmed scope remain saved.",
        )
    candidates = _candidates_from_response(response, gap_description)
    return candidates, _value(response, "id")


def _candidates_from_response(response: Any, gap_description: str) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    consulted: dict[str, dict[str, Any]] = {}
    message_parts: list[tuple[str, list[Any]]] = []
    for item in _value(response, "output", []) or []:
        item_type = _value(item, "type")
        if item_type == "web_search_call":
            action = _value(item, "action", {}) or {}
            for source in _value(action, "sources", []) or []:
                raw_url = _value(source, "url")
                if raw_url:
                    try:
                        url = _canonical_public_url(str(raw_url))
                    except ValueError:
                        continue
                    consulted[url] = {
                        "title": _value(source, "title") or _value(source, "name"),
                    }
        if item_type == "message":
            for content in _value(item, "content", []) or []:
                if _value(content, "type") == "output_text":
                    message_parts.append((str(_value(content, "text", "")), list(_value(content, "annotations", []) or [])))
    seen: set[str] = set()
    for text, annotations in message_parts:
        for annotation in annotations:
            if _value(annotation, "type") != "url_citation":
                continue
            raw_url = _value(annotation, "url")
            if not raw_url:
                continue
            try:
                url = _canonical_public_url(str(raw_url))
            except ValueError:
                continue
            if url in seen:
                continue
            start = int(_value(annotation, "start_index", 0) or 0)
            end = int(_value(annotation, "end_index", start) or start)
            excerpt = _sentence_excerpt(text, start, end)
            candidates.append({
                "canonical_url": url,
                "title": str(_value(annotation, "title") or consulted.get(url, {}).get("title") or _publisher(url))[:300],
                "publisher": _publisher(url),
                "citation_excerpt": excerpt or "This cited result addresses the confirmed source gap.",
                "selection_reason": f"The cited result directly supports the named gap: {gap_description}"[:500],
            })
            seen.add(url)
            if len(candidates) == 3:
                return candidates
    return candidates


def _demo_candidates(query_scope: str, gap_description: str) -> list[dict[str, str]]:
    variance = bool(re.search(r"variance|dimension|square.root|scal", f"{query_scope} {gap_description}", re.I))
    if variance:
        rows = [
            (
                "Attention Is All You Need",
                "https://arxiv.org/abs/1706.03762",
                "arXiv",
                "Demo-grounded summary: the Transformer paper defines scaled dot-product attention and motivates scaling large dot products before softmax.",
            ),
            (
                "Attention Scoring Functions",
                "https://d2l.ai/chapter_attention-mechanisms-and-transformers/attention-scoring-functions.html",
                "Dive into Deep Learning",
                "Demo-grounded summary: this textbook section connects dot-product attention, normalization, and the query/key dimension.",
            ),
            (
                "The Annotated Transformer",
                "https://nlp.seas.harvard.edu/annotated-transformer/",
                "Harvard NLP",
                "Demo-grounded summary: the annotated implementation explains why large dot products can push softmax into low-gradient regions.",
            ),
        ]
    else:
        rows = [
            (
                "Dot Product",
                "https://mathworld.wolfram.com/DotProduct.html",
                "Wolfram MathWorld",
                "Demo-grounded summary: a dot product combines matching vector components into one scalar comparison.",
            ),
            (
                "Linear Algebra",
                "https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/",
                "MIT OpenCourseWare",
                "Demo-grounded summary: this public course provides the broader vector and matrix foundation behind dot products.",
            ),
            (
                "numpy.dot",
                "https://numpy.org/doc/stable/reference/generated/numpy.dot.html",
                "NumPy",
                "Demo-grounded summary: the reference shows concrete dot-product behavior for vectors and arrays.",
            ),
        ]
    return [
        {
            "title": title,
            "canonical_url": _canonical_public_url(url),
            "publisher": publisher,
            "citation_excerpt": excerpt,
            "selection_reason": f"This fixed Demo candidate is narrowly relevant to: {gap_description}"[:500],
        }
        for title, url, publisher, excerpt in rows
    ]


def _persist_search_results(
    settings: Settings,
    workspace_id: str,
    request: dict[str, Any],
    candidates: list[dict[str, str]],
    response_id: str | None,
) -> None:
    accessed_at = datetime.now(UTC).replace(microsecond=0).isoformat()
    with connect(settings.database_path) as connection:
        current = connection.execute(
            "SELECT search_status FROM search_requests WHERE id = ? AND workspace_id = ?",
            (request["id"], workspace_id),
        ).fetchone()
        if not current or current["search_status"] != "running":
            raise SourceError("search_state_changed", "The search state changed before results were saved.", status_code=409)
        connection.execute("DELETE FROM external_sources WHERE search_request_id = ?", (request["id"],))
        for rank, item in enumerate(candidates[:3], start=1):
            url = _canonical_public_url(item["canonical_url"])
            connection.execute(
                """
                INSERT INTO external_sources(
                    id, workspace_id, session_id, concept_id, source_gap_id,
                    search_request_id, canonical_url, title, publisher, accessed_at,
                    selection_reason, citation_excerpt, locator, rank
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()), workspace_id, request["session_id"], request["concept_id"],
                    request["source_gap_id"], request["id"], url, item["title"][:300],
                    item["publisher"][:200], accessed_at, item["selection_reason"][:500],
                    item["citation_excerpt"][:1000], f"Web citation · accessed {accessed_at}", rank,
                ),
            )
        connection.execute(
            """
            UPDATE search_requests SET search_status = 'completed', response_id = ?,
                version = version + 1, completed_at = CURRENT_TIMESTAMP WHERE id = ?
            """,
            (response_id, request["id"]),
        )
        connection.execute(
            """
            UPDATE learning_sessions SET state = 'search_results', version = version + 1,
                last_saved_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND workspace_id = ?
            """,
            (request["session_id"], workspace_id),
        )
        _record_event(
            connection,
            workspace_id,
            str(request["session_id"]),
            "external_search_completed",
            {"search_request_id": request["id"], "candidate_count": min(3, len(candidates))},
        )


def _persist_search_failure(database_path: Path, workspace_id: str, request: dict[str, Any], error_code: str) -> None:
    with connect(database_path) as connection:
        connection.execute(
            """
            UPDATE search_requests SET search_status = 'failed', error_code = ?,
                version = version + 1, completed_at = CURRENT_TIMESTAMP WHERE id = ?
            """,
            (error_code, request["id"]),
        )
        connection.execute(
            """
            UPDATE learning_sessions SET state = 'learning_concept', version = version + 1,
                last_saved_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND workspace_id = ?
            """,
            (request["session_id"], workspace_id),
        )
        _record_event(
            connection,
            workspace_id,
            str(request["session_id"]),
            "external_search_failed",
            {"search_request_id": request["id"], "error_code": error_code},
        )


def _owned_request_and_session(connection, workspace_id: str, request_id: str):
    row = connection.execute(
        "SELECT * FROM search_requests WHERE id = ? AND workspace_id = ?",
        (request_id, workspace_id),
    ).fetchone()
    if not row:
        raise SourceError("search_request_not_found", "This search request is unavailable.", status_code=404)
    session = connection.execute(
        "SELECT * FROM learning_sessions WHERE id = ? AND workspace_id = ?",
        (row["session_id"], workspace_id),
    ).fetchone()
    if not session:
        raise SourceError("session_not_found", "This learning session is unavailable.", status_code=404)
    return row, session


def _require_versions(row, session, expected_request_version: int, expected_session_version: int) -> None:
    if int(row["version"]) != expected_request_version or int(session["version"]) != expected_session_version:
        raise SourceError(
            "search_version_conflict",
            "This search step changed in another page. Reload the saved request before continuing.",
            status_code=409,
            saved_state="The newer confirmation and learning state are preserved.",
        )


def _public_request(row: dict[str, Any]) -> dict[str, Any]:
    return {
        key: row.get(key)
        for key in (
            "id", "session_id", "concept_id", "source_gap_id", "agent_decision_id",
            "query_scope", "reason_for_user", "confirmation_status", "search_status",
            "generation_mode", "model", "version", "error_code", "created_at",
            "confirmed_at", "executed_at", "completed_at",
        )
    }


def _public_external_source(row: dict[str, Any]) -> dict[str, Any]:
    result = {
        key: row.get(key)
        for key in (
            "id", "session_id", "concept_id", "source_gap_id", "search_request_id",
            "canonical_url", "title", "publisher", "accessed_at", "selection_reason",
            "citation_excerpt", "locator", "status", "rank", "created_at", "selected_at",
        )
    }
    result["source_origin"] = "external"
    return result


def _public_session(session: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": session["id"],
        "name": session["name"],
        "state": session["state"],
        "version": session["version"],
        "is_paused": bool(session.get("is_paused")),
        "resume_state": session.get("resume_state"),
        "active_concept_id": session.get("active_concept_id"),
        "search_permission": bool(session.get("search_permission")),
    }


def _canonical_public_url(raw_url: str) -> str:
    if len(raw_url) > 2000:
        raise ValueError("URL too long")
    parsed = urlsplit(raw_url.strip())
    if parsed.scheme.lower() != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Only public HTTPS URLs are allowed")
    host = parsed.hostname.rstrip(".").lower()
    if host == "localhost" or host.endswith(".localhost"):
        raise ValueError("Local URLs are not allowed")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address and not address.is_global:
        raise ValueError("Private or reserved addresses are not allowed")
    netloc = host
    if parsed.port and parsed.port != 443:
        netloc = f"{host}:{parsed.port}"
    return urlunsplit(("https", netloc, parsed.path or "/", parsed.query, ""))


def _publisher(url: str) -> str:
    host = urlsplit(url).hostname or "External source"
    return host.removeprefix("www.")


def _sentence_excerpt(text: str, start: int, end: int) -> str:
    if not text:
        return ""
    start = max(0, min(start, len(text)))
    end = max(start, min(end, len(text)))
    left = max(text.rfind(".", 0, start), text.rfind("\n", 0, start))
    right_candidates = [index for index in (text.find(".", end), text.find("\n", end)) if index >= 0]
    right = min(right_candidates) + 1 if right_candidates else min(len(text), end + 320)
    excerpt = re.sub(r"\s+", " ", text[left + 1:right]).strip(" -•\t")
    return excerpt[:600]


def _value(item: Any, name: str, default: Any = None) -> Any:
    if isinstance(item, dict):
        return item.get(name, default)
    return getattr(item, name, default)


def _safety_identifier(workspace_id: str) -> str:
    import hashlib

    return hashlib.sha256(workspace_id.encode("utf-8")).hexdigest()


def _record_event(connection, workspace_id: str, session_id: str, event_type: str, detail: dict[str, Any]) -> None:
    connection.execute(
        """
        INSERT INTO session_events(id, workspace_id, session_id, event_type, detail_json)
        VALUES (?, ?, ?, ?, ?)
        """,
        (str(uuid.uuid4()), workspace_id, session_id, event_type, json.dumps(detail)),
    )
