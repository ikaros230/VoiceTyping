"""Local speech-to-text using faster-whisper."""

from __future__ import annotations

import os
from typing import Optional

import numpy as np
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000


class WhisperEngine:
    """Wraps faster-whisper for offline speech recognition."""

    def __init__(
        self,
        model_size: str = "base",
        device: str = "auto",
        compute_type: str = "default",
        language: str = "zh",
        hf_endpoint: Optional[str] = None,
        model_path: Optional[str] = None,
    ) -> None:
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type if compute_type != "default" else self._default_compute_type(device)
        self.language = language
        self.hf_endpoint = hf_endpoint
        self.model_path = model_path
        self._model: Optional[WhisperModel] = None

    @staticmethod
    def _default_compute_type(device: str) -> str:
        if device == "cuda":
            return "float16"
        return "int8"

    def _apply_hf_endpoint(self) -> None:
        if self.hf_endpoint:
            os.environ["HF_ENDPOINT"] = self.hf_endpoint.rstrip("/")

    def _model_id(self) -> str:
        if self.model_path:
            return self.model_path
        return self.model_size

    def _ensure_model(self) -> WhisperModel:
        if self._model is None:
            model_id = self._model_id()
            print(f"[WhisperEngine] Loading model '{model_id}'...")
            if self.hf_endpoint and not self.model_path:
                print(f"[WhisperEngine] Using HuggingFace mirror: {self.hf_endpoint}")
            self._apply_hf_endpoint()
            try:
                self._model = WhisperModel(
                    model_id,
                    device=self.device,
                    compute_type=self.compute_type,
                )
            except Exception as exc:
                raise RuntimeError(
                    f"无法加载模型 '{model_id}'：{exc}\n"
                    "若在国内网络，请确认 config.json 中 hf_endpoint 为 https://hf-mirror.com；"
                    "或手动下载模型后设置 model_path。"
                ) from exc
            print("[WhisperEngine] Model ready.")
        return self._model

    def transcribe(self, audio: np.ndarray, beam_size: int = 5) -> str:
        """Transcribe a float32 mono audio array at 16 kHz."""
        if audio.size == 0:
            return ""

        model = self._ensure_model()
        segments, _info = model.transcribe(
            audio,
            language=self.language,
            beam_size=beam_size,
        )
        return "".join(segment.text for segment in segments).strip()

    def warmup(self) -> None:
        """Pre-load the model to reduce first-transcription latency."""
        try:
            self._ensure_model()
        except Exception as exc:
            print(f"[WhisperEngine] {exc}")
