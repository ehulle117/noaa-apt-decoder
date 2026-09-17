#!/bin/bash
# Capture + decode + post one LRPT pass, then remove its own one-shot cron
# line - always, even on failure, so a bad pass doesn't leave a stale entry.
set -e
cd "$(dirname "$0")"
source venv/bin/activate

FREQ="$1"
DURATION="$2"
BASENAME="$3"
DISCORD_CHANNEL_ID="1550242832512458752"

cleanup() {
  crontab -l | grep -v "${BASENAME}" | crontab -
}
trap cleanup EXIT

mkdir -p passes
python3 capture_lrpt.py "$FREQ" "$DURATION" "passes/${BASENAME}.raw"
python3 decode_lrpt.py "passes/${BASENAME}.raw" "passes/${BASENAME}.png"
python3 post_discord.py "$DISCORD_CHANNEL_ID" "passes/${BASENAME}.png" "Meteor-M2-4 LRPT pass: ${BASENAME}"
