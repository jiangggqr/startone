"""Contextual Tutor constrained to the active concept and verified sources."""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any, Callable
import uuid

from app.ai import (
    ModelGatewayError,
    SourceReference,
    TutorResponseOutput,
    parse_structured_response,
)
from app.config import Settings
from app.db import connect
from app.focus import get_focus_workspace
from app.sources import SourceError, get_session


DEMO_TUTOR_MODEL = "deterministic-demo-tutor-v1"
QUICK_ACTIONS = [
    {"id": "simplify", "label": "Explain more simply"},
    {"id": "define_terms", "label": "Define the key terms"},
    {"id": "concrete_example", "label": "Give a concrete example"},
    {"id": "previous_connection", "label": "Connect to the previous concept"},
    {"id": "hint_only", "label": "Give only a hint"},
    {"id": "check_understanding", "label": "Check my understanding"},
]
QUICK_ACTION_IDS = {item["id"] for item in QUICK_ACTIONS}


def open_tutor(
    database_path: Path,
    workspace_id: str,
    session_id: str,
    expected_session_version: int,
) -> dict[str, Any]:
    session = get_session(database_path, workspace_id, session_id)
    _require_tutor_state(session)
    _require_version(int(session["version"]), expected_session_version, "session_version_conflict")
    concept_id = str(session.get("active_concept_id") or "")
    if not concept_id:
        raise SourceError("active_concept_missing", "Open a current concept before starting Tutor.", status_code=409)
    with connect(database_path) as connection:
        thread = connection.execute(
            """
            SELECT * FROM tutor_threads
            WHERE session_id = ? AND workspace_id = ? AND concept_id = ?
            """,
            (session_id, workspace_id, concept_id),
        ).fetchone()
        if thread:
            thread_id = str(thread["id"])
            connection.execute(
                """
                UPDATE tutor_threads
                SET status = 'open', closed_at = NULL, version = version + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (thread_id,),
            )
        else:
            thread_id = str(uuid.uuid4())
            connection.execute(
                """
                INSERT INTO tutor_threads(id, workspace_id, session_id, concept_id)
                VALUES (?, ?, ?, ?)
                """,
                (thread_id, workspace_id, session_id, concept_id),
            )
        connection.execute(
            """
            UPDATE learning_sessions
            SET tutor_open = 1, active_activity_id = ?, version = version + 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND workspace_id = ?
            """,
            (thread_id, session_id, workspace_id),
        )
        _record_event(connection, workspace_id, session_id, "tutor_opened", {"thread_id": thread_id})
    return get_tutor(database_path, workspace_id, session_id)


def get_tutor(database_path: Path, workspace_id: str, session_id: str) -> dict[str, Any]:
    session = get_session(database_path, workspace_id, session_id)
    if session["state"] != "learning_concept":
        raise SourceError("tutor_not_available", "Tutor is available inside the current concept.", status_code=409)
    focus = get_focus_workspace(database_path, workspace_id, session_id)
    with connect(database_path) as connection:
        thread = connection.execute(
            """
            SELECT * FROM tutor_threads
            WHERE session_id = ? AND workspace_id = ? AND concept_id = ?
            """,
            (session_id, workspace_id, session.get("active_concept_id")),
        ).fetchone()
        if not thread:
            raise SourceError(
                "tutor_not_open",
                "Open Tutor from the current concept before sending a message.",
                status_code=409,
                saved_state="Your concept and focus note remain saved.",
            )
        rows = connection.execute(
            "SELECT * FROM tutor_messages WHERE thread_id = ? ORDER BY rowid",
            (thread["id"],),
        ).fetchall()
    route = focus["route"]
    current_index = next((index for index, item in enumerate(route) if item["is_active"]), 0)
    previous_title = route[current_index - 1]["title"] if current_index > 0 else None
    next_title = route[current_index + 1]["title"] if current_index + 1 < len(route) else None
    all_source_details = _all_source_details(database_path, workspace_id, session_id)
    return {
        "session": focus["session"] | {"tutor_open": bool(session.get("tutor_open"))},
        "thread": _public_thread(dict(thread)),
        "context": {
            "concept": focus["active_concept"],
            "previous_concept_title": previous_title,
            "next_concept_title": next_title,
            "focus_note": focus["drafts"]["focus_note"],
        },
        "messages": [
            _public_message(dict(row), all_source_details)
            for row in rows
        ],
        "quick_actions": QUICK_ACTIONS,
        "guidance_ladder": [
            "Clarify the exact difficulty",
            "Give a direction",
            "Give a structure",
            "Give key terms",
            "Give part of an example",
            "Give a concise explanation",
            "Ask a checking question",
        ],
        "boundaries": {
            "active_concept_only": True,
            "can_change_route": False,
            "uses_uploaded_material_only": True,
            "creates_agent_decision": False,
        },
    }


def send_tutor_message(
    settings: Settings,
    workspace_id: str,
    session_id: str,
    message: str,
    quick_action: str | None,
    expected_thread_version: int,
    *,
    client_factory: Callable[[Settings], Any] | None = None,
) -> dict[str, Any]:
    session = get_session(settings.database_path, workspace_id, session_id)
    _require_tutor_state(session)
    if quick_action is not None and quick_action not in QUICK_ACTION_IDS:
        raise SourceError("invalid_tutor_action", "Choose one of the available Tutor support actions.")
    cleaned = message.strip()
    if not cleaned:
        raise SourceError("empty_tutor_message", "Write a question or choose a support action.", status_code=422)
    context = _tutor_generation_context(settings.database_path, workspace_id, session_id, cleaned)
    thread = context["thread"]
    if thread["status"] != "open" or not session.get("tutor_open"):
        raise SourceError("tutor_not_open", "Reopen Tutor before sending another message.", status_code=409)
    _require_version(int(thread["version"]), expected_thread_version, "tutor_version_conflict")
    activity_id = _start_ai_activity(settings, workspace_id, session_id)
    try:
        if settings.mode == "demo":
            output = _demo_tutor_response(context, cleaned, quick_action)
            model = DEMO_TUTOR_MODEL
            response_id = None
        else:
            result = parse_structured_response(
                settings,
                workspace_id,
                TutorResponseOutput,
                _tutor_instructions(context, quick_action),
                _tutor_source_context(context, cleaned),
                client_factory=client_factory,
            )
            output = result.output
            model = settings.openai_model
            response_id = result.response_id
        _validate_source_refs(settings.database_path, workspace_id, session_id, output)
        _persist_turn(
            settings.database_path,
            workspace_id,
            session_id,
            thread,
            cleaned,
            quick_action,
            expected_thread_version,
            output,
        )
        _finish_ai_activity(settings.database_path, activity_id, "success", response_id=response_id)
    except ModelGatewayError as exc:
        _finish_ai_activity(settings.database_path, activity_id, "error", error_code=exc.error_code)
        raise SourceError(
            exc.error_code,
            exc.user_message,
            status_code=503,
            saved_state="Your previous Tutor conversation and unsent text are saved.",
        ) from exc
    except SourceError as exc:
        _finish_ai_activity(settings.database_path, activity_id, "error", error_code=exc.error_code)
        raise
    payload = get_tutor(settings.database_path, workspace_id, session_id)
    payload["generation"] = {
        "mode": settings.mode,
        "model": model,
    }
    return payload


def close_tutor(
    database_path: Path,
    workspace_id: str,
    session_id: str,
    expected_thread_version: int,
) -> dict[str, Any]:
    session = get_session(database_path, workspace_id, session_id)
    _require_tutor_state(session)
    with connect(database_path) as connection:
        thread = connection.execute(
            """
            SELECT * FROM tutor_threads
            WHERE session_id = ? AND workspace_id = ? AND concept_id = ?
            """,
            (session_id, workspace_id, session.get("active_concept_id")),
        ).fetchone()
        if not thread:
            raise SourceError("tutor_not_open", "There is no Tutor conversation to close.", status_code=409)
        _require_version(int(thread["version"]), expected_thread_version, "tutor_version_conflict")
        new_messages = connection.execute(
            """
            SELECT rowid AS message_rowid, guidance_level, checking_question,
                   confusion_signal, prerequisite_gap_signal
            FROM tutor_messages
            WHERE thread_id = ? AND role = 'tutor' AND rowid > ?
            ORDER BY rowid
            """,
            (thread["id"], int(thread["last_evidence_message_rowid"] or 0)),
        ).fetchall()
        signals = connection.execute(
            """
            SELECT
              SUM(CASE WHEN confusion_signal IS NOT NULL THEN 1 ELSE 0 END) AS confusion_count,
              SUM(CASE WHEN prerequisite_gap_signal IS NOT NULL THEN 1 ELSE 0 END) AS prerequisite_count
            FROM tutor_messages WHERE thread_id = ? AND role = 'tutor'
            """,
            (thread["id"],),
        ).fetchone()
        evidence_id = None
        latest_message_rowid = int(thread["last_evidence_message_rowid"] or 0)
        if new_messages:
            latest_message_rowid = int(new_messages[-1]["message_rowid"])
            confusion_signals = list(dict.fromkeys(
                str(row["confusion_signal"]).strip()
                for row in new_messages
                if row["confusion_signal"] and str(row["confusion_signal"]).strip()
            ))
            gap_signals = list(dict.fromkeys(
                str(row["prerequisite_gap_signal"]).strip()
                for row in new_messages
                if row["prerequisite_gap_signal"] and str(row["prerequisite_gap_signal"]).strip()
            ))
            evidence_id = str(uuid.uuid4())
            connection.execute(
                """
                INSERT INTO learning_evidence(
                    id, workspace_id, session_id, concept_id, origin_id, activity_type,
                    outcome, key_point_coverage_json, misconception_tags_json, hint_depth,
                    elapsed_seconds, tutor_confusion_signals_json, source_gap_signal
                ) VALUES (?, ?, ?, ?, ?, 'tutor_check', 'unresolved', '[]', '[]', ?, 0, ?, ?)
                """,
                (
                    evidence_id, workspace_id, session_id, thread["concept_id"],
                    f"tutor:{thread['id']}:{latest_message_rowid}",
                    max(int(row["guidance_level"] or 0) for row in new_messages),
                    json.dumps(confusion_signals), gap_signals[0] if gap_signals else None,
                ),
            )
        connection.execute(
            """
            UPDATE tutor_threads
            SET status = 'closed', version = version + 1,
                last_evidence_message_rowid = ?,
                updated_at = CURRENT_TIMESTAMP, closed_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (latest_message_rowid, thread["id"]),
        )
        connection.execute(
            """
            UPDATE learning_sessions
            SET tutor_open = 0, active_activity_id = NULL,
                version = version + 1, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND workspace_id = ?
            """,
            (session_id, workspace_id),
        )
        _record_event(
            connection,
            workspace_id,
            session_id,
            "tutor_closed",
            {
                "thread_id": str(thread["id"]),
                "confusion_signal_count": int(signals["confusion_count"] or 0),
                "prerequisite_signal_count": int(signals["prerequisite_count"] or 0),
                "learning_evidence_created": evidence_id is not None,
                "learning_evidence_id": evidence_id,
            },
        )
    return get_focus_workspace(database_path, workspace_id, session_id)


def _tutor_generation_context(
    database_path: Path,
    workspace_id: str,
    session_id: str,
    user_message: str,
) -> dict[str, Any]:
    payload = get_tutor(database_path, workspace_id, session_id)
    with connect(database_path) as connection:
        chunks = connection.execute(
            """
            SELECT c.*, d.filename, d.source_origin
            FROM source_chunks c JOIN source_documents d ON d.id = c.source_id
            WHERE d.session_id = ? AND d.workspace_id = ?
              AND d.parse_status IN ('success', 'partial_success')
            ORDER BY d.created_at, c.start_char
            """,
            (session_id, workspace_id),
        ).fetchall()
        session = connection.execute(
            "SELECT * FROM learning_sessions WHERE id = ? AND workspace_id = ?",
            (session_id, workspace_id),
        ).fetchone()
    all_chunks = [dict(row) for row in chunks]
    active_chunk_ids = {
        str(ref["chunk_id"])
        for ref in payload["context"]["concept"]["source_refs"]
    }
    query_terms = {
        term
        for term in re.findall(r"[a-z0-9]+", user_message.lower())
        if len(term) >= 4
    }
    selected = [chunk for chunk in all_chunks if str(chunk["id"]) in active_chunk_ids]
    ranked = sorted(
        (chunk for chunk in all_chunks if str(chunk["id"]) not in active_chunk_ids),
        key=lambda chunk: sum(
            term in f"{chunk.get('heading_path') or ''} {chunk.get('text') or ''}".lower()
            for term in query_terms
        ),
        reverse=True,
    )
    selected.extend(
        chunk
        for chunk in ranked
        if query_terms
        and any(term in f"{chunk.get('heading_path') or ''} {chunk.get('text') or ''}".lower() for term in query_terms)
    )
    payload["chunks"] = selected[:6]
    payload["available_filenames"] = sorted({str(chunk["filename"]) for chunk in all_chunks})
    payload["session_record"] = dict(session) if session else {}
    return payload


def _demo_tutor_response(
    context: dict[str, Any],
    user_message: str,
    quick_action: str | None,
) -> TutorResponseOutput:
    active_refs = [SourceReference.model_validate(item) for item in context["context"]["concept"]["source_refs"]]
    primary_ref = active_refs[0]
    primary_origin = "uploaded"
    source_label = "uploaded material"
    lowered = user_message.lower()
    prior = context["context"].get("previous_concept_title") or "the previous concept"
    has_matrix_source = "matrix_prerequisite.md" in context["available_filenames"]

    if quick_action == "simplify":
        return TutorResponseOutput(
            message="Self-attention does two jobs: it compares the current position with other positions, then combines information from them according to those relevance scores.",
            guidance_level=6,
            checking_question="Which of those two jobs changes the current position's representation?",
            source_origin=primary_origin,
            source_refs=[primary_ref],
            confusion_signal=None,
            prerequisite_gap_signal=None,
        )
    if quick_action == "define_terms":
        return TutorResponseOutput(
            message="A relevance score is a number that represents how strongly one position should use information from another. A value representation is the information that can be combined after those scores become weights.",
            guidance_level=4,
            checking_question="What controls how much each value contributes?",
            source_origin=primary_origin,
            source_refs=[primary_ref],
            confusion_signal=None,
            prerequisite_gap_signal=None,
        )
    if quick_action == "concrete_example":
        return TutorResponseOutput(
            message="For example, in 'The animal did not cross the street because it was tired,' the mechanism described in your material lets 'it' give more weight to 'animal' than to 'street,' then combine more animal-related information.",
            guidance_level=5,
            checking_question="In this example, why should 'animal' contribute more than 'street'?",
            source_origin="uploaded",
            source_refs=[primary_ref],
            confusion_signal=None,
            prerequisite_gap_signal=None,
        )
    if quick_action == "previous_connection":
        return TutorResponseOutput(
            message=f"{prior} established why tokens need information from other positions. Self-attention is the mechanism that compares those positions and combines the useful information.",
            guidance_level=3,
            checking_question="Which part of self-attention addresses the need for cross-token context?",
            source_origin=primary_origin,
            source_refs=[primary_ref],
            confusion_signal=None,
            prerequisite_gap_signal=None,
        )
    if quick_action == "hint_only":
        return TutorResponseOutput(
            message="Use two verbs and keep them in order: first compare, then ____.",
            guidance_level=2,
            checking_question="What second verb completes the process?",
            source_origin=primary_origin,
            source_refs=[primary_ref],
            confusion_signal=None,
            prerequisite_gap_signal=None,
        )
    if quick_action == "check_understanding":
        return TutorResponseOutput(
            message="Try this without reopening the explanation: describe the two jobs of self-attention in one sentence.",
            guidance_level=7,
            checking_question="What happens after relevance has been compared?",
            source_origin=primary_origin,
            source_refs=[primary_ref],
            confusion_signal=None,
            prerequisite_gap_signal=None,
        )
    if any(term in lowered for term in ("dot product", "matrix", "vector")):
        signal = None if has_matrix_source else f"The {source_label} does not define the named dot-product prerequisite."
        message = (
            f"The {source_label} defines a dot product as multiplying matching vector components and adding them to produce one score. For this concept, that score is used only to decide relevance before values are combined."
            if has_matrix_source
            else f"That question points to the dot-product prerequisite, which the current {source_label} does not define. I can keep the gap visible so StartOne can ask you to add material that covers it."
        )
        ref = _find_chunk_ref(context["chunks"], "dot product") if has_matrix_source else primary_ref
        return TutorResponseOutput(
            message=message,
            guidance_level=4,
            checking_question="For self-attention, what is the score used for after it is computed?",
            source_origin=primary_origin,
            source_refs=[ref],
            confusion_signal="User asked for a mathematical prerequisite while learning self-attention.",
            prerequisite_gap_signal=signal,
        )
    if any(term in lowered for term in ("don't understand", "do not understand", "confused", "not sure", "unclear")):
        return TutorResponseOutput(
            message="Let's narrow it down. Self-attention first decides which other positions matter, then uses that decision to combine their information. Which part is unclear: deciding relevance or combining information?",
            guidance_level=1,
            checking_question="Is the comparison step or the combination step the unclear part?",
            source_origin=primary_origin,
            source_refs=[primary_ref],
            confusion_signal="User explicitly reported that part of the active concept remains unclear.",
            prerequisite_gap_signal=None,
        )
    if any(term in lowered for term in ("combine", "weighted", "value")):
        return TutorResponseOutput(
            message="You identified the combination step. The precise detail is that relevance scores act as weights, so more relevant value information contributes more to the new representation.",
            guidance_level=3,
            checking_question="What would happen to a value with a larger relevance weight?",
            source_origin=primary_origin,
            source_refs=[primary_ref],
            confusion_signal=None,
            prerequisite_gap_signal=None,
        )
    return TutorResponseOutput(
        message="Let's start with one smaller question: why might the current position need information from another position in the same sequence?",
        guidance_level=1,
        checking_question="What can context reveal that the current position alone cannot?",
        source_origin=primary_origin,
        source_refs=[primary_ref],
        confusion_signal=None,
        prerequisite_gap_signal=None,
    )


def _find_chunk_ref(chunks: list[dict[str, Any]], term: str) -> SourceReference:
    lowered = term.lower()
    for chunk in chunks:
        if lowered in f"{chunk.get('heading_path') or ''} {chunk.get('text') or ''}".lower():
            return SourceReference(source_id=str(chunk["source_id"]), chunk_id=str(chunk["id"]))
    raise SourceError("source_reference_invalid", "The Tutor prerequisite source is unavailable.", status_code=409)


def _tutor_instructions(context: dict[str, Any], quick_action: str | None) -> str:
    concept = context["context"]["concept"]
    session = context["session_record"]
    origin_rule = "Uploaded material is the only learning source."
    return (
        "You are the Contextual Tutor inside an English learning app. Stay strictly inside the active concept. "
        f"{origin_rule} Use the least sufficient guidance by default, following levels 1 through 7. "
        "You may explain, clarify, give a simple example grounded in the supplied material, or ask a checking question. "
        "You must not change the route, choose a next concept, score mastery, create a recommendation, end the session, "
        "use outside material, or make medical claims. Never reveal hidden reasoning. "
        "Every source reference must be an exact supplied source_id/chunk_id pair and source_origin must be uploaded. "
        "A prerequisite_gap_signal is only a factual, named observation that the supplied material lacks the prerequisite; "
        "it may allow the Planning Agent to ask the learner for more material, but it is not itself a recommendation. "
        "Do not infer prior mastery or assume a pre-test exists; calibrate support from the current conversation and validated evidence only. "
        f"Active concept: {concept['title']}. Role: {concept['role_in_map']}. Definition: {concept['plain_definition']}. "
        f"Learner goal: {session.get('goal')}. Prior knowledge: {session.get('prior_knowledge')}. "
        f"Requested quick action: {quick_action or 'free question'}."
    )


def _tutor_source_context(context: dict[str, Any], user_message: str) -> str:
    parts = []
    used = 0
    for chunk in context["chunks"]:
        text = str(chunk["text"])
        if used + len(text) > 22_000:
            break
        used += len(text)
        parts.append(
            "\n".join(
                [
                    "<source_excerpt>",
                    f"source_id: {chunk['source_id']}",
                    f"chunk_id: {chunk['id']}",
                    f"filename: {chunk['filename']}",
                    f"source_origin: {chunk['source_origin']}",
                    f"heading: {chunk.get('heading_path') or ''}",
                    f"lines: {chunk.get('start_line') or ''}-{chunk.get('end_line') or ''}",
                    "content:",
                    text,
                    "</source_excerpt>",
                ]
            )
        )
    recent = context["messages"][-12:]
    conversation = "\n".join(f"{item['role']}: {item['message']}" for item in recent)
    return (
        "\n\n".join(parts)
        + "\n\n<untrusted_conversation>\n"
        + conversation
        + f"\nuser: {user_message}\n</untrusted_conversation>"
    )


def _validate_source_refs(
    database_path: Path,
    workspace_id: str,
    session_id: str,
    output: TutorResponseOutput,
) -> None:
    requested = {(ref.source_id, ref.chunk_id) for ref in output.source_refs}
    with connect(database_path) as connection:
        valid = {
            (str(row["source_id"]), str(row["chunk_id"]))
            for row in connection.execute(
                """
                SELECT d.id AS source_id, c.id AS chunk_id
                FROM source_chunks c JOIN source_documents d ON d.id = c.source_id
                WHERE d.session_id = ? AND d.workspace_id = ?
                  AND d.parse_status IN ('success', 'partial_success')
                """,
                (session_id, workspace_id),
            )
        }
    if not requested.issubset(valid):
        raise SourceError(
            "source_reference_invalid",
            "The Tutor response referenced an unavailable source location, so it was not saved or displayed. Retry the message.",
            status_code=422,
            saved_state="Your previous Tutor conversation and unsent text are saved.",
        )


def _persist_turn(
    database_path: Path,
    workspace_id: str,
    session_id: str,
    thread: dict[str, Any],
    user_message: str,
    quick_action: str | None,
    expected_thread_version: int,
    output: TutorResponseOutput,
) -> None:
    with connect(database_path) as connection:
        current = connection.execute(
            "SELECT version, status FROM tutor_threads WHERE id = ? AND workspace_id = ?",
            (thread["id"], workspace_id),
        ).fetchone()
        if not current or current["status"] != "open":
            raise SourceError("tutor_not_open", "Reopen Tutor before sending another message.", status_code=409)
        _require_version(int(current["version"]), expected_thread_version, "tutor_version_conflict")
        user_id = str(uuid.uuid4())
        tutor_id = str(uuid.uuid4())
        connection.execute(
            """
            INSERT INTO tutor_messages(
                id, workspace_id, session_id, thread_id, concept_id, role,
                message, quick_action
            ) VALUES (?, ?, ?, ?, ?, 'user', ?, ?)
            """,
            (user_id, workspace_id, session_id, thread["id"], thread["concept_id"], user_message, quick_action),
        )
        connection.execute(
            """
            INSERT INTO tutor_messages(
                id, workspace_id, session_id, thread_id, concept_id, role,
                message, guidance_level, checking_question, source_origin,
                source_refs_json, confusion_signal, prerequisite_gap_signal
            ) VALUES (?, ?, ?, ?, ?, 'tutor', ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                tutor_id,
                workspace_id,
                session_id,
                thread["id"],
                thread["concept_id"],
                output.message,
                output.guidance_level,
                output.checking_question,
                output.source_origin,
                json.dumps([ref.model_dump() for ref in output.source_refs]),
                output.confusion_signal,
                output.prerequisite_gap_signal,
            ),
        )
        connection.execute(
            """
            UPDATE tutor_threads
            SET version = version + 1, last_guidance_level = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (output.guidance_level, thread["id"]),
        )
        connection.execute(
            """
            UPDATE learning_sessions
            SET last_saved_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND workspace_id = ?
            """,
            (session_id, workspace_id),
        )
        _record_event(
            connection,
            workspace_id,
            session_id,
            "tutor_turn",
            {
                "thread_id": str(thread["id"]),
                "user_message_id": user_id,
                "tutor_message_id": tutor_id,
                "guidance_level": output.guidance_level,
                "source_origin": output.source_origin,
                "confusion_signal_present": output.confusion_signal is not None,
                "prerequisite_gap_signal_present": output.prerequisite_gap_signal is not None,
            },
        )


def _public_thread(thread: dict[str, Any]) -> dict[str, Any]:
    return {key: thread.get(key) for key in ("id", "session_id", "concept_id", "status", "version", "last_guidance_level", "created_at", "updated_at", "closed_at")}


def _public_message(message: dict[str, Any], source_details: list[dict[str, Any]]) -> dict[str, Any]:
    refs = json.loads(str(message.get("source_refs_json") or "[]"))
    details = [
        detail
        for detail in source_details
        if any(detail["source_id"] == ref["source_id"] and detail["chunk_id"] == ref["chunk_id"] for ref in refs)
    ]
    return {
        "id": message["id"],
        "role": message["role"],
        "message": message["message"],
        "quick_action": message.get("quick_action"),
        "guidance_level": message.get("guidance_level"),
        "checking_question": message.get("checking_question"),
        "source_origin": message.get("source_origin"),
        "source_refs": refs,
        "source_ref_details": details,
        "confusion_signal": message.get("confusion_signal"),
        "prerequisite_gap_signal": message.get("prerequisite_gap_signal"),
        "created_at": message.get("created_at"),
    }


def _all_source_details(database_path: Path, workspace_id: str, session_id: str) -> list[dict[str, Any]]:
    with connect(database_path) as connection:
        rows = connection.execute(
            """
            SELECT d.id AS source_id, d.filename, d.source_origin, d.media_kind,
                   c.id AS chunk_id, c.heading_path, c.page_number, c.page_chunk_index,
                   c.paragraph_number, c.start_line, c.end_line, c.start_char, c.end_char
            FROM source_chunks c JOIN source_documents d ON d.id = c.source_id
            WHERE d.session_id = ? AND d.workspace_id = ?
              AND d.parse_status IN ('success', 'partial_success')
            ORDER BY d.created_at, c.start_char
            """,
            (session_id, workspace_id),
        ).fetchall()
    details = []
    for row in rows:
        item = dict(row)
        if item["media_kind"] == "pdf":
            location = f"Page {item['page_number']} · excerpt {item['page_chunk_index']}"
        elif item["media_kind"] == "pasted":
            location = f"Paragraph {item['paragraph_number']} · characters {item['start_char']}–{item['end_char']}"
        else:
            location = f"{item['heading_path'] or 'Document'} · lines {item['start_line']}–{item['end_line']}"
        details.append(
            {
                "source_id": item["source_id"],
                "chunk_id": item["chunk_id"],
                "filename": item["filename"],
                "source_origin": item["source_origin"],
                "location": location,
            }
        )
    return details


def _require_tutor_state(session: dict[str, Any]) -> None:
    if session.get("is_paused"):
        raise SourceError(
            "session_paused",
            "Resume the session before using Tutor.",
            status_code=409,
            saved_state="Your Tutor conversation and drafts remain saved.",
        )
    if session["state"] != "learning_concept":
        raise SourceError("tutor_not_available", "Tutor is available inside the current concept.", status_code=409)


def _require_version(current: int, expected: int, code: str) -> None:
    if current != expected:
        raise SourceError(
            code,
            "This Tutor conversation changed in another page. Reload it before sending again.",
            status_code=409,
            saved_state="The newer Tutor conversation and your unsent text are preserved.",
        )


def _start_ai_activity(settings: Settings, workspace_id: str, session_id: str) -> str:
    activity_id = str(uuid.uuid4())
    model = DEMO_TUTOR_MODEL if settings.mode == "demo" else settings.openai_model
    with connect(settings.database_path) as connection:
        connection.execute(
            """
            INSERT INTO ai_activity_logs(
                id, workspace_id, session_id, operation, generation_mode, model, status
            ) VALUES (?, ?, ?, 'tutor_turn', ?, ?, 'started')
            """,
            (activity_id, workspace_id, session_id, settings.mode, model),
        )
    return activity_id


def _finish_ai_activity(
    database_path: Path,
    activity_id: str,
    status: str,
    *,
    response_id: str | None = None,
    error_code: str | None = None,
) -> None:
    with connect(database_path) as connection:
        connection.execute(
            """
            UPDATE ai_activity_logs
            SET status = ?, response_id = ?, error_code = ?, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (status, response_id, error_code, activity_id),
        )


def _record_event(connection, workspace_id: str, session_id: str, event_type: str, detail: dict[str, Any]) -> None:
    connection.execute(
        """
        INSERT INTO session_events(id, workspace_id, session_id, event_type, detail_json)
        VALUES (?, ?, ?, ?, ?)
        """,
        (str(uuid.uuid4()), workspace_id, session_id, event_type, json.dumps(detail)),
    )
