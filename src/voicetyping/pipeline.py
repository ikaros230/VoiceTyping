"""Core pipeline: record → transcribe → (optionally) inject."""

from __future__ import annotations

import threading
import time
from enum import Enum
from typing import Callable, Optional

from voicetyping.audio.recorder import AudioRecorder
from voicetyping.output.base import TextInjector
from voicetyping.stt.whisper_engine import WhisperEngine


class PipelineState(Enum):
    IDLE = "idle"
    RECORDING = "recording"
    TRANSCRIBING = "transcribing"


class VoicePipeline:
    """Orchestrates audio capture, speech recognition, and text injection."""

    def __init__(
        self,
        recorder: Optional[AudioRecorder] = None,
        engine: Optional[WhisperEngine] = None,
        injector: Optional[TextInjector] = None,
        min_record_seconds: float = 0.3,
    ) -> None:
        self.recorder = recorder or AudioRecorder()
        self.engine = engine or WhisperEngine()
        self.injector = injector
        self.min_record_seconds = min_record_seconds
        self._state = PipelineState.IDLE
        self._record_start_time: Optional[float] = None
        self._on_state_change: Optional[Callable[[PipelineState], None]] = None

    @property
    def state(self) -> PipelineState:
        return self._state

    def set_state_callback(self, callback: Callable[[PipelineState], None]) -> None:
        self._on_state_change = callback

    def _set_state(self, state: PipelineState) -> None:
        self._state = state
        if self._on_state_change:
            self._on_state_change(state)

    def start_recording(self) -> None:
        if self._state != PipelineState.IDLE:
            return
        self._record_start_time = time.monotonic()
        self._set_state(PipelineState.RECORDING)
        self.recorder.start()

    def stop_recording_and_transcribe(self) -> str:
        if self._state != PipelineState.RECORDING:
            return ""

        elapsed = time.monotonic() - (self._record_start_time or 0)
        audio = self.recorder.stop()

        if elapsed < self.min_record_seconds or audio.size == 0:
            self._set_state(PipelineState.IDLE)
            return ""

        self._set_state(PipelineState.TRANSCRIBING)
        try:
            text = self.engine.transcribe(audio)
        finally:
            self._set_state(PipelineState.IDLE)

        return text

    def record_and_transcribe(self, duration: float = 5.0) -> str:
        """Record for a fixed duration and return transcribed text."""
        self._set_state(PipelineState.RECORDING)
        audio = self.recorder.record_for(duration)
        self._set_state(PipelineState.TRANSCRIBING)
        try:
            text = self.engine.transcribe(audio)
        finally:
            self._set_state(PipelineState.IDLE)
        return text

    def record_transcribe_and_inject(self, duration: float = 5.0) -> str:
        """Record, transcribe, and inject text into the active window."""
        text = self.record_and_transcribe(duration)
        if text and self.injector:
            self.injector.inject(text)
        return text

    def stop_and_inject(self) -> None:
        """Stop push-to-talk recording, transcribe, and inject in a background thread."""

        def _worker() -> None:
            text = self.stop_recording_and_transcribe()
            if text and self.injector:
                self.injector.inject(text)

        threading.Thread(target=_worker, daemon=True).start()
