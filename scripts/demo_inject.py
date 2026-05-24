"""Demo script: record → transcribe → inject into active window."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from voicetyping.output.windows import WindowsTextInjector
from voicetyping.pipeline import VoicePipeline

DURATION = 5.0


def main() -> None:
    print(f"Recording {DURATION}s... Focus a text field, then speak!")
    pipeline = VoicePipeline(injector=WindowsTextInjector())
    text = pipeline.record_transcribe_and_inject(duration=DURATION)
    print(f"Injected: {text}")


if __name__ == "__main__":
    main()
