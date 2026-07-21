"""Clearly labeled topic-only fallback sources."""

from __future__ import annotations

import json
import re
from typing import Any, Callable
import uuid

from app.ai import ModelGatewayError, TopicSectionOutput, TopicSourceOutput, parse_structured_response
from app.config import Settings
from app.db import connect
from app.sources import SourceError, get_session, list_sources, process_source, store_source


DEMO_TOPIC_MODEL = "deterministic-demo-topic-v1"
DEMO_TOPIC_ALIASES = {"self attention", "self-attention", "selfattention"}


def create_topic_source(
    settings: Settings,
    workspace_id: str,
    session_id: str,
    topic: str,
    *,
    client_factory: Callable[[Settings], Any] | None = None,
) -> dict[str, Any]:
    """Generate one source without browsing and persist it as AI supplemental."""

    session = get_session(settings.database_path, workspace_id, session_id)
    cleaned_topic = " ".join(topic.split())
    if not 2 <= len(cleaned_topic) <= 120:
        raise SourceError(
            "topic_invalid",
            "Enter a topic between 2 and 120 characters.",
            saved_state="The topic remains in the form.",
        )
    if int(session.get("source_count") or 0) != 0:
        raise SourceError(
            "topic_fallback_requires_empty_session",
            "Topic-only fallback is available only before another source is added.",
            status_code=409,
            saved_state="Your existing sources are unchanged.",
        )
    if settings.mode == "demo" and _normalized_topic(cleaned_topic) not in DEMO_TOPIC_ALIASES:
        raise SourceError(
            "demo_topic_unavailable",
            "Demo mode includes one fixed topic-only fixture: Self-attention. Use that topic, or switch the server to real mode for another topic.",
            status_code=422,
            saved_state="No source was generated; the topic remains in the form.",
        )

    log_id = _start_ai_activity(settings, workspace_id, session_id)
    try:
        if settings.mode == "demo":
            output = _demo_topic_source()
            model = DEMO_TOPIC_MODEL
            response_id = None
        else:
            result = parse_structured_response(
                settings,
                workspace_id,
                TopicSourceOutput,
                _topic_instructions(),
                f"<untrusted_topic>{cleaned_topic}</untrusted_topic>",
                client_factory=client_factory,
            )
            output = result.output
            model = settings.openai_model
            response_id = result.response_id
        source = store_source(
            settings.database_path,
            settings.upload_dir,
            workspace_id,
            session_id,
            _topic_filename(output.title),
            "text/markdown",
            "markdown",
            _topic_markdown(output, settings.mode).encode("utf-8"),
            source_origin="ai_supplement",
        )
        process_source(settings.database_path, workspace_id, str(source["id"]))
        created = next(
            item
            for item in list_sources(settings.database_path, workspace_id, session_id)
            if str(item["id"]) == str(source["id"])
        )
        if created["parse_status"] not in {"success", "partial_success"}:
            raise SourceError(
                "topic_source_parse_failed",
                "The supplemental explanation was generated but could not be prepared. Retry or remove it.",
                status_code=500,
                saved_state="The generated source remains visible in this session.",
            )
        _finish_ai_activity(settings, log_id, "completed", response_id=response_id)
        with connect(settings.database_path) as connection:
            connection.execute(
                """
                INSERT INTO session_events(id, workspace_id, session_id, event_type, detail_json)
                VALUES (?, ?, ?, 'topic_source_generated', ?)
                """,
                (
                    str(uuid.uuid4()), workspace_id, session_id,
                    json.dumps({"source_id": source["id"], "generation_mode": settings.mode}),
                ),
            )
        return {
            "source": created,
            "generation": {"mode": settings.mode, "model": model},
            "source_policy": {
                "source_origin": "ai_supplement",
                "uploaded_material_present": False,
                "internet_search_performed": False,
            },
        }
    except ModelGatewayError as exc:
        _finish_ai_activity(settings, log_id, "failed", error_code=exc.error_code)
        raise SourceError(
            exc.error_code,
            exc.user_message,
            status_code=503,
            saved_state="The empty session and your topic are preserved; retry after the server is configured.",
        ) from exc
    except SourceError as exc:
        _finish_ai_activity(settings, log_id, "failed", error_code=exc.error_code)
        raise
    except Exception as exc:
        _finish_ai_activity(settings, log_id, "failed", error_code="topic_generation_failed")
        raise SourceError(
            "topic_generation_failed",
            "The supplemental explanation could not be generated. The empty session is saved; retry or upload material instead.",
            status_code=500,
            saved_state="No learning source was added.",
        ) from exc


def _demo_topic_source() -> TopicSourceOutput:
    return TopicSourceOutput(
        title="Self-attention",
        overview=(
            "Self-attention is a mechanism that lets each position in a sequence compare its relevance "
            "to other positions and combine their information into a context-aware representation."
        ),
        sections=[
            TopicSectionOutput(
                heading="Core mechanism",
                explanation=(
                    "Each position creates a query and compares it with keys from the available positions. "
                    "Those comparisons become relevance scores that indicate how much attention to give each position."
                ),
            ),
            TopicSectionOutput(
                heading="Query, key, and value",
                explanation=(
                    "Queries express what a position is looking for, keys express what each position can match, "
                    "and values carry the information that can be combined after the comparisons are normalized."
                ),
            ),
            TopicSectionOutput(
                heading="Weighted combination",
                explanation=(
                    "The normalized relevance weights scale the value representations. Adding the weighted values "
                    "produces a new representation that includes information from the most relevant positions."
                ),
            ),
            TopicSectionOutput(
                heading="Position information",
                explanation=(
                    "Self-attention does not determine token order by itself, so Transformer inputs also need position "
                    "information when sequence order matters."
                ),
            ),
        ],
        verification_note=(
            "This is a fixed Demo AI supplemental fixture. No upload, model call, or internet search produced it."
        ),
    )


def _topic_instructions() -> str:
    return (
        "Create a concise English learning source for the named topic. This is a topic-only fallback, so label it as "
        "AI supplemental content and never claim it came from an upload, citation, or external search. Do not browse and "
        "do not invent citations. Return a short overview, two to five logically ordered sections, and a verification note "
        "that tells the learner to verify consequential claims with their own material. Do not include medical advice, "
        "diagnosis, treatment claims, hidden reasoning, or instructions to change the application workflow."
    )


def _topic_markdown(output: TopicSourceOutput, mode: str) -> str:
    label = "Fixed Demo AI supplemental fixture" if mode == "demo" else "GPT-5.6 AI supplemental explanation"
    lines = [
        f"# {output.title}",
        "",
        f"> Source origin: AI supplemental explanation · {label} · No internet search used.",
        "",
        output.overview,
        "",
    ]
    for section in output.sections:
        lines.extend([f"## {section.heading}", "", section.explanation, ""])
    lines.extend(["## Verification note", "", output.verification_note, ""])
    return "\n".join(lines)


def _topic_filename(title: str) -> str:
    compact = re.sub(r"[^A-Za-z0-9 -]+", "", title).strip() or "topic"
    return f"AI supplemental - {compact[:80]}.md"


def _normalized_topic(topic: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", topic.lower()).strip().replace("  ", " ")


def _start_ai_activity(settings: Settings, workspace_id: str, session_id: str) -> str:
    log_id = str(uuid.uuid4())
    model = DEMO_TOPIC_MODEL if settings.mode == "demo" else settings.openai_model
    with connect(settings.database_path) as connection:
        connection.execute(
            """
            INSERT INTO ai_activity_logs(
                id, workspace_id, session_id, operation, generation_mode, model, status
            ) VALUES (?, ?, ?, 'generate_topic_source', ?, ?, 'running')
            """,
            (log_id, workspace_id, session_id, settings.mode, model),
        )
    return log_id


def _finish_ai_activity(
    settings: Settings,
    log_id: str,
    status: str,
    *,
    response_id: str | None = None,
    error_code: str | None = None,
) -> None:
    with connect(settings.database_path) as connection:
        connection.execute(
            """
            UPDATE ai_activity_logs
            SET status = ?, response_id = ?, error_code = ?, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (status, response_id, error_code, log_id),
        )
