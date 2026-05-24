"""Tests for transcription history."""

import json
import tempfile
from pathlib import Path

from voicetyping.history.store import HistoryStore


def test_history_add_and_list():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "history.json"
        store = HistoryStore(path=path, max_items=10)
        store.add("你好世界", "simplified")
        store.add("第二句", "traditional")

        entries = store.get_all()
        assert len(entries) == 2
        assert entries[0].text == "第二句"
        assert entries[1].text == "你好世界"
        assert entries[0].script == "traditional"


def test_history_persists_to_disk():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "history.json"
        store = HistoryStore(path=path)
        store.add("持久化测试", "simplified")

        reloaded = HistoryStore(path=path)
        entries = reloaded.get_all()
        assert len(entries) == 1
        assert entries[0].text == "持久化测试"


def test_history_max_items():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "history.json"
        store = HistoryStore(path=path, max_items=2)
        store.add("1", "simplified")
        store.add("2", "simplified")
        store.add("3", "simplified")

        entries = store.get_all()
        assert len(entries) == 2
        assert entries[0].text == "3"
        assert entries[1].text == "2"


def test_history_delete_and_clear():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "history.json"
        store = HistoryStore(path=path)
        entry = store.add("待删除", "simplified")
        store.delete(entry.id)
        assert store.get_all() == []

        store.add("a", "simplified")
        store.clear()
        assert store.get_all() == []
        assert json.loads(path.read_text(encoding="utf-8")) == []
