"""Session records, exports, copying, deletion, and AI transparency."""

from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any
import uuid

from app.db import connect
from app.sources import SourceError, get_session


def copy_session(
    database_path: Path,
    workspace_id: str,
    session_id: str,
    max_sessions: int | None = None,
    max_sources: int | None = None,
) -> dict[str, Any]:
    """Create a fresh study session that reuses immutable source blobs."""

    original = get_session(database_path, workspace_id, session_id)
    copied_session_id = str(uuid.uuid4())
    copy_name = f"Copy of {original['name']}"[:180]
    setup_fields = (
        "goal", "prior_knowledge", "available_minutes", "energy_level", "language",
        "current_question", "support_preferences_json", "show_timer", "search_permission",
        "setup_completed",
    )
    with connect(database_path) as connection:
        session_count = int(connection.execute(
            "SELECT COUNT(*) AS count FROM learning_sessions WHERE workspace_id = ?",
            (workspace_id,),
        ).fetchone()["count"])
        if max_sessions is not None and session_count >= max_sessions:
            raise SourceError(
                "workspace_session_quota_reached",
                f"This workspace can keep up to {max_sessions} study sessions. Delete one before copying another.",
                status_code=429,
                saved_state="The original session and all existing data are unchanged.",
            )
        source_rows = connection.execute(
            """
            SELECT * FROM source_documents
            WHERE session_id = ? AND workspace_id = ?
            ORDER BY created_at, rowid
            """,
            (session_id, workspace_id),
        ).fetchall()
        source_count = int(connection.execute(
            "SELECT COUNT(*) AS count FROM source_documents WHERE workspace_id = ?",
            (workspace_id,),
        ).fetchone()["count"])
        if max_sources is not None and source_count + len(source_rows) > max_sources:
            raise SourceError(
                "workspace_source_quota_reached",
                f"Copying this session would exceed the workspace limit of {max_sources} sources. Remove sources or another session first.",
                status_code=429,
                saved_state="The original session and all existing data are unchanged.",
            )
        new_state = "sources_reviewable" if source_rows else "session_created"
        connection.execute(
            f"""
            INSERT INTO learning_sessions(
                id, workspace_id, name, mode, state, {', '.join(setup_fields)}
            ) VALUES (?, ?, ?, ?, ?, {', '.join('?' for _ in setup_fields)})
            """,
            (
                copied_session_id,
                workspace_id,
                copy_name,
                original["mode"],
                new_state,
                *(original.get(field) for field in setup_fields),
            ),
        )
        for source in source_rows:
            copied_source_id = str(uuid.uuid4())
            connection.execute(
                """
                INSERT INTO source_documents(
                    id, workspace_id, session_id, blob_id, filename, media_type,
                    media_kind, source_origin, parse_status, page_count, line_count,
                    error_code, error_message, version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    copied_source_id, workspace_id, copied_session_id, source["blob_id"],
                    source["filename"], source["media_type"], source["media_kind"],
                    source["source_origin"], source["parse_status"], source["page_count"],
                    source["line_count"], source["error_code"], source["error_message"],
                    source["version"],
                ),
            )
            chunks = connection.execute(
                "SELECT * FROM source_chunks WHERE source_id = ? ORDER BY start_char, rowid",
                (source["id"],),
            ).fetchall()
            for chunk in chunks:
                connection.execute(
                    """
                    INSERT INTO source_chunks(
                        id, source_id, heading_path, page_number, page_chunk_index,
                        paragraph_number, start_line, end_line, start_char, end_char,
                        text, search_text, checksum
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(uuid.uuid4()), copied_source_id, chunk["heading_path"],
                        chunk["page_number"], chunk["page_chunk_index"],
                        chunk["paragraph_number"], chunk["start_line"], chunk["end_line"],
                        chunk["start_char"], chunk["end_char"], chunk["text"],
                        chunk["search_text"], chunk["checksum"],
                    ),
                )
        connection.execute(
            """
            INSERT INTO session_events(id, workspace_id, session_id, event_type, detail_json)
            VALUES (?, ?, ?, 'session_copied', ?)
            """,
            (
                str(uuid.uuid4()), workspace_id, copied_session_id,
                json.dumps({"copied_from_session_id": session_id, "source_count": len(source_rows)}),
            ),
        )
    return get_session(database_path, workspace_id, copied_session_id)


def delete_session(
    database_path: Path,
    upload_dir: Path,
    workspace_id: str,
    session_id: str,
) -> dict[str, Any]:
    """Delete one session and remove only blobs that have no remaining reference."""

    session = get_session(database_path, workspace_id, session_id)
    cleanup_paths: list[str] = []
    with connect(database_path) as connection:
        blobs = connection.execute(
            """
            SELECT DISTINCT b.id, b.storage_path
            FROM source_blobs b JOIN source_documents d ON d.blob_id = b.id
            WHERE d.session_id = ? AND d.workspace_id = ?
            """,
            (session_id, workspace_id),
        ).fetchall()
        connection.execute(
            "DELETE FROM learning_sessions WHERE id = ? AND workspace_id = ?",
            (session_id, workspace_id),
        )
        for blob in blobs:
            still_used = connection.execute(
                "SELECT 1 FROM source_documents WHERE blob_id = ? LIMIT 1",
                (blob["id"],),
            ).fetchone()
            if not still_used:
                connection.execute(
                    "DELETE FROM source_blobs WHERE id = ? AND workspace_id = ?",
                    (blob["id"], workspace_id),
                )
                cleanup_paths.append(str(blob["storage_path"]))
    cleanup_complete = _unlink_workspace_files(upload_dir, workspace_id, cleanup_paths)
    return {
        "deleted_session_id": session_id,
        "deleted_session_name": session["name"],
        "removed_unreferenced_blobs": len(cleanup_paths),
        "file_cleanup_complete": cleanup_complete,
    }


def delete_workspace_data(
    database_path: Path,
    upload_dir: Path,
    workspace_id: str,
) -> dict[str, Any]:
    """Delete every record and uploaded blob owned by one anonymous workspace."""

    with connect(database_path) as connection:
        paths = [
            str(row["storage_path"])
            for row in connection.execute(
                "SELECT storage_path FROM source_blobs WHERE workspace_id = ?",
                (workspace_id,),
            ).fetchall()
        ]
        session_count = int(connection.execute(
            "SELECT COUNT(*) AS count FROM learning_sessions WHERE workspace_id = ?",
            (workspace_id,),
        ).fetchone()["count"])
        connection.execute("DELETE FROM learning_sessions WHERE workspace_id = ?", (workspace_id,))
        connection.execute("DELETE FROM source_blobs WHERE workspace_id = ?", (workspace_id,))
        connection.execute("DELETE FROM workspaces WHERE id = ?", (workspace_id,))
    cleanup_complete = _unlink_workspace_files(upload_dir, workspace_id, paths)
    workspace_dir = (upload_dir / workspace_id).resolve()
    try:
        workspace_dir.rmdir()
    except (FileNotFoundError, OSError):
        pass
    return {
        "deleted": True,
        "deleted_sessions": session_count,
        "deleted_blobs": len(paths),
        "file_cleanup_complete": cleanup_complete,
    }


def workspace_export(database_path: Path, workspace_id: str) -> dict[str, Any]:
    """Return a portable record without server paths, hidden rubrics, prompts, or response IDs."""

    with connect(database_path) as connection:
        sessions = _dict_rows(connection.execute(
            "SELECT * FROM learning_sessions WHERE workspace_id = ? ORDER BY created_at, id",
            (workspace_id,),
        ).fetchall())
        sources = _dict_rows(connection.execute(
            """
            SELECT id, session_id, filename, media_type, media_kind, source_origin,
                   parse_status, page_count, line_count, error_code, created_at, updated_at
            FROM source_documents WHERE workspace_id = ? ORDER BY created_at, id
            """,
            (workspace_id,),
        ).fetchall())
        source_chunks = _dict_rows(connection.execute(
            """
            SELECT c.id, c.source_id, c.heading_path, c.page_number, c.page_chunk_index,
                   c.paragraph_number, c.start_line, c.end_line, c.start_char, c.end_char,
                   c.text, c.checksum
            FROM source_chunks c JOIN source_documents d ON d.id = c.source_id
            WHERE d.workspace_id = ? ORDER BY d.created_at, c.start_char
            """,
            (workspace_id,),
        ).fetchall())
        source_reports = _dict_rows(connection.execute(
            """
            SELECT id, session_id, source_id, chunk_id, reason, note, status, created_at
            FROM source_reference_reports
            WHERE workspace_id = ? ORDER BY created_at, rowid
            """,
            (workspace_id,),
        ).fetchall())
        coverages = _json_rows(connection.execute(
            "SELECT session_id, output_json, generation_mode, model, created_at, updated_at FROM source_coverages WHERE workspace_id = ?",
            (workspace_id,),
        ).fetchall(), "output_json", "coverage")
        maps = _json_rows(connection.execute(
            "SELECT session_id, output_json, generation_mode, model, confirmed_at, created_at, updated_at FROM knowledge_maps WHERE workspace_id = ?",
            (workspace_id,),
        ).fetchall(), "output_json", "knowledge_map")
        concepts = _json_columns(_dict_rows(connection.execute(
            "SELECT * FROM concepts WHERE workspace_id = ? ORDER BY session_id, order_index",
            (workspace_id,),
        ).fetchall()), ("prerequisite_keys_json", "source_refs_json"))
        drafts = _dict_rows(connection.execute(
            "SELECT session_id, activity_id, draft_type, content, hint_depth, server_version, sync_status, updated_at FROM drafts WHERE workspace_id = ? ORDER BY updated_at",
            (workspace_id,),
        ).fetchall())
        tutor_messages = _json_columns(_dict_rows(connection.execute(
            """
            SELECT session_id, concept_id, role, message, quick_action, guidance_level,
                   checking_question, source_origin, source_refs_json, confusion_signal,
                   prerequisite_gap_signal, created_at
            FROM tutor_messages WHERE workspace_id = ? ORDER BY created_at, rowid
            """,
            (workspace_id,),
        ).fetchall()), ("source_refs_json",))
        activities = _json_columns(_dict_rows(connection.execute(
            """
            SELECT id, session_id, concept_id, type, prompt, source_origin, source_refs_json,
                   generation_mode, model, status, hint_depth, strategy, remedial_round,
                   parent_activity_id, created_at, submitted_at, closed_at
            FROM activities WHERE workspace_id = ? ORDER BY created_at, rowid
            """,
            (workspace_id,),
        ).fetchall()), ("source_refs_json",))
        attempts = _dict_rows(connection.execute(
            "SELECT id, session_id, activity_id, raw_answer, selected_option_id, hint_depth, elapsed_seconds, submitted_at FROM attempts WHERE workspace_id = ? ORDER BY submitted_at",
            (workspace_id,),
        ).fetchall())
        feedback = _json_rows(connection.execute(
            """
            SELECT session_id, concept_id, activity_id, attempt_id, output_json,
                   source_origin, source_refs_json, generation_mode, model, status,
                   created_at, completed_at
            FROM feedbacks WHERE workspace_id = ? ORDER BY created_at, rowid
            """,
            (workspace_id,),
        ).fetchall(), "output_json", "feedback")
        feedback = _json_columns(feedback, ("source_refs_json",))
        evidence = _json_columns(_dict_rows(connection.execute(
            """
            SELECT id, session_id, concept_id, activity_id, attempt_id, activity_type,
                   outcome, key_point_coverage_json, misconception_tags_json, hint_depth,
                   elapsed_seconds, tutor_confusion_signals_json, remedial_result,
                   source_gap_signal, timestamp
            FROM learning_evidence WHERE workspace_id = ? ORDER BY timestamp, rowid
            """,
            (workspace_id,),
        ).fetchall()), (
            "key_point_coverage_json", "misconception_tags_json", "tutor_confusion_signals_json",
        ))
        decisions = _dict_rows(connection.execute(
            """
            SELECT id, session_id, concept_id, action, reason_for_user, estimated_minutes,
                   target_concept_id, return_to_concept_id, required_tool, generation_mode,
                   model, status, selected_action, override_reason, created_at, resolved_at
            FROM agent_decisions WHERE workspace_id = ? ORDER BY created_at, rowid
            """,
            (workspace_id,),
        ).fetchall())
        searches = _dict_rows(connection.execute(
            """
            SELECT id, session_id, concept_id, source_gap_id, agent_decision_id,
                   query_scope, reason_for_user, permission_snapshot, confirmation_status,
                   search_status, generation_mode, model, error_code, created_at,
                   confirmed_at, executed_at, completed_at
            FROM search_requests WHERE workspace_id = ? ORDER BY created_at, rowid
            """,
            (workspace_id,),
        ).fetchall())
        external_sources = _dict_rows(connection.execute(
            "SELECT * FROM external_sources WHERE workspace_id = ? ORDER BY created_at, rank",
            (workspace_id,),
        ).fetchall())
        ai_activity = _dict_rows(connection.execute(
            """
            SELECT session_id, operation, generation_mode, model, status, error_code,
                   created_at, completed_at
            FROM ai_activity_logs WHERE workspace_id = ? ORDER BY created_at, rowid
            """,
            (workspace_id,),
        ).fetchall())
        events = _json_columns(_dict_rows(connection.execute(
            "SELECT session_id, event_type, detail_json, created_at FROM session_events WHERE workspace_id = ? ORDER BY created_at, rowid",
            (workspace_id,),
        ).fetchall()), ("detail_json",))
    return {
        "export": {
            "product": "StartOne",
            "format_version": 1,
            "exported_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
            "excludes": ["API keys", "server file paths", "hidden answer keys", "internal prompts", "model response IDs"],
        },
        "sessions": sessions,
        "sources": sources,
        "source_chunks": source_chunks,
        "source_reference_reports": source_reports,
        "source_coverages": coverages,
        "knowledge_maps": maps,
        "concepts": concepts,
        "drafts": drafts,
        "tutor_messages": tutor_messages,
        "activities": activities,
        "attempts": attempts,
        "feedback": feedback,
        "learning_evidence": evidence,
        "agent_decisions": decisions,
        "search_requests": searches,
        "external_sources": external_sources,
        "ai_activity": ai_activity,
        "session_events": events,
    }


def workspace_export_markdown(data: dict[str, Any]) -> str:
    lines = [
        "# StartOne learning record",
        "",
        f"Exported: {data['export']['exported_at']}",
        "",
    ]
    sessions = data["sessions"]
    if not sessions:
        return "\n".join(lines + ["No learning sessions are saved in this workspace.", ""])
    for session in sessions:
        session_id = session["id"]
        lines.extend([
            f"## {session['name']}",
            "",
            f"- State: {str(session['state']).replace('_', ' ')}",
            f"- Goal: {session.get('goal') or 'Not set'}",
            f"- Mode: {session.get('mode')}",
            f"- Last saved: {session.get('last_saved_at') or session.get('updated_at')}",
            "",
            "### Sources",
            "",
        ])
        sources = [item for item in data["sources"] if item["session_id"] == session_id]
        lines.extend(
            [f"- {item['filename']} — {item['parse_status']} ({item['source_origin']})" for item in sources]
            or ["- No saved sources"]
        )
        concepts = [item for item in data["concepts"] if item["session_id"] == session_id]
        lines.extend(["", "### Concepts", ""])
        lines.extend(
            [f"- {item['title']} — {item['status']}" for item in concepts]
            or ["- No knowledge map generated"]
        )
        evidence = [item for item in data["learning_evidence"] if item["session_id"] == session_id]
        lines.extend(["", "### Learning evidence", ""])
        lines.extend(
            [f"- {item['activity_type']}: {item['outcome']} · hints {item['hint_depth']} · {item['elapsed_seconds']} seconds" for item in evidence]
            or ["- No evidence recorded"]
        )
        decisions = [item for item in data["agent_decisions"] if item["session_id"] == session_id]
        lines.extend(["", "### Planning decisions", ""])
        lines.extend(
            [f"- {item.get('selected_action') or item['action']}: {item['reason_for_user']}" for item in decisions]
            or ["- No Agent decision recorded"]
        )
        lines.append("")
    return "\n".join(lines)


def ai_activity_log(database_path: Path, workspace_id: str) -> list[dict[str, Any]]:
    with connect(database_path) as connection:
        rows = connection.execute(
            """
            SELECT l.id, l.session_id, s.name AS session_name, l.operation,
                   l.generation_mode, l.model, l.status, l.error_code,
                   l.created_at, l.completed_at
            FROM ai_activity_logs l JOIN learning_sessions s ON s.id = l.session_id
            WHERE l.workspace_id = ? AND s.workspace_id = ?
            ORDER BY l.created_at DESC, l.rowid DESC LIMIT 200
            """,
            (workspace_id, workspace_id),
        ).fetchall()
    return _dict_rows(rows)


def get_session_summary(database_path: Path, workspace_id: str, session_id: str) -> dict[str, Any]:
    session = get_session(database_path, workspace_id, session_id)
    with connect(database_path) as connection:
        concepts = _dict_rows(connection.execute(
            "SELECT id, title, status, order_index FROM concepts WHERE session_id = ? AND workspace_id = ? ORDER BY order_index",
            (session_id, workspace_id),
        ).fetchall())
        evidence = _dict_rows(connection.execute(
            "SELECT activity_type, outcome, source_gap_signal, timestamp FROM learning_evidence WHERE session_id = ? AND workspace_id = ? ORDER BY timestamp, rowid",
            (session_id, workspace_id),
        ).fetchall())
        latest_note = connection.execute(
            "SELECT content FROM drafts WHERE session_id = ? AND workspace_id = ? AND draft_type = 'focus_note'",
            (session_id, workspace_id),
        ).fetchone()
        current = connection.execute(
            "SELECT title FROM concepts WHERE id = ? AND workspace_id = ?",
            (session.get("active_concept_id"), workspace_id),
        ).fetchone()
    current_title = str(current["title"]) if current else "the first planned concept"
    completed = [item["title"] for item in concepts if item["status"] == "completed"]
    remaining = [item["title"] for item in concepts if item["status"] != "completed"]
    return {
        "session": {
            "id": session["id"],
            "name": session["name"],
            "state": session["state"],
            "ended_at": session.get("ended_at"),
        },
        "summary": {
            "title": "Session complete" if session["state"] == "session_summary" else "Saved session checkpoint",
            "current_concept": current_title,
            "completed_concepts": completed,
            "still_to_review": remaining,
            "evidence_count": len(evidence),
            "latest_outcome": evidence[-1]["outcome"] if evidence else None,
            "saved_focus_note": str(latest_note["content"]) if latest_note else "No focus note was saved.",
            "restart_action": f"For two minutes, explain {current_title} in one sentence before reopening the source.",
            "penalty_for_stopping": False,
        },
    }


def _unlink_workspace_files(upload_dir: Path, workspace_id: str, paths: list[str]) -> bool:
    root = (upload_dir / workspace_id).resolve()
    complete = True
    for raw_path in paths:
        candidate = Path(raw_path).resolve()
        if not candidate.is_relative_to(root):
            complete = False
            continue
        try:
            candidate.unlink(missing_ok=True)
        except OSError:
            complete = False
    return complete


def _dict_rows(rows) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


def _json_rows(rows, source_key: str, destination_key: str) -> list[dict[str, Any]]:
    result = []
    for raw in rows:
        row = dict(raw)
        row[destination_key] = _parse_json(row.pop(source_key, None))
        result.append(row)
    return result


def _json_columns(rows: list[dict[str, Any]], keys: tuple[str, ...]) -> list[dict[str, Any]]:
    for row in rows:
        for key in keys:
            if key in row:
                destination = key.removesuffix("_json")
                row[destination] = _parse_json(row.pop(key))
    return rows


def _parse_json(value: Any) -> Any:
    try:
        return json.loads(str(value or "null"))
    except json.JSONDecodeError:
        return None
