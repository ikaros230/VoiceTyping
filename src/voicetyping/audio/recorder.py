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

    def __init__(self, sample_rate: int = SAMPLE_RATE) -> None:
        self.sample_rate = sample_rate
        self._frames: list[np.ndarray] = []
        self._stream: Optional[sd.InputStream] = None
        self._lock = threading.Lock()
        self._recording = False

    @property
    def is_recording(self) -> bool:
        return self._recording

    def _callback(self, indata: np.ndarray, _frames: int, _time, status) -> None:
        if status:
            print(f"[AudioRecorder] {status}")
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

        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=CHANNELS,
            dtype=DTYPE,
            callback=self._callback,
        )
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
