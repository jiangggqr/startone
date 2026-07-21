"""SQLite connection and schema initialization."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 12

SOURCE_SCHEMA = """
CREATE TABLE IF NOT EXISTS workspaces (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_version INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS learning_sessions (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'session_created',
    mode TEXT NOT NULL CHECK(mode IN ('demo', 'real')),
    version INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_sessions_workspace_updated
    ON learning_sessions(workspace_id, updated_at DESC);

CREATE TABLE IF NOT EXISTS source_blobs (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    checksum TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    byte_size INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(workspace_id, checksum)
);

CREATE TABLE IF NOT EXISTS source_documents (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
    blob_id TEXT NOT NULL REFERENCES source_blobs(id),
    filename TEXT NOT NULL,
    media_type TEXT NOT NULL,
    media_kind TEXT NOT NULL CHECK(media_kind IN ('pdf', 'markdown', 'text', 'pasted')),
    source_origin TEXT NOT NULL DEFAULT 'uploaded'
        CHECK(source_origin = 'uploaded'),
    parse_status TEXT NOT NULL,
    page_count INTEGER,
    line_count INTEGER,
    error_code TEXT,
    error_message TEXT,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_sources_session_created
    ON source_documents(session_id, created_at);

CREATE TABLE IF NOT EXISTS source_chunks (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL REFERENCES source_documents(id) ON DELETE CASCADE,
    heading_path TEXT,
    page_number INTEGER,
    page_chunk_index INTEGER,
    paragraph_number INTEGER,
    start_line INTEGER,
    end_line INTEGER,
    start_char INTEGER NOT NULL,
    end_char INTEGER NOT NULL,
    text TEXT NOT NULL,
    search_text TEXT NOT NULL,
    checksum TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_chunks_source ON source_chunks(source_id);
CREATE INDEX IF NOT EXISTS idx_chunks_checksum ON source_chunks(checksum);

CREATE TABLE IF NOT EXISTS source_events (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
    source_id TEXT REFERENCES source_documents(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    detail_code TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

LEARNING_PATH_SCHEMA = """
ALTER TABLE learning_sessions ADD COLUMN goal TEXT;
ALTER TABLE learning_sessions ADD COLUMN prior_knowledge TEXT;
ALTER TABLE learning_sessions ADD COLUMN available_minutes INTEGER;
ALTER TABLE learning_sessions ADD COLUMN energy_level TEXT;
ALTER TABLE learning_sessions ADD COLUMN language TEXT NOT NULL DEFAULT 'English';
ALTER TABLE learning_sessions ADD COLUMN current_question TEXT;
ALTER TABLE learning_sessions ADD COLUMN support_preferences_json TEXT NOT NULL DEFAULT '[]';
ALTER TABLE learning_sessions ADD COLUMN show_timer INTEGER NOT NULL DEFAULT 0;
ALTER TABLE learning_sessions ADD COLUMN setup_completed INTEGER NOT NULL DEFAULT 0;

CREATE TABLE source_coverages (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL UNIQUE REFERENCES learning_sessions(id) ON DELETE CASCADE,
    output_json TEXT NOT NULL,
    generation_mode TEXT NOT NULL CHECK(generation_mode IN ('demo', 'real')),
    model TEXT,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE source_gaps (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
    concept_key TEXT,
    description TEXT NOT NULL,
    why_needed TEXT NOT NULL,
    evidence TEXT NOT NULL,
    current_source_refs_json TEXT NOT NULL,
    requested_material TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'candidate'
        CHECK(status IN ('candidate', 'validated', 'resolved', 'dismissed')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TEXT
);
CREATE INDEX idx_source_gaps_session_status
    ON source_gaps(session_id, status);

CREATE TABLE knowledge_maps (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL UNIQUE REFERENCES learning_sessions(id) ON DELETE CASCADE,
    output_json TEXT NOT NULL,
    generation_mode TEXT NOT NULL CHECK(generation_mode IN ('demo', 'real')),
    model TEXT,
    version INTEGER NOT NULL DEFAULT 1,
    confirmed_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE concepts (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
    concept_key TEXT NOT NULL,
    title TEXT NOT NULL,
    plain_definition TEXT NOT NULL,
    role_in_map TEXT NOT NULL,
    prerequisite_keys_json TEXT NOT NULL,
    order_index INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'planned',
    estimated_minutes INTEGER NOT NULL,
    source_refs_json TEXT NOT NULL,
    UNIQUE(session_id, concept_key)
);
CREATE INDEX idx_concepts_session_order
    ON concepts(session_id, order_index);

CREATE TABLE ai_activity_logs (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
    operation TEXT NOT NULL,
    generation_mode TEXT NOT NULL CHECK(generation_mode IN ('demo', 'real')),
    model TEXT,
    status TEXT NOT NULL,
    response_id TEXT,
    error_code TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TEXT
);
CREATE INDEX idx_ai_activity_session_created
    ON ai_activity_logs(session_id, created_at);
"""

FOCUS_WORKSPACE_SCHEMA = """
ALTER TABLE learning_sessions ADD COLUMN resume_state TEXT;
ALTER TABLE learning_sessions ADD COLUMN is_paused INTEGER NOT NULL DEFAULT 0;
ALTER TABLE learning_sessions ADD COLUMN active_concept_id TEXT;
ALTER TABLE learning_sessions ADD COLUMN active_activity_id TEXT;
ALTER TABLE learning_sessions ADD COLUMN timer_started_at TEXT;
ALTER TABLE learning_sessions ADD COLUMN elapsed_seconds INTEGER NOT NULL DEFAULT 0;
ALTER TABLE learning_sessions ADD COLUMN remaining_seconds INTEGER;
ALTER TABLE learning_sessions ADD COLUMN started_at TEXT;
ALTER TABLE learning_sessions ADD COLUMN last_saved_at TEXT;
ALTER TABLE learning_sessions ADD COLUMN ended_at TEXT;

CREATE TABLE drafts (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
    activity_id TEXT,
    draft_type TEXT NOT NULL,
    content TEXT NOT NULL,
    hint_depth INTEGER NOT NULL DEFAULT 0,
    server_version INTEGER NOT NULL DEFAULT 1,
    sync_status TEXT NOT NULL DEFAULT 'saved',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, draft_type)
);
CREATE INDEX idx_drafts_session_updated
    ON drafts(session_id, updated_at DESC);

CREATE TABLE session_events (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    detail_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_session_events_session_created
    ON session_events(session_id, created_at);
"""

TUTOR_SCHEMA = """
ALTER TABLE learning_sessions ADD COLUMN tutor_open INTEGER NOT NULL DEFAULT 0;

CREATE TABLE tutor_threads (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
    concept_id TEXT NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open', 'closed')),
    version INTEGER NOT NULL DEFAULT 1,
    last_guidance_level INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closed_at TEXT,
    UNIQUE(session_id, concept_id)
);
CREATE INDEX idx_tutor_threads_session_concept
    ON tutor_threads(session_id, concept_id, status, updated_at DESC);

CREATE TABLE tutor_messages (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
    thread_id TEXT NOT NULL REFERENCES tutor_threads(id) ON DELETE CASCADE,
    concept_id TEXT NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK(role IN ('user', 'tutor')),
    message TEXT NOT NULL,
    quick_action TEXT,
    guidance_level INTEGER NOT NULL DEFAULT 0,
    checking_question TEXT,
    source_origin TEXT CHECK(source_origin = 'uploaded'),
    source_refs_json TEXT NOT NULL DEFAULT '[]',
    confusion_signal TEXT,
    prerequisite_gap_signal TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_tutor_messages_thread_created
    ON tutor_messages(thread_id, created_at, id);
"""

ACTIVITY_SCHEMA = """
CREATE TABLE activities (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
    concept_id TEXT NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    type TEXT NOT NULL CHECK(type IN ('quiz', 'recall', 'remedial')),
    prompt TEXT NOT NULL,
    output_json TEXT NOT NULL,
    source_origin TEXT NOT NULL CHECK(source_origin = 'uploaded'),
    source_refs_json TEXT NOT NULL,
    generation_mode TEXT NOT NULL CHECK(generation_mode IN ('demo', 'real')),
    model TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'submitted', 'closed')),
    hint_depth INTEGER NOT NULL DEFAULT 0 CHECK(hint_depth BETWEEN 0 AND 3),
    version INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    submitted_at TEXT,
    closed_at TEXT
);
CREATE INDEX idx_activities_session_created
    ON activities(session_id, created_at DESC);

CREATE TABLE attempts (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
    activity_id TEXT NOT NULL UNIQUE REFERENCES activities(id) ON DELETE CASCADE,
    raw_answer TEXT,
    selected_option_id TEXT,
    hint_depth INTEGER NOT NULL CHECK(hint_depth BETWEEN 0 AND 3),
    elapsed_seconds INTEGER NOT NULL DEFAULT 0,
    submitted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_attempts_session_submitted
    ON attempts(session_id, submitted_at DESC);
"""

MASTERY_SCHEMA = """
ALTER TABLE activities ADD COLUMN parent_activity_id TEXT REFERENCES activities(id);
ALTER TABLE activities ADD COLUMN strategy TEXT;
ALTER TABLE activities ADD COLUMN remedial_round INTEGER NOT NULL DEFAULT 0;
ALTER TABLE tutor_threads ADD COLUMN last_evidence_message_rowid INTEGER NOT NULL DEFAULT 0;

CREATE TABLE feedbacks (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
    concept_id TEXT NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    activity_id TEXT NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    attempt_id TEXT NOT NULL UNIQUE REFERENCES attempts(id) ON DELETE CASCADE,
    output_json TEXT NOT NULL,
    source_origin TEXT NOT NULL CHECK(source_origin = 'uploaded'),
    source_refs_json TEXT NOT NULL,
    generation_mode TEXT NOT NULL CHECK(generation_mode IN ('demo', 'real')),
    model TEXT,
    status TEXT NOT NULL DEFAULT 'shown' CHECK(status IN ('shown', 'completed')),
    version INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TEXT
);
CREATE INDEX idx_feedbacks_session_created
    ON feedbacks(session_id, created_at DESC);

ALTER TABLE activities ADD COLUMN parent_feedback_id TEXT REFERENCES feedbacks(id);

CREATE TABLE learning_evidence (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
    concept_id TEXT NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    activity_id TEXT REFERENCES activities(id) ON DELETE CASCADE,
    attempt_id TEXT REFERENCES attempts(id) ON DELETE CASCADE,
    origin_id TEXT NOT NULL,
    activity_type TEXT NOT NULL CHECK(activity_type IN ('tutor_check', 'quiz', 'recall', 'remedial')),
    outcome TEXT NOT NULL CHECK(outcome IN ('mastered', 'partial', 'needs_support', 'unresolved')),
    key_point_coverage_json TEXT NOT NULL DEFAULT '[]',
    misconception_tags_json TEXT NOT NULL DEFAULT '[]',
    hint_depth INTEGER NOT NULL DEFAULT 0 CHECK(hint_depth BETWEEN 0 AND 7),
    elapsed_seconds INTEGER NOT NULL DEFAULT 0,
    tutor_confusion_signals_json TEXT NOT NULL DEFAULT '[]',
    remedial_result TEXT CHECK(remedial_result IN ('improved', 'not_improved')),
    source_gap_signal TEXT,
    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(workspace_id, origin_id)
);
CREATE INDEX idx_learning_evidence_session_time
    ON learning_evidence(session_id, timestamp DESC);
"""

AGENT_SCHEMA = """
CREATE TABLE agent_decisions (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
    concept_id TEXT NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    evidence_fingerprint TEXT NOT NULL,
    evidence_snapshot_json TEXT NOT NULL,
    action TEXT NOT NULL CHECK(action IN (
        'continue_next', 'retry_current', 'switch_activity', 'simplify_current',
        'insert_prerequisite', 'review_previous', 'request_more_material', 'finish_session'
    )),
    reason_for_user TEXT NOT NULL,
    estimated_minutes INTEGER NOT NULL CHECK(estimated_minutes BETWEEN 0 AND 45),
    target_concept_id TEXT REFERENCES concepts(id),
    return_to_concept_id TEXT REFERENCES concepts(id),
    required_tool TEXT NOT NULL CHECK(required_tool IN (
        'activate_concept', 'create_activity', 'open_tutor', 'open_material_upload', 'create_summary'
    )),
    confidence REAL NOT NULL CHECK(confidence BETWEEN 0 AND 1),
    generation_mode TEXT NOT NULL CHECK(generation_mode IN ('demo', 'real')),
    model TEXT,
    status TEXT NOT NULL DEFAULT 'proposed' CHECK(status IN ('proposed', 'accepted', 'overridden')),
    selected_action TEXT CHECK(selected_action IN (
        'continue_next', 'retry_current', 'switch_activity', 'simplify_current',
        'insert_prerequisite', 'review_previous', 'request_more_material', 'finish_session'
    )),
    override_reason TEXT,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TEXT,
    UNIQUE(session_id, evidence_fingerprint)
);
CREATE INDEX idx_agent_decisions_session_created
    ON agent_decisions(session_id, created_at DESC);

CREATE TABLE learning_detours (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
    decision_id TEXT NOT NULL REFERENCES agent_decisions(id) ON DELETE CASCADE,
    kind TEXT NOT NULL CHECK(kind IN ('prerequisite', 'review')),
    detour_concept_id TEXT NOT NULL REFERENCES concepts(id),
    return_concept_id TEXT NOT NULL REFERENCES concepts(id),
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'returned')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    returned_at TEXT
);
CREATE INDEX idx_learning_detours_session_status
    ON learning_detours(session_id, status, created_at DESC);
"""

SOURCE_REPORT_SCHEMA = """
CREATE TABLE source_reference_reports (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
    source_id TEXT NOT NULL REFERENCES source_documents(id) ON DELETE CASCADE,
    chunk_id TEXT NOT NULL REFERENCES source_chunks(id) ON DELETE CASCADE,
    reason TEXT NOT NULL CHECK(reason IN ('location_incorrect', 'content_mismatch', 'other')),
    note TEXT,
    status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open', 'reviewed', 'resolved')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_source_reports_workspace_created
    ON source_reference_reports(workspace_id, created_at DESC);
"""


def connect(database_path: Path) -> sqlite3.Connection:
    """Open a configured SQLite connection with safety pragmas enabled."""

    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    return connection


def initialize_database(database_path: Path) -> None:
    """Create the database and record the current schema version."""

    database_path.parent.mkdir(parents=True, exist_ok=True)
    with connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        applied = {
            int(row["version"])
            for row in connection.execute("SELECT version FROM schema_migrations")
        }
        if 1 not in applied:
            connection.execute("INSERT INTO schema_migrations(version) VALUES (1)")
        if 2 not in applied:
            connection.executescript(SOURCE_SCHEMA)
            connection.execute("INSERT INTO schema_migrations(version) VALUES (2)")
        if 3 not in applied:
            connection.executescript(LEARNING_PATH_SCHEMA)
            connection.execute("INSERT INTO schema_migrations(version) VALUES (3)")
        if 4 not in applied:
            connection.executescript(FOCUS_WORKSPACE_SCHEMA)
            connection.execute("INSERT INTO schema_migrations(version) VALUES (4)")
        if 5 not in applied:
            connection.executescript(TUTOR_SCHEMA)
            connection.execute("INSERT INTO schema_migrations(version) VALUES (5)")
        if 6 not in applied:
            connection.executescript(ACTIVITY_SCHEMA)
            connection.execute("INSERT INTO schema_migrations(version) VALUES (6)")
        if 7 not in applied:
            connection.executescript(MASTERY_SCHEMA)
            connection.execute("INSERT INTO schema_migrations(version) VALUES (7)")
        if 8 not in applied:
            connection.executescript(AGENT_SCHEMA)
            connection.execute("INSERT INTO schema_migrations(version) VALUES (8)")
        if 9 not in applied:
            connection.execute("INSERT INTO schema_migrations(version) VALUES (9)")
        if 10 not in applied:
            _migrate_source_origin_constraint(connection)
            connection.execute("INSERT INTO schema_migrations(version) VALUES (10)")
        if 11 not in applied:
            connection.executescript(SOURCE_REPORT_SCHEMA)
            connection.execute("INSERT INTO schema_migrations(version) VALUES (11)")
        if 12 not in applied:
            _migrate_uploaded_material_only(connection)
            connection.execute("INSERT INTO schema_migrations(version) VALUES (12)")
        # A process restart cannot resume an in-flight synchronous model call.
        # Close stale records so the saved session returns to an honest,
        # retryable state instead of appearing to analyze forever.
        activity_table = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'ai_activity_logs'"
        ).fetchone()
        if activity_table:
            connection.execute(
                """
                UPDATE ai_activity_logs
                SET status = 'failed', error_code = 'operation_interrupted',
                    completed_at = CURRENT_TIMESTAMP
                WHERE status = 'running'
                """
            )


def _migrate_source_origin_constraint(connection: sqlite3.Connection) -> None:
    """Keep the legacy migration slot without widening the source boundary."""

    row = connection.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'source_documents'"
    ).fetchone()
    if not row or "CHECK(source_origin = 'uploaded')" in str(row["sql"]):
        return

    # Rows created by retired topic-only or supplemental-source flows cannot
    # remain learning sources under the uploaded-material-only boundary.
    connection.execute(
        "DELETE FROM source_documents WHERE source_origin <> 'uploaded'"
    )
    connection.commit()
    connection.execute("PRAGMA foreign_keys = OFF")
    try:
        connection.executescript(
            """
            CREATE TABLE source_documents_v10 (
                id TEXT PRIMARY KEY,
                workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
                session_id TEXT NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
                blob_id TEXT NOT NULL REFERENCES source_blobs(id),
                filename TEXT NOT NULL,
                media_type TEXT NOT NULL,
                media_kind TEXT NOT NULL CHECK(media_kind IN ('pdf', 'markdown', 'text', 'pasted')),
                source_origin TEXT NOT NULL DEFAULT 'uploaded'
                    CHECK(source_origin = 'uploaded'),
                parse_status TEXT NOT NULL,
                page_count INTEGER,
                line_count INTEGER,
                error_code TEXT,
                error_message TEXT,
                version INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            INSERT INTO source_documents_v10(
                id, workspace_id, session_id, blob_id, filename, media_type,
                media_kind, source_origin, parse_status, page_count, line_count,
                error_code, error_message, version, created_at, updated_at
            )
            SELECT id, workspace_id, session_id, blob_id, filename, media_type,
                   media_kind, source_origin, parse_status, page_count, line_count,
                   error_code, error_message, version, created_at, updated_at
            FROM source_documents;
            DROP TABLE source_documents;
            ALTER TABLE source_documents_v10 RENAME TO source_documents;
            CREATE INDEX idx_sources_session_created
                ON source_documents(session_id, created_at);
            """
        )
        violations = connection.execute("PRAGMA foreign_key_check").fetchall()
        if violations:
            raise RuntimeError("Source-origin migration produced invalid foreign-key references.")
        connection.commit()
    finally:
        connection.execute("PRAGMA foreign_keys = ON")


def _migrate_uploaded_material_only(connection: sqlite3.Connection) -> None:
    """Remove the retired web-search surface and migrate its Agent action safely."""

    _migrate_source_origin_constraint(connection)
    connection.commit()
    connection.execute("PRAGMA foreign_keys = OFF")
    try:
        connection.executescript(
            """
            DROP TABLE IF EXISTS concept_external_sources;
            DROP TABLE IF EXISTS external_sources;
            DROP TABLE IF EXISTS search_requests;
            """
        )

        session_columns = {
            str(row["name"])
            for row in connection.execute("PRAGMA table_info(learning_sessions)")
        }
        if {"state", "resume_state", "updated_at"} <= session_columns:
            connection.execute(
                """
                UPDATE learning_sessions
                SET state = 'learning_concept',
                    resume_state = CASE
                        WHEN resume_state IN ('search_confirmation', 'search_running', 'search_results')
                        THEN 'learning_concept' ELSE resume_state END,
                    updated_at = CURRENT_TIMESTAMP
                WHERE state IN ('search_confirmation', 'search_running', 'search_results')
                """
            )

        gap_columns = {
            str(row["name"])
            for row in connection.execute("PRAGMA table_info(source_gaps)")
        }
        if "suggested_query_scope" in gap_columns and "requested_material" not in gap_columns:
            connection.execute(
                "ALTER TABLE source_gaps RENAME COLUMN suggested_query_scope TO requested_material"
            )

        _migrate_json_payload_column(
            connection, "source_coverages", "output_json"
        )
        _migrate_json_payload_column(
            connection, "knowledge_maps", "output_json"
        )
        _migrate_json_payload_column(
            connection, "agent_decisions", "evidence_snapshot_json"
        )

        decision_sql = connection.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'agent_decisions'"
        ).fetchone()
        if decision_sql and "request_more_material" not in str(decision_sql["sql"]):
            connection.executescript(
                """
                CREATE TABLE agent_decisions_v12 (
                    id TEXT PRIMARY KEY,
                    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
                    session_id TEXT NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
                    concept_id TEXT NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
                    evidence_fingerprint TEXT NOT NULL,
                    evidence_snapshot_json TEXT NOT NULL,
                    action TEXT NOT NULL CHECK(action IN (
                        'continue_next', 'retry_current', 'switch_activity', 'simplify_current',
                        'insert_prerequisite', 'review_previous', 'request_more_material', 'finish_session'
                    )),
                    reason_for_user TEXT NOT NULL,
                    estimated_minutes INTEGER NOT NULL CHECK(estimated_minutes BETWEEN 0 AND 45),
                    target_concept_id TEXT REFERENCES concepts(id),
                    return_to_concept_id TEXT REFERENCES concepts(id),
                    required_tool TEXT NOT NULL CHECK(required_tool IN (
                        'activate_concept', 'create_activity', 'open_tutor', 'open_material_upload', 'create_summary'
                    )),
                    confidence REAL NOT NULL CHECK(confidence BETWEEN 0 AND 1),
                    generation_mode TEXT NOT NULL CHECK(generation_mode IN ('demo', 'real')),
                    model TEXT,
                    status TEXT NOT NULL DEFAULT 'proposed' CHECK(status IN ('proposed', 'accepted', 'overridden')),
                    selected_action TEXT CHECK(selected_action IN (
                        'continue_next', 'retry_current', 'switch_activity', 'simplify_current',
                        'insert_prerequisite', 'review_previous', 'request_more_material', 'finish_session'
                    )),
                    override_reason TEXT,
                    version INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TEXT,
                    UNIQUE(session_id, evidence_fingerprint)
                );
                INSERT INTO agent_decisions_v12(
                    id, workspace_id, session_id, concept_id, evidence_fingerprint,
                    evidence_snapshot_json, action, reason_for_user, estimated_minutes,
                    target_concept_id, return_to_concept_id, required_tool, confidence,
                    generation_mode, model, status, selected_action, override_reason,
                    version, created_at, resolved_at
                )
                SELECT
                    id, workspace_id, session_id, concept_id, evidence_fingerprint,
                    evidence_snapshot_json,
                    CASE WHEN action = 'request_search' THEN 'request_more_material' ELSE action END,
                    reason_for_user, estimated_minutes, target_concept_id, return_to_concept_id,
                    CASE WHEN required_tool = 'request_search' THEN 'open_material_upload' ELSE required_tool END,
                    confidence, generation_mode, model, status,
                    CASE WHEN selected_action = 'request_search' THEN 'request_more_material' ELSE selected_action END,
                    override_reason, version, created_at, resolved_at
                FROM agent_decisions;
                DROP TABLE agent_decisions;
                ALTER TABLE agent_decisions_v12 RENAME TO agent_decisions;
                CREATE INDEX idx_agent_decisions_session_created
                    ON agent_decisions(session_id, created_at DESC);
                """
            )

        if "search_permission" in session_columns:
            connection.execute("ALTER TABLE learning_sessions DROP COLUMN search_permission")

        violations = connection.execute("PRAGMA foreign_key_check").fetchall()
        if violations:
            raise RuntimeError("Uploaded-material-only migration produced invalid foreign-key references.")
        connection.commit()
    finally:
        connection.execute("PRAGMA foreign_keys = ON")


def _migrate_json_payload_column(
    connection: sqlite3.Connection,
    table: str,
    column: str,
) -> None:
    table_exists = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table,),
    ).fetchone()
    if not table_exists:
        return
    columns = {
        str(row["name"])
        for row in connection.execute(f"PRAGMA table_info({table})")
    }
    if column not in columns:
        return
    for row in connection.execute(
        f"SELECT rowid AS record_rowid, {column} AS payload FROM {table}"
    ).fetchall():
        try:
            payload = json.loads(str(row["payload"]))
        except (TypeError, ValueError):
            continue
        migrated = _rewrite_legacy_material_boundary(payload)
        if migrated != payload:
            connection.execute(
                f"UPDATE {table} SET {column} = ? WHERE rowid = ?",
                (json.dumps(migrated), row["record_rowid"]),
            )


def _rewrite_legacy_material_boundary(
    value: Any,
    *,
    parent_key: str | None = None,
) -> Any:
    if isinstance(value, dict):
        migrated: dict[str, Any] = {}
        for key, child in value.items():
            new_key = {
                "suggested_query_scope": "requested_material",
                "request_search": "request_more_material",
            }.get(str(key), str(key))
            migrated[new_key] = _rewrite_legacy_material_boundary(
                child,
                parent_key=new_key,
            )
        return migrated
    if isinstance(value, list):
        return [
            _rewrite_legacy_material_boundary(item, parent_key=parent_key)
            for item in value
        ]
    if value == "request_search":
        return (
            "open_material_upload"
            if parent_key == "required_tool"
            else "request_more_material"
        )
    return value


def ensure_workspace(database_path: Path, workspace_id: str) -> None:
    """Create or touch an anonymous workspace."""

    with connect(database_path) as connection:
        connection.execute(
            """
            INSERT INTO workspaces(id) VALUES (?)
            ON CONFLICT(id) DO UPDATE SET last_seen_at = CURRENT_TIMESTAMP
            """,
            (workspace_id,),
        )


def current_schema_version(database_path: Path) -> int:
    """Return the latest applied schema version."""

    with connect(database_path) as connection:
        row = connection.execute(
            "SELECT COALESCE(MAX(version), 0) AS version FROM schema_migrations"
        ).fetchone()
    return int(row["version"] if row else 0)
