"""Configuration schema, validation, and serialization for Typr."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from typr.storage.paths import get_config_dir, get_config_file


VALID_THEMES = ("mint", "amber", "cyan", "mono")
VALID_MODES = ("words", "time", "quotes", "code")
VALID_DIFFICULTIES = ("normal", "expert", "master")
VALID_RESTARTS = ("tab", "enter", "off")
VALID_TIMERS = ("mini", "bar", "off")
VALID_CARETS = ("line", "block", "underline", "off")
VALID_TEXT_SIZES = ("normal", "large", "adaptive")
VALID_CODE_LANGUAGES = (
    "python",
    "rust",
    "cpp",
    "javascript",
    "typescript",
    "go",
    "bash",
    "sql",
    "html",
    "css",
)


@dataclass
class AppConfig:
    """Strongly typed application configuration."""

    theme: str = "mint"
    mode: str = "words"
    time: int = 30
    words: int = 25
    punctuation: bool = False
    numbers: bool = False
    language: str = "english"
    code_language: str = "python"
    difficulty: str = "normal"
    quick_restart: str = "tab"
    live_wpm: bool = True
    live_acc: bool = True
    live_burst: bool = False
    timer_style: str = "mini"
    cursor_style: str = "line"
    sound_enabled: bool = False
    save_history: bool = True
    max_line_width: int = 80
    focus_mode: bool = False
    text_size: str = "large"
    fade_completed: bool = True
    smooth_caret: bool = True
    custom_colors: Dict[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate and sanitize configuration fields."""
        if self.theme not in VALID_THEMES:
            self.theme = "mint"
        if self.mode not in VALID_MODES:
            self.mode = "words"
        if self.difficulty not in VALID_DIFFICULTIES:
            self.difficulty = "normal"
        if self.quick_restart not in VALID_RESTARTS:
            self.quick_restart = "tab"
        if self.timer_style not in VALID_TIMERS:
            self.timer_style = "mini"
        if self.cursor_style not in VALID_CARETS:
            self.cursor_style = "line"
        if self.text_size not in VALID_TEXT_SIZES:
            self.text_size = "large"
        if self.code_language not in VALID_CODE_LANGUAGES:
            self.code_language = "python"

        self.time = max(5, min(3600, int(self.time)))
        self.words = max(5, min(1000, int(self.words)))
        self.max_line_width = max(30, min(160, int(self.max_line_width)))


def load_config(path: Optional[Path] = None) -> AppConfig:
    """Load and validate configuration from disk, falling back to defaults."""
    target_path = path or get_config_file()
    cfg = AppConfig()

    if target_path.is_file():
        try:
            raw = json.loads(target_path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                # Only accept fields defined on AppConfig
                valid_fields = AppConfig.__annotations__.keys()
                for k, v in raw.items():
                    if k in valid_fields:
                        setattr(cfg, k, v)
        except (OSError, json.JSONDecodeError, ValueError):
            pass

    cfg.validate()
    return cfg


def save_config(config: AppConfig, path: Optional[Path] = None) -> None:
    """Save configuration to disk atomically."""
    target_path = path or get_config_file()
    config.validate()

    target_dir = target_path.parent
    target_dir.mkdir(parents=True, exist_ok=True)

    data = asdict(config)
    tmp_file = target_path.with_suffix(".tmp")
    try:
        tmp_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        tmp_file.replace(target_path)
    except OSError:
        if tmp_file.exists():
            try:
                tmp_file.unlink()
            except OSError:
                pass


def reset_config(path: Optional[Path] = None) -> AppConfig:
    """Reset configuration to factory defaults."""
    cfg = AppConfig()
    save_config(cfg, path)
    return cfg

