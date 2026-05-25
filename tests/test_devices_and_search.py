"""Tests for audio devices and history search."""

from unittest.mock import patch

from voicetyping.audio.devices import get_device_label, list_input_devices
from voicetyping.audio.recorder import AudioRecorder
from voicetyping.history.store import HistoryStore


def test_list_input_devices():
    mock_devices = [
        {"name": "Speakers", "max_input_channels": 0, "max_output_channels": 2},
        {"name": "Mic Array", "max_input_channels": 2, "max_output_channels": 0},
        {"name": "Headset", "max_input_channels": 1, "max_output_channels": 1},
    ]
    with patch("voicetyping.audio.devices.sd.query_devices", return_value=mock_devices):
        with patch("voicetyping.audio.devices.sd.default.device", (1, 2)):
            devices = list_input_devices()

    assert len(devices) == 2
    assert devices[0].name == "Mic Array"
    assert devices[1].name == "Headset"
    assert devices[0].is_default is True


def test_get_device_label_default():
    assert get_device_label(None) == "系统默认"


def test_recorder_set_device_while_idle():
    recorder = AudioRecorder(device=1)
    assert recorder.set_device(2) is True
    assert recorder.device == 2


def test_history_search():
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmp:
        store = HistoryStore(path=Path(tmp) / "history.json")
        store.add("今天天气很好", "simplified")
        store.add("Meeting notes", "simplified")
        store.add("明天开会", "simplified")

        assert len(store.search("天")) == 2
        assert len(store.search("meeting")) == 1
        assert store.search("") == store.get_all()
