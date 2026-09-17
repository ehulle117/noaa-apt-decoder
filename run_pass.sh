#!/bin/bash
# Capture + decode one pass, then remove its own one-shot cron line.
# Usage: run_pass.sh <satellite> <duration_seconds> <output_basename>
set -e
cd "$(dirname "$0")"
source venv/bin/activate

SAT="$1"
DURATION="$2"
BASENAME="$3"

mkdir -p passes
python3 capture.py "$SAT" "$DURATION" "passes/${BASENAME}.wav"
python3 decode.py "passes/${BASENAME}.wav" "passes/${BASENAME}.png"

crontab -l | grep -v "${BASENAME}" | crontab -
