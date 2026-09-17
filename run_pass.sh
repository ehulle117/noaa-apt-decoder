#!/bin/bash
# Capture + decode one LRPT pass, then remove its own one-shot cron line.
# Usage: run_pass.sh <freq_mhz> <duration_seconds> <output_basename>
set -e
cd "$(dirname "$0")"
source venv/bin/activate

FREQ="$1"
DURATION="$2"
BASENAME="$3"

mkdir -p passes
python3 capture_lrpt.py "$FREQ" "$DURATION" "passes/${BASENAME}.raw"
python3 decode_lrpt.py "passes/${BASENAME}.raw" "passes/${BASENAME}.png"

crontab -l | grep -v "${BASENAME}" | crontab -
