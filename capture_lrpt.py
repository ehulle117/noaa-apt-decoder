#!/usr/bin/env python3
"""Record raw IQ of a Meteor-M2 LRPT pass with an RTL-SDR.

Usage: python3 capture_lrpt.py <freq_mhz> <duration_seconds> <output.raw>
Example: python3 capture_lrpt.py 137.9M 600 pass.raw
"""
import subprocess
import sys

# RTL-SDR only accepts sample rates in ~225001-300000 or ~900001-3200000 Hz
# (hardware gap in between); 140000 silently falls back to something else.
# 250000 stays in the low valid range with headroom for 72k/80k baud LRPT.
SAMPLE_RATE = 250000


def capture(freq: str, duration: int, out_raw: str) -> None:
    n_samples = SAMPLE_RATE * duration
    subprocess.run(
        [
            "rtl_sdr", "-f", freq, "-s", str(SAMPLE_RATE), "-g", "45", "-p", "0",
            "-n", str(n_samples), out_raw,
        ],
        check=True,
    )


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <freq_mhz e.g. 137.9M> <duration_s> <output.raw>")
        sys.exit(1)
    freq_arg, duration_arg, out_arg = sys.argv[1:4]
    capture(freq_arg, int(duration_arg), out_arg)
