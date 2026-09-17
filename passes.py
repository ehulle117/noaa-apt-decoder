#!/usr/bin/env python3
"""Compute upcoming Meteor-M2 LRPT satellite passes for a ground location.

Fetches fresh TLEs from Celestrak and predicts every pass above a minimum
elevation in the next N hours - no scraping, no browser, just orbital math.

NOAA APT (NOAA-15/18/19) was fully decommissioned in 2025; Meteor-M2-4 is
the current standard LRPT target (verify at db.satnogs.org before relying
on this list long-term, since satellites do go dark).
"""
import datetime
import sys

import requests
from skyfield.api import EarthSatellite, load, wgs84

LAT, LON, ALT_M = 42.4430, -76.5019, 120  # Ithaca, NY

SATELLITES = {
    "meteor-m2-4": ("59051", "137.9000M"),
}

MIN_ELEVATION_DEG = 20  # lower passes are weak/noisy for a fixed antenna


def fetch_tle(norad_id: str) -> tuple[str, str]:
    url = f"https://celestrak.org/NORAD/elements/gp.php?CATNR={norad_id}&FORMAT=tle"
    lines = requests.get(url, timeout=15).text.strip().splitlines()
    return lines[-2], lines[-1]


def upcoming_passes(hours: int = 24) -> list[dict]:
    ts = load.timescale()
    observer = wgs84.latlon(LAT, LON, ALT_M)
    now = ts.now()
    end = ts.from_datetime(now.utc_datetime() + datetime.timedelta(hours=hours))

    results = []
    for sat_key, (norad_id, freq) in SATELLITES.items():
        line1, line2 = fetch_tle(norad_id)
        sat = EarthSatellite(line1, line2, sat_key, ts)

        t, events = sat.find_events(observer, now, end, altitude_degrees=MIN_ELEVATION_DEG)
        # events: 0=rise above min elevation, 1=culminate, 2=set below min elevation.
        # The first/last pass in the window may be clipped (missing its rise
        # or set), so scan for consecutive 0,1,2 triplets rather than assuming
        # every window starts aligned on a rise.
        for i in range(len(events) - 2):
            if events[i] != 0 or events[i + 1] != 1 or events[i + 2] != 2:
                continue
            rise_t, culminate_t, set_t = t[i], t[i + 1], t[i + 2]
            alt, _, _ = (sat - observer).at(culminate_t).altaz()
            results.append({
                "satellite": sat_key,
                "freq": freq,
                "start": rise_t.utc_datetime(),
                "end": set_t.utc_datetime(),
                "max_elevation_deg": round(alt.degrees, 1),
                "duration_s": int((set_t.utc_datetime() - rise_t.utc_datetime()).total_seconds()),
            })
    results.sort(key=lambda p: p["start"])
    return results


if __name__ == "__main__":
    hours = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    for p in upcoming_passes(hours):
        print(f"{p['satellite']:8s} {p['start']:%Y-%m-%d %H:%M:%S} UTC  "
              f"{p['duration_s']:4d}s  max_el={p['max_elevation_deg']:5.1f}°")
