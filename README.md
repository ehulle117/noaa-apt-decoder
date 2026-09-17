# noaa-apt-decoder

Record and decode NOAA weather satellite APT images with an RTL-SDR dongle.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Also requires `rtl_fm` (from `rtl-sdr`) and `sox` on your PATH:

```bash
brew install rtl-sdr sox
```

## Usage

1. Find the next overhead pass of NOAA-15/18/19 for your location (e.g.
   n2yo.com or heavens-above.com) and note its frequency and duration.
2. Record the pass:
   ```bash
   python3 capture.py noaa18 600 pass.wav
   ```
3. Decode it into an image:
   ```bash
   python3 decode.py pass.wav pass.png
   ```

Run `python3 decode.py --self-check` to sanity-check the decode pipeline
against a synthetic signal without needing a real recording.

## Automatic scheduling (indefinite capture)

`schedule_passes.py` predicts every NOAA-15/18/19 pass above 20° elevation
for the next ~26 hours (via Skyfield + fresh Celestrak TLEs) and installs
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

APT audio is a 2400 Hz subcarrier amplitude-modulated with image data, sent
at a fixed 4160 words/second (2 lines/sec x 2080 words/line, each line
carrying sync + telemetry + image data for both the A and B channels).
`decode.py` takes the Hilbert transform envelope of the audio, resamples it
to 4160 Hz, and reshapes it into 2080-pixel-wide rows.
