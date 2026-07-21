"""Structured feedback, local remediation, and recommendation-free learning evidence."""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any, Callable
import uuid

from app.ai import (
    FeedbackOutput,
    ModelGatewayError,
    RemedialActivityOutput,
    SourceReference,
    parse_structured_response,
)
from app.config import Settings
from app.db import connect
from app.sources import SourceError, get_session


DEMO_FEEDBACK_MODEL = "deterministic-demo-feedback-v1"
DEMO_REMEDIAL_MODEL = "deterministic-demo-remedial-v1"
REMEDIAL_STRATEGIES = [
    "smaller_question",
    "concrete_example",
    "contrast_question",
    "rephrase_task",
    "simpler_explanation",
]


def generate_feedback(
    settings: Settings,
    workspace_id: str,
    attempt_id: str,
    *,
    client_factory: Callable[[Settings], Any] | None = None,
) -> dict[str, Any]:
    """Generate feedback and atomically record factual evidence for one submitted attempt."""

    existing = _feedback_by_attempt(settings.database_path, workspace_id, attempt_id)
    if existing:
        return get_feedback(settings.database_path, workspace_id, str(existing["id"]))
    context = _feedback_context(settings.database_path, workspace_id, attempt_id)
    session = context["session"]
    expected_state = "remedial_practice" if context["activity"]["type"] == "remedial" else "practicing"
    if session.get("is_paused"):
        raise SourceError(
            "session_paused",
            "Resume the session before preparing feedback.",
            status_code=409,
            saved_state="Your submitted answer and hint depth remain saved.",
        )
    if session["state"] != expected_state or session.get("active_activity_id") != context["activity"]["id"]:
        raise SourceError("feedback_not_available", "This submitted activity is no longer the active mastery step.", status_code=409)

    log_id = _start_ai_activity(settings, workspace_id, str(session["id"]), "generate_feedback")
    try:
        if settings.mode == "demo":
            output, coverage, misconception_tags = _demo_feedback(context)
            model = DEMO_FEEDBACK_MODEL
            response_id = None
        else:
            result = parse_structured_response(
                settings,
                workspace_id,
                FeedbackOutput,
                _feedback_instructions(context),
                _feedback_source_context(context),
                client_factory=client_factory,
            )
            output = result.output
            coverage, misconception_tags = _coverage_from_model_feedback(context, output)
            model = settings.openai_model
            response_id = result.response_id
        _validate_source_refs(settings.database_path, workspace_id, str(session["id"]), output.source_origin, output.source_refs)
        feedback_id = _persist_feedback_and_evidence(
            settings.database_path,
            workspace_id,
            context,
            output,
            coverage,
            misconception_tags,
            settings.mode,
            model,
        )
        _finish_ai_activity(settings.database_path, log_id, "success", response_id=response_id)
    except ModelGatewayError as exc:
        _finish_ai_activity(settings.database_path, log_id, "error", error_code=exc.error_code)
        raise SourceError(
            exc.error_code,
            exc.user_message,
            status_code=503,
            saved_state="Your submitted answer is saved. Feedback can be retried safely.",
        ) from exc
    except SourceError as exc:
        _finish_ai_activity(settings.database_path, log_id, "error", error_code=exc.error_code)
        raise
    return get_feedback(settings.database_path, workspace_id, feedback_id)


def get_feedback(database_path: Path, workspace_id: str, feedback_id: str) -> dict[str, Any]:
    with connect(database_path) as connection:
        row = connection.execute(
            """
            SELECT f.*, a.type AS activity_type, a.strategy, a.remedial_round,
                   c.title AS concept_title, s.name AS session_name, s.state AS session_state,
                   s.version AS session_version, s.is_paused, s.resume_state,
                   s.active_activity_id, s.last_saved_at
            FROM feedbacks f
            JOIN activities a ON a.id = f.activity_id
            JOIN concepts c ON c.id = f.concept_id
            JOIN learning_sessions s ON s.id = f.session_id
            WHERE f.id = ? AND f.workspace_id = ? AND s.workspace_id = ?
            """,
            (feedback_id, workspace_id, workspace_id),
        ).fetchone()
        if not row:
            raise SourceError("feedback_not_found", "This feedback is not available in the current workspace.", status_code=404)
        evidence = connection.execute(
            "SELECT * FROM learning_evidence WHERE attempt_id = ? AND workspace_id = ?",
            (row["attempt_id"], workspace_id),
        ).fetchone()
        prior_strategies = connection.execute(
            """
            SELECT strategy FROM activities
            WHERE workspace_id = ? AND session_id = ? AND type = 'remedial'
              AND parent_activity_id = COALESCE((SELECT parent_activity_id FROM activities WHERE id = ?), ?)
            ORDER BY remedial_round
            """,
            (workspace_id, row["session_id"], row["activity_id"], row["activity_id"]),
        ).fetchall()
    output = json.loads(str(row["output_json"]))
    refs = json.loads(str(row["source_refs_json"]))
    from app.activities import _source_details

    ref_details = _source_details(database_path, workspace_id, str(row["session_id"]), refs)
    public_evidence = _public_evidence(dict(evidence)) if evidence else None
    outcome = str(evidence["outcome"] if evidence else "unresolved")
    return {
        "feedback": {
            "id": row["id"],
            "attempt_id": row["attempt_id"],
            "activity_id": row["activity_id"],
            "concept_id": row["concept_id"],
            "concept_title": row["concept_title"],
            "activity_type": row["activity_type"],
            "strategy": row["strategy"],
            "remedial_round": row["remedial_round"],
            "status": row["status"],
            "version": row["version"],
            **output,
            "source_refs": refs,
            "source_ref_details": ref_details,
            "created_at": row["created_at"],
        },
        "evidence": public_evidence,
        "session": {
            "id": row["session_id"],
            "name": row["session_name"],
            "state": row["session_state"],
            "version": row["session_version"],
            "is_paused": bool(row["is_paused"]),
            "resume_state": row["resume_state"],
            "active_activity_id": row["active_activity_id"],
            "last_saved_at": row["last_saved_at"],
        },
        "remediation": {
            "available": row["status"] == "shown" and outcome != "mastered",
            "recommended_strategy": _next_strategy([str(item["strategy"]) for item in prior_strategies]),
            "prior_strategy_count": len(prior_strategies),
        },
        "generation": {
            "mode": row["generation_mode"],
            "model": row["model"],
            "internet_search_performed": False,
        },
        "boundaries": {
            "feedback_is_guided_mastery": True,
            "learning_evidence_is_factual_only": True,
            "agent_decision_created": False,
            "can_search": False,
        },
    }


def get_feedback_for_attempt(database_path: Path, workspace_id: str, attempt_id: str) -> dict[str, Any]:
    row = _feedback_by_attempt(database_path, workspace_id, attempt_id)
    if not row:
        raise SourceError("feedback_not_ready", "Feedback has not been prepared for this answer yet.", status_code=404)
    return get_feedback(database_path, workspace_id, str(row["id"]))


def complete_feedback(
    database_path: Path,
    workspace_id: str,
    feedback_id: str,
    expected_session_version: int,
) -> dict[str, Any]:
    with connect(database_path) as connection:
        row = connection.execute(
            """
            SELECT f.*, s.state AS session_state, s.version AS session_version,
                   s.is_paused, s.active_activity_id
            FROM feedbacks f JOIN learning_sessions s ON s.id = f.session_id
            WHERE f.id = ? AND f.workspace_id = ? AND s.workspace_id = ?
            """,
            (feedback_id, workspace_id, workspace_id),
        ).fetchone()
        if not row:
            raise SourceError("feedback_not_found", "This feedback is not available in the current workspace.", status_code=404)
        if row["is_paused"]:
            raise SourceError("session_paused", "Resume the session before completing this feedback step.", status_code=409)
        _require_version(int(row["session_version"]), expected_session_version)
        if row["status"] == "completed" and row["session_state"] == "evidence_ready":
            return get_evidence(database_path, workspace_id, str(row["session_id"]))
        if row["session_state"] != "feedback_shown" or row["active_activity_id"] != row["activity_id"]:
            raise SourceError("feedback_not_active", "This feedback is no longer the active mastery step.", status_code=409)
        connection.execute(
            "UPDATE feedbacks SET status = 'completed', version = version + 1, completed_at = CURRENT_TIMESTAMP WHERE id = ?",
            (feedback_id,),
        )
        connection.execute(
            """
            UPDATE learning_sessions
            SET state = 'evidence_ready', active_activity_id = NULL, version = version + 1,
                last_saved_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND workspace_id = ?
            """,
            (row["session_id"], workspace_id),
        )
        _record_event(connection, workspace_id, str(row["session_id"]), "evidence_ready", {
            "feedback_id": feedback_id,
            "learning_evidence_id": _evidence_id_for_attempt(connection, str(row["attempt_id"])),
            "agent_decision_created": False,
        })
    return get_evidence(database_path, workspace_id, str(row["session_id"]))


def create_remedial_activity(
    settings: Settings,
    workspace_id: str,
    feedback_id: str,
    expected_session_version: int,
    *,
    client_factory: Callable[[Settings], Any] | None = None,
) -> dict[str, Any]:
    feedback_body = get_feedback(settings.database_path, workspace_id, feedback_id)
    feedback = feedback_body["feedback"]
    session = get_session(settings.database_path, workspace_id, str(feedback_body["session"]["id"]))
    if session.get("is_paused"):
        raise SourceError("session_paused", "Resume the session before starting remedial practice.", status_code=409)
    _require_version(int(session["version"]), expected_session_version)
    if session["state"] != "feedback_shown" or session.get("active_activity_id") != feedback["activity_id"]:
        raise SourceError("remedial_not_available", "Remedial practice is available only from the active feedback step.", status_code=409)
    if not feedback_body["remediation"]["available"]:
        raise SourceError("remedial_not_needed", "This evidence is ready for planning without a remedial step.", status_code=409)
    context = _remedial_context(settings.database_path, workspace_id, feedback_id)
    strategy = str(feedback_body["remediation"]["recommended_strategy"])
    log_id = _start_ai_activity(settings, workspace_id, str(session["id"]), "generate_remedial_activity")
    try:
        if settings.mode == "demo":
            output = _demo_remedial(context, strategy)
            model = DEMO_REMEDIAL_MODEL
            response_id = None
        else:
            result = parse_structured_response(
                settings,
                workspace_id,
                RemedialActivityOutput,
                _remedial_instructions(context, strategy),
                _remedial_source_context(context),
                client_factory=client_factory,
            )
            output = result.output
            model = settings.openai_model
            response_id = result.response_id
        if output.strategy != strategy or len(set(output.hint_levels)) != 3:
            raise SourceError("remedial_output_invalid", "The remedial activity structure was not usable. Retry generation.", status_code=422)
        _validate_source_refs(settings.database_path, workspace_id, str(session["id"]), output.source_origin, output.source_refs)
        activity_id = _persist_remedial_activity(
            settings.database_path,
            workspace_id,
            context,
            output,
            expected_session_version,
            settings.mode,
            model,
        )
        _finish_ai_activity(settings.database_path, log_id, "success", response_id=response_id)
    except ModelGatewayError as exc:
        _finish_ai_activity(settings.database_path, log_id, "error", error_code=exc.error_code)
        raise SourceError(
            exc.error_code,
            exc.user_message,
            status_code=503,
            saved_state="Your feedback and evidence remain saved. Remedial practice can be retried.",
        ) from exc
    except SourceError as exc:
        _finish_ai_activity(settings.database_path, log_id, "error", error_code=exc.error_code)
        raise
    from app.activities import get_activity

    return get_activity(settings.database_path, workspace_id, activity_id)


def get_evidence(database_path: Path, workspace_id: str, session_id: str) -> dict[str, Any]:
    session = get_session(database_path, workspace_id, session_id)
    with connect(database_path) as connection:
        rows = connection.execute(
            """
            SELECT * FROM learning_evidence
            WHERE workspace_id = ? AND session_id = ?
            ORDER BY timestamp, rowid
            """,
            (workspace_id, session_id),
        ).fetchall()
    return {
        "session": {
            "id": session["id"],
            "state": session["state"],
            "version": session["version"],
            "is_paused": bool(session.get("is_paused")),
            "resume_state": session.get("resume_state"),
            "active_concept_id": session.get("active_concept_id"),
            "active_activity_id": session.get("active_activity_id"),
        },
        "learning_evidence": [_public_evidence(dict(row)) for row in rows],
        "boundaries": {
            "contains_observations_only": True,
            "contains_recommendations": False,
            "agent_decision_created": False,
            "internet_search_performed": False,
        },
    }


def _feedback_context(database_path: Path, workspace_id: str, attempt_id: str) -> dict[str, Any]:
    with connect(database_path) as connection:
        row = connection.execute(
            """
            SELECT at.*, a.type AS activity_type, a.output_json, a.source_origin,
                   a.source_refs_json, a.status AS activity_status, a.concept_id,
                   a.parent_activity_id, a.strategy, a.remedial_round,
                   c.title AS concept_title, c.plain_definition, c.role_in_map,
                   s.id AS owned_session_id, s.state AS session_state, s.version AS session_version,
                   s.is_paused, s.active_activity_id
            FROM attempts at
            JOIN activities a ON a.id = at.activity_id
            JOIN concepts c ON c.id = a.concept_id
            JOIN learning_sessions s ON s.id = a.session_id
            WHERE at.id = ? AND at.workspace_id = ? AND s.workspace_id = ?
            """,
            (attempt_id, workspace_id, workspace_id),
        ).fetchone()
        if not row:
            raise SourceError("attempt_not_found", "This submitted answer is not available in the current workspace.", status_code=404)
        if row["activity_status"] != "submitted":
            raise SourceError("attempt_not_submitted", "Submit the answer before preparing feedback.", status_code=409)
        source_rows = []
        for ref in json.loads(str(row["source_refs_json"])):
            chunk = connection.execute(
                """
                SELECT c.id, c.source_id, c.text, d.filename, d.source_origin
                FROM source_chunks c JOIN source_documents d ON d.id = c.source_id
                WHERE c.id = ? AND d.id = ? AND d.workspace_id = ? AND d.session_id = ?
                """,
                (ref["chunk_id"], ref["source_id"], workspace_id, row["session_id"]),
            ).fetchone()
            if chunk:
                source_rows.append(dict(chunk))
        tutor_rows = connection.execute(
            """
            SELECT confusion_signal, prerequisite_gap_signal
            FROM tutor_messages
            WHERE workspace_id = ? AND session_id = ? AND concept_id = ? AND role = 'tutor'
              AND (confusion_signal IS NOT NULL OR prerequisite_gap_signal IS NOT NULL)
            ORDER BY rowid DESC LIMIT 8
            """,
            (workspace_id, row["session_id"], row["concept_id"]),
        ).fetchall()
    item = dict(row)
    session = {
        "id": item["owned_session_id"],
        "state": item["session_state"],
        "version": item["session_version"],
        "is_paused": bool(item["is_paused"]),
        "active_activity_id": item["active_activity_id"],
    }
    activity = {
        "id": item["activity_id"],
        "type": item["activity_type"],
        "output": json.loads(str(item["output_json"])),
        "source_origin": item["source_origin"],
        "source_refs": json.loads(str(item["source_refs_json"])),
        "concept_id": item["concept_id"],
        "parent_activity_id": item["parent_activity_id"],
        "strategy": item["strategy"],
        "remedial_round": item["remedial_round"],
    }
    return {
        "attempt": item,
        "activity": activity,
        "session": session,
        "concept": {
            "id": item["concept_id"],
            "title": item["concept_title"],
            "plain_definition": item["plain_definition"],
            "role_in_map": item["role_in_map"],
        },
        "source_chunks": source_rows,
        "tutor_signals": [dict(signal) for signal in tutor_rows],
    }


def _demo_feedback(context: dict[str, Any]) -> tuple[FeedbackOutput, list[dict[str, str]], list[str]]:
    activity = context["activity"]
    attempt = context["attempt"]
    output = activity["output"]
    refs = [SourceReference.model_validate(ref) for ref in activity["source_refs"]]
    if activity["type"] == "quiz":
        selected = str(attempt["selected_option_id"])
        correct = selected == str(output["correct_option_id"])
        selected_option = next(item for item in output["options"] if str(item["id"]) == selected)
        explanation = next(
            item["explanation"] for item in output["explanation_by_option"] if str(item["option_id"]) == selected
        )
        key_point = str(context["concept"]["plain_definition"])
        coverage = [{"key_point": key_point, "status": "covered" if correct else "missing"}]
        tags = [] if correct else [str(selected_option["misconception_tag"])]
        return FeedbackOutput(
            mastered_points=[key_point] if correct else [],
            missing_or_unclear_points=[] if correct else [key_point],
            misconceptions=[] if correct else [f"The selected answer reflects: {selected_option['misconception_tag'].replace('_', ' ')}."],
            compact_correction=explanation,
            next_micro_action=(
                f"Restate the core action of {context['concept']['title']} once without looking at the source."
                if correct
                else f"Answer one smaller question about the missing step in {context['concept']['title']}."
            ),
            encouragement=(
                "You matched the source's central action and completed the check without unnecessary hints."
                if correct and int(attempt["hint_depth"]) == 0
                else "You made a checkable choice; that gives the next short practice a precise target."
            ),
            source_origin=activity["source_origin"],
            source_refs=refs,
        ), coverage, tags

    answer = str(attempt["raw_answer"] or "")
    expected = list(output["expected_key_points"])
    statuses = _recall_coverage(
        answer,
        expected,
        str(context["concept"]["title"]),
        str(activity["type"]),
    )
    coverage = [
        {"key_point": point, "status": "covered" if covered else "missing"}
        for point, covered in zip(expected, statuses, strict=True)
    ]
    mastered = [item["key_point"] for item in coverage if item["status"] == "covered"]
    missing = [item["key_point"] for item in coverage if item["status"] == "missing"]
    answer_lower = answer.lower()
    misconceptions = [pattern for pattern in output.get("misconception_patterns", []) if _misconception_matches(answer_lower, pattern)]
    tags = [_tag_for_text(item) for item in misconceptions]
    return FeedbackOutput(
        mastered_points=mastered,
        missing_or_unclear_points=missing,
        misconceptions=misconceptions,
        compact_correction=" ".join(expected),
        next_micro_action=(
            f"Restate the two-step sequence of {context['concept']['title']} once in one sentence."
            if not missing
            else f"Answer one smaller question about this missing point: {missing[0]}"
        ),
        encouragement=(
            f"You clearly included {len(mastered)} of {len(expected)} source-grounded key points."
            if mastered
            else "You completed a checkable attempt, which makes the unclear point specific enough to practice."
        ),
        source_origin=activity["source_origin"],
        source_refs=refs,
    ), coverage, tags


def _recall_coverage(
    answer: str,
    expected: list[str],
    concept_title: str,
    activity_type: str,
) -> list[bool]:
    lowered = answer.lower()
    if concept_title.lower() == "self-attention" and activity_type == "recall":
        groups = [
            (("compare", "position"), ("relation", "position"), ("which", "matter")),
            (("relevance", "score"), ("relevance", "weight"), ("attention", "weight")),
            (("combin", "value"), ("weighted", "value"), ("context", "representation")),
        ]
        return [any(all(token in lowered for token in variant) for variant in group) for group in groups[: len(expected)]]
    answer_tokens = set(re.findall(r"[a-z0-9]+", lowered))
    results = []
    for point in expected:
        point_tokens = {token for token in re.findall(r"[a-z0-9]+", point.lower()) if len(token) > 3}
        threshold = max(1, min(2, len(point_tokens) // 4))
        results.append(len(answer_tokens & point_tokens) >= threshold)
    return results


def _misconception_matches(answer: str, pattern: str) -> bool:
    pattern_lower = pattern.lower()
    markers = [word for word in ("delete", "reorder", "only", "original", "automatic") if word in pattern_lower]
    return bool(markers) and all(word in answer for word in markers[:2])


def _coverage_from_model_feedback(
    context: dict[str, Any], output: FeedbackOutput
) -> tuple[list[dict[str, str]], list[str]]:
    activity_output = context["activity"]["output"]
    if context["activity"]["type"] == "quiz":
        selected = str(context["attempt"]["selected_option_id"])
        correct = selected == str(activity_output["correct_option_id"])
        selected_item = next(item for item in activity_output["options"] if str(item["id"]) == selected)
        return ([{
            "key_point": str(context["concept"]["plain_definition"]),
            "status": "covered" if correct else "missing",
        }], [] if correct else [str(selected_item["misconception_tag"])])
    expected = list(activity_output["expected_key_points"])
    covered_count = min(len(expected), len(output.mastered_points))
    coverage = [
        {"key_point": point, "status": "covered" if index < covered_count else "missing"}
        for index, point in enumerate(expected)
    ]
    return coverage, [_tag_for_text(item) for item in output.misconceptions]


def _persist_feedback_and_evidence(
    database_path: Path,
    workspace_id: str,
    context: dict[str, Any],
    output: FeedbackOutput,
    coverage: list[dict[str, str]],
    misconception_tags: list[str],
    generation_mode: str,
    model: str,
) -> str:
    feedback_id = str(uuid.uuid4())
    evidence_id = str(uuid.uuid4())
    activity = context["activity"]
    attempt = context["attempt"]
    covered_count = sum(1 for item in coverage if item["status"] == "covered")
    if covered_count == len(coverage) and not misconception_tags:
        outcome = "mastered"
    elif covered_count > 0:
        outcome = "partial"
    else:
        outcome = "needs_support"
    confusion_signals = _unique_nonempty(
        str(item.get("confusion_signal") or "") for item in context["tutor_signals"]
    )
    prerequisite_signals = _unique_nonempty(
        str(item.get("prerequisite_gap_signal") or "") for item in context["tutor_signals"]
    )
    source_gap_signal = prerequisite_signals[0] if prerequisite_signals else None
    remedial_result = None
    with connect(database_path) as connection:
        existing = connection.execute(
            "SELECT id FROM feedbacks WHERE attempt_id = ? AND workspace_id = ?",
            (attempt["id"], workspace_id),
        ).fetchone()
        if existing:
            return str(existing["id"])
        session = connection.execute(
            "SELECT * FROM learning_sessions WHERE id = ? AND workspace_id = ?",
            (attempt["session_id"], workspace_id),
        ).fetchone()
        expected_state = "remedial_practice" if activity["type"] == "remedial" else "practicing"
        if not session or session["state"] != expected_state or session["active_activity_id"] != activity["id"]:
            raise SourceError("feedback_state_changed", "The mastery step changed before feedback was saved. Reload the session.", status_code=409)
        if activity["type"] == "remedial":
            remedial_result = _derive_remedial_result(connection, workspace_id, activity, coverage)
        refs_json = json.dumps([item.model_dump() for item in output.source_refs])
        connection.execute(
            """
            INSERT INTO feedbacks(
                id, workspace_id, session_id, concept_id, activity_id, attempt_id,
                output_json, source_origin, source_refs_json, generation_mode, model
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                feedback_id, workspace_id, attempt["session_id"], activity["concept_id"],
                activity["id"], attempt["id"], output.model_dump_json(), output.source_origin,
                refs_json, generation_mode, model,
            ),
        )
        connection.execute(
            """
            INSERT INTO learning_evidence(
                id, workspace_id, session_id, concept_id, activity_id, attempt_id,
                origin_id, activity_type, outcome, key_point_coverage_json,
                misconception_tags_json, hint_depth, elapsed_seconds,
                tutor_confusion_signals_json, remedial_result, source_gap_signal
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                evidence_id, workspace_id, attempt["session_id"], activity["concept_id"],
                activity["id"], attempt["id"], f"attempt:{attempt['id']}", activity["type"],
                outcome, json.dumps(coverage), json.dumps(misconception_tags),
                int(attempt["hint_depth"]), int(attempt["elapsed_seconds"]),
                json.dumps(confusion_signals), remedial_result, source_gap_signal,
            ),
        )
        connection.execute(
            """
            UPDATE learning_sessions
            SET state = 'feedback_shown', version = version + 1,
                last_saved_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND workspace_id = ?
            """,
            (attempt["session_id"], workspace_id),
        )
        _record_event(connection, workspace_id, str(attempt["session_id"]), "feedback_shown", {
            "feedback_id": feedback_id,
            "activity_id": activity["id"],
            "learning_evidence_id": evidence_id,
            "agent_decision_created": False,
        })
    return feedback_id


def _derive_remedial_result(connection, workspace_id: str, activity: dict[str, Any], coverage: list[dict[str, str]]) -> str:
    root_id = str(activity.get("parent_activity_id") or activity["id"])
    prior_remedials = connection.execute(
        """
        SELECT e.key_point_coverage_json
        FROM learning_evidence e JOIN activities a ON a.id = e.activity_id
        WHERE e.workspace_id = ? AND a.parent_activity_id = ? AND a.type = 'remedial'
        ORDER BY e.timestamp DESC, e.rowid DESC
        """,
        (workspace_id, root_id),
    ).fetchall()
    if prior_remedials:
        prior = json.loads(str(prior_remedials[0]["key_point_coverage_json"]))
    else:
        root = connection.execute(
            """
            SELECT key_point_coverage_json FROM learning_evidence
            WHERE workspace_id = ? AND activity_id = ?
            ORDER BY timestamp DESC, rowid DESC LIMIT 1
            """,
            (workspace_id, root_id),
        ).fetchone()
        prior = json.loads(str(root["key_point_coverage_json"])) if root else []
    current_ratio = _coverage_ratio(coverage)
    return "improved" if current_ratio > _coverage_ratio(prior) else "not_improved"


def _remedial_context(database_path: Path, workspace_id: str, feedback_id: str) -> dict[str, Any]:
    with connect(database_path) as connection:
        row = connection.execute(
            """
            SELECT f.*, a.output_json AS activity_output_json, a.parent_activity_id,
                   a.type AS activity_type, a.remedial_round, c.title AS concept_title,
                   c.plain_definition, c.role_in_map
            FROM feedbacks f JOIN activities a ON a.id = f.activity_id
            JOIN concepts c ON c.id = f.concept_id
            WHERE f.id = ? AND f.workspace_id = ?
            """,
            (feedback_id, workspace_id),
        ).fetchone()
        if not row:
            raise SourceError("feedback_not_found", "This feedback is not available in the current workspace.", status_code=404)
        parent_id = str(row["parent_activity_id"] or row["activity_id"])
        count = connection.execute(
            "SELECT COUNT(*) AS count FROM activities WHERE parent_activity_id = ? AND workspace_id = ? AND type = 'remedial'",
            (parent_id, workspace_id),
        ).fetchone()
        refs = json.loads(str(row["source_refs_json"]))
        chunks = []
        for ref in refs:
            chunk = connection.execute(
                """
                SELECT c.id, c.source_id, c.text, d.filename, d.source_origin
                FROM source_chunks c JOIN source_documents d ON d.id = c.source_id
                WHERE c.id = ? AND d.id = ? AND d.workspace_id = ? AND d.session_id = ?
                """,
                (ref["chunk_id"], ref["source_id"], workspace_id, row["session_id"]),
            ).fetchone()
            if chunk:
                chunks.append(dict(chunk))
    return {
        "feedback": dict(row) | {"output": json.loads(str(row["output_json"]))},
        "activity_output": json.loads(str(row["activity_output_json"])),
        "parent_activity_id": parent_id,
        "next_round": int(count["count"] or 0) + 1,
        "refs": refs,
        "chunks": chunks,
    }


def _demo_remedial(context: dict[str, Any], strategy: str) -> RemedialActivityOutput:
    row = context["feedback"]
    concept_title = str(row["concept_title"])
    missing = list(context["feedback"]["output"].get("missing_or_unclear_points", []))
    target = missing[0] if missing else str(row["plain_definition"])
    prompts = {
        "smaller_question": f"Complete one short line: In {concept_title}, relevance scores control how ___ information is combined.",
        "concrete_example": f"Imagine one word needs context from another word. In one sentence, say what {concept_title} compares and what information it brings in.",
        "contrast_question": f"Which is closer to {concept_title}: reordering the input, or combining information by relevance? Explain the difference in one sentence.",
        "rephrase_task": f"Rephrase this point in your own words without adding a new idea: {target}",
        "simpler_explanation": f"Use only the verbs compare and combine to explain {concept_title} in one sentence.",
    }
    refs = [SourceReference.model_validate(item) for item in context["refs"]]
    expected_target = (
        "Relevance scores control how value information is combined."
        if concept_title == "Self-attention" and strategy == "smaller_question"
        else target
    )
    return RemedialActivityOutput(
        strategy=strategy,
        title=f"One smaller step for {concept_title}",
        prompt=prompts[strategy],
        completion_condition="Write one sentence that answers only this prompt.",
        expected_key_points=[expected_target],
        misconception_patterns=list(context["activity_output"].get("misconception_patterns", []))[:4],
        hint_levels=[
            "Focus on the single missing relationship named in the prompt.",
            "Use this structure: compare or score → controls → information combined.",
            f"Source-grounded target: {target}",
        ],
        source_origin=str(row["source_origin"]),
        source_refs=refs,
    )


def _persist_remedial_activity(
    database_path: Path,
    workspace_id: str,
    context: dict[str, Any],
    output: RemedialActivityOutput,
    expected_session_version: int,
    generation_mode: str,
    model: str,
) -> str:
    activity_id = str(uuid.uuid4())
    row = context["feedback"]
    with connect(database_path) as connection:
        session = connection.execute(
            "SELECT * FROM learning_sessions WHERE id = ? AND workspace_id = ?",
            (row["session_id"], workspace_id),
        ).fetchone()
        if not session:
            raise SourceError("session_not_found", "This learning session is not available.", status_code=404)
        _require_version(int(session["version"]), expected_session_version)
        if session["state"] != "feedback_shown" or session["active_activity_id"] != row["activity_id"]:
            raise SourceError("remedial_state_changed", "The active feedback changed before remedial practice was saved.", status_code=409)
        connection.execute(
            """
            INSERT INTO activities(
                id, workspace_id, session_id, concept_id, type, prompt, output_json,
                source_origin, source_refs_json, generation_mode, model,
                parent_activity_id, parent_feedback_id, strategy, remedial_round
            ) VALUES (?, ?, ?, ?, 'remedial', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                activity_id, workspace_id, row["session_id"], row["concept_id"], output.prompt,
                output.model_dump_json(), output.source_origin,
                json.dumps([item.model_dump() for item in output.source_refs]), generation_mode,
                model, context["parent_activity_id"], row["id"], output.strategy, context["next_round"],
            ),
        )
        draft = connection.execute(
            "SELECT id FROM drafts WHERE workspace_id = ? AND session_id = ? AND draft_type = 'remedial'",
            (workspace_id, row["session_id"]),
        ).fetchone()
        if draft:
            connection.execute(
                """
                UPDATE drafts SET activity_id = ?, content = '', hint_depth = 0,
                    server_version = server_version + 1, sync_status = 'saved', updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (activity_id, draft["id"]),
            )
        else:
            connection.execute(
                """
                INSERT INTO drafts(id, workspace_id, session_id, activity_id, draft_type, content, hint_depth)
                VALUES (?, ?, ?, ?, 'remedial', '', 0)
                """,
                (str(uuid.uuid4()), workspace_id, row["session_id"], activity_id),
            )
        connection.execute(
            """
            UPDATE learning_sessions SET state = 'remedial_practice', active_activity_id = ?,
                version = version + 1, last_saved_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND workspace_id = ?
            """,
            (activity_id, row["session_id"], workspace_id),
        )
        _record_event(connection, workspace_id, str(row["session_id"]), "remedial_activity_created", {
            "activity_id": activity_id,
            "parent_activity_id": context["parent_activity_id"],
            "strategy": output.strategy,
            "remedial_round": context["next_round"],
            "agent_decision_created": False,
        })
    return activity_id


def _feedback_instructions(context: dict[str, Any]) -> str:
    origin_rule = _origin_rule(context["source_chunks"])
    return (
        "Evaluate only the submitted answer for the active concept. Return the fixed feedback fields: mastered points, "
        "missing or unclear points, misconceptions, one compact correction, one specific encouragement, and one next micro-action. "
        "The next micro-action must stay inside the current concept and may only suggest a hint, another practice, or remediation. "
        "It must not change the route, end the session, request search, or make an Agent decision. Meaningful paraphrases count. "
        f"Use only verified source IDs and chunk IDs provided below. {origin_rule} Do not reveal hidden reasoning."
    )


def _feedback_source_context(context: dict[str, Any]) -> str:
    activity = context["activity"]
    attempt = context["attempt"]
    lines = [
        f"Active concept: {context['concept']['title']}",
        f"Activity type: {activity['type']}",
        f"Submitted answer: {attempt['selected_option_id'] or attempt['raw_answer']}",
        f"Server-side evaluation key: {json.dumps(activity['output'])}",
    ]
    for chunk in context["source_chunks"]:
        lines.append(
            f"SOURCE_ID={chunk['source_id']} CHUNK_ID={chunk['id']} ORIGIN={chunk['source_origin']} "
            f"FILE={chunk['filename']}\n{chunk['text']}"
        )
    return "\n\n".join(lines)


def _remedial_instructions(context: dict[str, Any], strategy: str) -> str:
    origin_rule = _origin_rule(context["chunks"])
    return (
        f"Create exactly one short remedial activity using the strategy {strategy}. The strategy field must equal that value. "
        "Target only the latest specific missing or unclear point for the active concept. Include exactly three progressive hints. "
        "Do not repeat the full original task, change the learning route, request search, make an Agent decision, or mention hidden reasoning. "
        f"Use only the supplied verified source IDs and chunk IDs. {origin_rule}"
    )


def _remedial_source_context(context: dict[str, Any]) -> str:
    row = context["feedback"]
    lines = [
        f"Active concept: {row['concept_title']}",
        f"Definition: {row['plain_definition']}",
        f"Latest feedback: {json.dumps(context['feedback']['output'])}",
    ]
    for chunk in context["chunks"]:
        lines.append(
            f"SOURCE_ID={chunk['source_id']} CHUNK_ID={chunk['id']} ORIGIN={chunk['source_origin']} "
            f"FILE={chunk['filename']}\n{chunk['text']}"
        )
    return "\n\n".join(lines)


def _origin_rule(chunks: list[dict[str, Any]]) -> str:
    if any(chunk.get("source_origin") == "uploaded" for chunk in chunks):
        return "Uploaded material is primary; keep every supplemental origin explicit."
    return "The source is AI supplemental; never describe it as uploaded or externally cited."


def _validate_source_refs(
    database_path: Path,
    workspace_id: str,
    session_id: str,
    source_origin: str,
    refs: list[SourceReference],
) -> None:
    found_origins = []
    with connect(database_path) as connection:
        for ref in refs:
            row = connection.execute(
                """
                SELECT d.source_origin FROM source_chunks c JOIN source_documents d ON d.id = c.source_id
                WHERE d.id = ? AND c.id = ? AND d.workspace_id = ? AND d.session_id = ?
                """,
                (ref.source_id, ref.chunk_id, workspace_id, session_id),
            ).fetchone()
            if not row:
                raise SourceError("feedback_source_reference_invalid", "Feedback cited an unavailable source location, so it was not shown.", status_code=422)
            found_origins.append(str(row["source_origin"]))
    if source_origin in {"uploaded", "external"} and any(origin != source_origin for origin in found_origins):
        raise SourceError("feedback_source_origin_invalid", "The feedback source label did not match its verified references.", status_code=422)


def _public_evidence(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "activity_type": row["activity_type"],
        "concept_id": row["concept_id"],
        "outcome": row["outcome"],
        "key_point_coverage": json.loads(str(row["key_point_coverage_json"])),
        "misconception_tags": json.loads(str(row["misconception_tags_json"])),
        "hint_depth": row["hint_depth"],
        "elapsed_seconds": row["elapsed_seconds"],
        "tutor_confusion_signals": json.loads(str(row["tutor_confusion_signals_json"])),
        "remedial_result": row["remedial_result"],
        "source_gap_signal": row["source_gap_signal"],
        "timestamp": row["timestamp"],
    }


def _next_strategy(prior: list[str]) -> str:
    for strategy in REMEDIAL_STRATEGIES:
        if strategy not in prior:
            return strategy
    last = prior[-1] if prior else ""
    return next(strategy for strategy in REMEDIAL_STRATEGIES if strategy != last)


def _coverage_ratio(coverage: list[dict[str, str]]) -> float:
    return sum(item.get("status") == "covered" for item in coverage) / max(1, len(coverage))


def _tag_for_text(value: str) -> str:
    compact = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return compact[:80] or "observed_misconception"


def _unique_nonempty(values) -> list[str]:
    return list(dict.fromkeys(value.strip() for value in values if value and value.strip()))


def _feedback_by_attempt(database_path: Path, workspace_id: str, attempt_id: str):
    with connect(database_path) as connection:
        return connection.execute(
            "SELECT * FROM feedbacks WHERE attempt_id = ? AND workspace_id = ?",
            (attempt_id, workspace_id),
        ).fetchone()


def _evidence_id_for_attempt(connection, attempt_id: str) -> str | None:
    row = connection.execute("SELECT id FROM learning_evidence WHERE attempt_id = ?", (attempt_id,)).fetchone()
    return str(row["id"]) if row else None


def _require_version(actual: int, expected: int) -> None:
    if actual != expected:
        raise SourceError(
            "session_version_conflict",
            "This saved mastery step changed in another page. Reload it before continuing.",
            status_code=409,
            saved_state="The newer saved copy is unchanged.",
        )


def _start_ai_activity(settings: Settings, workspace_id: str, session_id: str, operation: str) -> str:
    log_id = str(uuid.uuid4())
    model = DEMO_FEEDBACK_MODEL if operation == "generate_feedback" else DEMO_REMEDIAL_MODEL
    with connect(settings.database_path) as connection:
        connection.execute(
            """
            INSERT INTO ai_activity_logs(id, workspace_id, session_id, operation, generation_mode, model, status)
            VALUES (?, ?, ?, ?, ?, ?, 'started')
            """,
            (log_id, workspace_id, session_id, operation, settings.mode, model if settings.mode == "demo" else settings.openai_model),
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
            UPDATE ai_activity_logs SET status = ?, response_id = ?, error_code = ?, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (status, response_id, error_code, log_id),
        )


def _record_event(connection, workspace_id: str, session_id: str, event_type: str, detail: dict[str, Any]) -> None:
    connection.execute(
        """
        INSERT INTO session_events(id, workspace_id, session_id, event_type, detail_json)
        VALUES (?, ?, ?, ?, ?)
        """,
        (str(uuid.uuid4()), workspace_id, session_id, event_type, json.dumps(detail)),
    )
