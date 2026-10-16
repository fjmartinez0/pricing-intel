"""One-time migration (2026-10-15): level bands for all roles, and exclude strategy records for
unnamed (confidential) employers. Safe to run more than once."""
import common as c

jobs = c.load("opportunities.json")
for j in jobs:
    if j.get("level_band") not in c.LEVEL_BANDS:
        j["level_band"] = "manager_plus"
    j.setdefault("level", None)
c.save("opportunities.json", jobs)

strategy = c.load("strategy.json")
for s in strategy:
    if c.is_confidential(s.get("company")) and s.get("analysis_status") != "excluded":
        s["analysis_status"] = "excluded"
        s["excluded_reason"] = "Employer not named"
        print("excluded", s["id"], s["company"])
c.save("strategy.json", strategy)
print("level bands set on", len(jobs), "roles")
