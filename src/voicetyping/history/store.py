"""Persistent storage for voice transcription history."""

from __future__ import annotations

import json
import threading
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from voicetyping.config.settings import ChineseScript, _config_dir

HistoryChangeCallback = Callable[[str], None]


@dataclass
class HistoryEntry:
    id: str
    text: str
    created_at: str
    script: ChineseScript


def history_path() -> Path:
    return _config_dir() / "history.json"


class HistoryStore:
    """Stores transcription history with JSON persistence."""

    def __init__(self, path: Optional[Path] = None, max_items: int = 100) -> None:
        self.path = path or history_path()
        self.max_items = max_items
        self._entries: list[HistoryEntry] = []
        self._lock = threading.Lock()
        self._listeners: list[HistoryChangeCallback] = []
        self._load()

    def add_listener(self, callback: HistoryChangeCallback) -> None:
        with self._lock:
            if callback not in self._listeners:
                self._listeners.append(callback)

    def remove_listener(self, callback: HistoryChangeCallback) -> None:
        with self._lock:
            if callback in self._listeners:
                self._listeners.remove(callback)

    def _notify(self, event: str) -> None:
        with self._lock:
            listeners = list(self._listeners)
        for callback in listeners:
            try:
                callback(event)
            except Exception as exc:
                print(f"[HistoryStore] Listener error: {exc}")

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self._entries = [HistoryEntry(**item) for item in data]
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            print(f"[HistoryStore] Failed to load history: {exc}")

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [asdict(entry) for entry in self._entries]
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def add(self, text: str, script: ChineseScript) -> HistoryEntry:
        entry = HistoryEntry(
            id=uuid.uuid4().hex,
            text=text,
            created_at=datetime.now(timezone.utc).isoformat(),
            script=script,
        )
        with self._lock:
            self._entries.insert(0, entry)
            self._entries = self._entries[: self.max_items]
            self._save()
        self._notify("add")
        return entry

    def get_all(self) -> list[HistoryEntry]:
        with self._lock:
            return list(self._entries)

    def clear(self) -> None:
        with self._lock:
            self._entries = []
            self._save()
        self._notify("change")

    def delete(self, entry_id: str) -> None:
        with self._lock:
            self._entries = [entry for entry in self._entries if entry.id != entry_id]
            self._save()
        self._notify("change")
