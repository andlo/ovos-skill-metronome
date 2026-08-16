#!/usr/bin/env python3
"""Regenerates sounds/accent.wav and sounds/click.wav - short
generated sine-wave clicks with an exponential-decay envelope
(no external audio samples, no licensing, nothing to source).

Usage: python3 scripts/generate_clicks.py
"""
import wave
import struct
import math
from pathlib import Path

SOUNDS_DIR = Path(__file__).resolve().parent.parent / "sounds"


def generate_click(path, freq, duration_ms=45, sample_rate=44100, volume=0.6):
    n = int(sample_rate * duration_ms / 1000)
    with wave.open(str(path), "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        frames = []
        for i in range(n):
            t = i / sample_rate
            # fast attack, exponential decay - avoids pops at start/end
            envelope = math.exp(-i / (n * 0.25))
            sample = volume * envelope * math.sin(2 * math.pi * freq * t)
            frames.append(struct.pack("<h", int(sample * 32767)))
        f.writeframes(b"".join(frames))


if __name__ == "__main__":
    SOUNDS_DIR.mkdir(exist_ok=True)
    # accent = higher pitch (downbeat), click = lower pitch (regular beat)
    generate_click(SOUNDS_DIR / "accent.wav", freq=1500)
    generate_click(SOUNDS_DIR / "click.wav", freq=900)
    print(f"wrote {SOUNDS_DIR / 'accent.wav'} and {SOUNDS_DIR / 'click.wav'}")
