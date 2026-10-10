"""Send ntfy alerts.

New-role alert: only for opportunities that did not exist before this run, located in Canada or
Colombia, and not closed/inactive. Reposts, closures, strategy changes and quiet days send nothing.
Failure alert (--fail): goes to a separate low-priority topic.

Config comes from environment variables (see config.example.env):
  NTFY_SERVER (default https://ntfy.sh), NTFY_TOPIC, NTFY_FAIL_TOPIC, DASHBOARD_URL

Usage:
  python3 scripts/notify.py --before .run/before.json --after data/opportunities.json [--dry-run]
  python3 scripts/notify.py --fail "message"
"""
import argparse
import json
import os
import sys
import urllib.request

import common as c

MAX_SINGLE = 3


def send(topic, message, title=None, priority="default", click=None, dry_run=False):
    server = os.environ.get("NTFY_SERVER", "https://ntfy.sh").rstrip("/")
    if dry_run or not topic:
        print("[%s] %s%s" % (topic or "no topic set", (title + ": ") if title else "", message))
        return
    headers = {"Priority": priority}
    if title:
        headers["Title"] = title.encode("utf-8").decode("latin-1", "ignore")
    if click:
        headers["Click"] = click
    req = urllib.request.Request("%s/%s" % (server, topic), data=message.encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req, timeout=20) as r:
        r.read()


def new_roles(before, after):
    old_ids = {j["id"] for j in before}
    return [j for j in after if j["id"] not in old_ids
            and j.get("country") in c.CORE_COUNTRIES
            and j.get("lifecycle_status") not in ("inactive", "closed")]


def line(j):
    place = j.get("city") or j.get("country")
    text = "New opportunity at %s: %s (%s)" % (j["company"], j["title"], place)
    if j.get("lifecycle_status") != "active":
        text += ", not yet verified"
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--before")
    ap.add_argument("--after")
    ap.add_argument("--fail")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    click = os.environ.get("DASHBOARD_URL")

    if a.fail:
        send(os.environ.get("NTFY_FAIL_TOPIC"), a.fail, title="Pricing tracker problem",
             priority="low", click=click, dry_run=a.dry_run)
        return 0

    with open(a.before, encoding="utf-8") as f:
        before = json.load(f)
    with open(a.after, encoding="utf-8") as f:
        after = json.load(f)
    roles = new_roles(before, after)
    topic = os.environ.get("NTFY_TOPIC")
    if not roles:
        print("No new Canada/Colombia roles; no alert sent")
        return 0
    if len(roles) <= MAX_SINGLE:
        for j in roles:
            send(topic, line(j), click=click, dry_run=a.dry_run)
    else:
        names = ", ".join(sorted({j["company"] for j in roles}))
        send(topic, "%d new opportunities: %s" % (len(roles), names), click=click, dry_run=a.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
