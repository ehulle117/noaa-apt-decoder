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

## How it works

APT audio is a 2400 Hz subcarrier amplitude-modulated with image data, sent
at a fixed 4160 words/second (2 lines/sec x 2080 words/line, each line
carrying sync + telemetry + image data for both the A and B channels).
`decode.py` takes the Hilbert transform envelope of the audio, resamples it
to 4160 Hz, and reshapes it into 2080-pixel-wide rows.
