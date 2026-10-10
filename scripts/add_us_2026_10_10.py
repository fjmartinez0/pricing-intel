"""One-time addition (2026-10-10): US roles verified on the employer's own posting, plus Gusto's
Toronto option as a Canada role. Safe to run more than once; existing roles are skipped."""
import common as c

T = "2026-10-10"
V = "Employer posting checked and open (manual review 2026-10-10)"
BASE = dict(title_aliases=[], first_seen=T, last_verified_active=T, lifecycle_status="active", verification_note=V,
            scope_fit="in_scope", scope_note=None, secondary_url=None, repost_count=0, last_active=None,
            inactive_date=None, check=None, employer_posting_date=None, strategy_confidence="Medium")
NEW = [
 dict(company="Cisco", title="Senior Manager, Pricing Strategy and Monetization (Remote)", business_unit="Product pricing",
      category="Monetization", country="United States", city="Multiple US locations", work_mode="Remote", work_model="Remote",
      location_note="Remote in many US states; Seattle hybrid option", salary_advertised="USD 180,200–242,200 base (up to 324,100 in NYC metro)",
      employer_posting_date="2026-08-17", requisition_id="2019507",
      official_url="https://cisco.wd5.myworkdayjobs.com/Cisco_Careers/job/San-Jose-California-US/Senior-Manager--Pricing-Strategy-and-Monetization--Remote-_2019507",
      summary="Pricing and monetization strategy across Cisco's hardware and software portfolio; leads annual pricing reviews, elasticity studies and pricing tools.",
      pricing_focus="Hardware and software portfolio pricing"),
 dict(company="Gallup", title="Director of Pricing", business_unit=None, category="Pricing", country="United States", city="Omaha, NE",
      work_mode="Hybrid", work_model="On-site at least 3 days a week", location_note=None, salary_advertised="USD 150,000–250,000 (estimated)",
      requisition_id="4021000009", official_url="https://job-boards.greenhouse.io/gallup/jobs/4021000009",
      check={"type": "greenhouse", "board": "gallup", "id": "4021000009"},
      summary="Build and redesign a unified global pricing strategy across software, surveys, assessments, consulting and learning; 7+ years of global pricing.",
      pricing_focus="Multi-product global pricing"),
 dict(company="Gusto", title="Senior Pricing and Monetization Manager", business_unit=None, category="Monetization", country="United States",
      city="Denver, San Francisco, New York + 4 more", work_mode="Hybrid", work_model="2–3 days a week in office",
      location_note="Also Atlanta, Chicago, Phoenix, Las Vegas", salary_advertised="USD 152,000–218,000 by location",
      requisition_id="7904943", official_url="https://job-boards.greenhouse.io/gusto/jobs/7904943",
      check={"type": "greenhouse", "board": "gusto", "id": "7904943"},
      summary="Leads pricing and packaging across payroll, time and HR, and embedded financial services; AI-native role building MVPs and pricing KPIs.",
      pricing_focus="SMB SaaS packaging"),
 dict(company="Gusto", title="Senior Pricing and Monetization Manager", business_unit=None, category="Monetization", country="Canada",
      city="Toronto", work_mode="Remote", work_model="Remote (Toronto listing)", location_note="Same posting also lists seven US cities",
      salary_advertised="CAD 133,000–160,000", requisition_id="7904943", official_url="https://job-boards.greenhouse.io/gusto/jobs/7904943",
      check={"type": "greenhouse", "board": "gusto", "id": "7904943"},
      summary="Leads pricing and packaging across payroll, time and HR, and embedded financial services; AI-native role building MVPs and pricing KPIs.",
      pricing_focus="SMB SaaS packaging"),
 dict(company="Kenvue", title="Senior Manager, Global Revenue Growth Management Capabilities", business_unit="Global RGM", category="RGM",
      country="United States", city="Summit, NJ", work_mode="Hybrid", work_model="Hybrid", location_note=None,
      salary_advertised="USD 153,850–217,200 base", requisition_id=None,
      official_url="https://jobs.kenvue.com/senior-manager-global-revenue-growth-management-capabilities/job/CAA3AF01C1AE918A44BA96AD78C73518",
      summary="Builds global RGM playbooks, tools and training for pricing, promotions and trade investment across Kenvue markets.",
      pricing_focus="CPG RGM capabilities"),
 dict(company="3M", title="Director, Pricing Strategy & Governance", business_unit="Transportation & Electronics", category="Pricing",
      country="United States", city="Maplewood, MN", work_mode="In person", work_model="On-site at least 4 days a week", location_note=None,
      salary_advertised="USD 287,281–351,122 (base plus variable)", employer_posting_date="2026-09-29", requisition_id="R01171560",
      official_url="https://3m.wd1.myworkdayjobs.com/en-US/Search/job/Director--Pricing-Strategy---Governance_R01171560-1",
      summary="Build pricing as a core commercial function for the Transportation & Electronics group: strategy, governance, discount controls and new-product pricing; 15+ years.",
      pricing_focus="Industrial B2B pricing governance"),
 dict(company="The Home Depot", title="Sr. Manager, Pricing Strategy", business_unit=None, category="Pricing", country="United States",
      city="Atlanta, GA", work_mode="Hybrid", work_model="Hybrid", location_note=None, salary_advertised="Not stated", requisition_id="21868438",
      official_url="https://careers.homedepot.com/job/21868438/sr-manager-pricing-strategy",
      summary="Leads five direct reports developing and running pricing strategies for merchants, the Pro business and subsidiaries.",
      pricing_focus="Retail pricing"),
 dict(company="Veeam", title="Senior Director Monetization Strategy (Remote Bay Area or Seattle)", business_unit=None, category="Monetization",
      country="United States", city="Bay Area or Seattle", work_mode="Remote", work_model="Remote", location_note=None,
      salary_advertised="Not stated", requisition_id=None,
      official_url="https://careers.veeam.com/job/san-francisco/senior-director-monetization-strategy-remote-bay-area-or-seattle/22681/93992366848",
      secondary_url="https://job-boards.greenhouse.io/veeamsoftware/jobs/4834482101",
      summary="Monetization strategy and packaging for data resilience and AI security offerings; economic models, customer research, launch and measurement.",
      pricing_focus="Packaging; AI security"),
]

jobs = c.load("opportunities.json")
have = {(c.norm_url(j.get("official_url")), j.get("country")) for j in jobs}
order = list(jobs[0].keys())
for n in NEW:
    if (c.norm_url(n["official_url"]), n["country"]) in have:
        continue
    rec = dict(BASE); rec.update(n)
    rec["id"] = c.next_id([j["id"] for j in jobs], "JOB-")
    keys = ["id"] + [k for k in order if k != "id"] + [k for k in rec if k not in order and k != "id"]
    jobs.append({k: rec.get(k) for k in keys})
    c.append_check({"date": T, "job_id": rec["id"], "url": rec["official_url"], "result": "positive",
                    "method": "manual_review", "http_status": 200, "note": V})
    print("added", rec["id"], rec["company"], "/", rec["country"])
c.save("opportunities.json", jobs)
