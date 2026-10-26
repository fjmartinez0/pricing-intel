"""One-time migration (2026-10-26). Safe to run more than once.

1. Records which level bands each country tab shows (Colombia now shows analyst-level roles too).
2. Fixes level bands: Canada/Colombia roles whose title is analyst level (Analyst, Especialista,
   Coordinador...) but were filed as manager_plus.
3. Retires out-of-scope roles (freight forwarding, costing, solution design) as Closed with
   close_reason "out_of_scope"; they are never rechecked or re-added afterwards.

Usage: python3 scripts/migrate_2026_10_26.py [--dry-run]
"""
import sys

import common as c

dry = "--dry-run" in sys.argv
today = c.today()
jobs = c.load("opportunities.json")
meta = c.load("meta.json")
changes, new_checks = [], []

if meta.get("country_tab_bands") != c.COUNTRY_TAB_BANDS:
    meta["country_tab_bands"] = c.COUNTRY_TAB_BANDS
    changes.append("meta: Colombia tab now shows analyst-level roles")

for j in jobs:
    title = j.get("title")
    lvl = c.analyst_level(title)
    if j.get("country") in c.ANALYST_COUNTRIES and j.get("level_band") == "manager_plus" and lvl:
        j["level_band"], j["level"] = "analyst", lvl
        changes.append("%s band -> analyst (%s): %s / %s" % (j["id"], lvl, j["company"], title))
    if j.get("level_band") == "analyst" and j.get("level") not in c.ANALYST_LEVELS:
        j["level"] = lvl or "Analyst"
        changes.append("%s level set to %s: %s / %s" % (j["id"], j["level"], j["company"], title))

    if c.out_of_scope(title) and j.get("close_reason") != "out_of_scope":
        was = j["lifecycle_status"]
        note = "Retired as out of scope: freight forwarding, costing or solution design (%s)" % today
        j["close_reason"] = "out_of_scope"
        if was in ("active", "unable_to_verify"):
            j["lifecycle_status"] = "inactive"
            j["last_active"] = j.get("last_verified_active") or j.get("last_active")
            j["inactive_date"] = today
        j["verification_note"] = note
        new_checks.append({"date": today, "job_id": j["id"], "url": j.get("official_url") or j.get("secondary_url"),
                           "result": "inactive", "method": "scope_review", "http_status": None, "note": note})
        changes.append("%s retired as out of scope (was %s): %s / %s" % (j["id"], was, j["company"], title))

print("\n".join(changes) or "Nothing to change (already migrated)")
if dry:
    print("(dry run: nothing saved)")
elif changes:
    c.save("opportunities.json", jobs)
    c.save("meta.json", meta)
    for e in new_checks:
        c.append_check(e)
    print("Saved %d changes" % len(changes))
