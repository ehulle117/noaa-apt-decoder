#!/usr/bin/env python3
"""Decode a raw IQ LRPT capture (from capture_lrpt.py) into an image.

Wraps two external tools:
- meteor_demod: raw IQ -> soft-QPSK symbols
- meteor_decode: soft-QPSK symbols -> BMP image (converted to PNG here)

Usage: python3 decode_lrpt.py <input.raw> <output.png> [symrate] [samplerate]
"""
import subprocess
import sys
import tempfile

from PIL import Image

DEFAULT_SYMRATE = 72000
DEFAULT_SAMPLERATE = 250000  # must match capture_lrpt.py's SAMPLE_RATE


def decode(raw_path: str, png_path: str, symrate: int = DEFAULT_SYMRATE,
           samplerate: int = DEFAULT_SAMPLERATE) -> None:
    with tempfile.NamedTemporaryFile(suffix=".s") as sym_f, \
         tempfile.NamedTemporaryFile(suffix=".bmp") as bmp_f:
        subprocess.run(
            [
                "meteor_demod", "-B", "-s", str(samplerate), "-r", str(symrate),
                "--bps", "8", "-o", sym_f.name, raw_path,
            ],
            check=True,
        )
        subprocess.run(
            ["meteor_decode", "-B", "-d", "-o", bmp_f.name, sym_f.name],
            check=True,
        )
        Image.open(bmp_f.name).save(png_path)


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4, 5):
        print(f"Usage: {sys.argv[0]} <input.raw> <output.png> [symrate] [samplerate]")
        sys.exit(1)
    args = sys.argv[1:]
    raw, png = args[0], args[1]
    symrate = int(args[2]) if len(args) > 2 else DEFAULT_SYMRATE
    samplerate = int(args[3]) if len(args) > 3 else DEFAULT_SAMPLERATE
    decode(raw, png, symrate, samplerate)
    print(f"Wrote {png}")
