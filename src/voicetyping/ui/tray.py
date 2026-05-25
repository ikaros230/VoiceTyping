"""System tray UI for VoiceTyping."""

from __future__ import annotations

import threading
from typing import Callable, Optional

from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem

from voicetyping.audio.devices import get_device_label
from voicetyping.config.settings import ChineseScript
from voicetyping.hotkey.utils import format_hotkey
from voicetyping.pipeline import PipelineState

SCRIPT_LABELS = {
    "simplified": "简体中文",
    "traditional": "繁體中文",
}


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
        get_chinese_script: Callable[[], ChineseScript],
        get_hotkey: Callable[[], str],
        get_input_device: Callable[[], Optional[int]],
        on_chinese_script_change: Optional[Callable[[ChineseScript], None]] = None,
        on_change_hotkey: Optional[Callable[[], None]] = None,
        on_select_microphone: Optional[Callable[[], None]] = None,
        on_open_history: Optional[Callable[[], None]] = None,
        on_quit: Optional[Callable[[], None]] = None,
        on_open_settings: Optional[Callable[[], None]] = None,
    ) -> None:
        self._get_chinese_script = get_chinese_script
        self._get_hotkey = get_hotkey
        self._get_input_device = get_input_device
        self._on_chinese_script_change = on_chinese_script_change
        self._on_change_hotkey = on_change_hotkey
        self._on_select_microphone = on_select_microphone
        self._on_open_history = on_open_history
        self._on_quit = on_quit
        self._on_open_settings = on_open_settings
        self._icon: Optional[Icon] = None
        self._state = PipelineState.IDLE

    def update_state(self, state: PipelineState) -> None:
        self._state = state
        if self._icon:
            self._icon.icon = ICONS.get(state, ICONS[PipelineState.IDLE])
            self._icon.title = self._title_for_state(state)

    def notify(self, title: str, message: str) -> None:
        if self._icon:
            try:
                self._icon.notify(message, title)
            except Exception as exc:
                print(f"[TrayApp] Notification failed: {exc}")

    def _title_for_state(self, state: PipelineState) -> str:
        script_label = SCRIPT_LABELS[self._get_chinese_script()]
        titles = {
            PipelineState.IDLE: f"VoiceTyping — 就绪 ({script_label})",
            PipelineState.RECORDING: "VoiceTyping — 🎤 麦克风使用中",
            PipelineState.TRANSCRIBING: "VoiceTyping — 识别中",
        }
        return titles.get(state, "VoiceTyping")

    def _build_menu(self) -> Menu:
        return Menu(
            MenuItem("历史剪贴板", self._open_history),
            MenuItem(
                "文字输出",
                Menu(
                    MenuItem(
                        "简体中文",
                        lambda: self._select_script("simplified"),
                        checked=lambda _: self._get_chinese_script() == "simplified",
                        radio=True,
                    ),
                    MenuItem(
                        "繁體中文",
                        lambda: self._select_script("traditional"),
                        checked=lambda _: self._get_chinese_script() == "traditional",
                        radio=True,
                    ),
                ),
            ),
            MenuItem(f"修改热键 ({format_hotkey(self._get_hotkey())})", self._change_hotkey),
            MenuItem(self._mic_menu_label(), self._select_microphone),
            MenuItem("设置", self._open_settings),
            MenuItem("退出", self._quit),
        )

    def _select_script(self, script: ChineseScript) -> None:
        if self._get_chinese_script() == script:
            return
        if self._on_chinese_script_change:
            self._on_chinese_script_change(script)
        self.refresh_menu()
        if self._icon and self._state == PipelineState.IDLE:
            self._icon.title = self._title_for_state(PipelineState.IDLE)

    def _mic_menu_label(self) -> str:
        label = get_device_label(self._get_input_device())
        if len(label) > 24:
            label = label[:24] + "..."
        return f"选择麦克风 ({label})"

    def _select_microphone(self) -> None:
        if self._on_select_microphone:
            threading.Thread(target=self._on_select_microphone, daemon=True).start()

    def _change_hotkey(self) -> None:
        if self._on_change_hotkey:
            threading.Thread(target=self._on_change_hotkey, daemon=True).start()

    def refresh_menu(self) -> None:
        if self._icon:
            self._icon.menu = self._build_menu()
            self._icon.update_menu()

    def _open_history(self, _icon=None, _item=None) -> None:
        if self._on_open_history:
            threading.Thread(target=self._on_open_history, daemon=True).start()

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
            self._title_for_state(PipelineState.IDLE),
            menu=self._build_menu(),
            default=self._open_history,
        )
        self._icon.run()

    def stop(self) -> None:
        if self._icon:
            self._icon.stop()
