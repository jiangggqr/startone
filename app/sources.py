"""Source storage, parsing, grounding, and local retrieval."""

from __future__ import annotations

import bisect
import hashlib
import re
import sqlite3
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from app.db import connect


SUPPORTED_EXTENSIONS = {
    ".pdf": ("application/pdf", "pdf"),
    ".md": ("text/markdown", "markdown"),
    ".markdown": ("text/markdown", "markdown"),
    ".txt": ("text/plain", "text"),
}
CHUNK_SIZE = 1800
CHUNK_OVERLAP = 150


class SourceError(Exception):
    def __init__(
        self,
        error_code: str,
        user_message: str,
        *,
        status_code: int = 400,
        recoverable: bool = True,
        saved_state: str = "No new source was saved.",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(user_message)
        self.error_code = error_code
        self.user_message = user_message
        self.status_code = status_code
        self.recoverable = recoverable
        self.saved_state = saved_state
        self.details = details


@dataclass(frozen=True, slots=True)
class ParsedSource:
    chunks: list[dict[str, Any]]
    page_count: int | None
    line_count: int | None
    status: str = "success"
    warning_code: str | None = None
    warning_message: str | None = None


def clean_filename(filename: str | None) -> str:
    candidate = Path(filename or "untitled").name
    candidate = "".join(char for char in candidate if char.isprintable()).strip()
    return (candidate or "untitled")[:180]


def media_for_filename(filename: str) -> tuple[str, str]:
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise SourceError(
            "unsupported_file_type",
            "This file type is not supported. Upload PDF, Markdown, or TXT.",
        )
    return SUPPORTED_EXTENSIONS[extension]


def validate_file_bytes(media_kind: str, data: bytes) -> None:
    if not data:
        raise SourceError("empty_file", "This file is empty. Choose a file that contains learning material.")
    if media_kind == "pdf" and not data.startswith(b"%PDF-"):
        raise SourceError("invalid_pdf", "This file does not contain a valid PDF header.")
    if media_kind != "pdf" and b"\x00" in data[:4096]:
        raise SourceError(
            "invalid_text_file",
            "This file appears to be binary data. Upload UTF-8 Markdown or TXT.",
        )


def create_session(database_path: Path, workspace_id: str, mode: str) -> dict[str, Any]:
    session_id = str(uuid.uuid4())
    with connect(database_path) as connection:
        connection.execute(
            """
            INSERT INTO learning_sessions(id, workspace_id, name, mode)
            VALUES (?, ?, ?, ?)
            """,
            (session_id, workspace_id, "Untitled study session", mode),
        )
    return get_session(database_path, workspace_id, session_id)


def get_session(database_path: Path, workspace_id: str, session_id: str) -> dict[str, Any]:
    with connect(database_path) as connection:
        row = connection.execute(
            """
            SELECT s.*,
                   COUNT(d.id) AS source_count,
                   SUM(CASE WHEN d.parse_status IN ('success', 'partial_success') THEN 1 ELSE 0 END)
                       AS ready_source_count
            FROM learning_sessions s
            LEFT JOIN source_documents d ON d.session_id = s.id
            WHERE s.id = ? AND s.workspace_id = ?
            GROUP BY s.id
            """,
            (session_id, workspace_id),
        ).fetchone()
    if not row:
        raise SourceError(
            "session_not_found",
            "This study session is not available in your workspace.",
            status_code=404,
            saved_state="Your other sessions and sources are unchanged.",
        )
    return dict(row)


def list_sessions(database_path: Path, workspace_id: str) -> list[dict[str, Any]]:
    with connect(database_path) as connection:
        rows = connection.execute(
            """
            SELECT s.*,
                   COUNT(d.id) AS source_count,
                   SUM(CASE WHEN d.parse_status IN ('success', 'partial_success') THEN 1 ELSE 0 END)
                       AS ready_source_count
            FROM learning_sessions s
            LEFT JOIN source_documents d ON d.session_id = s.id
            WHERE s.workspace_id = ?
            GROUP BY s.id
            ORDER BY s.updated_at DESC
            """,
            (workspace_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def store_source(
    database_path: Path,
    upload_dir: Path,
    workspace_id: str,
    session_id: str,
    filename: str,
    media_type: str,
    media_kind: str,
    data: bytes,
) -> dict[str, Any]:
    get_session(database_path, workspace_id, session_id)
    checksum = hashlib.sha256(data).hexdigest()
    workspace_dir = upload_dir / workspace_id
    workspace_dir.mkdir(parents=True, exist_ok=True)

    with connect(database_path) as connection:
        blob = connection.execute(
            "SELECT * FROM source_blobs WHERE workspace_id = ? AND checksum = ?",
            (workspace_id, checksum),
        ).fetchone()
        if blob:
            blob_id = str(blob["id"])
        else:
            blob_id = str(uuid.uuid4())
            storage_path = workspace_dir / f"{blob_id}.bin"
            storage_path.write_bytes(data)
            connection.execute(
                """
                INSERT INTO source_blobs(id, workspace_id, checksum, storage_path, byte_size)
                VALUES (?, ?, ?, ?, ?)
                """,
                (blob_id, workspace_id, checksum, str(storage_path), len(data)),
            )

        source_id = str(uuid.uuid4())
        connection.execute(
            """
            INSERT INTO source_documents(
                id, workspace_id, session_id, blob_id, filename, media_type,
                media_kind, parse_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
            """,
            (source_id, workspace_id, session_id, blob_id, filename, media_type, media_kind),
        )
        _record_event(connection, workspace_id, session_id, source_id, "source_parse_started")
        connection.execute(
            "UPDATE learning_sessions SET state = 'sources_processing', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (session_id,),
        )
    return get_source(database_path, workspace_id, source_id, include_chunks=False)


def process_source(database_path: Path, workspace_id: str, source_id: str) -> None:
    with connect(database_path) as connection:
        source = connection.execute(
            """
            SELECT d.*, b.storage_path
            FROM source_documents d
            JOIN source_blobs b ON b.id = d.blob_id
            WHERE d.id = ? AND d.workspace_id = ?
            """,
            (source_id, workspace_id),
        ).fetchone()
        if not source or source["parse_status"] == "cancelled":
            return
        connection.execute(
            "UPDATE source_documents SET parse_status = 'processing', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (source_id,),
        )

    try:
        path = Path(str(source["storage_path"]))
        if source["media_kind"] == "pdf":
            parsed = parse_pdf(path, source_id)
        else:
            data = path.read_bytes()
            try:
                text = data.decode("utf-8-sig")
            except UnicodeDecodeError as exc:
                raise SourceError(
                    "unsupported_text_encoding",
                    "This text file is not valid UTF-8. Save it as UTF-8 and retry.",
                ) from exc
            if source["media_kind"] == "pasted":
                parsed = parse_pasted(text, source_id, str(source["filename"]))
            else:
                parsed = parse_text(
                    text,
                    source_id,
                    str(source["filename"]),
                    str(source["media_kind"]),
                )

        with connect(database_path) as connection:
            latest = connection.execute(
                "SELECT parse_status, session_id FROM source_documents WHERE id = ? AND workspace_id = ?",
                (source_id, workspace_id),
            ).fetchone()
            if not latest or latest["parse_status"] == "cancelled":
                return
            connection.execute("DELETE FROM source_chunks WHERE source_id = ?", (source_id,))
            for chunk in parsed.chunks:
                connection.execute(
                    """
                    INSERT INTO source_chunks(
                        id, source_id, heading_path, page_number, page_chunk_index,
                        paragraph_number, start_line, end_line, start_char, end_char,
                        text, search_text, checksum
                    ) VALUES (
                        :id, :source_id, :heading_path, :page_number, :page_chunk_index,
                        :paragraph_number, :start_line, :end_line, :start_char, :end_char,
                        :text, :search_text, :checksum
                    )
                    """,
                    chunk,
                )
            connection.execute(
                """
                UPDATE source_documents
                SET parse_status = ?, page_count = ?, line_count = ?, error_code = ?,
                    error_message = ?, version = version + 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    parsed.status,
                    parsed.page_count,
                    parsed.line_count,
                    parsed.warning_code,
                    parsed.warning_message,
                    source_id,
                ),
            )
            _record_event(
                connection,
                workspace_id,
                str(latest["session_id"]),
                source_id,
                "source_parse_completed",
                parsed.warning_code,
            )
            _refresh_session_state(connection, str(latest["session_id"]))
    except SourceError as exc:
        _mark_parse_error(database_path, workspace_id, source_id, exc.error_code, exc.user_message)
    except Exception:
        _mark_parse_error(
            database_path,
            workspace_id,
            source_id,
            "parse_failed",
            "The file could not be parsed. The original upload is saved; retry or remove this file.",
        )


def parse_text(text: str, source_id: str, filename: str, media_kind: str) -> ParsedSource:
    if not text.strip():
        raise SourceError("no_extractable_text", "No readable text was found in this file.")
    line_starts = _line_starts(text)
    heading_stack: list[str] = []
    blocks: list[tuple[int, int, str]] = []
    block_start: int | None = None
    block_end = 0
    block_heading = Path(filename).stem
    block_has_body = False
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+?)\s*$")

    for line_number, start in enumerate(line_starts, start=1):
        end = line_starts[line_number] if line_number < len(line_starts) else len(text)
        visible_end = end
        while visible_end > start and text[visible_end - 1] in "\r\n":
            visible_end -= 1
        line = text[start:visible_end]
        heading_match = heading_pattern.match(line) if media_kind == "markdown" else None
        if heading_match:
            if block_start is not None and text[block_start:block_end].strip():
                blocks.append((block_start, block_end, block_heading))
            level = len(heading_match.group(1))
            heading_stack = heading_stack[: level - 1]
            heading_stack.append(heading_match.group(2).strip())
            block_heading = " > ".join(heading_stack)
            block_start = start
            block_end = visible_end
            block_has_body = False
            continue
        if line.strip():
            if block_start is None:
                block_start = start
            block_end = visible_end
            block_has_body = True
        elif block_start is not None and block_has_body and text[block_start:block_end].strip():
            blocks.append((block_start, block_end, block_heading))
            block_start = None
            block_has_body = False
    if block_start is not None and text[block_start:block_end].strip():
        blocks.append((block_start, block_end, block_heading))

    chunks: list[dict[str, Any]] = []
    for start, end, heading in blocks:
        for piece_start, piece_end in _split_span(text, start, end):
            chunks.append(
                _make_chunk(
                    source_id,
                    text[piece_start:piece_end],
                    heading_path=heading,
                    start_line=_line_at(line_starts, piece_start),
                    end_line=_line_at(line_starts, max(piece_start, piece_end - 1)),
                    start_char=piece_start,
                    end_char=piece_end,
                )
            )
    if not chunks:
        raise SourceError("no_extractable_text", "No readable text was found in this file.")
    return ParsedSource(chunks=chunks, page_count=None, line_count=len(text.splitlines()))


def parse_pasted(text: str, source_id: str, title: str) -> ParsedSource:
    if not text.strip():
        raise SourceError("empty_pasted_text", "Paste some learning material before saving.")
    spans = _paragraph_spans(text)
    chunks: list[dict[str, Any]] = []
    paragraph = 0
    for start, end in spans:
        paragraph += 1
        for piece_start, piece_end in _split_span(text, start, end):
            chunks.append(
                _make_chunk(
                    source_id,
                    text[piece_start:piece_end],
                    heading_path=title,
                    paragraph_number=paragraph,
                    start_char=piece_start,
                    end_char=piece_end,
                )
            )
    return ParsedSource(chunks=chunks, page_count=None, line_count=len(text.splitlines()))


def parse_pdf(path: Path, source_id: str) -> ParsedSource:
    try:
        reader = PdfReader(path)
    except Exception as exc:
        raise SourceError("invalid_pdf", "The PDF could not be opened. Choose another copy and retry.") from exc
    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception as exc:
            raise SourceError("encrypted_pdf", "This PDF is password protected and cannot be parsed.") from exc

    chunks: list[dict[str, Any]] = []
    blank_pages = 0
    for page_number, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        if not text.strip():
            blank_pages += 1
            continue
        page_chunk_index = 0
        for paragraph_start, paragraph_end in _paragraph_spans(text):
            for piece_start, piece_end in _split_span(text, paragraph_start, paragraph_end):
                page_chunk_index += 1
                chunks.append(
                    _make_chunk(
                        source_id,
                        text[piece_start:piece_end],
                        page_number=page_number,
                        page_chunk_index=page_chunk_index,
                        start_char=piece_start,
                        end_char=piece_end,
                    )
                )
    if not chunks:
        raise SourceError(
            "no_extractable_text",
            "No selectable text was found in this PDF. Use a text-based PDF or add OCR before retrying.",
        )
    if blank_pages:
        return ParsedSource(
            chunks=chunks,
            page_count=len(reader.pages),
            line_count=None,
            status="partial_success",
            warning_code="pages_without_text",
            warning_message=f"Parsed readable pages; {blank_pages} page(s) contained no selectable text.",
        )
    return ParsedSource(chunks=chunks, page_count=len(reader.pages), line_count=None)


def get_source(
    database_path: Path,
    workspace_id: str,
    source_id: str,
    *,
    include_chunks: bool = True,
) -> dict[str, Any]:
    with connect(database_path) as connection:
        row = connection.execute(
            """
            SELECT d.*, b.byte_size, b.checksum,
                   COUNT(c.id) AS chunk_count
            FROM source_documents d
            JOIN source_blobs b ON b.id = d.blob_id
            LEFT JOIN source_chunks c ON c.source_id = d.id
            WHERE d.id = ? AND d.workspace_id = ?
            GROUP BY d.id
            """,
            (source_id, workspace_id),
        ).fetchone()
        if not row:
            raise SourceError(
                "source_not_found",
                "This source is not available in your workspace.",
                status_code=404,
                saved_state="Your session and other sources are unchanged.",
            )
        result = dict(row)
        if include_chunks:
            chunks = connection.execute(
                "SELECT * FROM source_chunks WHERE source_id = ? ORDER BY rowid",
                (source_id,),
            ).fetchall()
            result["chunks"] = [dict(chunk) for chunk in chunks]
    return result


def list_sources(database_path: Path, workspace_id: str, session_id: str) -> list[dict[str, Any]]:
    get_session(database_path, workspace_id, session_id)
    with connect(database_path) as connection:
        rows = connection.execute(
            """
            SELECT d.*, b.byte_size, b.checksum, COUNT(c.id) AS chunk_count
            FROM source_documents d
            JOIN source_blobs b ON b.id = d.blob_id
            LEFT JOIN source_chunks c ON c.source_id = d.id
            WHERE d.session_id = ? AND d.workspace_id = ?
            GROUP BY d.id
            ORDER BY d.created_at
            """,
            (session_id, workspace_id),
        ).fetchall()
    return [dict(row) for row in rows]


def retry_source(database_path: Path, workspace_id: str, source_id: str) -> dict[str, Any]:
    source = get_source(database_path, workspace_id, source_id, include_chunks=False)
    with connect(database_path) as connection:
        connection.execute(
            """
            UPDATE source_documents
            SET parse_status = 'pending', error_code = NULL, error_message = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (source_id,),
        )
        _record_event(
            connection,
            workspace_id,
            str(source["session_id"]),
            source_id,
            "source_parse_started",
            "retry",
        )
    return get_source(database_path, workspace_id, source_id, include_chunks=False)


def cancel_source(database_path: Path, workspace_id: str, source_id: str) -> dict[str, Any]:
    source = get_source(database_path, workspace_id, source_id, include_chunks=False)
    if source["parse_status"] not in {"pending", "processing"}:
        raise SourceError(
            "source_not_processing",
            "This source has already finished processing.",
            status_code=409,
            saved_state="The parsed source remains available.",
        )
    with connect(database_path) as connection:
        connection.execute(
            "UPDATE source_documents SET parse_status = 'cancelled', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (source_id,),
        )
    return get_source(database_path, workspace_id, source_id, include_chunks=False)


def delete_source(database_path: Path, workspace_id: str, source_id: str) -> None:
    source = get_source(database_path, workspace_id, source_id, include_chunks=False)
    blob_id = str(source["blob_id"])
    with connect(database_path) as connection:
        blob = connection.execute(
            "SELECT storage_path FROM source_blobs WHERE id = ? AND workspace_id = ?",
            (blob_id, workspace_id),
        ).fetchone()
        connection.execute("DELETE FROM source_documents WHERE id = ?", (source_id,))
        remaining = connection.execute(
            "SELECT COUNT(*) AS count FROM source_documents WHERE blob_id = ?",
            (blob_id,),
        ).fetchone()
        if remaining and int(remaining["count"]) == 0:
            connection.execute("DELETE FROM source_blobs WHERE id = ?", (blob_id,))
            if blob:
                Path(str(blob["storage_path"])).unlink(missing_ok=True)
        _refresh_session_state(connection, str(source["session_id"]))


def search_chunks(
    database_path: Path,
    workspace_id: str,
    session_id: str,
    query: str,
    limit: int = 8,
) -> list[dict[str, Any]]:
    get_session(database_path, workspace_id, session_id)
    terms = [term.lower() for term in re.findall(r"[\w-]+", query, flags=re.UNICODE) if len(term) > 1]
    if not terms:
        return []
    conditions = " OR ".join("c.search_text LIKE ?" for _ in terms)
    params: list[Any] = [session_id, workspace_id, *[f"%{term}%" for term in terms], limit]
    with connect(database_path) as connection:
        rows = connection.execute(
            f"""
            SELECT c.*, d.filename, d.media_kind, d.source_origin
            FROM source_chunks c
            JOIN source_documents d ON d.id = c.source_id
            WHERE d.session_id = ? AND d.workspace_id = ? AND ({conditions})
            ORDER BY c.source_id, c.rowid
            LIMIT ?
            """,
            params,
        ).fetchall()
    return [dict(row) for row in rows]


def _make_chunk(
    source_id: str,
    text: str,
    *,
    heading_path: str | None = None,
    page_number: int | None = None,
    page_chunk_index: int | None = None,
    paragraph_number: int | None = None,
    start_line: int | None = None,
    end_line: int | None = None,
    start_char: int,
    end_char: int,
) -> dict[str, Any]:
    checksum = hashlib.sha256(text.encode("utf-8")).hexdigest()
    locator = ":".join(
        str(value)
        for value in (
            heading_path,
            page_number,
            page_chunk_index,
            paragraph_number,
            start_line,
            end_line,
            start_char,
            end_char,
            checksum,
        )
    )
    return {
        "id": str(uuid.uuid5(uuid.UUID(source_id), locator)),
        "source_id": source_id,
        "heading_path": heading_path,
        "page_number": page_number,
        "page_chunk_index": page_chunk_index,
        "paragraph_number": paragraph_number,
        "start_line": start_line,
        "end_line": end_line,
        "start_char": start_char,
        "end_char": end_char,
        "text": text,
        "search_text": " ".join(text.lower().split()),
        "checksum": checksum,
    }


def _split_span(text: str, start: int, end: int) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    cursor = start
    while cursor < end:
        piece_end = min(end, cursor + CHUNK_SIZE)
        if piece_end < end:
            natural_break = max(
                text.rfind("\n", cursor + CHUNK_SIZE // 2, piece_end),
                text.rfind(" ", cursor + CHUNK_SIZE // 2, piece_end),
            )
            if natural_break > cursor:
                piece_end = natural_break
        spans.append((cursor, piece_end))
        if piece_end >= end:
            break
        cursor = max(cursor + 1, piece_end - CHUNK_OVERLAP)
    return spans


def _paragraph_spans(text: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    cursor = 0
    for separator in re.finditer(r"(?:\r?\n)[\t ]*(?:\r?\n)+", text):
        start, end = _trim_span(text, cursor, separator.start())
        if start < end:
            spans.append((start, end))
        cursor = separator.end()
    start, end = _trim_span(text, cursor, len(text))
    if start < end:
        spans.append((start, end))
    return spans


def _trim_span(text: str, start: int, end: int) -> tuple[int, int]:
    while start < end and text[start].isspace():
        start += 1
    while end > start and text[end - 1].isspace():
        end -= 1
    return start, end


def _line_starts(text: str) -> list[int]:
    starts = [0]
    starts.extend(match.end() for match in re.finditer(r"\n", text))
    if starts[-1] == len(text):
        starts.pop()
    return starts or [0]


def _line_at(line_starts: list[int], position: int) -> int:
    return bisect.bisect_right(line_starts, position)


def _record_event(
    connection: sqlite3.Connection,
    workspace_id: str,
    session_id: str,
    source_id: str,
    event_type: str,
    detail_code: str | None = None,
) -> None:
    connection.execute(
        """
        INSERT INTO source_events(id, workspace_id, session_id, source_id, event_type, detail_code)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (str(uuid.uuid4()), workspace_id, session_id, source_id, event_type, detail_code),
    )


def _mark_parse_error(
    database_path: Path,
    workspace_id: str,
    source_id: str,
    error_code: str,
    message: str,
) -> None:
    with connect(database_path) as connection:
        source = connection.execute(
            "SELECT session_id, parse_status FROM source_documents WHERE id = ? AND workspace_id = ?",
            (source_id, workspace_id),
        ).fetchone()
        if not source or source["parse_status"] == "cancelled":
            return
        connection.execute(
            """
            UPDATE source_documents
            SET parse_status = 'error', error_code = ?, error_message = ?,
                version = version + 1, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (error_code, message, source_id),
        )
        _record_event(
            connection,
            workspace_id,
            str(source["session_id"]),
            source_id,
            "source_parse_failed",
            error_code,
        )
        _refresh_session_state(connection, str(source["session_id"]))


def _refresh_session_state(connection: sqlite3.Connection, session_id: str) -> None:
    statuses = [
        str(row["parse_status"])
        for row in connection.execute(
            "SELECT parse_status FROM source_documents WHERE session_id = ?",
            (session_id,),
        )
    ]
    if not statuses:
        state = "session_created"
    elif any(status in {"pending", "processing"} for status in statuses):
        state = "sources_processing"
    elif any(status in {"success", "partial_success"} for status in statuses):
        state = "sources_reviewable"
    else:
        state = "sources_reviewable"
    connection.execute(
        "UPDATE learning_sessions SET state = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (state, session_id),
    )
