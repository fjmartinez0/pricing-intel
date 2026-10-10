"""One-time addition (2026-10-10): Twilio's Colombia role (verified on its Greenhouse board) and
strategy analyses for software companies: Twilio, Cisco, Gusto, Veeam.
Run after add_us_2026_10_10.py. Safe to run more than once."""
import common as c

T = "2026-10-10"
V = "Employer posting checked and open (manual review 2026-10-10)"
N = lambda date, summary, source, url: {"date": date, "summary": summary, "source": source, "url": url}

TWILIO_JOB = dict(
    company="Twilio", title="Senior Price Realization Strategy Manager", business_unit="Monetization & Pricing Strategy",
    category="Pricing", country="Colombia", city="Anywhere", work_mode="Remote", work_model="Remote, based in Colombia",
    location_note="Remote; must be based in Colombia; occasional travel", salary_advertised="Not stated",
    employer_posting_date=None, requisition_id="7078821", official_url="https://job-boards.greenhouse.io/twilio/jobs/7078821",
    secondary_url=None, check={"type": "greenhouse", "board": "twilio", "id": "7078821"},
    summary="Shape pricing and discounting strategy and build pricing operations with Product, Deal Desk and Finance; reports to the Director of Monetization & Pricing Strategy; 8+ years, 3+ in B2B SaaS pricing.",
    pricing_focus="Price realization; discount governance; usage pricing", strategy_confidence="Medium",
    title_aliases=[], first_seen=T, last_verified_active=T, lifecycle_status="active", verification_note=V,
    scope_fit="in_scope", scope_note=None, repost_count=0, last_active=None, inactive_date=None)

STRATS = [
 dict(company="Twilio", country="Colombia", business_unit="Monetization & Pricing Strategy", industry="Software",
  pricing_theme="Tightening price realization on a usage-priced communications platform",
  current_model="Pay-as-you-go usage pricing per message and minute (SMS from $0.0083, outbound voice $0.014 per minute) with volume discounts as usage grows; custom enterprise deals through sales; some per-user pricing (Flex at $150 per named user per month). Carrier A2P fees are passed through at cost.",
  posting_evidence=[
   "Senior Price Realization Strategy Manager; remote, must be based in Colombia; reports to the Director of Monetization & Pricing Strategy.",
   "Shapes pricing and discounting strategy, weighing price elasticity, product strategy and competitive differentiation.",
   "Builds pricing operational processes with Product, Deal Desk, Finance, GTM Strategy, Sales and Marketing.",
   "Requires 8+ years, 3+ with significant B2B SaaS pricing responsibility; consumption and subscription experience desired; Tableau or Looker dashboards."],
  news=[N("2026-08-06", "Q2 2026: revenue $1.50B (+22%, 17% organic); dollar-based net expansion 116% vs 108% a year earlier; non-GAAP gross margin 49% vs 51%; full-year growth guidance raised.", "Twilio press release", "https://www.twilio.com/en-us/press/releases/q2-2026-earnings")],
  interpretation="Growth has re-accelerated and expansion is strong, but gross margin slipped two points, so the priority is keeping more of each dollar of usage: less discount leakage on large deals and tighter volume tiers and commitments. Putting \"price realization\" next to Deal Desk means the job measures the gap between list and achieved price and closes it through discount governance, rather than setting list prices. Basing the role in Colombia suggests Twilio is building a nearshore pricing operations capability.",
  open_questions=["How much discount authority does sales have today, and how is realization measured?", "Will newer AI voice products get their own pricing?", "Is the scope global or the Americas?"],
  caveat="The posting names no products; the margin link and the nearshore reading are inferences.", confidence="Medium"),
 dict(company="Cisco", country="United States", business_unit="Product pricing", industry="Software",
  pricing_theme="Portfolio pricing discipline: annual SKU reviews and new consumption metrics",
  current_model="List prices by SKU for hardware, software subscriptions and services, sold mostly through partners at a discount. Splunk is priced by data ingested or by workload, with activity-based pricing in controlled availability.",
  posting_evidence=[
   "Senior Manager, Pricing Strategy and Monetization (Remote); many US states; USD 180,200–242,200 base; posted Aug 17, 2026.",
   "Develops and executes pricing and monetization strategy across the hardware and software portfolio with product, finance and sales.",
   "Leads annual pricing reviews, competitive and market analysis, price elasticity studies and scalable pricing tools."],
  news=[
   N("2026-08-01", "Price changes on select software and services took effect, set SKU by SKU; legacy support offers stopped being sold after Jul 25, 2026.", "Schneider IT Management (reseller summary)", "https://www.schneider.im/cisco-software-pricing-and-support-changes/"),
   N("2026-09-18", "Splunk introduced activity-based pricing in controlled availability, charging when data is searched rather than when it is indexed.", "TechTarget", "https://www.techtarget.com/it-infrastructure/news/366650721/Seismic-shift-in-Splunk-pricing-spotlights-AI-data-management")],
  interpretation="Cisco runs pricing as an annual, SKU-by-SKU discipline and is consolidating support offers, which simplifies the catalogue and moves customers to newer support tiers. Splunk's activity-based pricing shows Cisco testing consumption metrics that suit AI-era data volumes. This role centres on running the annual cycle and the analytics behind it (elasticity, benchmarks), which suits an analytical pricing manager more than a packaging innovator.",
  open_questions=["Which part of the portfolio does the role cover: networking, security or Splunk?", "How much of realized price is decided by partner discounts versus list price?"],
  caveat="The price-change details come from a reseller summary, not Cisco; the posting names no products.", confidence="Medium"),
 dict(company="Gusto", country="United States", business_unit="Product pricing", industry="Software",
  pricing_theme="Packaging an SMB platform expanding from payroll into HR and embedded finance",
  current_model="Three plans priced as a monthly base plus a per-person fee: Simple $49 + $6, Plus $80 + $12, Premium $180 + $22. Many paid add-ons, e.g. next-day pay $15/mo + $3 per person, business compliance $85/mo per state, Gusto Money Plus $19/mo.",
  posting_evidence=[
   "Senior Pricing and Monetization Manager; hybrid in seven US cities or remote from Toronto; USD 152,000–218,000 or CAD 133,000–160,000.",
   "Leads pricing and packaging across payroll, time and HR, and embedded financial services.",
   "Works with product, finance, marketing, sales and data, with executive visibility on pricing KPIs.",
   "Described as an AI-native role that builds MVPs quickly."],
  news=[],
  interpretation="Gusto charges a base fee plus per-employee fees with a long list of add-ons, so growth now comes from attaching more products (time, HR, compliance, financial services) to each customer. Owning packaging across these lines points to folding add-ons into tiers or bundles, and deciding which financial services earn fees versus serve retention. The \"AI-native, build MVPs\" framing suggests fast pricing experiments rather than annual repricing.",
  open_questions=["Will add-ons be bundled into tiers?", "How will embedded financial services be monetized: fees, float or interchange?", "Does Toronto signal a Canadian pricing push?"],
  caveat="No first-party pricing announcement found in recent months; prices are from Gusto's pricing page in October 2026.", confidence="Medium"),
 dict(company="Veeam", country="United States", business_unit="Monetization strategy", industry="Software",
  pricing_theme="Pricing a new data-and-AI security platform on top of a per-workload backup business",
  current_model="Veeam Data Platform editions (such as Essentials, Foundation and Advanced) sold as annual subscriptions in Universal License instance packs, per reseller listings.",
  posting_evidence=[
   "Senior Director Monetization Strategy; remote, Bay Area or Seattle.",
   "Develops go-to-market monetization strategy and economic models; refines packaging and pricing for resilience and AI security offerings.",
   "Leads data analysis and customer research; launches and measures pricing initiatives globally with marketing, product and sales."],
  news=[N("2026-05-12", "Launched the DataAI Command Platform, combining the acquired Securiti AI with Veeam's resilience products; new resilience modules in preview for existing customers with no re-migration; no pricing disclosed.", "Veeam press release", "https://www.veeam.com/company/press-release/veeam-launches-dataai-command-platform-the-industrys-first-unified-data-and-ai-trust-infrastructure-for-the-agentic-era.html")],
  interpretation="Veeam bought its way into data and AI security and now has to price it next to a per-workload backup business. The core decisions are whether security is sold as add-on modules to existing customers (an upsell) or as a new platform tier, and which value metric fits security: workloads, data volume, identities or AI assets. Hiring at senior director level signals that packaging of the combined portfolio is still open.",
  open_questions=["Add-on modules or a new platform tier?", "What value metric will AI security use?", "What migration incentives will the installed base get?"],
  caveat="The launch release gives no editions or prices; the posting was only partly readable.", confidence="Medium"),
]

jobs = c.load("opportunities.json")
if not any(c.norm_url(j.get("official_url")) == c.norm_url(TWILIO_JOB["official_url"]) and j["country"] == "Colombia" for j in jobs):
    rec = dict(TWILIO_JOB); rec["id"] = c.next_id([j["id"] for j in jobs], "JOB-")
    order = ["id"] + [k for k in jobs[0].keys() if k != "id"]
    jobs.append({k: rec.get(k) for k in order + [k for k in rec if k not in order]})
    c.append_check({"date": T, "job_id": rec["id"], "url": rec["official_url"], "result": "positive",
                    "method": "manual_review", "http_status": 200, "note": V})
    c.save("opportunities.json", jobs)
    print("added", rec["id"], "Twilio / Colombia")

strategy = c.load("strategy.json")
for s in STRATS:
    linked = sorted(j["id"] for j in jobs if j["company"] == s["company"] and j["lifecycle_status"] == "active"
                    and (j["country"] == s["country"] or s["company"] == "Gusto"))
    if not linked:
        print("skipped", s["company"], "(no verified role found; run add_us_2026_10_10.py first)")
        continue
    existing = next((x for x in strategy if c.norm(x["company"]) == c.norm(s["company"])), None)
    rec = {k: v for k, v in s.items() if k != "country"}
    rec.update(linked_job_ids=linked, last_updated=T, analysis_status="analyzed")
    if existing:
        existing.update(rec)
        print("updated", existing["id"], s["company"])
    else:
        rec.update(id=c.next_id([x["id"] for x in strategy], "STR-"), baseline_date=T)
        strategy.append(rec)
        print("added", rec["id"], s["company"])
c.save("strategy.json", strategy)
