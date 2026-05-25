"""Global hotkey listener for push-to-talk."""

from __future__ import annotations

from typing import Callable, Optional

import keyboard


class HotkeyListener:
    """Listens for a push-to-talk hotkey: hold to record, release to transcribe."""

    def __init__(
        self,
        hotkey: str = "ctrl+shift+space",
        on_press: Optional[Callable[[], None]] = None,
        on_release: Optional[Callable[[], None]] = None,
    ) -> None:
        self.hotkey = hotkey
        self.on_press = on_press
        self.on_release = on_release
        self._active = False
        self._hook = None

    def set_hotkey(self, hotkey: str) -> None:
        """Update the active hotkey without restarting the hook."""
        self._active = False
        self.hotkey = hotkey

    def start(self) -> None:
        self._hook = keyboard.hook(self._handle_event, suppress=False)

    def stop(self) -> None:
        if self._hook is not None:
            keyboard.unhook(self._hook)
            self._hook = None

    def _handle_event(self, event) -> None:
        pressed = keyboard.is_pressed(self.hotkey)

        if pressed and not self._active:
            self._active = True
            if self.on_press:
                self.on_press()
        elif not pressed and self._active:
            self._active = False
            if self.on_release:
                self.on_release()
