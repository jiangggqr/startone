"""SQLite connection and schema initialization."""

from __future__ import annotations

import sqlite3
from pathlib import Path


SCHEMA_VERSION = 5

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
