"""Integrity rules. Any failure stops the run before anything is published.

Usage: python3 scripts/validate.py [--base-ref <git ref>]
With --base-ref, the data is also compared with that commit: no records removed, first_seen
never changed, and every changed last_verified_active backed by a positive check.
"""
import argparse
import json
import re
import subprocess
import sys

import common as c

URL_RE = re.compile(r"https?://")


def at_ref(ref, name):
    try:
        out = subprocess.run(["git", "show", "%s:data/%s" % (ref, name)], cwd=c.ROOT,
                             capture_output=True, text=True, check=True).stdout
        return json.loads(out)
    except (subprocess.CalledProcessError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-ref")
    args = ap.parse_args()
    errs = []
    E = errs.append

    jobs = c.load("opportunities.json")
    strategy = c.load("strategy.json")
    people = c.load("people.json")
    checks = c.load_checks()
    meta = c.load("meta.json")
    baseline = meta["baseline_date"]
    positive = {(e["job_id"], e["date"]) for e in checks if e.get("result") == "positive"}

    ids = [j["id"] for j in jobs]
    if len(ids) != len(set(ids)):
        E("duplicate opportunity IDs")
    for j in jobs:
        jid = j["id"]
        if not re.fullmatch(r"JOB-(\d{4}|H\d{3})", jid):
            E("%s: bad ID format" % jid)
        if j["lifecycle_status"] not in c.LIFECYCLE:
            E("%s: bad lifecycle %r" % (jid, j["lifecycle_status"]))
        if j.get("scope_fit") not in c.SCOPE_FIT:
            E("%s: bad scope_fit" % jid)
        if j.get("country") not in c.COUNTRIES:
            E("%s: bad country %r" % (jid, j.get("country")))
        if not j.get("first_seen"):
            E("%s: missing first_seen" % jid)
        if j["lifecycle_status"] == "active" and not j.get("last_verified_active"):
            E("%s: active without a verified date" % jid)
        if j["lifecycle_status"] in ("inactive", "closed") and not j.get("inactive_date"):
            E("%s: %s without inactive_date" % (jid, j["lifecycle_status"]))
        if not (j.get("official_url") or j.get("secondary_url")):
            E("%s: no URL" % jid)
        lv = j.get("last_verified_active")
        if lv and lv > baseline and (jid, lv) not in positive:
            E("%s: last_verified_active %s has no positive check in checks.jsonl" % (jid, lv))

    sids = [s["id"] for s in strategy]
    if len(sids) != len(set(sids)):
        E("duplicate strategy IDs")
    for s in strategy:
        for f in ["pricing_theme", "posting_evidence", "interpretation", "caveat"]:
            if URL_RE.search(s.get(f) or ""):
                E("%s: URL in %s (not allowed on Pricing Strategy)" % (s["id"], f))
        if s.get("confidence") not in c.CONFIDENCE:
            E("%s: bad confidence %r" % (s["id"], s.get("confidence")))
        for lj in s["linked_job_ids"]:
            if lj not in ids:
                E("%s: links unknown job %s" % (s["id"], lj))
    for p in people:
        if p.get("opportunity_id") and p["opportunity_id"] not in ids:
            E("%s: links unknown job" % p["id"])
        prof = p.get("linkedin_profile")
        if prof and "linkedin.com/in/" not in prof:
            E("%s: profile URL is not a LinkedIn profile" % p["id"])

    if args.base_ref:
        for name, key in [("opportunities.json", "id"), ("strategy.json", "id"), ("people.json", "id")]:
            old = at_ref(args.base_ref, name)
            if old is None:
                continue
            new_ids = {x[key] for x in c.load(name)}
            for x in old:
                if x[key] not in new_ids:
                    E("%s removed from %s (records are never deleted)" % (x[key], name))
        old_jobs = {j["id"]: j for j in (at_ref(args.base_ref, "opportunities.json") or [])}
        for j in jobs:
            o = old_jobs.get(j["id"])
            if not o:
                continue
            if o.get("first_seen") != j.get("first_seen"):
                E("%s: first_seen changed" % j["id"])
            ov, nv = o.get("last_verified_active"), j.get("last_verified_active")
            if ov and not nv:
                E("%s: last_verified_active erased" % j["id"])
            if ov and nv and nv < ov:
                E("%s: last_verified_active moved backwards" % j["id"])
            if nv and nv != ov and (j["id"], nv) not in positive:
                E("%s: last_verified_active %s not backed by a check" % (j["id"], nv))

    if errs:
        print("VALIDATION FAILED")
        print("\n".join(" - " + e for e in errs))
        return 1
    print("Validation passed: %d opportunities, %d strategy records, %d people" % (len(jobs), len(strategy), len(people)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
