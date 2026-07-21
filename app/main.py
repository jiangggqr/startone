"""FastAPI entry point for StartFrame Agent."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncIterator, Callable, Literal
import uuid

from fastapi import BackgroundTasks, FastAPI, File, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app import __version__
from app.config import Settings
from app.db import current_schema_version, ensure_workspace, initialize_database
from app.learning import (
    adjust_knowledge_map,
    confirm_knowledge_map,
    generate_coverage,
    generate_knowledge_map,
    get_coverage,
    get_knowledge_map,
    list_source_gaps,
    load_demo_materials,
    update_session_setup,
)
from app.sources import (
    SourceError,
    cancel_source,
    clean_filename,
    create_session,
    delete_source,
    get_session,
    get_source,
    list_sessions,
    list_sources,
    media_for_filename,
    process_source,
    retry_source,
    search_chunks,
    store_source,
    validate_file_bytes,
)


STATIC_DIR = Path(__file__).resolve().parent / "static"
SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"
WORKSPACE_COOKIE = "startframe_workspace"


class HealthResponse(BaseModel):
    status: str
    mode: str
    database: str
    schema_version: int
    version: str


class PastedSourceRequest(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    text: str = Field(min_length=1, max_length=2_000_000)


class SessionSetupRequest(BaseModel):
    goal: str = Field(min_length=5, max_length=500)
    prior_knowledge: str = Field(min_length=2, max_length=500)
    available_minutes: int = Field(ge=5, le=240)
    energy_level: Literal["low", "medium", "high"]
    current_question: str | None = Field(default=None, max_length=1000)
    support_preferences: list[
        Literal["direct_explanation", "define_terms", "short_steps", "examples_on_request"]
    ] = Field(default_factory=list, max_length=4)
    show_timer: bool = False
    search_permission: bool = False
    version: int = Field(ge=1)


class PathAdjustmentRequest(BaseModel):
    route_concept_keys: list[str] = Field(min_length=2, max_length=5)


def create_app(
    settings: Settings | None = None,
    *,
    ai_client_factory: Callable[[Settings], Any] | None = None,
) -> FastAPI:
    resolved_settings = settings or Settings.from_env()

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        initialize_database(resolved_settings.database_path)
        application.state.settings = resolved_settings
        yield

    application = FastAPI(
        title="StartFrame Agent",
        version=__version__,
        docs_url="/api/docs",
        redoc_url=None,
        lifespan=lifespan,
    )
    application.state.settings = resolved_settings

    @application.exception_handler(SourceError)
    async def source_error_handler(request: Request, exc: SourceError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": exc.error_code,
                "user_message": exc.user_message,
                "recoverable": exc.recoverable,
                "retry_after_seconds": None,
                "field_errors": None,
                "saved_state": exc.saved_state,
                "request_id": str(uuid.uuid4()),
            },
        )

    @application.exception_handler(RequestValidationError)
    async def request_validation_error_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        field_errors = [
            {
                "field": ".".join(str(part) for part in error["loc"] if part not in {"body", "query"}),
                "message": str(error["msg"]),
            }
            for error in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={
                "error_code": "request_validation_failed",
                "user_message": "Check the highlighted information and try again.",
                "recoverable": True,
                "retry_after_seconds": None,
                "field_errors": field_errors,
                "saved_state": "Existing session data is unchanged.",
                "request_id": str(uuid.uuid4()),
            },
        )

    @application.middleware("http")
    async def anonymous_workspace(request: Request, call_next):  # type: ignore[no-untyped-def]
        workspace_id = _valid_workspace_id(request.cookies.get(WORKSPACE_COOKIE))
        is_new_workspace = workspace_id is None
        if workspace_id is None:
            workspace_id = str(uuid.uuid4())
        if request.url.path == "/" or request.url.path.startswith("/api/"):
            ensure_workspace(resolved_settings.database_path, workspace_id)
        request.state.workspace_id = workspace_id
        response = await call_next(request)
        if is_new_workspace:
            response.set_cookie(
                WORKSPACE_COOKIE,
                workspace_id,
                max_age=60 * 60 * 24 * 365,
                httponly=True,
                secure=resolved_settings.secure_cookies,
                samesite="lax",
                path="/",
            )
        return response

    @application.middleware("http")
    async def add_security_headers(request: Request, call_next):  # type: ignore[no-untyped-def]
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self' data:; style-src 'self'; "
            "script-src 'self'; connect-src 'self'; frame-ancestors 'none'"
        )
        return response

    @application.get("/", include_in_schema=False)
    async def homepage() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @application.get("/api/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            mode=resolved_settings.mode,
            database="ready",
            schema_version=current_schema_version(resolved_settings.database_path),
            version=__version__,
        )

    @application.post("/api/sessions", status_code=201)
    async def new_session(request: Request) -> dict:
        session = create_session(
            resolved_settings.database_path,
            _workspace_id(request),
            resolved_settings.mode,
        )
        return {"session": _public_session(session)}

    @application.get("/api/sessions")
    async def sessions(request: Request) -> dict:
        items = list_sessions(resolved_settings.database_path, _workspace_id(request))
        return {"sessions": [_public_session(item) for item in items]}

    @application.get("/api/sessions/{session_id}")
    async def session_detail(session_id: str, request: Request) -> dict:
        session = get_session(
            resolved_settings.database_path,
            _workspace_id(request),
            session_id,
        )
        return {"session": _public_session(session)}

    @application.patch("/api/sessions/{session_id}")
    async def update_session(
        session_id: str,
        payload: SessionSetupRequest,
        request: Request,
    ) -> dict:
        session = update_session_setup(
            resolved_settings.database_path,
            _workspace_id(request),
            session_id,
            payload.model_dump(exclude={"version"}),
            payload.version,
        )
        return {"session": _public_session(session)}

    @application.post("/api/sessions/{session_id}/sources", status_code=202)
    async def upload_sources(
        session_id: str,
        request: Request,
        background_tasks: BackgroundTasks,
        files: list[UploadFile] = File(...),
    ) -> JSONResponse:
        workspace_id = _workspace_id(request)
        get_session(resolved_settings.database_path, workspace_id, session_id)
        if len(files) > resolved_settings.max_files:
            raise SourceError(
                "too_many_files",
                f"Upload up to {resolved_settings.max_files} files at a time.",
                saved_state="No files from this upload were saved.",
            )

        accepted: list[dict] = []
        rejected: list[dict] = []
        for upload in files:
            filename = clean_filename(upload.filename)
            try:
                media_type, media_kind = media_for_filename(filename)
                data = await upload.read(resolved_settings.max_file_bytes + 1)
                if len(data) > resolved_settings.max_file_bytes:
                    raise SourceError(
                        "file_too_large",
                        f"{filename} is larger than {resolved_settings.max_file_bytes // (1024 * 1024)} MB.",
                    )
                validate_file_bytes(media_kind, data)
                source = store_source(
                    resolved_settings.database_path,
                    resolved_settings.upload_dir,
                    workspace_id,
                    session_id,
                    filename,
                    media_type,
                    media_kind,
                    data,
                )
                accepted.append(_public_source(source))
                background_tasks.add_task(
                    process_source,
                    resolved_settings.database_path,
                    workspace_id,
                    str(source["id"]),
                )
            except SourceError as exc:
                rejected.append(
                    {
                        "filename": filename,
                        "status": "error",
                        "error_code": exc.error_code,
                        "user_message": exc.user_message,
                        "recoverable": exc.recoverable,
                    }
                )
            finally:
                await upload.close()

        if accepted and rejected:
            status = "partial_success"
        elif accepted:
            status = "processing"
        else:
            status = "error"
        return JSONResponse(
            status_code=202 if accepted else 400,
            content={"status": status, "accepted": accepted, "rejected": rejected},
        )

    @application.post("/api/sessions/{session_id}/pasted-sources", status_code=202)
    async def add_pasted_source(
        session_id: str,
        payload: PastedSourceRequest,
        request: Request,
        background_tasks: BackgroundTasks,
    ) -> dict:
        workspace_id = _workspace_id(request)
        data = payload.text.encode("utf-8")
        if len(data) > resolved_settings.max_file_bytes:
            raise SourceError(
                "pasted_text_too_large",
                f"Pasted text must be smaller than {resolved_settings.max_file_bytes // (1024 * 1024)} MB.",
            )
        source = store_source(
            resolved_settings.database_path,
            resolved_settings.upload_dir,
            workspace_id,
            session_id,
            clean_filename(payload.title),
            "text/plain",
            "pasted",
            data,
        )
        background_tasks.add_task(
            process_source,
            resolved_settings.database_path,
            workspace_id,
            str(source["id"]),
        )
        return {"status": "processing", "source": _public_source(source)}

    @application.get("/api/sessions/{session_id}/sources")
    async def sources(session_id: str, request: Request) -> dict:
        items = list_sources(
            resolved_settings.database_path,
            _workspace_id(request),
            session_id,
        )
        return {"sources": [_public_source(item) for item in items]}

    @application.get("/api/sources/{source_id}")
    async def source_detail(source_id: str, request: Request) -> dict:
        source = get_source(
            resolved_settings.database_path,
            _workspace_id(request),
            source_id,
        )
        return {"source": _public_source(source, include_chunks=True)}

    @application.get("/api/sources/{source_id}/chunks/{chunk_id}")
    async def source_chunk(source_id: str, chunk_id: str, request: Request) -> dict:
        source = get_source(
            resolved_settings.database_path,
            _workspace_id(request),
            source_id,
        )
        chunk = next((item for item in source.get("chunks", []) if item["id"] == chunk_id), None)
        if not chunk:
            raise SourceError(
                "source_reference_invalid",
                "This source location is no longer available.",
                status_code=404,
                saved_state="The original source and your session remain available.",
            )
        return {"source": _public_source(source), "chunk": _public_chunk(chunk)}

    @application.get("/api/sources/{source_id}/progress")
    async def source_progress(source_id: str, request: Request) -> dict:
        source = get_source(
            resolved_settings.database_path,
            _workspace_id(request),
            source_id,
            include_chunks=False,
        )
        return {"source": _public_source(source)}

    @application.post("/api/sources/{source_id}/retry", status_code=202)
    async def retry_source_endpoint(
        source_id: str,
        request: Request,
        background_tasks: BackgroundTasks,
    ) -> dict:
        workspace_id = _workspace_id(request)
        source = retry_source(resolved_settings.database_path, workspace_id, source_id)
        background_tasks.add_task(
            process_source,
            resolved_settings.database_path,
            workspace_id,
            source_id,
        )
        return {"status": "retrying", "source": _public_source(source)}

    @application.post("/api/sources/{source_id}/cancel")
    async def cancel_source_endpoint(source_id: str, request: Request) -> dict:
        source = cancel_source(
            resolved_settings.database_path,
            _workspace_id(request),
            source_id,
        )
        return {"status": "cancelled", "source": _public_source(source)}

    @application.delete("/api/sources/{source_id}", status_code=204)
    async def delete_source_endpoint(source_id: str, request: Request) -> Response:
        delete_source(
            resolved_settings.database_path,
            _workspace_id(request),
            source_id,
        )
        return Response(status_code=204)

    @application.get("/api/sessions/{session_id}/source-search")
    async def source_search(session_id: str, q: str, request: Request) -> dict:
        results = search_chunks(
            resolved_settings.database_path,
            _workspace_id(request),
            session_id,
            q[:200],
        )
        return {"query": q[:200], "results": [_public_chunk(item) for item in results]}

    @application.post("/api/sessions/{session_id}/demo-materials", status_code=201)
    async def add_demo_materials(session_id: str, request: Request) -> dict:
        created = load_demo_materials(
            resolved_settings,
            _workspace_id(request),
            session_id,
            SAMPLE_DIR,
        )
        items = list_sources(
            resolved_settings.database_path,
            _workspace_id(request),
            session_id,
        )
        return {
            "created_count": len(created),
            "sources": [_public_source(item) for item in items],
            "fixture": "Transformer foundations",
        }

    @application.post("/api/sessions/{session_id}/coverage")
    async def create_coverage(session_id: str, request: Request) -> dict:
        return generate_coverage(
            resolved_settings,
            _workspace_id(request),
            session_id,
            client_factory=ai_client_factory,
        )

    @application.get("/api/sessions/{session_id}/coverage")
    async def coverage_detail(session_id: str, request: Request) -> dict:
        return get_coverage(
            resolved_settings.database_path,
            _workspace_id(request),
            session_id,
        )

    @application.get("/api/sessions/{session_id}/source-gaps")
    async def source_gaps(session_id: str, request: Request) -> dict:
        return {
            "source_gaps": list_source_gaps(
                resolved_settings.database_path,
                _workspace_id(request),
                session_id,
            ),
            "internet_search_performed": False,
        }

    @application.post("/api/sessions/{session_id}/path")
    async def create_path(session_id: str, request: Request) -> dict:
        return generate_knowledge_map(
            resolved_settings,
            _workspace_id(request),
            session_id,
            client_factory=ai_client_factory,
        )

    @application.get("/api/sessions/{session_id}/path")
    async def path_detail(session_id: str, request: Request) -> dict:
        return get_knowledge_map(
            resolved_settings.database_path,
            _workspace_id(request),
            session_id,
        )

    @application.patch("/api/sessions/{session_id}/path")
    async def adjust_path(
        session_id: str,
        payload: PathAdjustmentRequest,
        request: Request,
    ) -> dict:
        return adjust_knowledge_map(
            resolved_settings.database_path,
            _workspace_id(request),
            session_id,
            payload.route_concept_keys,
        )

    @application.post("/api/sessions/{session_id}/path/confirm")
    async def confirm_path(session_id: str, request: Request) -> dict:
        return confirm_knowledge_map(
            resolved_settings.database_path,
            _workspace_id(request),
            session_id,
        )

    application.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    return application


app = create_app()


def _valid_workspace_id(value: str | None) -> str | None:
    if not value:
        return None
    try:
        parsed = uuid.UUID(value)
    except ValueError:
        return None
    return str(parsed) if parsed.version == 4 else None


def _workspace_id(request: Request) -> str:
    return str(request.state.workspace_id)


def _public_session(session: dict) -> dict:
    fields = {
        "id",
        "name",
        "state",
        "mode",
        "version",
        "source_count",
        "ready_source_count",
        "goal",
        "prior_knowledge",
        "available_minutes",
        "energy_level",
        "language",
        "current_question",
        "show_timer",
        "search_permission",
        "setup_completed",
        "created_at",
        "updated_at",
    }
    result = {key: session.get(key) for key in fields if key in session}
    if "support_preferences_json" in session:
        import json

        result["support_preferences"] = json.loads(session.get("support_preferences_json") or "[]")
    for key in ("show_timer", "search_permission", "setup_completed"):
        if key in result:
            result[key] = bool(result[key])
    return result


def _public_source(source: dict, *, include_chunks: bool = False) -> dict:
    fields = {
        "id",
        "session_id",
        "filename",
        "media_type",
        "media_kind",
        "source_origin",
        "parse_status",
        "page_count",
        "line_count",
        "error_code",
        "error_message",
        "version",
        "byte_size",
        "checksum",
        "chunk_count",
        "created_at",
        "updated_at",
    }
    result = {key: source.get(key) for key in fields if key in source}
    if include_chunks:
        result["chunks"] = [_public_chunk(chunk) for chunk in source.get("chunks", [])]
    return result


def _public_chunk(chunk: dict) -> dict:
    fields = {
        "id",
        "source_id",
        "filename",
        "media_kind",
        "source_origin",
        "heading_path",
        "page_number",
        "page_chunk_index",
        "paragraph_number",
        "start_line",
        "end_line",
        "start_char",
        "end_char",
        "text",
        "checksum",
    }
    return {key: chunk.get(key) for key in fields if key in chunk}
