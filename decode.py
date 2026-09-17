#!/usr/bin/env python3
"""Decode a NOAA APT WAV recording (from capture.py) into a PNG image.

APT transmits at a fixed 4160 words/second: each 0.5s line is 2080 words
covering sync + telemetry + image data for both the A and B image channels.
The audio is AM: demodulate its envelope, resample to 4160 Hz, and reshape
into 2080-pixel rows.

Usage: python3 decode.py <input.wav> <output.png>
"""
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import hilbert, resample
from PIL import Image

WORDS_PER_LINE = 2080
LINE_RATE_HZ = 4160  # 2080 words/line * 2 lines/sec


def decode(wav_path: str) -> np.ndarray:
    rate, signal = wavfile.read(wav_path)
    signal = signal.astype(np.float64)

    envelope = np.abs(hilbert(signal))

    resampled_len = int(len(envelope) * LINE_RATE_HZ / rate)
    resampled = resample(envelope, resampled_len)

    # Normalize to 0-255 using 0.5/99.5 percentiles so a few noise spikes
    # don't blow out the contrast.
    lo, hi = np.percentile(resampled, (0.5, 99.5))
    scaled = np.clip((resampled - lo) * 255 / (hi - lo), 0, 255)

    n_lines = len(scaled) // WORDS_PER_LINE
    image = scaled[: n_lines * WORDS_PER_LINE].reshape(n_lines, WORDS_PER_LINE)
    return image.astype(np.uint8)


def _self_check() -> None:
    """Synthetic-signal sanity check: known line count in -> matches out."""
    rate = 11025
    n_lines = 20
    t = np.arange(int(n_lines * WORDS_PER_LINE * rate / LINE_RATE_HZ)) / rate
    carrier = np.sin(2 * np.pi * 2400 * t)
    envelope = 0.5 + 0.5 * np.sin(2 * np.pi * 0.3 * t)
    signal = (envelope * carrier * 20000).astype(np.int16)

    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wavfile.write(f.name, rate, signal)
        image = decode(f.name)
    os.unlink(f.name)

    assert image.shape[1] == WORDS_PER_LINE, f"unexpected width {image.shape[1]}"
    assert abs(image.shape[0] - n_lines) <= 1, f"unexpected line count {image.shape[0]}"
    print(f"self-check OK: decoded {image.shape[0]} lines x {image.shape[1]} px")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-check":
        _self_check()
        sys.exit(0)
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.wav> <output.png>")
        print(f"   or: {sys.argv[0]} --self-check")
        sys.exit(1)
    image = decode(sys.argv[1])
    Image.fromarray(image, mode="L").save(sys.argv[2])
    print(f"Wrote {sys.argv[2]}: {image.shape[0]} lines x {image.shape[1]} px")
