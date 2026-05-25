"""Tests for hotkey utilities."""

import pytest

from voicetyping.hotkey.utils import format_hotkey, normalize_hotkey, validate_hotkey


def test_normalize_hotkey():
    assert normalize_hotkey("Ctrl+Shift+Space") == "ctrl+shift+space"
    assert normalize_hotkey("control+alt+a") == "ctrl+alt+a"


def test_format_hotkey():
    assert format_hotkey("ctrl+shift+space") == "Ctrl + Shift + Space"


def test_validate_hotkey_requires_modifier():
    ok, _ = validate_hotkey("ctrl+shift+space")
    assert ok is True

    ok, message = validate_hotkey("space")
    assert ok is False
    assert "修饰键" in message

    ok, message = validate_hotkey("ctrl+shift")
    assert ok is False


def test_validate_hotkey_rejects_empty():
    ok, message = validate_hotkey("")
    assert ok is False
    assert message
