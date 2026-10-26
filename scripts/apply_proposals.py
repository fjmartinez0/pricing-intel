"""Merge Claude's daily proposal file into the dataset, deterministically.

Claude never edits data/ directly. It writes proposals/YYYY-MM-DD.json; this script decides
what is accepted. It assigns IDs, de-duplicates against history (reposts link to the existing
ID), sets first_seen, and never touches verification dates (only recheck.py does that).

Usage: python3 scripts/apply_proposals.py proposals/2026-10-12.json [--dry-run]
"""
import argparse
import json
import re
import sys

import common as c

URL_RE = re.compile(r"https?://\S+")
JOB_FIELDS = ["company", "title", "business_unit", "category", "country", "city", "work_model", "work_mode", "location_note",
              "salary_advertised", "employer_posting_date", "official_url", "secondary_url",
              "requisition_id", "summary", "pricing_focus", "scope_fit", "scope_note",
              "strategy_confidence", "level_band", "level"]


def clean(v):
    if isinstance(v, str):
        v = v.strip()
        return v or None
    return v


def is_url(v):
    return isinstance(v, str) and v.startswith(("https://", "http://"))


def find_match(jobs, p):
    req = c.norm(p.get("requisition_id"))
    urls = {c.norm_url(p.get("official_url")), c.norm_url(p.get("secondary_url"))} - {""}
    key = (c.norm(p.get("company")), c.norm(p.get("title")), p.get("country"))
    for j in jobs:
        if req and c.norm(j.get("requisition_id")) == req and c.norm(j.get("company")) == key[0]:
            return j
        if urls & ({c.norm_url(j.get("official_url")), c.norm_url(j.get("secondary_url"))} - {""}):
            return j
        aliases = [c.norm(a.split("(")[0]) for a in j.get("title_aliases", [])]
        if c.norm(j.get("company")) == key[0] and j.get("country") == key[2] and \
                (c.norm(j.get("title")) == key[1] or key[1] in aliases):
            return j
    return None


def validate_job(p):
    errs = []
    for f in ["company", "title", "category", "country", "city", "summary"]:
        if not clean(p.get(f)):
            errs.append("missing " + f)
    if p.get("category") not in c.CATEGORIES:
        errs.append("bad category %r" % p.get("category"))
    if p.get("country") not in c.COUNTRIES:
        errs.append("bad country %r" % p.get("country"))
    if p.get("scope_fit", "in_scope") not in c.SCOPE_FIT:
        errs.append("bad scope_fit")
    if c.out_of_scope(p.get("title")):
        errs.append("out of scope (freight forwarding, costing or solution design)")
    band = p.get("level_band") or "manager_plus"
    if band not in c.LEVEL_BANDS:
        errs.append("bad level_band %r" % band)
    if band == "analyst":
        if p.get("country") not in c.ANALYST_COUNTRIES:
            errs.append("analyst-level roles are tracked for Canada and Colombia only")
        if p.get("level") not in c.ANALYST_LEVELS:
            errs.append("analyst-level role needs level in %s" % ", ".join(c.ANALYST_LEVELS))
        if not c.PRICING_TITLE.search(c.norm(p.get("title"))):
            errs.append("analyst-level role must name pricing/RGM/revenue management in the title")
    if not (is_url(p.get("official_url")) or is_url(p.get("secondary_url"))):
        errs.append("no job-level URL")
    for f in ["official_url", "secondary_url"]:
        u = p.get(f) or ""
        if re.search(r"/(search|jobs/search|ofertas-empleo/trabajo-)|[?&](q|keywords)=", u):
            errs.append("%s looks like a search page" % f)
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("proposal")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    run_date = c.today()
    with open(args.proposal, encoding="utf-8") as f:
        prop = json.load(f)
    jobs = c.load("opportunities.json")
    strategy = c.load("strategy.json")
    people = c.load("people.json")
    log = []
    ref_map = {}  # "new:N" -> assigned job ID

    # 1. New opportunities
    for n, p in enumerate(prop.get("new_opportunities", [])):
        p = {k: clean(v) for k, v in p.items()}
        lvl = c.analyst_level(p.get("title"))
        if lvl and (p.get("level_band") or "manager_plus") == "manager_plus":
            p["level_band"], p["level"] = "analyst", lvl
            log.append("BAND new:%d %s / %s set to analyst (%s) from the title" % (n, p.get("company"), p.get("title"), lvl))
        errs = validate_job(p)
        if errs:
            log.append("REJECTED new:%d %s / %s: %s" % (n, p.get("company"), p.get("title"), "; ".join(errs)))
            continue
        match = find_match(jobs, p)
        if match and match.get("close_reason") == "out_of_scope":
            log.append("SKIPPED new:%d matches %s, retired as out of scope" % (n, match["id"]))
            continue
        if match:
            ref_map["new:%d" % n] = match["id"]
            if match["lifecycle_status"] in ("inactive", "closed"):
                match["repost_count"] = match.get("repost_count", 0) + 1
                match["lifecycle_status"] = "unable_to_verify"
                match["verification_note"] = "Reposting observed %s; awaiting check" % run_date
                match.pop("close_reason", None)
                for f in ["official_url", "requisition_id"]:
                    if p.get(f) and not match.get(f):
                        match[f] = p[f]
                log.append("REPOST %s %s / %s" % (match["id"], match["company"], match["title"]))
            else:
                if p.get("official_url") and not match.get("official_url"):
                    match["official_url"] = p["official_url"]
                    log.append("URL %s official link added" % match["id"])
                log.append("DUPLICATE %s (already tracked)" % match["id"])
            continue
        new_id = c.next_id([j["id"] for j in jobs], "JOB-")
        job = {f: p.get(f) for f in JOB_FIELDS}
        job.update(id=new_id, title_aliases=[], first_seen=run_date, last_verified_active=None,
                   lifecycle_status="unable_to_verify",
                   verification_note="Found by discovery %s; awaiting check" % run_date,
                   repost_count=0, last_active=None, inactive_date=None)
        job["scope_fit"] = job.get("scope_fit") or "in_scope"
        job["level_band"] = job.get("level_band") or "manager_plus"
        if job["level_band"] == "manager_plus":
            job["level"] = job.get("level") or None
        job["salary_advertised"] = job.get("salary_advertised") or "Not stated"
        job["work_model"] = job.get("work_model") or "Not stated"
        if job.get("work_mode") not in c.WORK_MODES:
            job["work_mode"] = c.infer_work_mode(job["work_model"])
        order = ["id"] + [k for k in jobs[0].keys() if k != "id"]
        order += [k for k in job if k not in order]
        jobs.append({k: job.get(k) for k in order})
        ref_map["new:%d" % n] = new_id
        log.append("NEW %s %s / %s (%s)" % (new_id, job["company"], job["title"], job["country"]))

    # 2. Official URLs found for existing leads (fills blanks only)
    by_id = {j["id"]: j for j in jobs}
    for u in prop.get("url_updates", []):
        j = by_id.get(u.get("id"))
        url = clean(u.get("official_url"))
        if not j or not is_url(url) or c.host_in(url, c.NO_CHECK_HOSTS + c.AGGREGATOR_HOSTS):
            log.append("REJECTED url_update %s" % u.get("id"))
            continue
        if j.get("official_url"):
            log.append("SKIPPED url_update %s (already has official link)" % j["id"])
            continue
        j["official_url"] = url
        if u.get("requisition_id") and not j.get("requisition_id"):
            j["requisition_id"] = clean(u["requisition_id"])
        log.append("URL %s official link added" % j["id"])

    # 3. Strategy updates (no URLs allowed on this tab)
    for s in prop.get("strategy_updates", []):
        s = {k: clean(v) for k, v in s.items()}
        text_fields = ["pricing_theme", "current_model", "interpretation", "caveat"]
        list_fields = ["posting_evidence", "open_questions"]
        for f in text_fields:
            if isinstance(s.get(f), str):
                s[f] = URL_RE.sub("", s[f]).strip() or None
        for f in list_fields:
            v = s.get(f)
            v = [v] if isinstance(v, str) else (v or [])
            s[f] = [URL_RE.sub("", str(x)).strip() for x in v if str(x).strip()]
        news = []
        for n_ in s.get("news") or []:
            if isinstance(n_, dict) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(n_.get("date") or "")) \
                    and clean(n_.get("summary")) and clean(n_.get("source")) and is_url(n_.get("url")):
                news.append({"date": n_["date"], "summary": URL_RE.sub("", n_["summary"]).strip(),
                             "source": n_["source"].strip(), "url": n_["url"].strip()})
        s["news"] = news
        detailed = bool(s.get("interpretation")) and len(s["posting_evidence"]) >= 2
        linked = [ref_map.get(r, r) for r in (s.get("linked_job_refs") or [])]
        linked = [r for r in linked if r in by_id or r in ref_map.values()]
        if c.is_confidential(s.get("company")):
            log.append("REJECTED strategy for %s (employer not named)" % s.get("company"))
            continue
        countries = {by_id[r]["country"] for r in linked if r in by_id}
        if countries == {"United States"} and c.norm(s.get("industry")) not in ("software", "saas"):
            log.append("REJECTED strategy for %s (US analyses are for software companies only)" % s.get("company"))
            continue
        target = None
        if s.get("id"):
            target = next((x for x in strategy if x["id"] == s["id"]), None)
        if not target:
            target = next((x for x in strategy if c.norm(x["company"]) == c.norm(s.get("company"))
                           and c.norm(x["business_unit"]) == c.norm(s.get("business_unit"))), None)
        if s.get("confidence") not in c.CONFIDENCE:
            s["confidence"] = None
        if target and target.get("analysis_status") == "excluded":
            log.append("SKIPPED strategy %s (excluded: %s)" % (target["id"], target.get("excluded_reason")))
            continue
        if target:
            if not detailed and target.get("analysis_status") == "analyzed":
                target["linked_job_ids"] = sorted(set(target["linked_job_ids"]) | set(linked))
                log.append("STRATEGY linked only %s (update lacked detail)" % target["id"])
                continue
            for f in text_fields + list_fields + ["confidence", "industry"]:
                if s.get(f):
                    target[f] = s[f]
            if news:
                seen = {(x.get("date"), x.get("summary")) for x in target.get("news") or []}
                target["news"] = sorted((target.get("news") or []) + [x for x in news if (x["date"], x["summary"]) not in seen],
                                        key=lambda x: x["date"], reverse=True)[:6]
            if detailed:
                target["analysis_status"] = "analyzed"
                target.pop("insufficient_reason", None)
            target["linked_job_ids"] = sorted(set(target["linked_job_ids"]) | set(linked))
            target["last_updated"] = run_date
            log.append("STRATEGY updated %s %s" % (target["id"], target["company"]))
        elif s.get("company") and s.get("interpretation") and linked:
            new_sid = c.next_id([x["id"] for x in strategy], "STR-")
            rec = dict(id=new_sid, company=s["company"], business_unit=s.get("business_unit") or "Not identified",
                       baseline_date=run_date, last_updated=run_date,
                       pricing_theme=s.get("pricing_theme"), current_model=s.get("current_model"),
                       posting_evidence=s["posting_evidence"], news=news,
                       interpretation=s["interpretation"], open_questions=s["open_questions"],
                       caveat=s.get("caveat") or "Inference from job postings only; not a confirmed corporate initiative.",
                       confidence=s.get("confidence") or "Low", linked_job_ids=sorted(set(linked)), industry=s.get("industry"),
                       analysis_status="analyzed" if detailed else "insufficient_detail")
            if not detailed:
                rec["insufficient_reason"] = "Posting lacks specific responsibilities."
            strategy.append(rec)
            log.append("STRATEGY new %s %s" % (new_sid, s["company"]))
        else:
            log.append("REJECTED strategy update for %s" % s.get("company"))

    # 4. People (named posters / relevant contacts; never invent profile URLs)
    for p in prop.get("people", []):
        p = {k: clean(v) for k, v in p.items()}
        opp = ref_map.get(p.get("opportunity_ref"), p.get("opportunity_ref"))
        if not p.get("name") or opp not in by_id and opp not in ref_map.values() or not is_url(p.get("evidence_url")):
            log.append("REJECTED person %s" % p.get("name"))
            continue
        if any(c.norm(x["name"]) == c.norm(p["name"]) and c.norm(x["company"]) == c.norm(p.get("company")) for x in people):
            log.append("DUPLICATE person %s" % p["name"])
            continue
        ctype = p.get("contact_type") if p.get("contact_type") in ("confirmed_poster", "relevant_contact") else "relevant_contact"
        if ctype == "relevant_contact":
            if not p.get("title") or not p.get("relevance"):
                log.append("REJECTED person %s (relevant contact needs title and relevance)" % p.get("name"))
                continue
            same_co = [x for x in people if x.get("contact_type") == "relevant_contact" and c.norm(x["company"]) == c.norm(p.get("company"))]
            if len(same_co) >= c.MAX_RELEVANT_PER_COMPANY:
                log.append("SKIPPED person %s (already %d contacts at %s)" % (p["name"], len(same_co), p.get("company")))
                continue
        profile = p.get("linkedin_profile")
        if not (is_url(profile) and "linkedin.com/in/" in profile):
            profile = None
        people.append(dict(id=c.next_id([x["id"] for x in people], "PERSON-"), name=p["name"], title=p.get("title"),
                           company=p.get("company"), contact_type=ctype,
                           relationship=p.get("relationship") or ("Publicly named poster / hiring team" if ctype == "confirmed_poster" else "Relevant contact"),
                           relevance=p.get("relevance"), opportunity_id=opp, linkedin_profile=profile,
                           verification=p.get("verification") or "Named in public source",
                           evidence_url=p["evidence_url"], found_via=p.get("found_via"), first_seen=run_date, notes=p.get("notes")))
        log.append("PERSON added %s (%s)" % (p["name"], p.get("company")))

    print("\n".join(log) or "Proposal contained no changes")
    if not args.dry_run:
        c.save("opportunities.json", jobs)
        c.save("strategy.json", strategy)
        c.save("people.json", people)
    return 0


if __name__ == "__main__":
    sys.exit(main())
