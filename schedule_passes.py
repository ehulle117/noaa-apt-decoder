#!/usr/bin/env python3
"""Schedule tomorrow's NOAA APT passes as one-shot cron jobs.

Run daily (itself via cron) so pass capture continues indefinitely with no
manual pass-checking. Skips passes that overlap a previous one since there's
only one SDR.
"""
import subprocess
from pathlib import Path
from zoneinfo import ZoneInfo

from passes import upcoming_passes

REPO_DIR = Path(__file__).parent.resolve()
LOCAL_TZ = ZoneInfo("America/New_York")


def build_cron_line(pass_info: dict) -> str:
    local_start = pass_info["start"].astimezone(LOCAL_TZ)
    basename = f"{pass_info['satellite']}_{local_start:%Y-%m-%dT%H%M}"
    # capture a little past the predicted end to not clip the tail
    duration = pass_info["duration_s"] + 30
    log = REPO_DIR / "passes" / f"{basename}.log"
    return (
        f"{local_start.minute} {local_start.hour} {local_start.day} {local_start.month} * "
        f"{REPO_DIR}/run_pass.sh {pass_info['satellite']} {duration} {basename} >> {log} 2>&1"
    )


def schedule(hours: int = 26) -> None:
    passes = upcoming_passes(hours)

    scheduled = []
    last_end = None
    for p in passes:
        if last_end is not None and p["start"] < last_end:
            continue  # overlaps the previous scheduled pass, skip
        scheduled.append(p)
        last_end = p["end"]

    existing = subprocess.run(
        ["crontab", "-l"], capture_output=True, text=True
    ).stdout
    # drop any run_pass.sh lines we previously scheduled, keep everything else
    kept_lines = [l for l in existing.splitlines() if "run_pass.sh" not in l]
    new_lines = kept_lines + [build_cron_line(p) for p in scheduled]

    subprocess.run(["crontab", "-"], input="\n".join(new_lines) + "\n", text=True, check=True)

    print(f"Scheduled {len(scheduled)} pass(es):")
    for p in scheduled:
        print(f"  {p['satellite']:8s} {p['start'].astimezone(LOCAL_TZ):%Y-%m-%d %H:%M} local  "
              f"max_el={p['max_elevation_deg']}°")


if __name__ == "__main__":
    (REPO_DIR / "passes").mkdir(exist_ok=True)
    schedule()
