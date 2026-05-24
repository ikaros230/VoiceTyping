"""Tests for VoiceTyping core modules."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from voicetyping.audio.recorder import SAMPLE_RATE, AudioRecorder
from voicetyping.config.settings import Settings, load_settings, save_settings
from voicetyping.output.windows import WindowsTextInjector
from voicetyping.pipeline import PipelineState, VoicePipeline


def test_settings_defaults():
    settings = Settings()
    assert settings.model_size == "base"
    assert settings.language == "zh"
    assert settings.hotkey == "ctrl+shift+space"
    assert settings.restore_clipboard is True


def test_settings_save_and_load():
    with tempfile.TemporaryDirectory() as tmp:
        config_file = Path(tmp) / "config.json"
        settings = Settings(model_size="base", language="en")
        with patch("voicetyping.config.settings.config_path", return_value=config_file):
            save_settings(settings)
            loaded = load_settings()
        assert loaded.model_size == "base"
        assert loaded.language == "en"


def test_settings_invalid_file_uses_defaults():
    with tempfile.TemporaryDirectory() as tmp:
        config_file = Path(tmp) / "config.json"
        config_file.write_text("{invalid json", encoding="utf-8")
        with patch("voicetyping.config.settings.config_path", return_value=config_file):
            loaded = load_settings()
        assert loaded.model_size == "base"


def test_recorder_stop_without_start_returns_empty():
    recorder = AudioRecorder()
    audio = recorder.stop()
    assert audio.size == 0
    assert audio.dtype == np.float32


def test_pipeline_state_transitions():
    recorder = MagicMock()
    recorder.start = MagicMock()
    recorder.stop = MagicMock(return_value=np.zeros(SAMPLE_RATE, dtype=np.float32))
    engine = MagicMock()
    engine.transcribe = MagicMock(return_value="你好")

    pipeline = VoicePipeline(recorder=recorder, engine=engine, min_record_seconds=0.0)
    states = []
    pipeline.set_state_callback(lambda s: states.append(s))

    pipeline.start_recording()
    assert pipeline.state == PipelineState.RECORDING

    text = pipeline.stop_recording_and_transcribe()
    assert text == "你好"
    assert pipeline.state == PipelineState.IDLE
    assert PipelineState.RECORDING in states
    assert PipelineState.TRANSCRIBING in states


def test_pipeline_short_recording_skipped():
    recorder = MagicMock()
    recorder.start = MagicMock()
    recorder.stop = MagicMock(return_value=np.zeros(100, dtype=np.float32))
    engine = MagicMock()

    pipeline = VoicePipeline(recorder=recorder, engine=engine, min_record_seconds=10.0)
    pipeline.start_recording()
    text = pipeline.stop_recording_and_transcribe()
    assert text == ""
    engine.transcribe.assert_not_called()


def test_windows_injector_skips_empty_text():
    injector = WindowsTextInjector()
    with patch("pyperclip.copy") as mock_copy:
        injector.inject("")
        mock_copy.assert_not_called()


def test_windows_injector_pastes_text():
    injector = WindowsTextInjector(restore_clipboard=False)
    with patch("pyperclip.copy") as mock_copy, patch("keyboard.send") as mock_send:
        injector.inject("测试")
        mock_copy.assert_called_once_with("测试")
        mock_send.assert_called_once_with("ctrl+v")
