"""Tests for audio level analysis."""

import numpy as np

from voicetyping.audio.levels import analyze_audio, compute_rms


def test_compute_rms_silent():
    audio = np.zeros(16000, dtype=np.float32)
    assert compute_rms(audio) == 0.0


def test_analyze_audio_detects_quiet():
    audio = np.full(16000, 0.001, dtype=np.float32)
    info = analyze_audio(audio, low_volume_rms=0.015)
    assert info.is_quiet is True


def test_analyze_audio_detects_normal():
    audio = np.full(16000, 0.2, dtype=np.float32)
    info = analyze_audio(audio, low_volume_rms=0.015)
    assert info.is_quiet is False
