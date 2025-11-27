"""
Utility helpers shared across trading components.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)


def configure_logger(name: str, log_file: Optional[Path] = None) -> logging.Logger:
    """
    Configure and return a logger that writes to stdout and optional file.
    """
    logger = logging.getLogger(name)
    if logger.handlers:  # reuse existing configuration
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        "%Y-%m-%d %H:%M:%S%z",
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.propagate = False
    return logger


def now_utc() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(tz=timezone.utc)


def ensure_timezone(dt: datetime) -> datetime:
    """
    Make timestamps timezone-aware (UTC) to avoid downstream bugs.
    """
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def chunks(iterable: Iterable[Any], size: int) -> Iterable[list[Any]]:
    """Yield successive fixed-size chunks from an iterable."""
    chunk: list[Any] = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) == size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def read_json(path: Path, default: Any | None = None) -> Any:
    """Read JSON from disk, returning default on missing file."""
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: Any) -> None:
    """Write JSON to disk atomically."""
    temp_path = path.with_suffix(".tmp")
    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, sort_keys=True)
    temp_path.replace(path)

