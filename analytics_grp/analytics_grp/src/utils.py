"""Shared utility methods."""

from __future__ import annotations

import logging
import os
from pathlib import Path


def setup_logging(level: int = logging.INFO) -> None:
    """Configure consistent logger formatting for the project."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def ensure_directories(*paths: str) -> None:
    """Create directories if they do not already exist."""
    for path in paths:
        Path(path).mkdir(parents=True, exist_ok=True)


def file_exists(path: str) -> bool:
    """Return True if a file exists and is non-empty."""
    return os.path.exists(path) and os.path.getsize(path) > 0

