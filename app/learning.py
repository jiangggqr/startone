"""Learner setup, grounded coverage, knowledge maps, and start actions."""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any, Literal
import uuid

from app.ai import (
    ClientFactory,
    ConceptEdge,
    ConceptOutput,
    CoveredConcept,
    KnowledgeMapOutput,
    ModelGatewayError,
    SourceCoverageOutput,
    SourceGapProposal,
    SourceReference,
    StartActionOutput,
    parse_structured_response,
)
from app.config import Settings
from app.db import connect
from app.sources import SourceError, get_session, process_source, store_source


READY_SOURCE_STATES = ("success", "partial_success")
DEMO_MODEL = "deterministic-demo-v1"


def update_session_setup(
    database_path: Path,
    workspace_id: str,
    session_id: str,
    values: dict[str, Any],
    expected_version: int,
) -> dict[str, Any]:
    session = get_session(database_path, workspace_id, session_id)
    goal = values["goal"].strip()
    prior_knowledge = values["prior_knowledge"].strip()
    if len(goal) < 5 or len(prior_knowledge) < 2:
        raise SourceError(
            "session_setup_invalid",
            "Add a specific learning goal and a short description of what you already know.",
            saved_state="Your form values remain in the browser.",
        )
    if int(session["version"]) != expected_version:
        raise SourceError(
            "session_version_conflict",
            "This session was updated in another page. Your form values are still here; reload the saved version and review your changes.",
            status_code=409,
            saved_state="Both the saved session and your unsent form values are preserved.",
        )
    name = _session_name(goal)
    with connect(database_path) as connection:
        cursor = connection.execute(
            """
            UPDATE learning_sessions
            SET name = ?, goal = ?, prior_knowledge = ?, available_minutes = ?,
                energy_level = ?, language = 'English', current_question = ?,
                support_preferences_json = ?, show_timer = ?, search_permission = ?,
                setup_completed = 1, version = version + 1, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND workspace_id = ? AND version = ?
            """,
            (
                name,
                goal,
                prior_knowledge,
                values["available_minutes"],
                values["energy_level"],
                (values.get("current_question") or "").strip() or None,
                json.dumps(values["support_preferences"]),
                int(values["show_timer"]),
                int(values["search_permission"]),
                session_id,
                workspace_id,
                expected_version,
            ),
        )
        if cursor.rowcount != 1:
            raise SourceError(
                "session_version_conflict",
                "This session changed before your setup could be saved. Reload the saved version and review your form values.",
                status_code=409,
                saved_state="Your browser still holds the form values.",
            )
    return get_session(database_path, workspace_id, session_id)


def load_demo_materials(
    settings: Settings,
    workspace_id: str,
    session_id: str,
    sample_dir: Path,
    scenario: Literal["standard", "controlled_search"] = "standard",
) -> list[dict[str, Any]]:
    if settings.mode != "demo":
        raise SourceError(
            "demo_fixture_unavailable",
            "Demo materials can only be loaded while the app is in Demo mode.",
            status_code=409,
            saved_state="Your current session and sources are unchanged.",
        )
    get_session(settings.database_path, workspace_id, session_id)
    created: list[dict[str, Any]] = []
    with connect(settings.database_path) as connection:
        existing = {
            str(row["filename"])
            for row in connection.execute(
                "SELECT filename FROM source_documents WHERE session_id = ? AND workspace_id = ?",
                (session_id, workspace_id),
            )
        }
    filenames = (
        ("transformer_notes.md",)
        if scenario == "controlled_search"
        else ("transformer_notes.md", "matrix_prerequisite.md")
    )
    for filename in filenames:
        if filename in existing:
            continue
        data = (sample_dir / filename).read_bytes()
        source = store_source(
            settings.database_path,
            settings.upload_dir,
            workspace_id,
            session_id,
            filename,
            "text/markdown",
            "markdown",
            data,
        )
        process_source(settings.database_path, workspace_id, str(source["id"]))
        created.append(source)
    return created


def generate_coverage(
    settings: Settings,
    workspace_id: str,
    session_id: str,
    *,
    client_factory: ClientFactory | None = None,
) -> dict[str, Any]:
    session = _require_ready_session(settings.database_path, workspace_id, session_id)
    operation = "source_coverage"
    activity_id = _start_ai_activity(settings, workspace_id, session_id, operation)
    try:
        chunks = _source_chunks(settings.database_path, workspace_id, session_id)
        if settings.mode == "demo":
            output = _demo_coverage(chunks)
            response_id = None
            model = DEMO_MODEL
        else:
            result = parse_structured_response(
                settings,
                workspace_id,
                SourceCoverageOutput,
                _coverage_instructions(session, chunks),
                _source_context(chunks),
                client_factory=client_factory,
            )
            output = result.output
            response_id = result.response_id
            model = settings.openai_model
        _validate_coverage(output)
        _validate_source_references(settings.database_path, workspace_id, session_id, output)
        _persist_coverage(settings, workspace_id, session_id, output, model)
        _finish_ai_activity(settings, activity_id, "completed", response_id=response_id)
        return _coverage_payload(settings.database_path, workspace_id, session_id, output, model)
    except ModelGatewayError as exc:
        _finish_ai_activity(settings, activity_id, "failed", error_code=exc.error_code)
        raise SourceError(
            exc.error_code,
            exc.user_message,
            status_code=503,
            saved_state="Your setup and uploaded sources are saved.",
        ) from exc
    except SourceError as exc:
        _finish_ai_activity(settings, activity_id, "failed", error_code=exc.error_code)
        raise
    except Exception:
        _finish_ai_activity(settings, activity_id, "failed", error_code="coverage_generation_failed")
        raise SourceError(
            "coverage_generation_failed",
            "Source coverage could not be generated. Your setup and sources are saved; retry generation.",
            status_code=500,
            saved_state="Your setup and uploaded sources are saved.",
        )


def get_coverage(database_path: Path, workspace_id: str, session_id: str) -> dict[str, Any]:
    get_session(database_path, workspace_id, session_id)
    with connect(database_path) as connection:
        row = connection.execute(
            "SELECT * FROM source_coverages WHERE session_id = ? AND workspace_id = ?",
            (session_id, workspace_id),
        ).fetchone()
    if not row:
        raise SourceError(
            "coverage_not_generated",
            "Source coverage has not been generated yet.",
            status_code=404,
            saved_state="Your setup and uploaded sources are saved.",
        )
    output = SourceCoverageOutput.model_validate_json(str(row["output_json"]))
    return _coverage_payload(database_path, workspace_id, session_id, output, str(row["model"]))


def generate_knowledge_map(
    settings: Settings,
    workspace_id: str,
    session_id: str,
    *,
    client_factory: ClientFactory | None = None,
) -> dict[str, Any]:
    session = _require_ready_session(settings.database_path, workspace_id, session_id)
    coverage_payload = get_coverage(settings.database_path, workspace_id, session_id)
    coverage = SourceCoverageOutput.model_validate(coverage_payload["coverage"])
    operation = "knowledge_map"
    activity_id = _start_ai_activity(settings, workspace_id, session_id, operation)
    try:
        chunks = _source_chunks(settings.database_path, workspace_id, session_id)
        if settings.mode == "demo":
            output = _demo_map(chunks, coverage, int(session["available_minutes"] or 25))
            response_id = None
            model = DEMO_MODEL
        else:
            result = parse_structured_response(
                settings,
                workspace_id,
                KnowledgeMapOutput,
                _map_instructions(session, coverage, chunks),
                _source_context(chunks),
                client_factory=client_factory,
            )
            output = result.output
            response_id = result.response_id
            model = settings.openai_model
        _validate_map(output)
        _validate_source_references(settings.database_path, workspace_id, session_id, output)
        _persist_map(settings, workspace_id, session_id, output, model)
        _finish_ai_activity(settings, activity_id, "completed", response_id=response_id)
        return _map_payload(settings.database_path, workspace_id, session_id, output, model, False)
    except ModelGatewayError as exc:
        _finish_ai_activity(settings, activity_id, "failed", error_code=exc.error_code)
        raise SourceError(
            exc.error_code,
            exc.user_message,
            status_code=503,
            saved_state="Your setup, sources, and coverage review are saved.",
        ) from exc
    except SourceError as exc:
        _finish_ai_activity(settings, activity_id, "failed", error_code=exc.error_code)
        raise
    except Exception:
        _finish_ai_activity(settings, activity_id, "failed", error_code="map_generation_failed")
        raise SourceError(
            "map_generation_failed",
            "The learning map could not be generated. Your coverage review is saved; retry generation.",
            status_code=500,
            saved_state="Your setup, sources, and coverage review are saved.",
        )


def get_knowledge_map(database_path: Path, workspace_id: str, session_id: str) -> dict[str, Any]:
    get_session(database_path, workspace_id, session_id)
    with connect(database_path) as connection:
        row = connection.execute(
            "SELECT * FROM knowledge_maps WHERE session_id = ? AND workspace_id = ?",
            (session_id, workspace_id),
        ).fetchone()
    if not row:
        raise SourceError(
            "map_not_generated",
            "A learning map has not been generated yet.",
            status_code=404,
            saved_state="Your setup, sources, and coverage review are saved.",
        )
    output = KnowledgeMapOutput.model_validate_json(str(row["output_json"]))
    return _map_payload(
        database_path,
        workspace_id,
        session_id,
        output,
        str(row["model"]),
        row["confirmed_at"] is not None,
    )


def adjust_knowledge_map(
    database_path: Path,
    workspace_id: str,
    session_id: str,
    route_concept_keys: list[str],
) -> dict[str, Any]:
    payload = get_knowledge_map(database_path, workspace_id, session_id)
    output = KnowledgeMapOutput.model_validate(payload["knowledge_map"])
    available = {concept.concept_key for concept in output.concepts}
    if len(route_concept_keys) < 2 or len(route_concept_keys) > 5 or len(set(route_concept_keys)) != len(route_concept_keys):
        raise SourceError(
            "invalid_learning_route",
            "Choose between 2 and 5 different concepts for this session.",
            saved_state="The existing learning map is unchanged.",
        )
    if any(key not in available for key in route_concept_keys):
        raise SourceError(
            "invalid_learning_route",
            "The adjusted route contains a concept that is not in this learning map.",
            saved_state="The existing learning map is unchanged.",
        )
    order = {concept.concept_key: index for index, concept in enumerate(output.concepts)}
    if route_concept_keys != sorted(route_concept_keys, key=order.get):
        raise SourceError(
            "invalid_learning_route_order",
            "Keep selected concepts in their dependency order.",
            saved_state="The existing learning map is unchanged.",
        )
    concepts_by_key = {concept.concept_key: concept for concept in output.concepts}
    selected = set(route_concept_keys)
    missing_prerequisites = {
        prerequisite
        for key in route_concept_keys
        for prerequisite in concepts_by_key[key].prerequisite_keys
        if prerequisite not in selected
    }
    if missing_prerequisites:
        raise SourceError(
            "invalid_learning_route_prerequisite",
            "The adjusted route leaves out a required prerequisite. Shorten from the end of the route instead.",
            saved_state="The existing learning map is unchanged.",
        )
    adjusted = output.model_copy(update={"recommended_route": route_concept_keys})
    with connect(database_path) as connection:
        connection.execute(
            """
            UPDATE knowledge_maps
            SET output_json = ?, version = version + 1, confirmed_at = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE session_id = ? AND workspace_id = ?
            """,
            (adjusted.model_dump_json(), session_id, workspace_id),
        )
        connection.execute(
            """
            UPDATE learning_sessions
            SET state = 'path_drafting', version = version + 1, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND workspace_id = ?
            """,
            (session_id, workspace_id),
        )
    return _map_payload(database_path, workspace_id, session_id, adjusted, payload["generation"]["model"], False)


def confirm_knowledge_map(database_path: Path, workspace_id: str, session_id: str) -> dict[str, Any]:
    payload = get_knowledge_map(database_path, workspace_id, session_id)
    session = get_session(database_path, workspace_id, session_id)
    if session["state"] not in {"path_drafting", "path_confirmed", "start_action"}:
        raise SourceError(
            "invalid_session_transition",
            "This learning map cannot be confirmed from the current session state.",
            status_code=409,
            saved_state="Your current session state is unchanged.",
        )
    with connect(database_path) as connection:
        connection.execute(
            """
            UPDATE knowledge_maps
            SET confirmed_at = COALESCE(confirmed_at, CURRENT_TIMESTAMP),
                version = version + 1, updated_at = CURRENT_TIMESTAMP
            WHERE session_id = ? AND workspace_id = ?
            """,
            (session_id, workspace_id),
        )
        connection.execute(
            """
            UPDATE learning_sessions
            SET state = 'start_action', version = version + 1, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND workspace_id = ?
            """,
            (session_id, workspace_id),
        )
    return get_knowledge_map(database_path, workspace_id, session_id)


def list_source_gaps(database_path: Path, workspace_id: str, session_id: str) -> list[dict[str, Any]]:
    get_session(database_path, workspace_id, session_id)
    with connect(database_path) as connection:
        rows = connection.execute(
            """
            SELECT * FROM source_gaps
            WHERE session_id = ? AND workspace_id = ?
            ORDER BY created_at, id
            """,
            (session_id, workspace_id),
        ).fetchall()
    return [
        {
            "id": row["id"],
            "concept_key": row["concept_key"],
            "description": row["description"],
            "why_needed": row["why_needed"],
            "evidence": row["evidence"],
            "current_source_refs": json.loads(str(row["current_source_refs_json"])),
            "suggested_query_scope": row["suggested_query_scope"],
            "status": row["status"],
        }
        for row in rows
    ]


def _require_ready_session(database_path: Path, workspace_id: str, session_id: str) -> dict[str, Any]:
    session = get_session(database_path, workspace_id, session_id)
    if not session.get("setup_completed"):
        raise SourceError(
            "session_setup_required",
            "Complete the short session setup before generating a learning path.",
            status_code=409,
            saved_state="Your uploaded sources are saved.",
        )
    if int(session.get("ready_source_count") or 0) < 1:
        raise SourceError(
            "ready_source_required",
            "Add at least one source with readable text before generating coverage.",
            status_code=409,
            saved_state="Your session and any existing uploads are saved.",
        )
    return session


def _source_chunks(database_path: Path, workspace_id: str, session_id: str) -> list[dict[str, Any]]:
    with connect(database_path) as connection:
        rows = connection.execute(
            """
            SELECT c.*, d.filename, d.media_kind, d.source_origin
            FROM source_chunks c
            JOIN source_documents d ON d.id = c.source_id
            WHERE d.session_id = ? AND d.workspace_id = ?
              AND d.parse_status IN ('success', 'partial_success')
            ORDER BY d.created_at, c.rowid
            """,
            (session_id, workspace_id),
        ).fetchall()
    return [dict(row) for row in rows]


def _ref(chunk: dict[str, Any]) -> SourceReference:
    return SourceReference(source_id=str(chunk["source_id"]), chunk_id=str(chunk["id"]))


def _find_chunk(chunks: list[dict[str, Any]], *terms: str) -> dict[str, Any]:
    for term in terms:
        lowered = term.lower()
        for chunk in chunks:
            haystack = f"{chunk.get('heading_path') or ''} {chunk.get('text') or ''}".lower()
            if lowered in haystack:
                return chunk
    return chunks[0]


def _demo_coverage(chunks: list[dict[str, Any]]) -> SourceCoverageOutput:
    filenames = {str(chunk["filename"]) for chunk in chunks}
    if "transformer_notes.md" in filenames:
        transformer = _find_chunk(chunks, "why transformer", "sequence models")
        self_attention = _find_chunk(chunks, "self-attention lets", "self-attention")
        qkv = _find_chunk(chunks, "query, key and value", "query is compared")
        scaled = _find_chunk(chunks, "scaled dot-product", "square root")
        positional = _find_chunk(chunks, "positional information", "token order")
        covered = [
            CoveredConcept(concept_key="transformer_goal", title="Transformer goal", coverage_summary="Why sequence representations need relationships across tokens.", source_refs=[_ref(transformer)]),
            CoveredConcept(concept_key="self_attention", title="Self-attention", coverage_summary="Compare relevance, then combine value information using those scores.", source_refs=[_ref(self_attention)]),
            CoveredConcept(concept_key="qkv", title="Query, Key, and Value", coverage_summary="How projections produce scores and weighted value combinations.", source_refs=[_ref(qkv)]),
            CoveredConcept(concept_key="scaled_dot_product", title="Scaled dot-product attention", coverage_summary="Dot-product scores are scaled before softmax for stability.", source_refs=[_ref(scaled)]),
            CoveredConcept(concept_key="positional_information", title="Positional information", coverage_summary="Position signals provide token order that self-attention alone lacks.", source_refs=[_ref(positional)]),
        ]
        gaps: list[SourceGapProposal] = []
        if "matrix_prerequisite.md" not in filenames:
            gaps.append(
                SourceGapProposal(
                    concept_key="scaled_dot_product",
                    description="The material uses a dot product for attention scores but does not define the vector operation.",
                    why_needed="A learner who lacks this prerequisite may not understand how query-key comparisons become one score.",
                    evidence="The attention notes name the dot product without a worked prerequisite explanation.",
                    current_source_refs=[_ref(scaled)],
                    suggested_query_scope="A short beginner explanation of vector dot products in attention.",
                )
            )
        gaps.append(
            SourceGapProposal(
                concept_key="scaled_dot_product",
                description="The material states that scaling stabilizes scores but does not explain why score variance grows with key dimension.",
                why_needed="This is useful only if the learner needs a deeper explanation of the square-root scaling factor.",
                evidence="The source gives the stabilization claim without a derivation or numeric example.",
                current_source_refs=[_ref(scaled)],
                suggested_query_scope="A concise derivation of variance scaling in scaled dot-product attention.",
            )
        )
        all_refs = []
        for concept in covered:
            if concept.source_refs[0] not in all_refs:
                all_refs.append(concept.source_refs[0])
        return SourceCoverageOutput(
            covered_concepts=covered,
            source_gaps=gaps,
            ignored_sections=[],
            source_refs=all_refs,
        )

    selected = []
    seen_headings: set[str] = set()
    for chunk in chunks:
        heading_path = str(chunk.get("heading_path") or "").strip()
        heading_key = heading_path.casefold()
        if heading_key in seen_headings or heading_key.endswith("verification note"):
            continue
        seen_headings.add(heading_key)
        selected.append(chunk)
        if len(selected) == 5:
            break
    covered = []
    for index, chunk in enumerate(selected, start=1):
        heading = str(chunk.get("heading_path") or f"Source concept {index}").split(" > ")[-1]
        key = re.sub(r"[^a-z0-9]+", "_", heading.lower()).strip("_") or f"concept_{index}"
        covered.append(
            CoveredConcept(
                concept_key=f"{key}_{index}",
                title=heading[:80],
                coverage_summary="This section is directly covered by the saved learning source.",
                source_refs=[_ref(chunk)],
            )
        )
    return SourceCoverageOutput(
        covered_concepts=covered,
        source_gaps=[],
        ignored_sections=[],
        source_refs=[_ref(chunk) for chunk in selected],
    )


def _demo_map(
    chunks: list[dict[str, Any]],
    coverage: SourceCoverageOutput,
    available_minutes: int,
) -> KnowledgeMapOutput:
    by_filename = {str(chunk["filename"]) for chunk in chunks}
    if "transformer_notes.md" in by_filename:
        transformer = _find_chunk(chunks, "why transformer", "sequence models")
        self_attention = _find_chunk(chunks, "self-attention lets", "self-attention")
        qkv = _find_chunk(chunks, "query, key and value", "query is compared")
        scaled = _find_chunk(chunks, "scaled dot-product", "square root")
        positional = _find_chunk(chunks, "positional information", "token order")
        concepts = [
            ConceptOutput(concept_key="transformer_goal", title="Transformer goal", plain_definition="Represent relationships across a sequence without processing every dependency one step at a time.", role_in_map="Frames why attention is useful.", prerequisite_keys=[], estimated_minutes=2, source_refs=[_ref(transformer)]),
            ConceptOutput(concept_key="self_attention", title="Self-attention", plain_definition="Each position compares relevance to other positions, then combines their value information using those weights.", role_in_map="Core mechanism for contextualizing each position.", prerequisite_keys=["transformer_goal"], estimated_minutes=7, source_refs=[_ref(self_attention)]),
            ConceptOutput(concept_key="qkv", title="Query, Key, and Value", plain_definition="Queries compare with keys to produce scores, while values carry the information that will be combined.", role_in_map="Names the three representations used by self-attention.", prerequisite_keys=["self_attention"], estimated_minutes=6, source_refs=[_ref(qkv)]),
            ConceptOutput(concept_key="scaled_dot_product", title="Scaled dot-product attention", plain_definition="Query-key dot products are scaled before softmax so attention scores remain stable.", role_in_map="Turns comparisons into usable attention weights.", prerequisite_keys=["qkv"], estimated_minutes=6, source_refs=[_ref(scaled)]),
            ConceptOutput(concept_key="positional_information", title="Positional information", plain_definition="Position signals let the model distinguish token order, which self-attention alone does not encode.", role_in_map="Adds sequence order to attention-based representations.", prerequisite_keys=["transformer_goal"], estimated_minutes=4, source_refs=[_ref(positional)]),
        ]
        return KnowledgeMapOutput(
            map_title="Transformer attention foundations",
            concepts=concepts,
            edges=[
                ConceptEdge(from_concept_key="transformer_goal", to_concept_key="self_attention", relationship="motivates"),
                ConceptEdge(from_concept_key="self_attention", to_concept_key="qkv", relationship="uses"),
                ConceptEdge(from_concept_key="qkv", to_concept_key="scaled_dot_product", relationship="enables"),
                ConceptEdge(from_concept_key="transformer_goal", to_concept_key="positional_information", relationship="also requires"),
            ],
            recommended_route=[
                "transformer_goal",
                "self_attention",
                "qkv",
                "scaled_dot_product",
                "positional_information",
            ],
            start_action=StartActionOutput(
                title="Write one sentence about self-attention",
                instruction="Without checking the notes, write one sentence describing what you currently think self-attention does.",
                estimated_seconds=90,
                completion_condition="Write one checkable sentence; it does not need to be correct.",
                why_this_first="A small recall attempt gives the Tutor a clear, low-pressure place to begin.",
            ),
            source_gaps=coverage.source_gaps,
        )

    selected = coverage.covered_concepts[:5]
    if len(selected) == 1:
        original = selected[0]
        selected = [
            original.model_copy(
                update={
                    "concept_key": f"{original.concept_key}_foundation",
                    "title": f"{original.title}: foundation",
                    "coverage_summary": f"Identify the purpose and vocabulary of {original.title}.",
                }
            ),
            original.model_copy(
                update={
                    "concept_key": f"{original.concept_key}_application",
                    "title": f"{original.title}: application",
                    "coverage_summary": f"Explain how the main ideas in {original.title} work together.",
                }
            ),
        ]
    concepts = [
        ConceptOutput(
            concept_key=item.concept_key,
            title=item.title,
            plain_definition=item.coverage_summary,
            role_in_map="A grounded step drawn from the saved learning source.",
            prerequisite_keys=[] if index == 0 else [selected[index - 1].concept_key],
            estimated_minutes=max(1, min(10, available_minutes // len(selected))),
            source_refs=item.source_refs,
        )
        for index, item in enumerate(selected)
    ]
    return KnowledgeMapOutput(
        map_title="Grounded learning path",
        concepts=concepts,
        edges=[
            ConceptEdge(from_concept_key=concepts[index - 1].concept_key, to_concept_key=concepts[index].concept_key, relationship="prepares for")
            for index in range(1, len(concepts))
        ],
        recommended_route=[item.concept_key for item in concepts],
        start_action=StartActionOutput(
            title="Write what you already know",
            instruction=f"Without reopening the source, write one sentence about {concepts[0].title}.",
            estimated_seconds=90,
            completion_condition="Write one checkable sentence; accuracy is not required.",
            why_this_first="This short recall attempt creates a concrete starting point.",
        ),
        source_gaps=coverage.source_gaps,
    )


def _validate_map(output: KnowledgeMapOutput) -> None:
    keys = [concept.concept_key for concept in output.concepts]
    if len(keys) != len(set(keys)) or any(not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", key) for key in keys):
        raise SourceError(
            "model_output_invalid",
            "The generated map reused a concept identifier. Nothing was saved; retry generation.",
            status_code=422,
        )
    if set(output.recommended_route) != set(keys) or len(output.recommended_route) != len(keys):
        raise SourceError(
            "model_output_invalid",
            "The generated route did not match its concepts. Nothing was saved; retry generation.",
            status_code=422,
        )
    known = set(keys)
    for concept in output.concepts:
        if any(key not in known or key == concept.concept_key for key in concept.prerequisite_keys):
            raise SourceError(
                "model_output_invalid",
                "The generated map contained an invalid prerequisite. Nothing was saved; retry generation.",
                status_code=422,
            )
    for edge in output.edges:
        if edge.from_concept_key not in known or edge.to_concept_key not in known:
            raise SourceError(
                "model_output_invalid",
                "The generated map contained an invalid dependency. Nothing was saved; retry generation.",
                status_code=422,
            )


def _validate_coverage(output: SourceCoverageOutput) -> None:
    keys = [concept.concept_key for concept in output.covered_concepts]
    if len(keys) != len(set(keys)) or any(not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", key) for key in keys):
        raise SourceError(
            "model_output_invalid",
            "The generated coverage used invalid concept identifiers. Nothing was saved; retry generation.",
            status_code=422,
        )


def _validate_source_references(
    database_path: Path,
    workspace_id: str,
    session_id: str,
    output: SourceCoverageOutput | KnowledgeMapOutput,
) -> None:
    references: set[tuple[str, str]] = set()
    payload = output.model_dump()

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            if set(value) >= {"source_id", "chunk_id"}:
                references.add((str(value["source_id"]), str(value["chunk_id"])))
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(payload)
    if not references:
        raise SourceError(
            "source_reference_invalid",
            "The generated result did not include a verifiable source location. Nothing was saved; retry generation.",
            status_code=422,
        )
    with connect(database_path) as connection:
        valid = {
            (str(row["source_id"]), str(row["chunk_id"]))
            for row in connection.execute(
                """
                SELECT d.id AS source_id, c.id AS chunk_id
                FROM source_chunks c
                JOIN source_documents d ON d.id = c.source_id
                WHERE d.session_id = ? AND d.workspace_id = ?
                  AND d.parse_status IN ('success', 'partial_success')
                """,
                (session_id, workspace_id),
            )
        }
    if not references.issubset(valid):
        raise SourceError(
            "source_reference_invalid",
            "Generated content referenced a source location that does not exist, so it was not saved or displayed. Retry generation.",
            status_code=422,
            saved_state="Your setup and uploaded sources are saved.",
        )


def _persist_coverage(
    settings: Settings,
    workspace_id: str,
    session_id: str,
    output: SourceCoverageOutput,
    model: str,
) -> None:
    with connect(settings.database_path) as connection:
        connection.execute(
            """
            INSERT INTO source_coverages(
                id, workspace_id, session_id, output_json, generation_mode, model
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                output_json = excluded.output_json,
                generation_mode = excluded.generation_mode,
                model = excluded.model,
                version = source_coverages.version + 1,
                updated_at = CURRENT_TIMESTAMP
            """,
            (str(uuid.uuid4()), workspace_id, session_id, output.model_dump_json(), settings.mode, model),
        )
        connection.execute("DELETE FROM source_gaps WHERE session_id = ?", (session_id,))
        for gap in output.source_gaps:
            gap_id = str(uuid.uuid5(uuid.UUID(session_id), gap.description))
            connection.execute(
                """
                INSERT INTO source_gaps(
                    id, workspace_id, session_id, concept_key, description, why_needed,
                    evidence, current_source_refs_json, suggested_query_scope, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'candidate')
                """,
                (
                    gap_id,
                    workspace_id,
                    session_id,
                    gap.concept_key,
                    gap.description,
                    gap.why_needed,
                    gap.evidence,
                    json.dumps([ref.model_dump() for ref in gap.current_source_refs]),
                    gap.suggested_query_scope,
                ),
            )
        connection.execute(
            """
            UPDATE learning_sessions
            SET state = 'path_drafting', version = version + 1, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND workspace_id = ?
            """,
            (session_id, workspace_id),
        )


def _persist_map(
    settings: Settings,
    workspace_id: str,
    session_id: str,
    output: KnowledgeMapOutput,
    model: str,
) -> None:
    with connect(settings.database_path) as connection:
        connection.execute(
            """
            INSERT INTO knowledge_maps(
                id, workspace_id, session_id, output_json, generation_mode, model
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                output_json = excluded.output_json,
                generation_mode = excluded.generation_mode,
                model = excluded.model,
                version = knowledge_maps.version + 1,
                confirmed_at = NULL,
                updated_at = CURRENT_TIMESTAMP
            """,
            (str(uuid.uuid4()), workspace_id, session_id, output.model_dump_json(), settings.mode, model),
        )
        connection.execute("DELETE FROM concepts WHERE session_id = ?", (session_id,))
        for index, concept in enumerate(output.concepts):
            connection.execute(
                """
                INSERT INTO concepts(
                    id, workspace_id, session_id, concept_key, title, plain_definition,
                    role_in_map, prerequisite_keys_json, order_index, estimated_minutes,
                    source_refs_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid5(uuid.UUID(session_id), concept.concept_key)),
                    workspace_id,
                    session_id,
                    concept.concept_key,
                    concept.title,
                    concept.plain_definition,
                    concept.role_in_map,
                    json.dumps(concept.prerequisite_keys),
                    index,
                    concept.estimated_minutes,
                    json.dumps([ref.model_dump() for ref in concept.source_refs]),
                ),
            )
        connection.execute(
            """
            UPDATE learning_sessions
            SET state = 'path_drafting', version = version + 1, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND workspace_id = ?
            """,
            (session_id, workspace_id),
        )


def _coverage_payload(
    database_path: Path,
    workspace_id: str,
    session_id: str,
    output: SourceCoverageOutput,
    model: str,
) -> dict[str, Any]:
    return {
        "coverage": output.model_dump(),
        "source_gaps": list_source_gaps(database_path, workspace_id, session_id),
        "source_ref_details": _source_ref_details(database_path, workspace_id, session_id),
        "generation": {
            "mode": "demo" if model == DEMO_MODEL else "real",
            "model": model,
            "internet_search_performed": False,
        },
    }


def _map_payload(
    database_path: Path,
    workspace_id: str,
    session_id: str,
    output: KnowledgeMapOutput,
    model: str,
    confirmed: bool,
) -> dict[str, Any]:
    return {
        "knowledge_map": output.model_dump(),
        "source_ref_details": _source_ref_details(database_path, workspace_id, session_id),
        "confirmed": confirmed,
        "generation": {
            "mode": "demo" if model == DEMO_MODEL else "real",
            "model": model,
            "internet_search_performed": False,
        },
    }


def _source_ref_details(database_path: Path, workspace_id: str, session_id: str) -> list[dict[str, Any]]:
    chunks = _source_chunks(database_path, workspace_id, session_id)
    details = []
    for chunk in chunks:
        if chunk["media_kind"] == "pdf":
            location = f"Page {chunk['page_number']} · excerpt {chunk['page_chunk_index']}"
        elif chunk["media_kind"] == "pasted":
            location = f"Paragraph {chunk['paragraph_number']} · characters {chunk['start_char']}–{chunk['end_char']}"
        else:
            location = f"{chunk['heading_path'] or 'Document'} · lines {chunk['start_line']}–{chunk['end_line']}"
        details.append(
            {
                "source_id": chunk["source_id"],
                "chunk_id": chunk["id"],
                "filename": chunk["filename"],
                "location": location,
                "source_origin": chunk["source_origin"],
            }
        )
    return details


def _source_context(chunks: list[dict[str, Any]]) -> str:
    parts = []
    used = 0
    for chunk in chunks:
        text = str(chunk["text"])
        if used + len(text) > 30_000:
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
                    f"page: {chunk.get('page_number') or ''}",
                    f"lines: {chunk.get('start_line') or ''}-{chunk.get('end_line') or ''}",
                    "content:",
                    text,
                    "</source_excerpt>",
                ]
            )
        )
    return "\n\n".join(parts)


def _coverage_instructions(session: dict[str, Any], chunks: list[dict[str, Any]]) -> str:
    source_policy = _generation_source_policy(chunks)
    return (
        "You generate source coverage for an English learning interface. "
        f"{source_policy} "
        "Identify what is explicitly covered and only concrete candidate gaps. A gap is not a search request. "
        "Use only exact source_id and chunk_id pairs supplied in the excerpts. Never invent a citation, page, line, "
        "fact, or source. Do not browse and do not suggest that browsing already occurred. Keep every user-facing field concise. "
        f"Learner goal: {session.get('goal')}. Prior knowledge: {session.get('prior_knowledge')}."
    )


def _map_instructions(
    session: dict[str, Any],
    coverage: SourceCoverageOutput,
    chunks: list[dict[str, Any]],
) -> str:
    source_policy = _generation_source_policy(chunks)
    return (
        "You generate a grounded English knowledge map with 2 to 5 concepts and a dependency-respecting route. "
        f"{source_policy} Every concept needs at least one exact supplied source reference. "
        "Use only exact source_id and chunk_id pairs supplied in the excerpts. Never browse or invent citations. "
        "Create exactly one start action lasting 60 to 120 seconds with a concrete completion condition. "
        "Candidate gaps remain observations and do not authorize search. "
        f"Goal: {session.get('goal')}. Available minutes: {session.get('available_minutes')}. "
        f"Energy: {session.get('energy_level')}. Coverage: {coverage.model_dump_json()}."
    )


def _generation_source_policy(chunks: list[dict[str, Any]]) -> str:
    if any(chunk.get("source_origin") == "uploaded" for chunk in chunks):
        return "Uploaded material is present and is the primary source; other origins remain labeled supplements."
    return (
        "No uploaded material is present. The supplied AI-generated topic source must remain labeled as an "
        "AI supplemental explanation and must never be described as uploaded or externally cited."
    )


def _start_ai_activity(
    settings: Settings,
    workspace_id: str,
    session_id: str,
    operation: str,
) -> str:
    activity_id = str(uuid.uuid4())
    model = DEMO_MODEL if settings.mode == "demo" else settings.openai_model
    with connect(settings.database_path) as connection:
        connection.execute(
            """
            INSERT INTO ai_activity_logs(
                id, workspace_id, session_id, operation, generation_mode, model, status
            ) VALUES (?, ?, ?, ?, ?, ?, 'running')
            """,
            (activity_id, workspace_id, session_id, operation, settings.mode, model),
        )
    return activity_id


def _finish_ai_activity(
    settings: Settings,
    activity_id: str,
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
            (status, response_id, error_code, activity_id),
        )


def _session_name(goal: str) -> str:
    compact = " ".join(goal.split())
    return compact if len(compact) <= 72 else compact[:69].rstrip() + "…"
