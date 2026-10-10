"""One-time data migration (2026-10-10): work_mode categories, clean city + location_note,
posting dates found on official postings, and the richer strategy records.
Keyed by ID, so it can be applied to the live dataset without touching anything else.
"""
import common as c

T = "2026-10-10"
JOBS = {
    # id: (work_mode, city, location_note, extra fields)
    "JOB-0001": ("Remote", "Anywhere", "Remote anywhere in Canada; occasional travel to Toronto", {}),
    "JOB-0002": ("Hybrid", "Montreal, Ottawa, Toronto", "3 days a week in office; must be based in Canada", {"requisition_id": "431648"}),
    "JOB-0003": ("Hybrid", "Toronto", "Toronto office or remote within the Toronto region", {}),
    "JOB-0004": ("In person", "Montreal", "Office-based", {}),
    "JOB-0005": ("In person", "Montreal", "Office-based", {}),
    "JOB-0006": ("Unknown", "Toronto", None, {}),
    "JOB-0007": ("Unknown", "Montreal", None, {}),
    "JOB-0008": ("Hybrid", "Montreal + 9 other cities", "Also North York, Kitchener, Ottawa, Calgary, Edmonton, Vancouver, Winnipeg, Moncton, Dartmouth; 2 days or 15 hours a week in office", {}),
    "JOB-0009": ("In person", "Montreal", "In-office per Built In listing; official posting does not say", {}),
    "JOB-0010": ("Remote", "Montreal", "Primarily remote per an earlier listing; not reconfirmed", {}),
    "JOB-0011": ("Remote", "Montreal, Quebec City", "Remote from Montreal with monthly travel, per an earlier listing", {}),
    "JOB-0012": ("Remote", "Anywhere", "Remote in Canada, per secondary listings", {}),
    "JOB-0013": ("Hybrid", "Not stated", "Official posting gives no city; earlier tracker recorded Montreal", {}),
    "JOB-0014": ("Unknown", "Vaudreuil-Dorion", None, {}),
    "JOB-0015": ("Hybrid", "Toronto", "Hybrid per an earlier listing", {}),
    "JOB-0016": ("Remote", "Anywhere", "Must reside in or hold a work permit for Colombia, Mexico or Peru", {}),
    "JOB-0017": ("Unknown", "Bogotá", "Occasional global travel", {"employer_posting_date": "2026-08-12"}),
    "JOB-0018": ("Hybrid", "Bogotá", "Hybrid per Adecco listing; official posting does not say", {"employer_posting_date": "2026-08-12"}),
    "JOB-0019": ("Hybrid", "Bogotá", None, {}),
    "JOB-0020": ("Unknown", "Bogotá", None, {}),
    "JOB-0021": ("Unknown", "Bogotá", None, {}),
    "JOB-0022": ("Unknown", "Bogotá", None, {}),
    "JOB-0023": ("Unknown", "Bogotá", None, {}),
    "JOB-H001": ("Unknown", "Bogotá", None, {}),
    "JOB-H002": ("Unknown", "Not stated", None, {}),
}

N = lambda date, summary, source, url: {"date": date, "summary": summary, "source": source, "url": url}

STRATEGY = {
 "STR-0001": dict(
  pricing_theme="First dedicated pricing owner: moving from one unlimited seat price to tiered, value-metric packaging",
  current_model="Seat-based annual subscription. Individual plan US$1,498 per user per year with unlimited questions and drafting; Team and Enterprise plans quoted by sales. No usage-based component is published.",
  posting_evidence=[
   "Director level, reports to the VP of GTM Strategy & Operations; remote in Canada; posted Oct 7, 2026; base 165,000–206,500.",
   "Owns plans, tiers, bundles and add-ons, value-metric selection, discount and renewal guidelines, and a monetization roadmap.",
   "Willingness-to-pay research, segmentation, win/loss and churn analysis, competitor price monitoring.",
   "Runs pricing experiments and rolls changes through CPQ, billing and reporting; trains Sales and Customer Success.",
   "Asks for seat, usage, value-based and hybrid model experience; AI product monetization is a plus."],
  news=[],
  interpretation="A single unlimited seat price suits sole practitioners but undercharges larger firms, and it exposes margin because AI inference cost grows with usage while price does not. The focus on value metrics, add-ons and hybrid models points to good-better-best tiers with a usage or capability fence and firm-level packaging as Blue J expands into new segments in North America and the UK. The CPQ and billing mandate shows this is an early-stage function: the hire sets the pricing operating model, not just price levels.",
  open_questions=["Is unlimited usage still profitable at current inference costs?", "Which value metric will replace or complement seats: firms, users, jurisdictions or volume?", "Who owns pricing decisions today, founders or sales?"],
  caveat="One posting; Blue J has made no public statement about pricing changes.",
  confidence="Medium"),
 "STR-0002": dict(
  pricing_theme="Enterprise solution pricing: bundled TCO-based deals, tighter discount governance, AI-assisted deal pricing",
  current_model="Custom enterprise contracts across IoT, mobility and 5G, cloud, cybersecurity, voice, collaboration and contact centre, and internet and private networks. Prices are not public.",
  posting_evidence=[
   "Senior product manager, Strategic Pricing, in Bell Business Markets Operations; hybrid, 3 days in office; Montreal, Ottawa or Toronto; posted Oct 6, deadline Oct 20, 2026.",
   "Builds pricing structures using total-cost-of-ownership and SWOT analysis; enforces pricing governance standards.",
   "Optimizes margin and competitiveness by segment and vertical; gathers competitive intelligence; trains sales.",
   "Requires practical AI and machine-learning knowledge for pricing, forecasting or dynamic pricing."],
  news=[
   N("2026-08-06", "Q2 2026 results: wireless industry pricing improved quarter over quarter and year over year; Bell plans less handset discounting; strong enterprise net adds including a large government contract.", "Yahoo Finance (BCE Q2 earnings call)", "https://finance.yahoo.com/technology/articles/bce-inc-bce-q2-2026-190501108.html"),
   N("2026-05-07", "CEO reaffirmed revenue targets for Bell AI Fabric data centres; the 300 MW Saskatchewan site's first phase is due in the first half of 2027.", "BNN Bloomberg", "https://www.bnnbloomberg.ca/business/company-news/2026/05/07/bell-ceo-confident-in-lofty-revenue-targets-as-it-doubles-down-on-ai-data-centres/")],
  interpretation="Bell is trying to protect enterprise margin while its mix shifts from connectivity to cloud, security and AI infrastructure. TCO-based structures and governance language point to bundled solution pricing and stricter discount control in a segment where reps have traded price for volume. The AI requirement suggests Bell wants guided deal pricing, such as price recommendations and win probability, rather than manual desk pricing. The pricing discipline management described for wireless in Q2 is likely being extended to enterprise.",
  open_questions=["Does the role cover AI Fabric and data-centre pricing, or only telecom and IT bundles?", "Is there an existing deal desk, and how much discount authority do reps have?"],
  caveat="The posting does not mention AI Fabric; that link is inference.",
  confidence="Medium"),
 "STR-0003": dict(
  pricing_theme="Pricing a stream of AI and agent features on top of a consumption business",
  current_model="Atlas is consumption-priced (cluster size and hours, storage, data transfer; free, flex and dedicated tiers) and was about 73% of revenue in Q2 FY27. Enterprise Advanced is a self-managed subscription.",
  posting_evidence=[
   "Pricing & Monetization Associate in Product; Toronto office or remote in the Toronto region; CAD 101,000–140,000; first published Aug 12, 2026.",
   "Leads pricing and packaging for new launches and changes to existing offerings, with business cases and trade-offs.",
   "Models revenue, margin, cohorts and usage; translates infrastructure cost and technical dependencies into unit economics.",
   "Drives SKU, billing, selling and tooling execution; benchmarks competitors; presents to leadership.",
   "Requires 5+ years including 2–3 in consulting or tech strategy."],
  news=[
   N("2026-09-01", "Q2 FY27: revenue $771.8M (+30%), Atlas $565.9M (+29%), 2,999 customers above $100K ARR; guidance raised on Atlas.", "MongoDB press release", "https://www.prnewswire.com/news-releases/mongodb-inc-announces-second-quarter-fiscal-2027-financial-results-302866656.html"),
   N("2026-09-01", "Launched the Atlas Managed MCP Server and made Automated Embeddings (Voyage AI), the Embedding and Reranking API and voyage-code-4 generally available; Search and Vector Search reached Enterprise Advanced.", "MongoDB press release", "https://www.prnewswire.com/news-releases/mongodb-inc-announces-second-quarter-fiscal-2027-financial-results-302866656.html")],
  interpretation="MongoDB is shipping AI retrieval and agent products (embeddings, reranking, a managed MCP server) that each need a price metric different from cluster hours, typically per token or per request. The posting's emphasis on infrastructure cost and SKUs indicates prices are built from cost-to-serve to protect Atlas gross margin as AI workloads grow. Bringing Vector Search to Enterprise Advanced also raises how to price AI capabilities inside self-managed licences.",
  open_questions=["Will AI features be metered separately or bundled as credits in Atlas tiers?", "How will Voyage models be priced against OpenAI and Cohere embeddings?"],
  caveat="The release gives no AI pricing figures; per-token metering is inference.",
  confidence="Medium"),
 "STR-0004": dict(
  pricing_theme="Resetting a live game's economy, retention-first, while in-game spending carries the company",
  current_model="Premium game sales plus in-game purchases (virtual currency, store items, battle passes). Player recurring investment was 60.6% of FY26 net bookings.",
  posting_evidence=[
   "Two concurrent Montreal roles, both office-based: Monetization Director and Associate Monetization Director. The game is not named.",
   "Director: long-term monetization plan that respects the game's core values, integrated into core gameplay; owns the virtual store catalogue and microtransaction pricing; defines KPIs; 7+ years.",
   "Associate Director: leads the microtransaction and player-engagement team; owns store and currency pricing, including hard and soft currency rebalancing; leads a Battle Pass redesign and new offers; forecasting; cross-brand partnerships and licensing."],
  news=[
   N("2026-05-20", "FY26: net bookings €1,525M (−17.4%); player recurring investment €925M (+14.7%), 60.6% of the total; FY27 guided down high single digits; 7 projects cancelled and 6 delayed; Vantage Studios formed with €1.16bn from Tencent.", "Ubisoft earnings release", "https://staticctf.ubisoft.com/8aefmxkxpxwl/1LR2VCCkksmsZ3BDdDrpQW/3bbed93696b39f8e2d8cebf527afb025/Ubisoft_FY26_PR_English_vF.pdf"),
   N("2026-07-12", "Ubisoft removed the claim that monetization makes games \"more fun\" from its annual report.", "Kotaku", "https://kotaku.com/ubisoft-drops-claim-that-monetization-makes-games-more-fun-from-annual-report-2000715026")],
  interpretation="In-game spending is now most of Ubisoft's revenue while premium sales fall, so monetization quality directly drives the turnaround. Hiring a director and a deputy together, with currency rebalancing and a Battle Pass redesign in scope, signals a reset of an existing title's economy rather than a new launch. The \"respects the core values of the game\" wording and the annual-report change point to deliberately less aggressive, retention-first monetization.",
  open_questions=["Which title is this, and is it run by Vantage Studios or a creative house?", "Is pricing set centrally or per game team?"],
  caveat="The game is not named; any link to Vantage Studios is not stated in the postings.",
  confidence="High"),
 "STR-0005": dict(
  pricing_theme="Value-based deal pricing as AI cuts the hours behind each engagement",
  current_model="Professional-services fees, mostly time-and-materials and fixed-fee engagements priced from rate cards by staff level.",
  posting_evidence=[
   "Associate Director, Pricing Strategy (Commercial Excellence), Toronto; posted Oct 2, 2026.",
   "Builds EY Canada's pricing capability: market insights, pricing strategy and change management.",
   "Sets pricing for large deals and strategic pursuits using value-based pricing tied to AI-enabled delivery.",
   "Standardizes pricing models, commercial structures and negotiation approaches across service lines; analyses deal economics; builds firm-wide tools and training."],
  news=[
   N("2026-04-07", "EY rolled out agentic AI across its global audit platform, EY Canvas: 130,000 Assurance professionals and 160,000 engagements, with end-to-end coverage targeted by 2028.", "EY newsroom", "https://www.ey.com/en_ca/newsroom/2026/04/ey-launches-enterprise-scale-agentic-ai-to-redefine-the-audit-experience-for-the-ai-era")],
  interpretation="When AI agents do work that used to be billed by the hour, fees fall unless price is tied to outcomes or deliverables. EY Canada is building a central pricing function to move large pursuits to fixed, value or outcome-based structures instead of leaving each partner to improvise. The emphasis on standard models and negotiation playbooks suggests margin leakage from inconsistent discounting is a current problem.",
  open_questions=["Does the scope include audit fees, which are regulated and AI-heavy, or only advisory and consulting?", "How are partners measured: revenue, margin or utilisation?"],
  caveat="The audit AI rollout is global; the posting is specific to Canada.",
  confidence="High"),
 "STR-0007": dict(
  pricing_theme="Building a direct-to-consumer insurance channel with its own ML-based pricing",
  current_model="Personal auto and home insurance sold mainly through brokers, with premiums set through provincially regulated rate filings.",
  posting_evidence=[
   "Director, Direct Venture Pricing; hybrid, 2 days a week; 10 Canadian locations including Montreal; estimated $170,000–220,000; posted Sep 26, 2026.",
   "Owns financial performance and pricing for a direct-to-member portfolio covering insurance and non-insurance products.",
   "Builds AI, machine-learning and predictive pricing models with governance, validation, monitoring and compliance.",
   "Prepares pricing proposals and business cases that meet provincial and federal rules; builds and leads a team."],
  news=[
   N("2026-06-02", "Wawanesa told brokers (by letter in March) that it is exploring a direct-to-consumer buying site and possibly captive agents, while promising not to compete with brokers; brokers are sceptical.", "Canadian Underwriter", "https://canadianunderwriter.ca/2026/06/02/brokers-respond-to-wawanesas-plan-to-add-a-direct-channel/")],
  interpretation="The posting moves the direct channel from \"exploring\" in June to building a priced product with its own P&L. A separate team with ML rating suggests direct premiums will come from their own models rather than broker rates, to compete with digital direct insurers such as belairdirect and Sonnet. Non-insurance products imply bundles or add-ons to raise revenue per member. Broker channel conflict will limit how far direct prices can undercut broker prices.",
  open_questions=["Which provinces and products launch first?", "Will the same risk be priced differently direct and through brokers?"],
  caveat="Launch timing, brand and provinces are not public.",
  confidence="High"),
 "STR-0008": dict(
  pricing_theme="Turning API access into metered revenue, next extending it to AI agents through MCP",
  current_model="Autodesk Platform Services: a free tier with monthly caps on four rated APIs; paid use through prepaid Flex tokens or pay-as-you-go. Data Model API usage is included with product subscriptions, pooled at team level, with paid overage.",
  posting_evidence=[
   "Official title Senior Program Manager, API Business Models (listed on LinkedIn as Senior Manager, API Monetization Strategy); Montreal, in-office; reposted around Oct 1, 2026.",
   "Defines and prioritizes business requirements and policies for the API monetization model and tracks how partners execute them.",
   "Thought leader on API monetization and its extension to MCP server monetization.",
   "Coordinates programs across teams."],
  news=[
   N("2025-12-07", "APS moved to Free and Paid tiers: monthly caps on four rated APIs, paid use via Flex tokens or pay-as-you-go, with migration required by Feb 18, 2026.", "Autodesk Platform Services blog", "https://aps.autodesk.com/blog/aps-business-model-evolution"),
   N("2026-08-17", "Manufacturing Data Model API pricing took effect: usage included with qualifying subscriptions, pooled at team level, overage paid.", "Autodesk Platform Services blog", "https://aps.autodesk.com/blog/data-model-apis-included-subscriptions-plus-flexible-ways-scale"),
   N("2026-10-06", "AEC Data Model API pricing took effect: only data moved out to external systems is charged.", "Autodesk Platform Services blog", "https://aps.autodesk.com/blog/data-model-apis-included-subscriptions-plus-flexible-ways-scale")],
  interpretation="Over the past year Autodesk has turned free developer APIs into metered revenue with a clear rule: use inside Autodesk products is included in the subscription, while extracting data or high-volume automation is paid. The MCP line indicates the next step is pricing AI-agent access to Autodesk data the same way, so agents built by customers or third parties consume tokens. The role puts these policies (caps, entitlements, pooling) into practice rather than setting price levels.",
  open_questions=["Will MCP access use Flex tokens or a new meter?", "Will partners and software vendors be priced differently from end customers?"],
  caveat="MCP monetization is one line in the posting; no MCP pricing is public yet. The Dec 2025 item is background, older than the last few months.",
  confidence="High"),
 "STR-0012": dict(
  pricing_theme="Standardizing pricing methods across several brands and insurer contracts",
  current_model="Glass repair and replacement priced through insurer and fleet agreements plus retail prices, across Speedy Glass, Apple Auto Glass and Lebeau Vitres d'autos.",
  posting_evidence=[
   "Senior Advisor, Pricing Management and Commercial Strategy; hybrid; city not stated; bilingual; 5+ years; no direct reports.",
   "Leads pricing strategies and large commercial initiatives, including follow-up after implementation.",
   "Keeps pricing structures, processes and methods consistent; builds pricing models, calculators and dashboards (SQL, Power BI).",
   "Contributes to budgeting and strategic planning."],
  news=[],
  interpretation="The emphasis on consistency and calculators suggests pricing is fragmented across brands, regions and insurer contracts, and Belron wants one method. Camera recalibration after windshield replacement, which Speedy Glass offers, is a growing service whose price is likely part of what needs standardizing. Because the role is a senior individual contributor, pricing decisions probably sit with commercial leadership.",
  open_questions=["Is the focus insurer contract pricing or retail prices?", "Is camera recalibration priced separately or bundled into replacement?"],
  caveat="No recent public pricing news found; channel mix is not stated in the posting.",
  confidence="Medium"),
 "STR-0015": dict(
  pricing_theme="Shifting growth to expansion revenue in a revenue-tiered SMB SaaS",
  current_model="Monthly or annual subscriptions (25% off annually) with four tiers per product, scaled by the customer's monthly revenue, users and warehouses. Separate products for e-invoicing, accounting, POS and payroll (payroll priced by employees). In Colombia, e-invoicing starts at COP 17,900 a month and accounting at COP 74,900. AI features (Alegra IA, an MCP connection) are bundled into every plan at no extra charge.",
  posting_evidence=[
   "Pricing and Monetization Manager, also called Expansion Manager in the description; remote, for residents or permit holders in Colombia, Mexico or Peru; 5–8+ years.",
   "Owns multi-country SaaS pricing, payment plans, ARR and NRR, upsell and cross-sell.",
   "Leads the Memberships product owner and builds the Expansion & Monetization team."],
  news=[],
  interpretation="Alegra already prices on a value metric, the customer's revenue, so the upgrade path is built in. The next lever is moving customers across products (invoicing to accounting, POS and payroll) and up tiers, which is why pricing sits with a memberships and expansion team: net revenue retention is now the priority. AI is bundled free in every plan, so a likely early decision for this role is whether AI becomes a tier differentiator or a paid add-on. Multi-country scope means localizing price points around each country's e-invoicing and tax rules.",
  open_questions=["Will AI be monetized separately or used to justify tier upgrades?", "Are cross-product bundles planned?"],
  caveat="Pricing was checked for Colombia only.",
  confidence="High"),
 "STR-0016": dict(
  pricing_theme="Global interchange and network-fee strategy run from a Bogotá hub",
  current_model="Network fees charged to issuers and acquirers, plus interchange set by Mastercard and paid by acquirers to issuers; Colombian interchange tables are published by Mastercard.",
  posting_evidence=[
   "Manager, Strategy Pricing & Interchange, on the Global Pricing & Interchange team; Bogotá; posted Aug 12, 2026.",
   "Executes the global pricing and interchange strategy and transformation initiatives under one global framework, from business case to regional rollout.",
   "Benchmarks performance and models economics and competitive position across the four-party ecosystem.",
   "Improves pricing decision tools; coaches junior staff; MBA strongly preferred."],
  news=[
   N("2026-10-06", "Colombia's Bre-B instant-payment system marked one year: 36 million active users (83% of adults) against 24% of adults holding a credit card, and over 8 million transactions a day.", "EBANX via GlobeNewswire (vendor data)", "https://www.globenewswire.com/news-release/2026/10/06/3375461/0/en/colombia-s-bre-b-marks-one-year-with-faster-adoption-than-brazil-s-pix-ebanx-analysis-finds.html")],
  interpretation="The role is global, not Colombia-specific: Bogotá is a delivery hub for Mastercard's central pricing team. The \"transformation\" language fits a period when account-to-account rails such as Bre-B and Pix compete with cards at checkout, and interchange and network fees are the levers networks use to keep issuers and acquirers committed. Expect work on fee simplification, incentive structures and competitive benchmarking rather than local price setting.",
  open_questions=["What transformation is under way: fee restructuring, simplification or new products?", "Which regions does the Bogotá team actually cover?"],
  caveat="The posting names no markets; the Bre-B link is context, not stated.",
  confidence="Medium"),
 "STR-0017": dict(
  pricing_theme="Price-waterfall discipline across consultants, own stores and e-commerce",
  current_model="Catalogue prices for direct-sales consultants, who earn a discount or margin, plus own stores, retail, e-commerce and marketplaces, across the Natura and Avon brands.",
  posting_evidence=[
   "Jefe de RGM, Bogotá; posted Aug 12, 2026; COP 12.5–15M per the Adecco listing.",
   "Controls the price waterfall from list to net price across direct sales (stated priority), retail, e-commerce and marketplaces; sets discount and incentive direction.",
   "Audits promotional ROI and flags margin-diluting tactics.",
   "Leads cross-channel price harmony to avoid cannibalizing direct sales and own stores (\"Set the Price\" vs \"Get the Price\").",
   "Builds RGM processes from scratch; 6+ years; direct-selling experience (Belcorp, Yanbal) preferred."],
  news=[
   N("2026-02-11", "Natura Colombia: in 2025 retail grew 500%, e-commerce 45% and direct sales 5%; 11 stores, with 7 more planned for 2026; over 180,000 consultants.", "El Cronista", "https://www.cronista.com/colombia/finanzas-y-economia/natura-colombia-redefine-su-estrategia-de-crecimiento-hacia-2026-la-regeneracion-es-parte-central-de-nuestro-modelo-de-negocio/"),
   N("2026-03-18", "Natura is repositioning Avon toward younger consumers with more technology; the CEO expects Avon's prices to rise from current levels.", "Bloomberg Línea", "https://www.bloomberglinea.com/negocios/natura-reposiciona-avon-y-alista-estrategia-para-enfrentar-las-marcas-de-influencers/")],
  interpretation="Sales are shifting fast from consultants to stores and e-commerce, which creates price conflict: if store or online prices undercut the catalogue, consultants lose margin and leave. The priority on direct-sales gross-to-net and channel harmony shows Natura wants one price architecture across channels and less promotional leakage. \"From scratch\" confirms RGM is a new capability in Colombia, and Avon's move upmarket adds a price-ladder question between the two brands.",
  open_questions=["Who sets consultant discounts and incentives today?", "How will the Natura and Avon price ladders be separated?"],
  caveat="The Avon repositioning article is regional, not specific to Colombia.",
  confidence="High"),
 "STR-0018": dict(
  pricing_theme="Moving a multi-property hotel group to demand-led, centralized pricing",
  current_model="Room rates set per property and channel (direct and online travel agencies). The employer is confidential.",
  posting_evidence=[
   "Director pricing, Bogotá; hybrid; COP 18–21M; posted Aug 12, 2026; middle-management level.",
   "Sets pricing strategy from booking pace and market behaviour; optimizes room inventory and distribution channels.",
   "Builds dashboards for leadership; transforms the rate structure to maximize profitability.",
   "Requires 7–10 years, 5+ in hotel pricing; RevPAR and forecasting; SQL and Power BI or Tableau."],
  news=[],
  interpretation="Booking-pace pricing plus \"transform the rate structure\" indicates the group still runs largely static or manual rates and wants a central revenue-management function across properties. Channel optimization usually means shifting the mix toward direct bookings to cut travel-agency commissions. Requiring SQL and BI skills at director level suggests there is no revenue-management system yet, or one is being implemented.",
  open_questions=["Which hotel group is hiring?", "Is a revenue-management system in place or planned?"],
  caveat="Employer unknown, so no company news can be checked.",
  confidence="Medium"),
}
THIN = {
 "STR-0006": "Official posting has no description in English; the French text has not been reviewed.",
 "STR-0009": "Only a LinkedIn listing; full responsibilities not read.",
 "STR-0010": "Unverified lead; only a one-line LinkedIn summary.",
 "STR-0011": "Only aggregator copies; responsibilities not read in full.",
 "STR-0013": "Unverified lead; only a one-line LinkedIn summary.",
 "STR-0014": "Official posting could not be opened; no responsibilities read.",
 "STR-0019": "Only a LinkedIn listing; full responsibilities not read.",
 "STR-0020": "Only a LinkedIn listing; full responsibilities not read.",
 "STR-0021": "Only a LinkedIn listing; full responsibilities not read.",
 "STR-0022": "Unverified lead; only a one-line LinkedIn summary.",
}


def main():
    jobs = c.load("opportunities.json")
    for j in jobs:
        if j["id"] in JOBS:
            mode, city, note, extra = JOBS[j["id"]]
            j["work_mode"], j["city"] = mode, city
            j["location_note"] = note or j.get("location_note")
            for k, v in extra.items():
                if not j.get(k) or k == "requisition_id":
                    j[k] = v
        if j.get("work_mode") not in c.WORK_MODES:
            j["work_mode"] = c.infer_work_mode(j.get("work_model"))
        j.setdefault("location_note", None)
    c.save("opportunities.json", jobs)

    strat = c.load("strategy.json")
    for s in strat:
        if s["id"] in STRATEGY:
            new = STRATEGY[s["id"]]
            s.update(new)
            s["posting_evidence"] = new["posting_evidence"]
            s["analysis_status"] = "analyzed"
            s["last_updated"] = T
        elif s["id"] in THIN:
            s["analysis_status"] = "insufficient_detail"
            s["insufficient_reason"] = THIN[s["id"]]
            s.setdefault("current_model", None)
            s.setdefault("news", [])
            s.setdefault("open_questions", [])
        else:  # records added by nightly runs before this update
            if isinstance(s.get("posting_evidence"), str):
                s["posting_evidence"] = [s["posting_evidence"]]
            for k, v in (("current_model", None), ("news", []), ("open_questions", [])):
                s.setdefault(k, v)
            if s.get("analysis_status") not in c.ANALYSIS_STATUS:
                s["analysis_status"] = "analyzed" if s.get("interpretation") else "insufficient_detail"
        if s["id"] == "STR-0004":
            s["linked_job_ids"] = ["JOB-0004", "JOB-0005"]
    c.save("strategy.json", strat)
    meta = c.load("meta.json")
    meta["schema_version"] = 2
    c.save("meta.json", meta)
    print("migrated", len(jobs), "jobs,", len(strat), "strategy records")


if __name__ == "__main__":
    main()
