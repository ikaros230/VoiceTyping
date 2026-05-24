"""System tray UI for VoiceTyping."""

from __future__ import annotations

import threading
from typing import Callable, Optional

from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem

from voicetyping.pipeline import PipelineState


def _make_icon(color: tuple[int, int, int]) -> Image.Image:
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([8, 8, size - 8, size - 8], fill=(*color, 255))
    return img


ICONS = {
    PipelineState.IDLE: _make_icon((100, 100, 100)),
    PipelineState.RECORDING: _make_icon((220, 50, 50)),
    PipelineState.TRANSCRIBING: _make_icon((50, 120, 220)),
}


class TrayApp:
    """Manages the system tray icon and menu."""

    def __init__(
        self,
        on_quit: Optional[Callable[[], None]] = None,
        on_open_settings: Optional[Callable[[], None]] = None,
    ) -> None:
        self._on_quit = on_quit
        self._on_open_settings = on_open_settings
        self._icon: Optional[Icon] = None
        self._state = PipelineState.IDLE

    def update_state(self, state: PipelineState) -> None:
        self._state = state
        if self._icon:
            self._icon.icon = ICONS.get(state, ICONS[PipelineState.IDLE])
            titles = {
                PipelineState.IDLE: "VoiceTyping — 就绪",
                PipelineState.RECORDING: "VoiceTyping — 录音中",
                PipelineState.TRANSCRIBING: "VoiceTyping — 识别中",
            }
            self._icon.title = titles.get(state, "VoiceTyping")

    def _build_menu(self) -> Menu:
        return Menu(
            MenuItem("设置", self._open_settings),
            MenuItem("退出", self._quit),
        )

    def _open_settings(self) -> None:
        if self._on_open_settings:
            threading.Thread(target=self._on_open_settings, daemon=True).start()

    def _quit(self) -> None:
        if self._on_quit:
            self._on_quit()
        if self._icon:
            self._icon.stop()

    def run(self) -> None:
        self._icon = Icon(
            "VoiceTyping",
            ICONS[PipelineState.IDLE],
            "VoiceTyping — 就绪",
            menu=self._build_menu(),
        )
        self._icon.run()

    def stop(self) -> None:
        if self._icon:
            self._icon.stop()
