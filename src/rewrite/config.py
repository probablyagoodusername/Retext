"""Configuration management — JSON config stored in %APPDATA%/Retext/."""

from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULT_CONFIG: dict = {
    "hotkey": "ctrl+shift+r",
    "gemini_api_key": "",
    "gemini_model": "gemini-2.5-flash",
}


def get_config_dir() -> Path:
    """Return %APPDATA%/Retext/, creating it if it doesn't exist."""
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise RuntimeError("%APPDATA% environment variable is not set")
    config_dir = Path(appdata) / "Retext"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_path() -> Path:
    """Return the full path to config.json."""
    return get_config_dir() / "config.json"


def load_config() -> dict:
    """Load config from disk, merging with defaults so new keys always exist."""
    path = get_config_path()
    config = dict(DEFAULT_CONFIG)
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            stored = json.load(f)
        config.update(stored)
    return config


def save_config(config: dict) -> None:
    """Write config dict to disk as formatted JSON."""
    path = get_config_path()
    with path.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
