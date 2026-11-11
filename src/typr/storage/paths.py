"""XDG Base Directory compliant path resolution for Typr with robust fallbacks."""

from __future__ import annotations

import os
from pathlib import Path


def get_config_dir() -> Path:
    """Return configuration directory, falling back gracefully if unwritable."""
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config and os.path.isabs(xdg_config):
        primary = Path(xdg_config) / "typr"
    else:
        primary = Path.home() / ".config" / "typr"

    try:
        primary.mkdir(parents=True, exist_ok=True)
        return primary
    except OSError:
        fallback = Path("/tmp") / "typr_config"
        try:
            fallback.mkdir(parents=True, exist_ok=True)
            return fallback
        except OSError:
            return Path.cwd() / ".typr_config"


def get_data_dir() -> Path:
    """Return data directory, falling back gracefully if unwritable."""
    xdg_data = os.environ.get("XDG_DATA_HOME")
    if xdg_data and os.path.isabs(xdg_data):
        primary = Path(xdg_data) / "typr"
    else:
        primary = Path.home() / ".local" / "share" / "typr"

    try:
        primary.mkdir(parents=True, exist_ok=True)
        return primary
    except OSError:
        fallback = Path("/tmp") / "typr_data"
        try:
            fallback.mkdir(parents=True, exist_ok=True)
            return fallback
        except OSError:
            return Path.cwd() / ".typr_data"


def get_config_file() -> Path:
    """Return path to config.json."""
    return get_config_dir() / "config.json"


def get_history_db_file() -> Path:
    """Return path to history.db."""
    return get_data_dir() / "history.db"
