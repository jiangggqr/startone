"""Evidence-bounded Adaptive Planning Agent and server-controlled transitions."""

from __future__ import annotations

from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Callable
import uuid

from app.ai import AgentAction, AgentDecisionOutput, ModelGatewayError
from app.config import Settings
from app.db import connect
from app.sources import SourceError, get_session


DEMO_AGENT_MODEL = "deterministic-demo-agent-v1"
ACTION_LABELS: dict[str, str] = {
    "continue_next": "Continue to the next concept",
    "retry_current": "Retry this concept",
    "switch_activity": "Switch practice format",
    "simplify_current": "Ask Tutor to simplify this concept",
    "insert_prerequisite": "Insert one short prerequisite",
    "review_previous": "Review the previous concept",
    "request_search": "Request an external source search",
    "finish_session": "Finish this session",
}
TOOL_BY_ACTION = {
    "continue_next": "activate_concept",
    "retry_current": "create_activity",
    "switch_activity": "create_activity",
    "simplify_current": "open_tutor",
    "insert_prerequisite": "activate_concept",
    "review_previous": "activate_concept",
    "request_search": "request_search",
    "finish_session": "create_summary",
}


def create_agent_decision(
    settings: Settings,
    workspace_id: str,
    session_id: str,
    *,
    client_factory: Callable[[Settings], Any] | None = None,
) -> dict[str, Any]:
    """Create exactly one next-action proposal from validated LearningEvidence."""

    session = get_session(settings.database_path, workspace_id, session_id)
    if session.get("is_paused"):
        raise SourceError(
            "session_paused",
            "Resume the session before asking the Planning Agent for a next action.",
            status_code=409,
            saved_state="Your evidence and exact restart point remain saved.",
        )
    if session["state"] not in {"evidence_ready", "agent_decision"}:
        raise SourceError(
            "agent_decision_not_available",
            "Finish the current mastery step before asking the Planning Agent.",
            status_code=409,
            saved_state="Your current learning step is unchanged.",
        )

    context = _decision_context(settings.database_path, workspace_id, session_id)
    fingerprint = _evidence_fingerprint(context)
    existing = _decision_by_fingerprint(
        settings.database_path, workspace_id, session_id, fingerprint
    )
    if existing:
        return get_agent_decision(
            settings.database_path, workspace_id, str(existing["id"])
        )

    allowed = _allowed_action_metadata(context)
    if not allowed:
        raise SourceError(
            "agent_action_unavailable",
            "There is not enough validated evidence for a safe next-action decision.",
            status_code=409,
            saved_state="Your evidence remains saved without a recommendation.",
        )

    log_id = _start_ai_activity(settings, workspace_id, session_id)
    try:
        if settings.mode == "demo":
            output = _demo_decision(context, allowed)
            model = DEMO_AGENT_MODEL
            response_id = None
        else:
            output, response_id = _real_decision(
                settings,
                workspace_id,
                context,
                allowed,
                client_factory=client_factory,
            )
            model = settings.openai_model
        _validate_decision_output(output, allowed)
        decision_id = _persist_decision(
            settings.database_path,
            workspace_id,
            session_id,
            context,
            allowed,
            fingerprint,
            output,
            settings.mode,
            model,
        )
        _finish_ai_activity(
            settings.database_path, log_id, "success", response_id=response_id
        )
    except ModelGatewayError as exc:
        _finish_ai_activity(
            settings.database_path, log_id, "error", error_code=exc.error_code
        )
        raise SourceError(
            exc.error_code,
            exc.user_message,
            status_code=503,
            saved_state="Your LearningEvidence remains saved. The Agent decision can be retried safely.",
        ) from exc
    except SourceError as exc:
        _finish_ai_activity(
            settings.database_path, log_id, "error", error_code=exc.error_code
        )
        raise
    return get_agent_decision(settings.database_path, workspace_id, decision_id)


def get_latest_agent_decision(
    database_path: Path, workspace_id: str, session_id: str
) -> dict[str, Any]:
    get_session(database_path, workspace_id, session_id)
    with connect(database_path) as connection:
        row = connection.execute(
            """
            SELECT id FROM agent_decisions
            WHERE workspace_id = ? AND session_id = ?
            ORDER BY created_at DESC, rowid DESC LIMIT 1
            """,
            (workspace_id, session_id),
        ).fetchone()
    if not row:
        raise SourceError(
            "agent_decision_not_found",
            "No Planning Agent decision has been created for this evidence yet.",
            status_code=404,
        )
    return get_agent_decision(database_path, workspace_id, str(row["id"]))


def get_agent_decision(
    database_path: Path, workspace_id: str, decision_id: str
) -> dict[str, Any]:
    with connect(database_path) as connection:
        row = connection.execute(
            """
            SELECT d.*, c.title AS concept_title
            FROM agent_decisions d
            JOIN concepts c ON c.id = d.concept_id
            JOIN learning_sessions s ON s.id = d.session_id
            WHERE d.id = ? AND d.workspace_id = ? AND s.workspace_id = ?
            """,
            (decision_id, workspace_id, workspace_id),
        ).fetchone()
    if not row:
        raise SourceError(
            "agent_decision_not_found",
            "This Planning Agent decision is not available in the current workspace.",
            status_code=404,
        )
    snapshot = json.loads(str(row["evidence_snapshot_json"]))
    session = get_session(
        database_path, workspace_id, str(row["session_id"])
    )
    metadata = snapshot["action_metadata"]
    alternatives = [
        _public_action(action, item)
        for action, item in metadata.items()
        if action != row["action"]
    ]
    selected_action = row["selected_action"] or row["action"]
    return {
        "decision": {
            "id": row["id"],
            "session_id": row["session_id"],
            "concept_id": row["concept_id"],
            "concept_title": row["concept_title"],
            "action": row["action"],
            "action_label": ACTION_LABELS[str(row["action"])],
            "reason_for_user": row["reason_for_user"],
            "estimated_minutes": row["estimated_minutes"],
            "target_concept_id": row["target_concept_id"],
            "return_to_concept_id": row["return_to_concept_id"],
            "required_tool": row["required_tool"],
            "confidence": row["confidence"],
            "status": row["status"],
            "selected_action": selected_action,
            "selected_action_label": ACTION_LABELS[str(selected_action)],
            "override_reason": row["override_reason"],
            "version": row["version"],
            "created_at": row["created_at"],
            "resolved_at": row["resolved_at"],
        },
        "evidence_summary": snapshot["evidence_summary"],
        "feasibility_context": snapshot["feasibility_context"],
        "allowed_alternatives": alternatives,
        "session": _public_session(session),
        "generation": {
            "mode": row["generation_mode"],
            "model": row["model"],
            "internet_search_performed": False,
        },
        "boundaries": {
            "learning_performance_basis": "LearningEvidence only",
            "exactly_one_recommended_action": True,
            "agent_teaching_content": False,
            "user_override_penalty": False,
            "search_requested": selected_action == "request_search",
            "internet_search_performed": False,
        },
    }


def accept_agent_decision(
    database_path: Path,
    workspace_id: str,
    decision_id: str,
    expected_session_version: int,
) -> dict[str, Any]:
    return _resolve_decision(
        database_path,
        workspace_id,
        decision_id,
        expected_session_version,
        override_action=None,
        override_reason=None,
    )


def override_agent_decision(
    database_path: Path,
    workspace_id: str,
    decision_id: str,
    action: AgentAction,
    reason: str | None,
    expected_session_version: int,
) -> dict[str, Any]:
    return _resolve_decision(
        database_path,
        workspace_id,
        decision_id,
        expected_session_version,
        override_action=action,
        override_reason=(reason or "").strip() or None,
    )


def _resolve_decision(
    database_path: Path,
    workspace_id: str,
    decision_id: str,
    expected_session_version: int,
    *,
    override_action: AgentAction | None,
    override_reason: str | None,
) -> dict[str, Any]:
    with connect(database_path) as connection:
        row = connection.execute(
            "SELECT * FROM agent_decisions WHERE id = ? AND workspace_id = ?",
            (decision_id, workspace_id),
        ).fetchone()
        if not row:
            raise SourceError(
                "agent_decision_not_found",
                "This Planning Agent decision is not available in the current workspace.",
                status_code=404,
            )
        session = connection.execute(
            "SELECT * FROM learning_sessions WHERE id = ? AND workspace_id = ?",
            (row["session_id"], workspace_id),
        ).fetchone()
        if not session:
            raise SourceError("session_not_found", "This learning session is not available.", status_code=404)
        if int(session["version"]) != expected_session_version:
            raise SourceError(
                "session_version_conflict",
                "This planning step changed in another page. Reload the saved decision before continuing.",
                status_code=409,
                saved_state="The newer saved decision and evidence are unchanged.",
            )
        if session["is_paused"]:
            raise SourceError(
                "session_paused",
                "Resume the session before applying a planning decision.",
                status_code=409,
            )
        if row["status"] != "proposed" or session["state"] != "agent_decision":
            raise SourceError(
                "agent_decision_already_resolved",
                "This Planning Agent decision has already been applied.",
                status_code=409,
                saved_state="The applied learning state is unchanged.",
            )

        snapshot = json.loads(str(row["evidence_snapshot_json"]))
        metadata_by_action = snapshot["action_metadata"]
        selected = str(override_action or row["action"])
        if selected not in metadata_by_action:
            raise SourceError(
                "agent_override_not_allowed",
                "That path is not valid for the current evidence and session constraints.",
                status_code=422,
                saved_state="The original Agent decision remains available.",
            )
        metadata = metadata_by_action[selected]
        _apply_controlled_transition(
            connection,
            workspace_id,
            dict(session),
            decision_id,
            selected,
            metadata,
        )
        status = "overridden" if override_action else "accepted"
        connection.execute(
            """
            UPDATE agent_decisions
            SET status = ?, selected_action = ?, override_reason = ?,
                version = version + 1, resolved_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (status, selected, override_reason, decision_id),
        )
        _record_event(
            connection,
            workspace_id,
            str(row["session_id"]),
            "agent_decision_overridden" if override_action else "agent_decision_accepted",
            {
                "decision_id": decision_id,
                "proposed_action": row["action"],
                "selected_action": selected,
                "override_has_penalty": False,
            },
        )

    result = get_agent_decision(database_path, workspace_id, decision_id)
    result["execution"] = _execution_payload(
        database_path,
        workspace_id,
        str(result["decision"]["session_id"]),
        selected,
        metadata,
    )
    return result


def _decision_context(
    database_path: Path, workspace_id: str, session_id: str
) -> dict[str, Any]:
    with connect(database_path) as connection:
        session = connection.execute(
            "SELECT * FROM learning_sessions WHERE id = ? AND workspace_id = ?",
            (session_id, workspace_id),
        ).fetchone()
        if not session or not session["active_concept_id"]:
            raise SourceError(
                "active_concept_missing",
                "The current concept is unavailable. Review the saved learning map.",
                status_code=409,
            )
        concept = connection.execute(
            "SELECT * FROM concepts WHERE id = ? AND session_id = ? AND workspace_id = ?",
            (session["active_concept_id"], session_id, workspace_id),
        ).fetchone()
        map_row = connection.execute(
            "SELECT output_json FROM knowledge_maps WHERE session_id = ? AND workspace_id = ?",
            (session_id, workspace_id),
        ).fetchone()
        evidence_rows = connection.execute(
            """
            SELECT * FROM learning_evidence
            WHERE session_id = ? AND workspace_id = ? AND concept_id = ?
            ORDER BY timestamp, rowid
            """,
            (session_id, workspace_id, session["active_concept_id"]),
        ).fetchall()
        if not evidence_rows:
            raise SourceError(
                "learning_evidence_required",
                "No validated LearningEvidence exists for the current concept yet.",
                status_code=409,
                saved_state="The current concept remains active without an Agent recommendation.",
            )
        gaps = connection.execute(
            """
            SELECT * FROM source_gaps
            WHERE session_id = ? AND workspace_id = ?
            ORDER BY created_at, rowid
            """,
            (session_id, workspace_id),
        ).fetchall()
        concepts = connection.execute(
            "SELECT * FROM concepts WHERE session_id = ? AND workspace_id = ? ORDER BY order_index",
            (session_id, workspace_id),
        ).fetchall()
        activities = connection.execute(
            """
            SELECT type, status, hint_depth, created_at FROM activities
            WHERE session_id = ? AND workspace_id = ? AND concept_id = ?
            ORDER BY created_at, rowid
            """,
            (session_id, workspace_id, session["active_concept_id"]),
        ).fetchall()
        detour = connection.execute(
            """
            SELECT * FROM learning_detours
            WHERE session_id = ? AND workspace_id = ? AND status = 'active'
              AND detour_concept_id = ?
            ORDER BY created_at DESC, rowid DESC LIMIT 1
            """,
            (session_id, workspace_id, session["active_concept_id"]),
        ).fetchone()
        previous_decision = connection.execute(
            """
            SELECT action, selected_action, evidence_snapshot_json FROM agent_decisions
            WHERE session_id = ? AND workspace_id = ? AND concept_id = ?
              AND status IN ('accepted', 'overridden')
            ORDER BY created_at DESC, rowid DESC LIMIT 1
            """,
            (session_id, workspace_id, session["active_concept_id"]),
        ).fetchone()
    if not concept or not map_row:
        raise SourceError("agent_context_invalid", "The saved planning context is incomplete.", status_code=409)

    evidence = [_evidence_dict(dict(row)) for row in evidence_rows]
    _validate_named_source_gaps(
        database_path, workspace_id, session_id, evidence, [dict(row) for row in gaps]
    )
    with connect(database_path) as connection:
        refreshed_gaps = connection.execute(
            "SELECT * FROM source_gaps WHERE session_id = ? AND workspace_id = ? ORDER BY created_at, rowid",
            (session_id, workspace_id),
        ).fetchall()

    session_dict = dict(session)
    remaining_seconds = _remaining_seconds(session_dict)
    route = list(json.loads(str(map_row["output_json"]))["recommended_route"])
    return {
        "session": session_dict,
        "concept": dict(concept),
        "concepts": [dict(row) for row in concepts],
        "route": route,
        "evidence": evidence,
        "source_gaps": [dict(row) for row in refreshed_gaps],
        "activities": [dict(row) for row in activities],
        "detour": dict(detour) if detour else None,
        "previous_decision": dict(previous_decision) if previous_decision else None,
        "remaining_seconds": remaining_seconds,
    }


def _allowed_action_metadata(context: dict[str, Any]) -> dict[str, dict[str, Any]]:
    concept = context["concept"]
    concepts = context["concepts"]
    by_key = {item["concept_key"]: item for item in concepts}
    by_id = {item["id"]: item for item in concepts}
    route = [key for key in context["route"] if key in by_key]
    active_key = str(concept["concept_key"])
    active_index = route.index(active_key) if active_key in route else 0
    latest_scored = next(
        (
            item
            for item in reversed(context["evidence"])
            if item["activity_type"] in {"quiz", "recall", "remedial"}
        ),
        None,
    )
    coverage = latest_scored["key_point_coverage"] if latest_scored else []
    covered = sum(item.get("status") == "covered" for item in coverage)
    coverage_ratio = covered / max(1, len(coverage))
    blocking = list(latest_scored["misconception_tags"]) if latest_scored else []
    mastered = bool(
        latest_scored
        and latest_scored["outcome"] == "mastered"
        and coverage_ratio >= 0.7
        and not blocking
    )
    active_detour = context.get("detour")
    continue_target = None
    if mastered and active_detour:
        continue_target = by_id.get(active_detour["return_concept_id"])
    elif mastered and active_index + 1 < len(route):
        continue_target = by_key[route[active_index + 1]]

    metadata: dict[str, dict[str, Any]] = {}
    if continue_target:
        metadata["continue_next"] = {
            "reason_for_user": (
                f"Your latest check covered {covered}/{len(coverage)} key points with no blocking misconception. "
                f"Continue to {continue_target['title']}."
            ),
            "estimated_minutes": int(continue_target["estimated_minutes"]),
            "target_concept_id": continue_target["id"],
            "return_to_concept_id": None,
            "required_tool": TOOL_BY_ACTION["continue_next"],
        }

    if not mastered:
        latest_outcome = latest_scored["outcome"] if latest_scored else "unresolved"
        metadata["retry_current"] = {
            "reason_for_user": f"The latest observable outcome is {latest_outcome.replace('_', ' ')}. Retry one short check on {concept['title']}.",
            "estimated_minutes": 2,
            "target_concept_id": concept["id"],
            "return_to_concept_id": None,
            "required_tool": TOOL_BY_ACTION["retry_current"],
        }
        metadata["switch_activity"] = {
            "reason_for_user": "The current concept is not yet mastered; a different retrieval format can produce a fresh observation without changing the route.",
            "estimated_minutes": 3,
            "target_concept_id": concept["id"],
            "return_to_concept_id": None,
            "required_tool": TOOL_BY_ACTION["switch_activity"],
        }
        metadata["simplify_current"] = {
            "reason_for_user": "The current evidence still shows an unresolved or missing point. Ask Tutor for a smaller explanation inside this concept.",
            "estimated_minutes": 2,
            "target_concept_id": concept["id"],
            "return_to_concept_id": None,
            "required_tool": TOOL_BY_ACTION["simplify_current"],
        }

        prerequisite_keys = json.loads(str(concept["prerequisite_keys_json"]))
        prerequisite = next(
            (
                by_key[key]
                for key in prerequisite_keys
                if key in by_key and by_key[key]["status"] != "completed"
            ),
            None,
        )
        gap_signal = next(
            (item["source_gap_signal"] for item in reversed(context["evidence"]) if item["source_gap_signal"]),
            None,
        )
        if prerequisite and gap_signal:
            metadata["insert_prerequisite"] = {
                "reason_for_user": f"LearningEvidence records a named prerequisite gap, and the map links {prerequisite['title']} directly to this concept.",
                "estimated_minutes": min(5, int(prerequisite["estimated_minutes"])),
                "target_concept_id": prerequisite["id"],
                "return_to_concept_id": concept["id"],
                "required_tool": TOOL_BY_ACTION["insert_prerequisite"],
            }

        previous = by_key.get(route[active_index - 1]) if active_index > 0 else None
        if previous:
            metadata["review_previous"] = {
                "reason_for_user": f"The current evidence is not yet mastered. Review {previous['title']} briefly, then return here.",
                "estimated_minutes": min(4, int(previous["estimated_minutes"])),
                "target_concept_id": previous["id"],
                "return_to_concept_id": concept["id"],
                "required_tool": TOOL_BY_ACTION["review_previous"],
            }

    validated_gaps = [gap for gap in context["source_gaps"] if gap["status"] == "validated"]
    local_support_exhausted = (
        len(context["evidence"]) >= 2
        or any(item.get("remedial_result") == "not_improved" for item in context["evidence"])
        or any(int(item.get("hint_depth") or 0) >= 3 for item in context["evidence"])
    )
    if (
        not mastered
        and bool(context["session"].get("search_permission"))
        and validated_gaps
        and local_support_exhausted
    ):
        gap = validated_gaps[0]
        metadata["request_search"] = {
            "reason_for_user": f"A named material gap remains after local support: {gap['description']} Search is only a request; you must confirm before anything runs.",
            "estimated_minutes": 2,
            "target_concept_id": concept["id"],
            "return_to_concept_id": concept["id"],
            "required_tool": TOOL_BY_ACTION["request_search"],
            "source_gap_id": gap["id"],
        }

    finish_reason = (
        "The available session time is nearly complete. Finish with a saved restart point."
        if context["remaining_seconds"] <= 120
        else "You can finish now without penalty; the session will save a concrete restart point."
    )
    metadata["finish_session"] = {
        "reason_for_user": finish_reason,
        "estimated_minutes": 0,
        "target_concept_id": None,
        "return_to_concept_id": concept["id"],
        "required_tool": TOOL_BY_ACTION["finish_session"],
    }
    return metadata


def _demo_decision(
    context: dict[str, Any], allowed: dict[str, dict[str, Any]]
) -> AgentDecisionOutput:
    if context["remaining_seconds"] <= 120:
        action = "finish_session"
    elif "continue_next" in allowed:
        action = "continue_next"
    elif "request_search" in allowed:
        action = "request_search"
    elif "insert_prerequisite" in allowed:
        action = "insert_prerequisite"
    else:
        latest_scored = next(
            (
                item
                for item in reversed(context["evidence"])
                if item["activity_type"] in {"quiz", "recall", "remedial"}
            ),
            None,
        )
        action = "simplify_current" if latest_scored and latest_scored.get("remedial_result") == "not_improved" else "retry_current"
        previous = context.get("previous_decision")
        if previous:
            previous_action = str(previous["selected_action"] or previous["action"])
            previous_snapshot = json.loads(str(previous["evidence_snapshot_json"]))
            previous_outcome = previous_snapshot["evidence_summary"].get("latest_outcome")
            current_outcome = _evidence_summary(context)["latest_outcome"]
            if previous_action == action and previous_outcome == current_outcome:
                action = next(
                    candidate
                    for candidate in ("switch_activity", "simplify_current", "retry_current", "finish_session")
                    if candidate in allowed and candidate != previous_action
                )
    item = allowed[action]
    return AgentDecisionOutput(
        action=action,  # type: ignore[arg-type]
        reason_for_user=item["reason_for_user"],
        estimated_minutes=item["estimated_minutes"],
        target_concept_id=item["target_concept_id"],
        return_to_concept_id=item["return_to_concept_id"],
        required_tool=item["required_tool"],
        confidence=0.92,
    )


def _real_decision(
    settings: Settings,
    workspace_id: str,
    context: dict[str, Any],
    allowed: dict[str, dict[str, Any]],
    *,
    client_factory: Callable[[Settings], Any] | None,
) -> tuple[AgentDecisionOutput, str | None]:
    if not settings.openai_api_key:
        raise ModelGatewayError(
            "openai_key_missing",
            "Real model mode needs a server-side OpenAI API key. Your evidence is saved; configure the key and retry.",
        )
    if client_factory is None:
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover
            raise ModelGatewayError(
                "openai_sdk_missing",
                "The OpenAI server dependency is not installed. Your evidence remains saved.",
            ) from exc
        client = OpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.openai_timeout_seconds,
            max_retries=1,
        )
    else:
        client = client_factory(settings)

    schema = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": list(allowed)},
            "reason_for_user": {"type": "string", "maxLength": 500},
            "estimated_minutes": {"type": "integer", "minimum": 0, "maximum": 45},
            "target_concept_id": {"type": ["string", "null"]},
            "return_to_concept_id": {"type": ["string", "null"]},
            "required_tool": {
                "type": "string",
                "enum": [
                    "activate_concept", "create_activity", "open_tutor",
                    "request_search", "create_summary",
                ],
            },
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        },
        "required": [
            "action", "reason_for_user", "estimated_minutes", "target_concept_id",
            "return_to_concept_id", "required_tool", "confidence",
        ],
        "additionalProperties": False,
    }
    prompt_context = {
        "learning_evidence_only": _evidence_summary(context),
        "feasibility_constraints_only": _feasibility_context(context),
        "allowed_actions": allowed,
    }
    safety_identifier = hashlib.sha256(workspace_id.encode("utf-8")).hexdigest()
    try:
        response = client.responses.create(
            model=settings.openai_model,
            reasoning={"effort": "low"},
            store=False,
            safety_identifier=safety_identifier,
            instructions=(
                "Select exactly one allowed learning action. LearningEvidence is the sole basis for any learning-performance claim. "
                "Time, route, prerequisites, source coverage, permission, retries, and user override history are feasibility constraints only. "
                "Copy the target IDs and required_tool from the chosen allowed action exactly. Give one short learner-facing reason. "
                "Do not teach, reveal hidden reasoning, invent evidence, execute a search, or propose any unlisted action."
            ),
            input=json.dumps(prompt_context),
            tools=[{
                "type": "function",
                "name": "select_next_learning_action",
                "description": "Select one server-validated next learning action from the supplied allowed actions.",
                "parameters": schema,
                "strict": True,
            }],
            tool_choice={"type": "function", "name": "select_next_learning_action"},
            parallel_tool_calls=False,
        )
    except Exception as exc:
        raise ModelGatewayError(
            "openai_request_failed",
            "The Agent model request could not be completed. Your evidence is saved; retry when the connection is available.",
        ) from exc
    calls = [item for item in getattr(response, "output", []) if getattr(item, "type", None) == "function_call"]
    if getattr(response, "status", "completed") != "completed" or len(calls) != 1 or getattr(calls[0], "name", None) != "select_next_learning_action":
        raise ModelGatewayError(
            "agent_output_invalid",
            "The Agent did not return one usable bounded action. Your evidence is saved; retry the decision.",
        )
    try:
        output = AgentDecisionOutput.model_validate_json(str(calls[0].arguments))
    except Exception as exc:
        raise ModelGatewayError(
            "agent_output_invalid",
            "The Agent action did not match the required structure. Your evidence is saved; retry the decision.",
        ) from exc
    return output, getattr(response, "id", None)


def _validate_decision_output(
    output: AgentDecisionOutput, allowed: dict[str, dict[str, Any]]
) -> None:
    if output.action not in allowed:
        raise SourceError(
            "agent_action_invalid",
            "The Agent proposed an action that is not valid for the current evidence.",
            status_code=422,
            saved_state="Your LearningEvidence remains saved without applying the action.",
        )
    server = allowed[output.action]
    for field in (
        "estimated_minutes", "target_concept_id", "return_to_concept_id", "required_tool"
    ):
        if getattr(output, field) != server[field]:
            raise SourceError(
                "agent_action_invalid",
                "The Agent action did not match the server-validated transition.",
                status_code=422,
                saved_state="Your LearningEvidence remains saved without applying the action.",
            )


def _persist_decision(
    database_path: Path,
    workspace_id: str,
    session_id: str,
    context: dict[str, Any],
    allowed: dict[str, dict[str, Any]],
    fingerprint: str,
    output: AgentDecisionOutput,
    generation_mode: str,
    model: str,
) -> str:
    decision_id = str(uuid.uuid4())
    snapshot = {
        "evidence_ids": [item["id"] for item in context["evidence"]],
        "evidence_summary": _evidence_summary(context),
        "feasibility_context": _feasibility_context(context),
        "action_metadata": allowed,
    }
    with connect(database_path) as connection:
        session = connection.execute(
            "SELECT * FROM learning_sessions WHERE id = ? AND workspace_id = ?",
            (session_id, workspace_id),
        ).fetchone()
        if not session or session["state"] != "evidence_ready" or session["is_paused"]:
            raise SourceError(
                "agent_context_changed",
                "The saved evidence boundary changed before the decision was stored. Reload and try again.",
                status_code=409,
            )
        connection.execute(
            """
            INSERT INTO agent_decisions(
                id, workspace_id, session_id, concept_id, evidence_fingerprint,
                evidence_snapshot_json, action, reason_for_user, estimated_minutes,
                target_concept_id, return_to_concept_id, required_tool, confidence,
                generation_mode, model
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                decision_id, workspace_id, session_id, context["concept"]["id"],
                fingerprint, json.dumps(snapshot), output.action, output.reason_for_user,
                output.estimated_minutes, output.target_concept_id,
                output.return_to_concept_id, output.required_tool, output.confidence,
                generation_mode, model,
            ),
        )
        connection.execute(
            """
            UPDATE learning_sessions
            SET state = 'agent_decision', active_activity_id = NULL,
                version = version + 1, last_saved_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND workspace_id = ?
            """,
            (session_id, workspace_id),
        )
        _record_event(connection, workspace_id, session_id, "agent_decision_created", {
            "decision_id": decision_id,
            "action": output.action,
            "evidence_ids": snapshot["evidence_ids"],
            "internet_search_performed": False,
        })
    return decision_id


def _apply_controlled_transition(
    connection,
    workspace_id: str,
    session: dict[str, Any],
    decision_id: str,
    action: str,
    metadata: dict[str, Any],
) -> None:
    session_id = str(session["id"])
    current_id = str(session["active_concept_id"])
    target_id = metadata.get("target_concept_id")
    return_id = metadata.get("return_to_concept_id")
    next_state = "learning_concept"

    if action == "continue_next":
        connection.execute("UPDATE concepts SET status = 'completed' WHERE id = ?", (current_id,))
        connection.execute("UPDATE concepts SET status = 'active' WHERE id = ?", (target_id,))
        detour = connection.execute(
            """
            SELECT id, return_concept_id FROM learning_detours
            WHERE session_id = ? AND workspace_id = ? AND status = 'active'
              AND detour_concept_id = ?
            ORDER BY created_at DESC, rowid DESC LIMIT 1
            """,
            (session_id, workspace_id, current_id),
        ).fetchone()
        if detour and str(detour["return_concept_id"]) == str(target_id):
            connection.execute(
                "UPDATE learning_detours SET status = 'returned', returned_at = CURRENT_TIMESTAMP WHERE id = ?",
                (detour["id"],),
            )
        _reset_focus_note(connection, workspace_id, session_id)
    elif action in {"insert_prerequisite", "review_previous"}:
        connection.execute("UPDATE concepts SET status = 'planned' WHERE id = ?", (current_id,))
        connection.execute("UPDATE concepts SET status = 'active' WHERE id = ?", (target_id,))
        connection.execute(
            """
            INSERT INTO learning_detours(
                id, workspace_id, session_id, decision_id, kind,
                detour_concept_id, return_concept_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()), workspace_id, session_id, decision_id,
                "prerequisite" if action == "insert_prerequisite" else "review",
                target_id, return_id,
            ),
        )
        _reset_focus_note(connection, workspace_id, session_id)
    elif action == "request_search":
        next_state = "search_confirmation"
    elif action == "finish_session":
        next_state = "session_summary"

    connection.execute(
        """
        UPDATE learning_sessions
        SET state = ?, active_concept_id = ?, active_activity_id = NULL,
            tutor_open = 0, timer_started_at = CASE WHEN ? = 'session_summary' THEN NULL ELSE timer_started_at END,
            ended_at = CASE WHEN ? = 'session_summary' THEN CURRENT_TIMESTAMP ELSE ended_at END,
            version = version + 1, last_saved_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND workspace_id = ?
        """,
        (
            next_state,
            target_id if action in {"continue_next", "insert_prerequisite", "review_previous"} else current_id,
            next_state,
            next_state,
            session_id,
            workspace_id,
        ),
    )


def _execution_payload(
    database_path: Path,
    workspace_id: str,
    session_id: str,
    action: str,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    session = get_session(database_path, workspace_id, session_id)
    payload: dict[str, Any] = {
        "action": action,
        "destination": {
            "request_search": "search_confirmation",
            "finish_session": "session_summary",
            "simplify_current": "tutor",
            "retry_current": "activity",
            "switch_activity": "activity",
        }.get(action, "focus"),
        "session": _public_session(session),
    }
    if action in {"retry_current", "switch_activity"}:
        with connect(database_path) as connection:
            latest = connection.execute(
                """
                SELECT type FROM activities
                WHERE session_id = ? AND workspace_id = ? AND type IN ('quiz', 'recall')
                ORDER BY created_at DESC, rowid DESC LIMIT 1
                """,
                (session_id, workspace_id),
            ).fetchone()
        previous_type = str(latest["type"]) if latest else "recall"
        payload["activity_type"] = (
            previous_type if action == "retry_current" else ("quiz" if previous_type == "recall" else "recall")
        )
    if action == "request_search":
        payload["source_gap_id"] = metadata.get("source_gap_id")
        payload["confirmation_required"] = True
        payload["internet_search_performed"] = False
    if action == "finish_session":
        with connect(database_path) as connection:
            concept = connection.execute(
                "SELECT title FROM concepts WHERE id = ? AND workspace_id = ?",
                (session["active_concept_id"], workspace_id),
            ).fetchone()
        payload["summary"] = {
            "title": "Session complete",
            "restart_action": f"Start a new session by reviewing {concept['title'] if concept else 'the saved concept'} and its latest LearningEvidence.",
            "penalty_for_stopping": False,
        }
    return payload


def _evidence_summary(context: dict[str, Any]) -> dict[str, Any]:
    evidence = context["evidence"]
    latest_scored = next(
        (item for item in reversed(evidence) if item["activity_type"] in {"quiz", "recall", "remedial"}),
        None,
    )
    latest = latest_scored or evidence[-1]
    coverage = latest["key_point_coverage"]
    return {
        "concept_id": context["concept"]["id"],
        "concept_title": context["concept"]["title"],
        "evidence_count": len(evidence),
        "latest_activity_type": latest["activity_type"],
        "latest_outcome": latest["outcome"],
        "covered_key_points": sum(item.get("status") == "covered" for item in coverage),
        "total_key_points": len(coverage),
        "misconception_tags": latest["misconception_tags"],
        "hint_depth": latest["hint_depth"],
        "remedial_result": latest["remedial_result"],
        "tutor_confusion_signals": list(dict.fromkeys(
            signal for item in evidence for signal in item["tutor_confusion_signals"]
        )),
        "source_gap_signals": list(dict.fromkeys(
            item["source_gap_signal"] for item in evidence if item["source_gap_signal"]
        )),
    }


def _feasibility_context(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "remaining_minutes": max(0, context["remaining_seconds"] // 60),
        "route": context["route"],
        "active_concept_key": context["concept"]["concept_key"],
        "prerequisite_keys": json.loads(str(context["concept"]["prerequisite_keys_json"])),
        "search_permission": bool(context["session"].get("search_permission")),
        "validated_source_gap_ids": [
            gap["id"] for gap in context["source_gaps"] if gap["status"] == "validated"
        ],
        "attempt_count": len(context["activities"]),
        "active_detour": bool(context.get("detour")),
    }


def _validate_named_source_gaps(
    database_path: Path,
    workspace_id: str,
    session_id: str,
    evidence: list[dict[str, Any]],
    gaps: list[dict[str, Any]],
) -> None:
    signals = [item["source_gap_signal"] for item in evidence if item["source_gap_signal"]]
    if not signals:
        return
    with connect(database_path) as connection:
        for gap in gaps:
            if gap["status"] != "candidate":
                continue
            gap_terms = _meaningful_terms(
                f"{gap['description']} {gap['why_needed']} {gap['suggested_query_scope']}"
            )
            if any(len(gap_terms & _meaningful_terms(signal)) >= 2 for signal in signals):
                connection.execute(
                    "UPDATE source_gaps SET status = 'validated' WHERE id = ? AND workspace_id = ? AND session_id = ?",
                    (gap["id"], workspace_id, session_id),
                )


def _meaningful_terms(value: str) -> set[str]:
    stop = {
        "the", "a", "an", "and", "or", "to", "of", "for", "in", "is", "does",
        "not", "this", "that", "material", "uploaded", "named", "define",
    }
    return {
        token
        for token in re.findall(r"[a-z0-9]+", value.lower())
        if len(token) > 2 and token not in stop
    }


def _evidence_dict(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "activity_type": row["activity_type"],
        "outcome": row["outcome"],
        "key_point_coverage": json.loads(str(row["key_point_coverage_json"])),
        "misconception_tags": json.loads(str(row["misconception_tags_json"])),
        "hint_depth": int(row["hint_depth"]),
        "elapsed_seconds": int(row["elapsed_seconds"]),
        "tutor_confusion_signals": json.loads(str(row["tutor_confusion_signals_json"])),
        "remedial_result": row["remedial_result"],
        "source_gap_signal": row["source_gap_signal"],
        "timestamp": row["timestamp"],
    }


def _evidence_fingerprint(context: dict[str, Any]) -> str:
    raw = json.dumps({
        "concept_id": context["concept"]["id"],
        "evidence_ids": [item["id"] for item in context["evidence"]],
        "search_permission": bool(context["session"].get("search_permission")),
        "route": context["route"],
        "active_detour_id": context["detour"]["id"] if context.get("detour") else None,
    }, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _decision_by_fingerprint(
    database_path: Path,
    workspace_id: str,
    session_id: str,
    fingerprint: str,
):
    with connect(database_path) as connection:
        return connection.execute(
            """
            SELECT * FROM agent_decisions
            WHERE workspace_id = ? AND session_id = ? AND evidence_fingerprint = ?
            """,
            (workspace_id, session_id, fingerprint),
        ).fetchone()


def _remaining_seconds(session: dict[str, Any]) -> int:
    remaining = int(session.get("remaining_seconds") or int(session.get("available_minutes") or 0) * 60)
    started = session.get("timer_started_at")
    if started and not session.get("is_paused"):
        parsed = datetime.fromisoformat(str(started).replace(" ", "T")).replace(tzinfo=UTC)
        remaining = max(0, remaining - max(0, int((datetime.now(UTC) - parsed).total_seconds())))
    return remaining


def _public_action(action: str, item: dict[str, Any]) -> dict[str, Any]:
    return {
        "action": action,
        "label": ACTION_LABELS[action],
        "reason_for_user": item["reason_for_user"],
        "estimated_minutes": item["estimated_minutes"],
        "target_concept_id": item["target_concept_id"],
        "return_to_concept_id": item["return_to_concept_id"],
        "required_tool": item["required_tool"],
    }


def _public_session(session: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": session["id"],
        "state": session["state"],
        "version": session["version"],
        "is_paused": bool(session.get("is_paused")),
        "resume_state": session.get("resume_state"),
        "active_concept_id": session.get("active_concept_id"),
        "active_activity_id": session.get("active_activity_id"),
    }


def _reset_focus_note(connection, workspace_id: str, session_id: str) -> None:
    connection.execute(
        """
        UPDATE drafts SET content = '', activity_id = NULL,
            server_version = server_version + 1, updated_at = CURRENT_TIMESTAMP
        WHERE workspace_id = ? AND session_id = ? AND draft_type = 'focus_note'
        """,
        (workspace_id, session_id),
    )


def _start_ai_activity(settings: Settings, workspace_id: str, session_id: str) -> str:
    log_id = str(uuid.uuid4())
    with connect(settings.database_path) as connection:
        connection.execute(
            """
            INSERT INTO ai_activity_logs(
                id, workspace_id, session_id, operation, generation_mode, model, status
            ) VALUES (?, ?, ?, 'select_agent_action', ?, ?, 'started')
            """,
            (
                log_id, workspace_id, session_id, settings.mode,
                DEMO_AGENT_MODEL if settings.mode == "demo" else settings.openai_model,
            ),
        )
    return log_id


def _finish_ai_activity(
    database_path: Path,
    log_id: str,
    status: str,
    *,
    response_id: str | None = None,
    error_code: str | None = None,
) -> None:
    with connect(database_path) as connection:
        connection.execute(
            """
            UPDATE ai_activity_logs SET status = ?, response_id = ?, error_code = ?,
                completed_at = CURRENT_TIMESTAMP WHERE id = ?
            """,
            (status, response_id, error_code, log_id),
        )


def _record_event(
    connection,
    workspace_id: str,
    session_id: str,
    event_type: str,
    detail: dict[str, Any],
) -> None:
    connection.execute(
        """
        INSERT INTO session_events(id, workspace_id, session_id, event_type, detail_json)
        VALUES (?, ?, ?, ?, ?)
        """,
        (str(uuid.uuid4()), workspace_id, session_id, event_type, json.dumps(detail)),
    )
