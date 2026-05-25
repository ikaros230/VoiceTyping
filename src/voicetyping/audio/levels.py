"""Audio level analysis helpers."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

DEFAULT_LOW_VOLUME_RMS = 0.015


@dataclass(frozen=True)
class AudioLevelInfo:
    peak: float
    rms: float
    is_quiet: bool


def compute_peak(audio: np.ndarray) -> float:
    if audio.size == 0:
        return 0.0
    return float(np.max(np.abs(audio)))


def compute_rms(audio: np.ndarray) -> float:
    if audio.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(audio))))


def analyze_audio(audio: np.ndarray, low_volume_rms: float = DEFAULT_LOW_VOLUME_RMS) -> AudioLevelInfo:
    peak = compute_peak(audio)
    rms = compute_rms(audio)
    return AudioLevelInfo(peak=peak, rms=rms, is_quiet=rms < low_volume_rms)
