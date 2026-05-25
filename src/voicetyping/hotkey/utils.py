"""Hotkey validation and formatting utilities."""

from __future__ import annotations

MODIFIERS = {"ctrl", "control", "shift", "alt", "win", "windows"}

DISPLAY_NAMES = {
    "ctrl": "Ctrl",
    "control": "Ctrl",
    "shift": "Shift",
    "alt": "Alt",
    "win": "Win",
    "windows": "Win",
    "space": "Space",
    "enter": "Enter",
    "tab": "Tab",
    "esc": "Esc",
    "escape": "Esc",
    "backspace": "Backspace",
    "delete": "Delete",
    "insert": "Insert",
    "home": "Home",
    "end": "End",
    "page up": "Page Up",
    "page down": "Page Down",
    "up": "Up",
    "down": "Down",
    "left": "Left",
    "right": "Right",
}


def normalize_hotkey(hotkey: str) -> str:
    """Normalize hotkey string for keyboard library."""
    parts = [part.strip().lower() for part in hotkey.split("+") if part.strip()]
    aliases = {"control": "ctrl", "windows": "win", "escape": "esc"}
    normalized = [aliases.get(part, part) for part in parts]
    return "+".join(normalized)


def format_hotkey(hotkey: str) -> str:
    """Format hotkey for display, e.g. ctrl+shift+space -> Ctrl + Shift + Space."""
    parts = normalize_hotkey(hotkey).split("+")
    labels = []
    for part in parts:
        if part in DISPLAY_NAMES:
            labels.append(DISPLAY_NAMES[part])
        elif len(part) == 1:
            labels.append(part.upper())
        else:
            labels.append(part.capitalize())
    return " + ".join(labels)


def validate_hotkey(hotkey: str) -> tuple[bool, str]:
    """Validate hotkey; returns (ok, error_message)."""
    normalized = normalize_hotkey(hotkey)
    if not normalized:
        return False, "快捷键不能为空。"

    parts = normalized.split("+")
    if len(parts) < 2:
        return False, "请至少使用一个修饰键（Ctrl / Shift / Alt）加一个按键。"

    if parts[-1] in MODIFIERS:
        return False, "快捷键不能只包含修饰键。"

    if not any(part in MODIFIERS for part in parts[:-1]):
        return False, "请至少包含 Ctrl、Shift 或 Alt 之一，避免与普通输入冲突。"

    return True, ""
