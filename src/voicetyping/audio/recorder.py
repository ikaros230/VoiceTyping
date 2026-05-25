"""Microphone audio capture for voice input."""

from __future__ import annotations

import threading
from typing import Optional

import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = "float32"


class AudioRecorder:
    """Records audio from the default microphone at 16 kHz mono."""

    def __init__(self, sample_rate: int = SAMPLE_RATE, device: Optional[int] = None) -> None:
        self.sample_rate = sample_rate
        self.device = device
        self._frames: list[np.ndarray] = []
        self._stream: Optional[sd.InputStream] = None
        self._lock = threading.Lock()
        self._recording = False
        self._current_level = 0.0
        self._peak_level = 0.0

    @property
    def current_level(self) -> float:
        with self._lock:
            return self._current_level

    @property
    def peak_level(self) -> float:
        with self._lock:
            return self._peak_level

    def reset_levels(self) -> None:
        with self._lock:
            self._current_level = 0.0
            self._peak_level = 0.0

    @property
    def is_recording(self) -> bool:
        return self._recording

    def set_device(self, device: Optional[int]) -> bool:
        """Change input device. Returns False if currently recording."""
        if self._recording:
            return False
        self.device = device
        return True

    def _callback(self, indata: np.ndarray, _frames: int, _time, status) -> None:
        if status:
            print(f"[AudioRecorder] {status}")
        chunk = indata.flatten()
        if chunk.size:
            rms = float(np.sqrt(np.mean(np.square(chunk))))
            peak = float(np.max(np.abs(chunk)))
            with self._lock:
                self._current_level = rms
                self._peak_level = max(self._peak_level, peak)
        with self._lock:
            if self._recording:
                self._frames.append(indata.copy())

    def start(self) -> None:
        """Begin recording from the microphone."""
        with self._lock:
            if self._recording:
                return
            self._frames = []
            self._recording = True
            self._current_level = 0.0
            self._peak_level = 0.0

        stream_kwargs = {
            "samplerate": self.sample_rate,
            "channels": CHANNELS,
            "dtype": DTYPE,
            "callback": self._callback,
        }
        if self.device is not None:
            stream_kwargs["device"] = self.device

        self._stream = sd.InputStream(**stream_kwargs)
        self._stream.start()

    def stop(self) -> np.ndarray:
        """Stop recording and return the captured audio as a float32 numpy array."""
        with self._lock:
            self._recording = False

        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        with self._lock:
            if not self._frames:
                return np.array([], dtype=np.float32)
            return np.concatenate(self._frames, axis=0).flatten()

    def record_for(self, duration: float) -> np.ndarray:
        """Record for a fixed duration in seconds."""
        self.start()
        sd.sleep(int(duration * 1000))
        return self.stop()
