"""Application settings with JSON persistence."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field

ModelSize = Literal["tiny", "base", "small", "medium", "large-v2", "large-v3"]
ChineseScript = Literal["simplified", "traditional"]


class Settings(BaseModel):
    model_size: ModelSize = "base"
    language: str = "zh"
    chinese_script: ChineseScript = "simplified"
    hotkey: str = "ctrl+shift+space"
    restore_clipboard: bool = True
    device: str = "auto"
    min_record_seconds: float = Field(default=0.3, ge=0.1, le=5.0)
    # HuggingFace mirror, e.g. "https://hf-mirror.com" for users in China
    hf_endpoint: Optional[str] = "https://hf-mirror.com"
    # Optional local model directory; overrides model_size when set
    model_path: Optional[str] = None
    history_max_items: int = Field(default=100, ge=10, le=1000)
    # None = system default microphone
    input_device: Optional[int] = None
    low_volume_rms_threshold: float = Field(default=0.015, ge=0.001, le=0.2)
    show_recording_indicator: bool = True


def _config_dir() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / "VoiceTyping"
    return Path.home() / ".voicetyping"


def config_path() -> Path:
    return _config_dir() / "config.json"


def load_settings() -> Settings:
    path = config_path()
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return Settings.model_validate(data)
        except (json.JSONDecodeError, ValueError) as exc:
            print(f"[Settings] Failed to load config: {exc}, using defaults.")
    return Settings()


def save_settings(settings: Settings) -> None:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        settings.model_dump_json(indent=2),
        encoding="utf-8",
    )
