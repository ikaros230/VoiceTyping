"""Audio input device discovery."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import sounddevice as sd


@dataclass(frozen=True)
class InputDevice:
    index: int
    name: str
    is_default: bool


def list_input_devices() -> list[InputDevice]:
    """Return available audio input devices."""
    devices = sd.query_devices()
    default_index = sd.default.device[0]
    if default_index is None or default_index < 0:
        default_index = None

    result: list[InputDevice] = []
    for index, info in enumerate(devices):
        if info["max_input_channels"] < 1:
            continue
        result.append(
            InputDevice(
                index=index,
                name=str(info["name"]),
                is_default=index == default_index,
            )
        )
    return result


def get_device_label(device_index: Optional[int]) -> str:
    """Return a human-readable label for a device index, or '系统默认'."""
    if device_index is None:
        return "系统默认"

    for device in list_input_devices():
        if device.index == device_index:
            label = device.name
            if device.is_default:
                label += " (默认)"
            return label

    return f"设备 #{device_index}"
