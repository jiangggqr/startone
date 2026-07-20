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
    host: str = "127.0.0.1"
    port: int = 8000

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

        return cls(
            mode=raw_mode,  # type: ignore[arg-type]
            database_path=database_path,
            host=os.getenv("STARTFRAME_HOST", "127.0.0.1"),
            port=port,
        )
