"""Microphone device selection dialog."""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Optional

from voicetyping.audio.devices import InputDevice, get_device_label, list_input_devices


class MicDialog:
    """Dialog to choose an audio input device."""

    @classmethod
    def open(
        cls,
        current_device: Optional[int],
        on_save: Callable[[Optional[int]], None],
    ) -> None:
        threading.Thread(
            target=cls._run,
            args=(current_device, on_save),
            daemon=True,
            name="MicDialog",
        ).start()

    @classmethod
    def _run(cls, current_device: Optional[int], on_save: Callable[[Optional[int]], None]) -> None:
        try:
            devices = list_input_devices()
        except Exception as exc:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("错误", f"无法获取麦克风列表：{exc}")
            root.destroy()
            return

        root = tk.Tk()
        root.title("选择麦克风")
        root.geometry("480x220")
        root.resizable(False, False)

        frame = ttk.Frame(root, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="录音输入设备", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        ttk.Label(
            frame,
            text="选择用于语音输入的麦克风，保存后立即生效。",
            wraplength=440,
        ).pack(anchor="w", pady=(4, 12))

        options: list[tuple[str, Optional[int]]] = [("系统默认", None)]
        for device in devices:
            label = device.name
            if device.is_default:
                label += " (默认)"
            options.append((label, device.index))

        labels = [label for label, _ in options]
        current_label = get_device_label(current_device)
        if current_label not in labels:
            current_label = labels[0]

        selected = tk.StringVar(value=current_label)
        combo = ttk.Combobox(frame, textvariable=selected, values=labels, state="readonly", width=52)
        combo.pack(fill="x", pady=(0, 16))

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x")

        def save() -> None:
            label = selected.get()
            device_index = None
            for option_label, index in options:
                if option_label == label:
                    device_index = index
                    break
            on_save(device_index)
            root.destroy()

        ttk.Button(buttons, text="保存", command=save).pack(side="right")
        ttk.Button(buttons, text="取消", command=root.destroy).pack(side="right", padx=(0, 8))

        if not devices:
            messagebox.showwarning("提示", "未检测到可用麦克风设备。", parent=root)

        root.mainloop()
