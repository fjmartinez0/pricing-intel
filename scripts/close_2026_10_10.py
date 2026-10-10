"""One-time manual review (2026-10-10): close three leads with evidence found by hand.
Safe to run more than once; it only changes roles that are still open."""
import common as c

T = "2026-10-10"
CLOSE = {
    "JOB-0020": ("inactive", "removed", "https://careers.rappi.com/en/careers",
                 "Not listed on Rappi's official careers site, which shows no pricing roles (manual review 2026-10-10)"),
    "JOB-0012": ("inactive", "removed", "https://job-boards.eu.greenhouse.io/cision",
                 "Not on Cision's official Greenhouse job board, which lists 39 open roles and none in pricing (manual review 2026-10-10)"),
    "JOB-0010": ("closed", "closed", "https://www.canadajobs.works/job/fasken-pricing-manager-gestionnaire-tarification-remote-ottawa-ontario",
                 "Job listing says it has expired and is no longer accepting applications; originally posted 2026-09-11 (manual review 2026-10-10)"),
}

jobs = c.load("opportunities.json")
for j in jobs:
    if j["id"] in CLOSE and j["lifecycle_status"] in ("active", "unable_to_verify"):
        status, reason, url, note = CLOSE[j["id"]]
        j["last_active"] = j.get("last_verified_active") or j.get("last_active")
        j["lifecycle_status"], j["close_reason"] = status, reason
        j["inactive_date"] = T
        j["verification_note"] = note
        if j["id"] == "JOB-0010" and not j.get("employer_posting_date"):
            j["employer_posting_date"] = "2026-09-11"
        c.append_check({"date": T, "job_id": j["id"], "url": url, "result": status,
                        "method": "manual_review", "http_status": None, "note": note})
        print("%s %s -> %s" % (j["id"], j["company"], status))
c.save("opportunities.json", jobs)
