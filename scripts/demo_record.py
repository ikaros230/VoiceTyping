"""Demo script: record audio and save to WAV file."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import numpy as np
from scipy.io import wavfile

from voicetyping.audio.recorder import AudioRecorder, SAMPLE_RATE

DURATION = 3.0
OUTPUT = Path(__file__).resolve().parent.parent / "test.wav"


def main() -> None:
    print(f"Recording {DURATION}s... Speak now!")
    recorder = AudioRecorder()
    audio = recorder.record_for(DURATION)

    if audio.size == 0:
        print("No audio captured. Check your microphone.")
        sys.exit(1)

    # Convert float32 [-1, 1] to int16 for WAV
    audio_int16 = (audio * 32767).clip(-32768, 32767).astype(np.int16)
    wavfile.write(str(OUTPUT), SAMPLE_RATE, audio_int16)
    print(f"Saved {len(audio) / SAMPLE_RATE:.1f}s audio to {OUTPUT}")


if __name__ == "__main__":
    main()
