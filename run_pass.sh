#!/bin/bash
# Capture + decode + post one LRPT pass, then remove its own one-shot cron
# line - always, even on failure, so a bad pass doesn't leave a stale entry.
#
# The RTL-SDR can only be held by one process at a time. adsb-tools runs
# dump1090-mutability persistently (systemd) plus its own poller/bridge -
# stop all of it before capturing and restart after, so a scheduled pass
# never silently fails with "device busy" again.
set -e
export PATH="/usr/local/bin:$PATH"  # cron's minimal PATH lacks /usr/local/bin, where meteor_demod/meteor_decode live
cd "$(dirname "$0")"
source venv/bin/activate

FREQ="$1"
DURATION="$2"
BASENAME="$3"
DISCORD_CHANNEL_ID="1550242832512458752"

stop_adsb() {
  sudo systemctl stop dump1090-mutability 2>/dev/null || true
  pkill -9 -f 'http.server 28080' 2>/dev/null || true
  pkill -9 -f "$HOME/adsb-tools/run.py" 2>/dev/null || true
  sleep 1
}

start_adsb() {
  ( cd "$HOME/adsb-tools" && ./start.sh >> adsb_restart.log 2>&1 ) || true
}

cleanup() {
  start_adsb
  crontab -l | grep -v "${BASENAME}" | crontab -
}
trap cleanup EXIT

stop_adsb

mkdir -p passes
python3 capture_lrpt.py "$FREQ" "$DURATION" "passes/${BASENAME}.raw"
python3 decode_lrpt.py "passes/${BASENAME}.raw" "passes/${BASENAME}.png"
python3 post_discord.py "$DISCORD_CHANNEL_ID" "passes/${BASENAME}.png" "Meteor-M2-4 LRPT pass: ${BASENAME}"
