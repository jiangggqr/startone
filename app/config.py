"""Environment-backed application settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

AppMode = Literal["demo", "real"]


@dataclass(frozen=True, slots=True)
class Settings:
    """Validated settings used by the web process."""

    mode: AppMode = "demo"
    database_path: Path = PROJECT_ROOT / "instance" / "startframe.sqlite3"
    upload_dir: Path = PROJECT_ROOT / "instance" / "uploads"
    max_file_bytes: int = 20 * 1024 * 1024
    max_files: int = 5
    secure_cookies: bool = False
    host: str = "127.0.0.1"
    port: int = 8000
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.6"
    openai_timeout_seconds: float = 45.0

    @classmethod
    def from_env(cls) -> "Settings":
        raw_mode = os.getenv("STARTFRAME_MODE", "demo").strip().lower()
        if raw_mode not in {"demo", "real"}:
            raise ValueError("STARTFRAME_MODE must be demo or real")

        raw_port = os.getenv("STARTFRAME_PORT", "8000")
        try:
            port = int(raw_port)
        except ValueError as exc:
            raise ValueError("STARTFRAME_PORT must be an integer") from exc
        if not 1 <= port <= 65535:
            raise ValueError("STARTFRAME_PORT must be between 1 and 65535")

        database_path = Path(
            os.getenv(
                "STARTFRAME_DATABASE_PATH",
                str(PROJECT_ROOT / "instance" / "startframe.sqlite3"),
            )
        ).expanduser()
        upload_dir = Path(
            os.getenv(
                "STARTFRAME_UPLOAD_DIR",
                str(PROJECT_ROOT / "instance" / "uploads"),
            )
        ).expanduser()

        try:
            max_file_mb = int(os.getenv("STARTFRAME_MAX_FILE_MB", "20"))
            max_files = int(os.getenv("STARTFRAME_MAX_FILES", "5"))
        except ValueError as exc:
            raise ValueError("Upload limits must be integers") from exc
        if not 1 <= max_file_mb <= 100:
            raise ValueError("STARTFRAME_MAX_FILE_MB must be between 1 and 100")
        if not 1 <= max_files <= 20:
            raise ValueError("STARTFRAME_MAX_FILES must be between 1 and 20")

        secure_cookies = os.getenv("STARTFRAME_SECURE_COOKIES", "false").lower()
        if secure_cookies not in {"true", "false"}:
            raise ValueError("STARTFRAME_SECURE_COOKIES must be true or false")

        openai_timeout_raw = os.getenv("STARTFRAME_OPENAI_TIMEOUT_SECONDS", "45")
        try:
            openai_timeout_seconds = float(openai_timeout_raw)
        except ValueError as exc:
            raise ValueError("STARTFRAME_OPENAI_TIMEOUT_SECONDS must be a number") from exc
        if not 5 <= openai_timeout_seconds <= 180:
            raise ValueError("STARTFRAME_OPENAI_TIMEOUT_SECONDS must be between 5 and 180")

        openai_api_key = os.getenv("OPENAI_API_KEY", "").strip() or None
        openai_model = os.getenv("STARTFRAME_OPENAI_MODEL", "gpt-5.6").strip()
        if not openai_model:
            raise ValueError("STARTFRAME_OPENAI_MODEL cannot be empty")

        return cls(
            mode=raw_mode,  # type: ignore[arg-type]
            database_path=database_path,
            upload_dir=upload_dir,
            max_file_bytes=max_file_mb * 1024 * 1024,
            max_files=max_files,
            secure_cookies=secure_cookies == "true",
            host=os.getenv("STARTFRAME_HOST", "127.0.0.1"),
            port=port,
            openai_api_key=openai_api_key,
            openai_model=openai_model,
            openai_timeout_seconds=openai_timeout_seconds,
        )
