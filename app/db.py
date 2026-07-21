"""SQLite connection and schema initialization."""

from __future__ import annotations

import sqlite3
from pathlib import Path


SCHEMA_VERSION = 9

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
    source_origin TEXT NOT NULL DEFAULT 'uploaded' CHECK(source_origin = 'uploaded'),
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
ALTER TABLE learning_sessions ADD COLUMN search_permission INTEGER NOT NULL DEFAULT 0;
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
    suggested_query_scope TEXT NOT NULL,
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
    source_origin TEXT CHECK(source_origin IN ('uploaded', 'ai_supplement')),
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
    source_origin TEXT NOT NULL CHECK(source_origin IN ('uploaded', 'external', 'ai_supplement')),
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
    source_origin TEXT NOT NULL CHECK(source_origin IN ('uploaded', 'external', 'ai_supplement')),
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
        'insert_prerequisite', 'review_previous', 'request_search', 'finish_session'
    )),
    reason_for_user TEXT NOT NULL,
    estimated_minutes INTEGER NOT NULL CHECK(estimated_minutes BETWEEN 0 AND 45),
    target_concept_id TEXT REFERENCES concepts(id),
    return_to_concept_id TEXT REFERENCES concepts(id),
    required_tool TEXT NOT NULL CHECK(required_tool IN (
        'activate_concept', 'create_activity', 'open_tutor', 'request_search', 'create_summary'
    )),
    confidence REAL NOT NULL CHECK(confidence BETWEEN 0 AND 1),
    generation_mode TEXT NOT NULL CHECK(generation_mode IN ('demo', 'real')),
    model TEXT,
    status TEXT NOT NULL DEFAULT 'proposed' CHECK(status IN ('proposed', 'accepted', 'overridden')),
    selected_action TEXT CHECK(selected_action IN (
        'continue_next', 'retry_current', 'switch_activity', 'simplify_current',
        'insert_prerequisite', 'review_previous', 'request_search', 'finish_session'
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

CONTROLLED_SEARCH_SCHEMA = """
CREATE TABLE search_requests (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
    concept_id TEXT NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    source_gap_id TEXT NOT NULL REFERENCES source_gaps(id) ON DELETE CASCADE,
    agent_decision_id TEXT NOT NULL UNIQUE REFERENCES agent_decisions(id) ON DELETE CASCADE,
    query_scope TEXT NOT NULL,
    reason_for_user TEXT NOT NULL,
    permission_snapshot INTEGER NOT NULL CHECK(permission_snapshot IN (0, 1)),
    confirmation_status TEXT NOT NULL DEFAULT 'pending'
        CHECK(confirmation_status IN ('pending', 'confirmed', 'declined')),
    search_status TEXT NOT NULL DEFAULT 'pending'
        CHECK(search_status IN ('pending', 'running', 'completed', 'failed', 'cancelled', 'ignored')),
    generation_mode TEXT NOT NULL CHECK(generation_mode IN ('demo', 'real')),
    model TEXT,
    response_id TEXT,
    error_code TEXT,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TEXT,
    executed_at TEXT,
    completed_at TEXT
);
CREATE INDEX idx_search_requests_session_created
    ON search_requests(session_id, created_at DESC);

CREATE TABLE external_sources (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
    concept_id TEXT NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    source_gap_id TEXT NOT NULL REFERENCES source_gaps(id) ON DELETE CASCADE,
    search_request_id TEXT NOT NULL REFERENCES search_requests(id) ON DELETE CASCADE,
    canonical_url TEXT NOT NULL,
    title TEXT NOT NULL,
    publisher TEXT NOT NULL,
    accessed_at TEXT NOT NULL,
    selection_reason TEXT NOT NULL,
    citation_excerpt TEXT NOT NULL,
    locator TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'candidate'
        CHECK(status IN ('candidate', 'selected', 'inaccessible', 'ignored')),
    rank INTEGER NOT NULL CHECK(rank BETWEEN 1 AND 10),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    selected_at TEXT,
    UNIQUE(search_request_id, canonical_url)
);
CREATE INDEX idx_external_sources_request_rank
    ON external_sources(search_request_id, rank);

CREATE TABLE concept_external_sources (
    concept_id TEXT NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    external_source_id TEXT NOT NULL UNIQUE REFERENCES external_sources(id) ON DELETE CASCADE,
    attached_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(concept_id, external_source_id)
);
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
            connection.executescript(CONTROLLED_SEARCH_SCHEMA)
            connection.execute("INSERT INTO schema_migrations(version) VALUES (9)")


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
