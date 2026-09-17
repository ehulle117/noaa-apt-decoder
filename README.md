# noaa-apt-decoder

Record and decode weather satellite images with an RTL-SDR dongle.

NOAA APT (NOAA-15/18/19) was fully decommissioned in 2025 and is kept here
only for reference (`capture.py`/`decode.py`). Active development targets
**Meteor-M2-4 LRPT** (`capture_lrpt.py`/`decode_lrpt.py`), currently the
standard hobbyist target on 137.9 MHz — verify at db.satnogs.org before
relying on this long-term, since satellites do go dark.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Also requires on your PATH:
- `rtl-sdr` (`rtl_sdr`, `rtl_fm`) and `sox` — `brew install rtl-sdr sox` (or `apt install rtl-sdr sox`)
- [`meteor_demod`](https://github.com/dbdexter-dev/meteor_demod) and
  [`meteor_decode`](https://github.com/dbdexter-dev/meteor_decode) — build
  from source (`cmake && make && sudo make install` in each repo)

## Usage (LRPT / Meteor-M2-4)

1. Find the next pass (`python3 passes.py` prints upcoming Meteor-M2-4
   passes above 20° elevation for the next 24h using live TLEs — no
   manual site-checking needed).
2. Record the pass:
   ```bash
   python3 capture_lrpt.py 137.9M 600 pass.raw
   ```
3. Decode it into an image:
   ```bash
   python3 decode_lrpt.py pass.raw pass.png
   ```

## Automatic scheduling (indefinite capture)

`schedule_passes.py` predicts every satellite pass above 20° elevation for
the next ~26 hours (via Skyfield + fresh Celestrak TLEs) and installs
one-shot cron jobs that call `run_pass.sh` at each pass's start time. Each
job captures, decodes into `passes/`, and removes its own cron line when done.

Set it up once (e.g. on a Pi with the SDR permanently attached):

```bash
crontab -l 2>/dev/null | { cat; echo "5 0 * * * cd $(pwd) && venv/bin/python3 schedule_passes.py >> passes/schedule.log 2>&1"; } | crontab -
python3 schedule_passes.py   # schedule the first batch immediately
```

That daily job re-schedules the next ~26 hours every night, so it keeps
running indefinitely without needing a pass-prediction site checked by hand.

## How it works

**LRPT** is a digital QPSK signal at a fixed symbol rate (72k or 80k baud).
`capture_lrpt.py` records raw IQ with `rtl_sdr`; `decode_lrpt.py` pipes that
through `meteor_demod` (QPSK demodulation -> soft symbols) and
`meteor_decode` (Viterbi + Reed-Solomon decode -> image), then converts the
resulting BMP to PNG.

**APT** (legacy, satellites now dead) was analog: a 2400 Hz subcarrier
amplitude-modulated with image data, sent at a fixed 4160 words/second.
`decode.py` took the Hilbert transform envelope of the audio, resampled it
to 4160 Hz, and reshaped it into 2080-pixel-wide rows.
