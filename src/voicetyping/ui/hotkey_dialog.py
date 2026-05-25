"""Dialog for capturing a new push-to-talk hotkey."""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Optional

import keyboard

from voicetyping.hotkey.utils import format_hotkey, normalize_hotkey, validate_hotkey


class HotkeyDialog:
    """Modal dialog to record a new global hotkey."""

    @classmethod
    def open(
        cls,
        current_hotkey: str,
        on_save: Callable[[str], None],
        on_pause_listener: Optional[Callable[[], None]] = None,
        on_resume_listener: Optional[Callable[[], None]] = None,
    ) -> None:
        threading.Thread(
            target=cls._run,
            args=(current_hotkey, on_save, on_pause_listener, on_resume_listener),
            daemon=True,
            name="HotkeyDialog",
        ).start()

    @classmethod
    def _run(
        cls,
        current_hotkey: str,
        on_save: Callable[[str], None],
        on_pause_listener: Optional[Callable[[], None]],
        on_resume_listener: Optional[Callable[[], None]],
    ) -> None:
        root = tk.Tk()
        root.title("修改快捷键")
        root.geometry("420x220")
        root.resizable(False, False)

        frame = ttk.Frame(root, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Push-to-Talk 快捷键", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        ttk.Label(
            frame,
            text="按住该组合键开始录音，松开后自动识别并输入。",
            wraplength=380,
        ).pack(anchor="w", pady=(4, 12))

        current_var = tk.StringVar(value=format_hotkey(current_hotkey))
        status_var = tk.StringVar(value="点击下方按钮后，按下新的快捷键组合。")

        ttk.Label(frame, text="当前快捷键：").pack(anchor="w")
        ttk.Label(frame, textvariable=current_var, font=("Segoe UI", 12)).pack(anchor="w", pady=(0, 8))
        ttk.Label(frame, textvariable=status_var, foreground="#555").pack(anchor="w", pady=(0, 12))

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x")

        capture_btn = ttk.Button(buttons, text="录制新快捷键")
        cancel_btn = ttk.Button(buttons, text="取消", command=root.destroy)
        cancel_btn.pack(side="right")

        capturing = {"active": False}

        def resume_listener() -> None:
            if on_resume_listener:
                on_resume_listener()

        def finish() -> None:
            resume_listener()
            root.destroy()

        def on_capture_complete(raw_hotkey: str) -> None:
            capturing["active"] = False
            capture_btn.config(state="normal")
            normalized = normalize_hotkey(raw_hotkey)
            ok, error = validate_hotkey(normalized)
            if not ok:
                status_var.set(error)
                messagebox.showerror("无效快捷键", error, parent=root)
                return
            on_save(normalized)
            finish()

        def capture_worker() -> None:
            try:
                hotkey = keyboard.read_hotkey(suppress=False)
                root.after(0, lambda: on_capture_complete(hotkey))
            except Exception as exc:
                root.after(0, lambda: _capture_failed(str(exc)))

        def _capture_failed(message: str) -> None:
            capturing["active"] = False
            capture_btn.config(state="normal")
            status_var.set(f"录制失败：{message}")
            resume_listener()

        def start_capture() -> None:
            if capturing["active"]:
                return
            capturing["active"] = True
            capture_btn.config(state="disabled")
            status_var.set("正在录制…请按下新的快捷键组合。")
            if on_pause_listener:
                on_pause_listener()
            threading.Thread(target=capture_worker, daemon=True, name="HotkeyCapture").start()

        capture_btn.config(command=start_capture)
        capture_btn.pack(side="right", padx=(0, 8))

        def on_close() -> None:
            if capturing["active"]:
                keyboard.unhook_all()
            finish()

        root.protocol("WM_DELETE_WINDOW", on_close)
        root.mainloop()
