"""Versioned drafts, resumable timing, and the single-concept focus workspace."""

from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any
import uuid

from app.db import connect
from app.sources import SourceError, get_session


ALLOWED_DRAFT_TYPES = {"start_action", "focus_note", "tutor", "quiz", "recall", "remedial"}


def save_draft(
    database_path: Path,
    workspace_id: str,
    session_id: str,
    draft_type: str,
    content: str,
    hint_depth: int,
    expected_version: int,
) -> dict[str, Any]:
    """Create or update one draft without ever silently overwriting another version."""

    if draft_type not in ALLOWED_DRAFT_TYPES:
        raise SourceError("invalid_draft_type", "This draft type is not supported.")
    session = get_session(database_path, workspace_id, session_id)
    _require_mutable_learning_state(session)
    cleaned = content.strip()
    with connect(database_path) as connection:
        row = connection.execute(
            "SELECT * FROM drafts WHERE session_id = ? AND workspace_id = ? AND draft_type = ?",
            (session_id, workspace_id, draft_type),
        ).fetchone()
        current_version = int(row["server_version"]) if row else 0
        if current_version != expected_version:
            server_draft = _public_draft(dict(row)) if row else None
            raise SourceError(
                "draft_version_conflict",
                "Another page saved a different version. Both versions are preserved for you to choose.",
                status_code=409,
                saved_state="The server copy is unchanged and your local copy remains on this device.",
                details={
                    "server_draft": server_draft,
                    "local_draft": {
                        "draft_type": draft_type,
                        "content": content,
                        "hint_depth": hint_depth,
                        "based_on_version": expected_version,
                    },
                },
            )
        if row:
            connection.execute(
                """
                UPDATE drafts
                SET content = ?, hint_depth = ?, activity_id = ?,
                    server_version = server_version + 1, sync_status = 'saved',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (cleaned, hint_depth, session.get("active_activity_id"), row["id"]),
            )
            draft_id = str(row["id"])
        else:
            draft_id = str(uuid.uuid4())
            connection.execute(
                """
                INSERT INTO drafts(
                    id, workspace_id, session_id, activity_id, draft_type,
                    content, hint_depth
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    draft_id,
                    workspace_id,
                    session_id,
                    session.get("active_activity_id"),
                    draft_type,
                    cleaned,
                    hint_depth,
                ),
            )
        connection.execute(
            """
            UPDATE learning_sessions
            SET last_saved_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND workspace_id = ?
            """,
            (session_id, workspace_id),
        )
        saved = connection.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,)).fetchone()
    return _public_draft(dict(saved))


def get_drafts(database_path: Path, workspace_id: str, session_id: str) -> list[dict[str, Any]]:
    get_session(database_path, workspace_id, session_id)
    with connect(database_path) as connection:
        rows = connection.execute(
            """
            SELECT * FROM drafts
            WHERE session_id = ? AND workspace_id = ?
            ORDER BY updated_at, draft_type
            """,
            (session_id, workspace_id),
        ).fetchall()
    return [_public_draft(dict(row)) for row in rows]


def resolve_draft_conflict(
    database_path: Path,
    workspace_id: str,
    session_id: str,
    draft_type: str,
    choice: str,
    local_content: str,
    server_version: int,
    hint_depth: int,
) -> dict[str, Any]:
    if choice == "server":
        current = _draft_by_type(database_path, workspace_id, session_id, draft_type)
        if current is None:
            raise SourceError(
                "draft_not_found",
                "The server draft is no longer available. Your local draft remains on this device.",
                status_code=404,
            )
        return current
    if choice != "local":
        raise SourceError("invalid_conflict_choice", "Choose either your local copy or the server copy.")
    return save_draft(
        database_path,
        workspace_id,
        session_id,
        draft_type,
        local_content,
        hint_depth,
        server_version,
    )


def complete_start_action(
    database_path: Path,
    workspace_id: str,
    session_id: str,
    expected_session_version: int,
) -> dict[str, Any]:
    session = get_session(database_path, workspace_id, session_id)
    _require_session_version(session, expected_session_version)
    if session["state"] != "start_action" or session.get("is_paused"):
        raise SourceError(
            "invalid_session_transition",
            "Resume this session and return to the start action before continuing.",
            status_code=409,
            saved_state="Your starting-point draft is saved.",
        )
    draft = _draft_by_type(database_path, workspace_id, session_id, "start_action")
    if not draft or not draft["content"].strip():
        raise SourceError(
            "start_action_incomplete",
            "Write one checkable sentence before entering the first concept.",
            status_code=422,
            saved_state="Any unfinished text remains on this device.",
        )

    with connect(database_path) as connection:
        map_row = connection.execute(
            """
            SELECT output_json, confirmed_at FROM knowledge_maps
            WHERE session_id = ? AND workspace_id = ?
            """,
            (session_id, workspace_id),
        ).fetchone()
        if not map_row or not map_row["confirmed_at"]:
            raise SourceError(
                "learning_map_not_confirmed",
                "Confirm the learning map before starting the focus session.",
                status_code=409,
            )
        output = json.loads(str(map_row["output_json"]))
        route = list(output["recommended_route"])
        active_key = "self_attention" if "self_attention" in route else route[0]
        active_index = route.index(active_key)
        concept = connection.execute(
            """
            SELECT * FROM concepts
            WHERE session_id = ? AND workspace_id = ? AND concept_key = ?
            """,
            (session_id, workspace_id, active_key),
        ).fetchone()
        if not concept:
            raise SourceError("active_concept_missing", "The first concept is unavailable. Regenerate the learning map.", status_code=409)
        connection.execute(
            "UPDATE concepts SET status = 'planned' WHERE session_id = ? AND workspace_id = ?",
            (session_id, workspace_id),
        )
        for completed_key in route[:active_index]:
            connection.execute(
                "UPDATE concepts SET status = 'completed' WHERE session_id = ? AND workspace_id = ? AND concept_key = ?",
                (session_id, workspace_id, completed_key),
            )
        connection.execute("UPDATE concepts SET status = 'active' WHERE id = ?", (concept["id"],))
        connection.execute(
            """
            UPDATE learning_sessions
            SET state = 'learning_concept', resume_state = NULL, is_paused = 0,
                active_concept_id = ?, active_activity_id = NULL,
                timer_started_at = CURRENT_TIMESTAMP, elapsed_seconds = 0,
                remaining_seconds = available_minutes * 60,
                started_at = COALESCE(started_at, CURRENT_TIMESTAMP),
                last_saved_at = CURRENT_TIMESTAMP, version = version + 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND workspace_id = ?
            """,
            (concept["id"], session_id, workspace_id),
        )
        _record_event(connection, workspace_id, session_id, "start_action_completed", {"draft_id": draft["id"]})
    return get_focus_workspace(database_path, workspace_id, session_id)


def pause_session(
    database_path: Path,
    workspace_id: str,
    session_id: str,
    expected_session_version: int,
) -> dict[str, Any]:
    session = get_session(database_path, workspace_id, session_id)
    _require_session_version(session, expected_session_version)
    if session.get("is_paused"):
        return session
    if session["state"] not in {
        "start_action", "learning_concept", "practicing", "feedback_shown",
        "remedial_practice", "evidence_ready", "agent_decision", "search_confirmation",
    }:
        raise SourceError("invalid_session_transition", "This session cannot be paused from its current step.", status_code=409)
    elapsed, remaining = _timer_values(session)
    with connect(database_path) as connection:
        connection.execute(
            """
            UPDATE learning_sessions
            SET resume_state = state, is_paused = 1, timer_started_at = NULL,
                elapsed_seconds = ?, remaining_seconds = ?, last_saved_at = CURRENT_TIMESTAMP,
                version = version + 1, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND workspace_id = ?
            """,
            (elapsed, remaining, session_id, workspace_id),
        )
        _record_event(connection, workspace_id, session_id, "session_paused", {"resume_state": session["state"]})
    return get_session(database_path, workspace_id, session_id)


def resume_session(
    database_path: Path,
    workspace_id: str,
    session_id: str,
    expected_session_version: int,
) -> dict[str, Any]:
    session = get_session(database_path, workspace_id, session_id)
    _require_session_version(session, expected_session_version)
    if not session.get("is_paused"):
        return session
    resume_state = str(session.get("resume_state") or session["state"])
    timer_sql = "CURRENT_TIMESTAMP" if resume_state in {
        "learning_concept", "practicing", "feedback_shown", "remedial_practice", "evidence_ready",
        "agent_decision", "search_confirmation",
    } else "NULL"
    with connect(database_path) as connection:
        connection.execute(
            f"""
            UPDATE learning_sessions
            SET state = ?, resume_state = NULL, is_paused = 0,
                timer_started_at = {timer_sql}, version = version + 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND workspace_id = ?
            """,
            (resume_state, session_id, workspace_id),
        )
        _record_event(connection, workspace_id, session_id, "session_resumed", {"state": resume_state})
    return get_session(database_path, workspace_id, session_id)


def get_focus_workspace(database_path: Path, workspace_id: str, session_id: str) -> dict[str, Any]:
    session = get_session(database_path, workspace_id, session_id)
    if session["state"] != "learning_concept":
        raise SourceError(
            "focus_not_started",
            "Complete the start action before opening the focus workspace.",
            status_code=409,
            saved_state="Your map and drafts are saved.",
        )
    with connect(database_path) as connection:
        map_row = connection.execute(
            "SELECT output_json FROM knowledge_maps WHERE session_id = ? AND workspace_id = ?",
            (session_id, workspace_id),
        ).fetchone()
        concept = connection.execute(
            "SELECT * FROM concepts WHERE id = ? AND session_id = ? AND workspace_id = ?",
            (session.get("active_concept_id"), session_id, workspace_id),
        ).fetchone()
        rows = connection.execute(
            "SELECT * FROM concepts WHERE session_id = ? AND workspace_id = ? ORDER BY order_index",
            (session_id, workspace_id),
        ).fetchall()
    if not map_row or not concept:
        raise SourceError("focus_state_invalid", "The saved focus state is incomplete. Review the learning map.", status_code=409)
    output = json.loads(str(map_row["output_json"]))
    route = list(output["recommended_route"])
    concepts = [dict(row) for row in rows]
    concept_by_key = {item["concept_key"]: item for item in concepts}
    active = dict(concept)
    refs = json.loads(str(active["source_refs_json"]))
    elapsed, remaining = _timer_values(session)
    route_items = [concept_by_key[key] for key in route if key in concept_by_key]
    active_route_index = next(
        (index for index, item in enumerate(route_items) if item["id"] == active["id"]),
        0,
    )
    start_draft = _draft_by_type(database_path, workspace_id, session_id, "start_action")
    focus_draft = _draft_by_type(database_path, workspace_id, session_id, "focus_note")
    return {
        "session": _focus_session(session),
        "active_concept": {
            "id": active["id"],
            "concept_key": active["concept_key"],
            "title": active["title"],
            "plain_definition": active["plain_definition"],
            "role_in_map": active["role_in_map"],
            "estimated_minutes": active["estimated_minutes"],
            "source_refs": refs,
            "source_ref_details": _source_details(database_path, workspace_id, session_id, refs),
        },
        "route": [
            {
                "id": item["id"],
                "concept_key": item["concept_key"],
                "title": item["title"],
                "status": item["status"],
                "is_active": item["id"] == active["id"],
            }
            for item in route_items
        ],
        "progress": {
            "current": active_route_index + 1,
            "total": len(route_items),
            "completed": sum(1 for item in route_items if item["status"] == "completed"),
        },
        "timer": {"elapsed_seconds": elapsed, "remaining_seconds": remaining},
        "drafts": {"start_action": start_draft, "focus_note": focus_draft},
        "source_policy": {
            "primary_origin": "uploaded",
            "internet_search_performed": False,
        },
        "restart_action": f"Resume {active['title']} and read the saved focus note before continuing.",
    }


def _source_details(
    database_path: Path,
    workspace_id: str,
    session_id: str,
    refs: list[dict[str, str]],
) -> list[dict[str, Any]]:
    details = []
    with connect(database_path) as connection:
        for ref in refs:
            row = connection.execute(
                """
                SELECT d.id AS source_id, d.filename, d.source_origin, d.media_kind,
                       c.id AS chunk_id, c.heading_path, c.page_number, c.page_chunk_index,
                       c.paragraph_number, c.start_line, c.end_line, c.start_char, c.end_char
                FROM source_chunks c JOIN source_documents d ON d.id = c.source_id
                WHERE d.id = ? AND c.id = ? AND d.workspace_id = ? AND d.session_id = ?
                """,
                (ref["source_id"], ref["chunk_id"], workspace_id, session_id),
            ).fetchone()
            if not row:
                continue
            item = dict(row)
            if item["media_kind"] == "pdf":
                location = f"Page {item['page_number']} · excerpt {item['page_chunk_index']}"
            elif item["media_kind"] == "pasted":
                location = f"Paragraph {item['paragraph_number']} · characters {item['start_char']}–{item['end_char']}"
            else:
                location = f"{item['heading_path'] or 'Document'} · lines {item['start_line']}–{item['end_line']}"
            details.append({
                "source_id": item["source_id"],
                "chunk_id": item["chunk_id"],
                "filename": item["filename"],
                "source_origin": item["source_origin"],
                "location": location,
            })
    if len(details) != len(refs):
        raise SourceError(
            "source_reference_invalid",
            "A saved source location is no longer available. Review the learning map before continuing.",
            status_code=409,
        )
    return details


def _draft_by_type(
    database_path: Path,
    workspace_id: str,
    session_id: str,
    draft_type: str,
) -> dict[str, Any] | None:
    with connect(database_path) as connection:
        row = connection.execute(
            "SELECT * FROM drafts WHERE session_id = ? AND workspace_id = ? AND draft_type = ?",
            (session_id, workspace_id, draft_type),
        ).fetchone()
    return _public_draft(dict(row)) if row else None


def _public_draft(draft: dict[str, Any]) -> dict[str, Any]:
    return {
        key: draft.get(key)
        for key in (
            "id", "session_id", "activity_id", "draft_type", "content", "hint_depth",
            "server_version", "sync_status", "created_at", "updated_at",
        )
    }


def _focus_session(session: dict[str, Any]) -> dict[str, Any]:
    result = {
        key: session.get(key)
        for key in (
            "id", "name", "state", "mode", "version", "is_paused", "resume_state",
            "active_concept_id", "active_activity_id", "show_timer", "started_at",
            "last_saved_at", "updated_at", "tutor_open",
        )
    }
    result["is_paused"] = bool(result["is_paused"])
    result["show_timer"] = bool(result["show_timer"])
    result["tutor_open"] = bool(result["tutor_open"])
    return result


def _timer_values(session: dict[str, Any]) -> tuple[int, int]:
    elapsed = int(session.get("elapsed_seconds") or 0)
    remaining = session.get("remaining_seconds")
    if remaining is None:
        remaining = int(session.get("available_minutes") or 0) * 60
    remaining = int(remaining)
    started = session.get("timer_started_at")
    if started and not session.get("is_paused"):
        parsed = datetime.fromisoformat(str(started).replace(" ", "T")).replace(tzinfo=UTC)
        delta = max(0, int((datetime.now(UTC) - parsed).total_seconds()))
        elapsed += delta
        remaining = max(0, remaining - delta)
    return elapsed, remaining


def _require_mutable_learning_state(session: dict[str, Any]) -> None:
    if session.get("is_paused"):
        raise SourceError(
            "session_paused",
            "Resume the session before changing learning work.",
            status_code=409,
            saved_state="Your existing drafts and progress remain saved.",
        )
    if session["state"] not in {
        "start_action", "learning_concept", "practicing", "feedback_shown",
        "remedial_practice", "evidence_ready", "agent_decision", "search_confirmation",
    }:
        raise SourceError(
            "draft_not_available",
            "This draft is not available at the current session step.",
            status_code=409,
        )


def _require_session_version(session: dict[str, Any], expected_version: int) -> None:
    if int(session["version"]) != expected_version:
        raise SourceError(
            "session_version_conflict",
            "This session changed in another page. Reload the saved session before continuing.",
            status_code=409,
            saved_state="The newer saved session is unchanged.",
        )


def _record_event(connection, workspace_id: str, session_id: str, event_type: str, detail: dict[str, Any]) -> None:
    connection.execute(
        """
        INSERT INTO session_events(id, workspace_id, session_id, event_type, detail_json)
        VALUES (?, ?, ?, ?, ?)
        """,
        (str(uuid.uuid4()), workspace_id, session_id, event_type, json.dumps(detail)),
    )
