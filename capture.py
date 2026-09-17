#!/usr/bin/env python3
"""Record a NOAA APT pass with an RTL-SDR and save it as a WAV file.

Usage: python3 capture.py <freq_mhz> <duration_seconds> <output.wav>
Example: python3 capture.py 137.9125 600 pass.wav
"""
import subprocess
import sys

NOAA_FREQS = {
    "noaa15": "137.6200M",
    "noaa18": "137.9125M",
    "noaa19": "137.1000M",
}


def capture(freq: str, duration: int, out_wav: str) -> None:
    # rtl_fm demodulates FM -> raw audio; sox resamples/converts to a WAV
    # at 11025 Hz, the rate decode.py expects.
    rtl_fm = subprocess.Popen(
        [
            "rtl_fm", "-f", freq, "-M", "fm", "-s", "60k", "-g", "45", "-p", "0",
            "-E", "deemp", "-",
        ],
        stdout=subprocess.PIPE,
    )
    sox = subprocess.Popen(
        [
            "sox", "-t", "raw", "-r", "60000", "-e", "signed", "-b", "16", "-c", "1",
            "-", out_wav, "rate", "11025",
        ],
        stdin=rtl_fm.stdout,
    )
    try:
        sox.wait(timeout=duration)
    except subprocess.TimeoutExpired:
        pass
    finally:
        rtl_fm.terminate()
        sox.terminate()
        sox.wait()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <freq_mhz|noaa15|noaa18|noaa19> <duration_s> <output.wav>")
        print(f"Known satellites: {NOAA_FREQS}")
        sys.exit(1)
    freq_arg, duration_arg, out_arg = sys.argv[1:4]
    freq = NOAA_FREQS.get(freq_arg, freq_arg)
    capture(freq, int(duration_arg), out_arg)
