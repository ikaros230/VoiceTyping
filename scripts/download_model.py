"""Pre-download the Whisper model."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from voicetyping.config.settings import load_settings
from voicetyping.stt.whisper_engine import WhisperEngine


def main() -> None:
    settings = load_settings()
    print(f"Downloading model: {settings.model_size}")
    if settings.hf_endpoint:
        print(f"Mirror: {settings.hf_endpoint}")

    engine = WhisperEngine(
        model_size=settings.model_size,
        device=settings.device,
        language=settings.language,
        hf_endpoint=settings.hf_endpoint,
        model_path=settings.model_path,
    )
    engine.warmup()
    print("Done. Model is cached locally.")


if __name__ == "__main__":
    main()
