"""Demo script: transcribe a WAV file."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import numpy as np
from scipy.io import wavfile

from voicetyping.stt.whisper_engine import WhisperEngine

INPUT = Path(__file__).resolve().parent.parent / "test.wav"


def main() -> None:
    if not INPUT.exists():
        print(f"File not found: {INPUT}")
        print("Run scripts/demo_record.py first to create a test recording.")
        sys.exit(1)

    sample_rate, data = wavfile.read(str(INPUT))
    if data.dtype == np.int16:
        audio = data.astype(np.float32) / 32768.0
    else:
        audio = data.astype(np.float32)

    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    if sample_rate != 16000:
        print(f"Warning: expected 16 kHz, got {sample_rate} Hz")

    print("Transcribing...")
    engine = WhisperEngine(model_size="base", language="zh")
    text = engine.transcribe(audio)
    print(f"Result: {text}")


if __name__ == "__main__":
    main()
