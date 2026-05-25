"""On-screen indicator shown while the microphone is active."""

from __future__ import annotations

import queue
import threading
import tkinter as tk
from tkinter import ttk
from typing import Optional


class RecordingIndicator:
    """Small always-on-top overlay for active microphone use."""

    _cmd_queue: queue.Queue = queue.Queue()
    _tk_thread: Optional[threading.Thread] = None
    _ready = threading.Event()

    @classmethod
    def show(cls) -> None:
        cls._ensure_thread()
        cls._cmd_queue.put(("show",))

    @classmethod
    def hide(cls) -> None:
        cls._ensure_thread()
        cls._cmd_queue.put(("hide",))

    @classmethod
    def update_level(cls, level: float) -> None:
        cls._ensure_thread()
        cls._cmd_queue.put(("level", level))

    @classmethod
    def show_low_volume_warning(cls) -> None:
        cls._ensure_thread()
        cls._cmd_queue.put(("warn",))

    @classmethod
    def _ensure_thread(cls) -> None:
        if cls._tk_thread and cls._tk_thread.is_alive():
            return
        cls._ready.clear()
        cls._tk_thread = threading.Thread(target=cls._tk_main, daemon=True, name="RecordingIndicatorTk")
        cls._tk_thread.start()
        cls._ready.wait(timeout=5)

    @classmethod
    def _tk_main(cls) -> None:
        root = tk.Tk()
        root.withdraw()

        overlay: Optional[tk.Toplevel] = None
        status_label: Optional[ttk.Label] = None
        level_bar: Optional[ttk.Progressbar] = None
        warn_label: Optional[ttk.Label] = None

        def ensure_overlay() -> tk.Toplevel:
            nonlocal overlay, status_label, level_bar, warn_label
            if overlay is not None and overlay.winfo_exists():
                return overlay

            overlay = tk.Toplevel(root)
            overlay.title("VoiceTyping Recording")
            overlay.overrideredirect(True)
            overlay.attributes("-topmost", True)
            overlay.configure(bg="#1f1f1f")

            frame = ttk.Frame(overlay, padding=12)
            frame.pack(fill="both", expand=True)

            status_label = ttk.Label(frame, text="🎤 麦克风使用中", font=("Segoe UI", 11, "bold"))
            status_label.pack(anchor="w")

            level_bar = ttk.Progressbar(frame, length=220, mode="determinate", maximum=100)
            level_bar.pack(fill="x", pady=(8, 4))

            warn_label = ttk.Label(frame, text="", foreground="#d64545")
            warn_label.pack(anchor="w")

            overlay.update_idletasks()
            width = overlay.winfo_width()
            height = overlay.winfo_height()
            screen_w = overlay.winfo_screenwidth()
            screen_h = overlay.winfo_screenheight()
            overlay.geometry(f"{width}x{height}+{max(0, (screen_w - width) // 2)}+{max(0, screen_h - height - 80)}")

            return overlay

        def handle_show() -> None:
            panel = ensure_overlay()
            if warn_label is not None:
                warn_label.config(text="")
            if level_bar is not None:
                level_bar["value"] = 0
            panel.deiconify()
            panel.lift()

        def handle_hide() -> None:
            if overlay is not None and overlay.winfo_exists():
                overlay.withdraw()

        def handle_level(level: float) -> None:
            if level_bar is None:
                return
            percent = min(100, max(0, int(level * 400)))
            level_bar["value"] = percent

        def handle_warn() -> None:
            if warn_label is not None:
                warn_label.config(text="⚠ 音量过小，请靠近麦克风或调高输入音量")

        def poll_queue() -> None:
            try:
                while True:
                    cmd, *args = cls._cmd_queue.get_nowait()
                    if cmd == "show":
                        handle_show()
                    elif cmd == "hide":
                        handle_hide()
                    elif cmd == "level":
                        handle_level(float(args[0]))
                    elif cmd == "warn":
                        handle_warn()
            except queue.Empty:
                pass
            root.after(80, poll_queue)

        cls._ready.set()
        poll_queue()
        root.mainloop()
