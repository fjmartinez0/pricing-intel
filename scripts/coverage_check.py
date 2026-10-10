"""Check that tonight's discovery search was thorough. Never stops the run; if coverage is light it
sends one low-priority message to the problems topic so a weak search doesn't go unnoticed.

Usage: python3 scripts/coverage_check.py proposals/2026-10-12.json [--dry-run]
"""
import json
import os
import subprocess
import sys

MINIMUM = {"Canada": 12, "Colombia": 12, "United States": 10}
MIN_WATCHLIST = 15


def main():
    path = sys.argv[1]
    dry = "--dry-run" in sys.argv
    with open(path, encoding="utf-8") as f:
        prop = json.load(f)
    counts = prop.get("searches_by_country") or {}
    gaps = ["%s %s/%s" % (c, counts.get(c, 0), m) for c, m in MINIMUM.items() if (counts.get(c) or 0) < m]
    checked = len(prop.get("watchlist_checked") or [])
    if checked < MIN_WATCHLIST:
        gaps.append("watchlist %d/%d" % (checked, MIN_WATCHLIST))
    print("Coverage: %s; watchlist employers checked: %d" % (counts, checked))
    if not gaps:
        print("Coverage OK")
        return 0
    msg = "Light search tonight: " + ", ".join(gaps) + ". Results may be incomplete."
    print(msg)
    here = os.path.dirname(os.path.abspath(__file__))
    cmd = [sys.executable, os.path.join(here, "notify.py"), "--fail", msg] + (["--dry-run"] if dry else [])
    subprocess.run(cmd, check=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
