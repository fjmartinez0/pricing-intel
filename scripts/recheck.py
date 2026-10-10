"""Recheck known job links and update lifecycle status. No AI involved.

Rules (from the project handoff):
- active only on a positive job-level check of the official posting; that is the only thing
  that sets last_verified_active.
- closed when the source explicitly says it no longer accepts applications.
- inactive when the posting is genuinely gone (404/410/redirect to a generic page), confirmed
  on two separate runs so a one-off glitch never retires a job.
- anything else (blocking, errors, LinkedIn-only, aggregator-only) is unable_to_verify.

Usage: python3 scripts/recheck.py [--ids JOB-0001 JOB-0002] [--new-only] [--dry-run]
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from urllib.parse import urlparse

import common as c

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

CLOSED_MARKERS = [
    "no longer accepting applications", "no longer accepting", "job is no longer available",
    "this job is no longer available", "position has been filled", "this job has expired",
    "job has expired", "posting has closed", "this position is closed", "job closed",
    "ya no está disponible", "ya no esta disponible", "oferta cerrada", "vacante cerrada",
    "ya no acepta postulaciones", "n'est plus disponible", "n’est plus disponible",
    "cette offre est expirée", "the job you are looking for is no longer",
]
APPLY_MARKERS = ["apply", "postular", "postúlate", "postulate", "postuler", "candidater", "aplicar"]


def fetch(url, accept="text/html,application/xhtml+xml"):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept,
                                               "Accept-Language": "en-CA,en;q=0.9,fr;q=0.8,es;q=0.7"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read(800_000).decode("utf-8", "replace")
            return r.status, r.geturl(), body
    except urllib.error.HTTPError as e:
        return e.code, url, ""
    except Exception as e:  # network error, timeout, TLS
        return None, url, str(e)


def result(kind, method, status, note, posted=None):
    r = {"result": kind, "method": method, "http_status": status, "note": note}
    if posted and re.fullmatch(r"\d{4}-\d{2}-\d{2}", posted[:10]):
        r["posted"] = posted[:10]
    return r


def check_greenhouse(board, job_id):
    st, _, body = fetch("https://boards-api.greenhouse.io/v1/boards/%s/jobs/%s" % (board, job_id),
                        "application/json")
    if st == 200 and '"id"' in body:
        try:
            first = json.loads(body).get("first_published") or ""
        except ValueError:
            first = ""
        return result("positive", "greenhouse_api", st, "Live on Greenhouse board", first)
    if st in (404, 410):
        return result("inactive", "greenhouse_api", st, "Not on Greenhouse board")
    return result("unable_to_verify", "greenhouse_api", st, "Greenhouse API error")


def check_smartrecruiters(url):
    parts = urlparse(url).path.strip("/").split("/")
    if len(parts) < 2:
        return None
    company, job_id = parts[0], re.match(r"(\d+)", parts[1])
    if not job_id:
        return None
    st, _, body = fetch("https://api.smartrecruiters.com/v1/companies/%s/postings/%s" % (company, job_id.group(1)),
                        "application/json")
    if st == 200:
        try:
            data = json.loads(body)
        except ValueError:
            data = {}
        if data.get("active") is False:
            return result("closed", "smartrecruiters_api", st, "Posting marked inactive")
        return result("positive", "smartrecruiters_api", st, "Live on SmartRecruiters", data.get("releasedDate") or "")
    if st in (404, 410):
        return result("inactive", "smartrecruiters_api", st, "Posting not found")
    return result("unable_to_verify", "smartrecruiters_api", st, "SmartRecruiters API error")


def check_workday(url):
    u = urlparse(url)
    parts = u.path.strip("/").split("/")
    if parts and re.fullmatch(r"[a-z]{2}(-[A-Z]{2})?", parts[0]):
        parts = parts[1:]
    if len(parts) < 3 or "job" not in parts:
        return None
    tenant = u.netloc.split(".")[0]
    site = parts[0]
    rest = "/".join(parts[1:])
    api = "https://%s/wday/cxs/%s/%s/%s" % (u.netloc, tenant, site, rest)
    st, _, body = fetch(api, "application/json")
    if st == 200:
        try:
            info = json.loads(body).get("jobPostingInfo", {})
        except ValueError:
            info = {}
        if not info:
            return result("unable_to_verify", "workday_api", st, "Unexpected Workday response")
        if info.get("canApply") is False:
            return result("closed", "workday_api", st, "Workday says applications closed")
        return result("positive", "workday_api", st, "Live on Workday", info.get("startDate") or "")
    if st in (404, 410):
        return result("inactive", "workday_api", st, "Workday posting not found")
    return result("unable_to_verify", "workday_api", st, "Workday API error")


def check_generic(url, requisition_id):
    st, final, body = fetch(url)
    if st is None:
        return result("unable_to_verify", "page", None, "Network error: %s" % body[:120])
    if st in (404, 410):
        return result("inactive", "page", st, "Page not found")
    if st != 200:
        return result("unable_to_verify", "page", st, "HTTP %s (possibly blocked)" % st)
    low = body.lower()
    if any(m in low for m in CLOSED_MARKERS):
        return result("closed", "page", st, "Page says the job is closed")
    if c.norm_url(final) != c.norm_url(url):
        token = requisition_id or re.findall(r"\d{5,}", url)[-1:] or [None]
        token = token if isinstance(token, str) else token[0]
        if token and token.lower() not in final.lower():
            return result("inactive", "page", st, "Redirected to a generic page")
    if any(m in low for m in APPLY_MARKERS):
        return result("positive", "page", st, "Posting page live with apply option")
    return result("unable_to_verify", "page", st, "Page loaded but no apply option found")


def check_job(job):
    override = job.get("check") or {}
    if override.get("type") == "greenhouse":
        return check_greenhouse(override["board"], override["id"]), "https://boards-api.greenhouse.io"
    url = job.get("official_url")
    if not url:
        src = "LinkedIn" if c.host_in(job.get("secondary_url"), c.NO_CHECK_HOSTS) else "secondary listing"
        return result("unable_to_verify", "none", None,
                      "No official posting; %s only (not checked automatically)" % src), job.get("secondary_url")
    if c.host_in(url, c.NO_CHECK_HOSTS):
        return result("unable_to_verify", "none", None, "LinkedIn not checked automatically"), url
    if c.host_in(url, c.AGGREGATOR_HOSTS):
        return result("unable_to_verify", "none", None, "Aggregator link is not proof of an open job"), url
    host = urlparse(url).netloc
    r = None
    if "myworkdayjobs.com" in host:
        r = check_workday(url)
    elif "smartrecruiters.com" in host:
        r = check_smartrecruiters(url)
        if r and r["result"] == "unable_to_verify":
            r = None  # API hiccup: fall back to the public posting page
    return (r or check_generic(url, job.get("requisition_id"))), url


def previous_result(checks, job_id):
    for e in reversed(checks):
        if e.get("job_id") == job_id:
            return e
    return None


def apply_result(job, r, run_date, checks):
    """Mutates job according to the lifecycle rules. Returns a short change description."""
    before = job["lifecycle_status"]
    kind = r["result"]
    if kind == "positive":
        if before in ("inactive", "closed"):
            job["repost_count"] = job.get("repost_count", 0) + 1
            job["inactive_date"] = None
        job["lifecycle_status"] = "active"
        job["last_verified_active"] = run_date
        if r.get("posted") and not job.get("employer_posting_date"):
            job["employer_posting_date"] = r["posted"]
        job["verification_note"] = "%s (%s)" % (r["note"], run_date)
    elif kind == "closed":
        if before != "closed":
            job["last_active"] = job.get("last_verified_active") or job.get("last_active")
            job["inactive_date"] = job.get("inactive_date") or run_date
        job["lifecycle_status"] = "closed"
        job["verification_note"] = "%s (%s)" % (r["note"], run_date)
    elif kind == "inactive":
        prev = previous_result(checks, job["id"])
        if prev and prev.get("result") == "inactive":
            if before not in ("inactive", "closed"):
                job["last_active"] = job.get("last_verified_active") or job.get("last_active")
                job["inactive_date"] = prev.get("date")  # first observed removal
            job["lifecycle_status"] = "inactive"
            job["verification_note"] = "%s on two checks (%s)" % (r["note"], run_date)
        else:
            if before == "active":
                job["lifecycle_status"] = "unable_to_verify"
            job["verification_note"] = "%s; confirming on next run (%s)" % (r["note"], run_date)
    else:
        if before == "active":
            job["lifecycle_status"] = "unable_to_verify"
        if before not in ("inactive", "closed"):
            job["verification_note"] = "%s (%s)" % (r["note"], run_date)
    return "%s -> %s" % (before, job["lifecycle_status"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", nargs="*")
    ap.add_argument("--new-only", action="store_true", help="only jobs first seen today")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    run_date = c.today()
    jobs = c.load("opportunities.json")
    checks = c.load_checks()
    targets = [j for j in jobs if j["lifecycle_status"] != "closed"]
    if args.ids:
        targets = [j for j in jobs if j["id"] in args.ids]
    if args.new_only:
        targets = [j for j in jobs if j.get("first_seen") == run_date]

    for job in targets:
        r, url = check_job(job)
        entry = {"date": run_date, "job_id": job["id"], "url": url, **r}
        change = apply_result(job, r, run_date, checks)
        print("%-9s %-17s %-22s %s" % (job["id"], r["result"], change, r["note"]))
        if not args.dry_run:
            c.append_check(entry)
            checks.append(entry)

    if not args.dry_run:
        c.save("opportunities.json", jobs)
        meta = c.load("meta.json")
        meta["last_run"] = run_date
        c.save("meta.json", meta)
    return 0


if __name__ == "__main__":
    sys.exit(main())
