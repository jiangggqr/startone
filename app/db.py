"""SQLite connection and schema initialization."""

from __future__ import annotations

import sqlite3
from pathlib import Path


SCHEMA_VERSION = 2

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
