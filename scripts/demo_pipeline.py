"""Demo script: record → transcribe → print."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from voicetyping.pipeline import VoicePipeline

DURATION = 5.0


def main() -> None:
    print(f"Recording {DURATION}s... Speak now!")
    pipeline = VoicePipeline()
    text = pipeline.record_and_transcribe(duration=DURATION)
    print(f"Result: {text}")


if __name__ == "__main__":
    main()
