"""Windows text injection via clipboard and Ctrl+V."""

from __future__ import annotations

import time

import keyboard
import pyperclip

from voicetyping.output.base import TextInjector


class WindowsTextInjector(TextInjector):
    """Injects text using clipboard paste on Windows."""

    def __init__(self, restore_clipboard: bool = True, paste_delay: float = 0.05) -> None:
        self.restore_clipboard = restore_clipboard
        self.paste_delay = paste_delay

    def inject(self, text: str) -> None:
        if not text:
            return

        original = None
        if self.restore_clipboard:
            try:
                original = pyperclip.paste()
            except pyperclip.PyperclipException:
                original = None

        pyperclip.copy(text)
        time.sleep(self.paste_delay)
        keyboard.send("ctrl+v")
        time.sleep(self.paste_delay)

        if self.restore_clipboard and original is not None:
            try:
                pyperclip.copy(original)
            except pyperclip.PyperclipException:
                pass
