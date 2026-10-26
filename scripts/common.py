"""Shared helpers for the pricing tracker pipeline (Python 3.9+, standard library only)."""
import json
import os
import re
import unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
TZ = ZoneInfo("America/Toronto")

LIFECYCLE = ["active", "unable_to_verify", "inactive", "closed"]
SCOPE_FIT = ["in_scope", "borderline"]
CATEGORIES = ["Pricing", "Monetization", "RGM", "Revenue Management"]
COUNTRIES = ["Canada", "Colombia", "United States", "Global remote"]
CORE_COUNTRIES = ["Canada", "Colombia"]
CONFIDENCE = ["High", "Medium", "Low"]

# Hosts that are never used as proof that a job is open.
NO_CHECK_HOSTS = ["linkedin.com"]
AGGREGATOR_HOSTS = [
    "echojobs.io", "eluta.ca", "jobs.ca", "oakhcft.com", "builtin", "indeed.", "glassdoor.",
    "jooble", "lensa", "bebee", "remoteleaf", "jobrapido", "getro", "themuse.com", "simplyhired",
]


def today():
    return datetime.now(TZ).strftime("%Y-%m-%d")


def path(name):
    return os.path.join(DATA, name)


def load(name):
    with open(path(name), encoding="utf-8") as f:
        return json.load(f)


def save(name, obj):
    tmp = path(name) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path(name))


def load_checks():
    p = path("checks.jsonl")
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def append_check(entry):
    with open(path("checks.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def norm(text):
    """Lowercase, strip accents and punctuation, collapse spaces: used for de-duplication."""
    if not text:
        return ""
    t = unicodedata.normalize("NFKD", text)
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    t = t.replace("&", " and ")
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return " ".join(t.split())


def norm_url(url):
    if not url:
        return ""
    u = url.strip().lower().split("#")[0].split("?")[0].rstrip("/")
    return re.sub(r"^https?://(www\.)?", "", u)


def host_in(url, hosts):
    u = (url or "").lower()
    return any(h in u for h in hosts)


def next_id(existing_ids, prefix, width=4):
    nums = [int(m.group(1)) for i in existing_ids for m in [re.match(prefix + r"(\d+)$", i)] if m]
    return "%s%0*d" % (prefix, width, (max(nums) + 1) if nums else 1)

WORK_MODES = ["Remote", "Hybrid", "In person", "Unknown"]
ANALYSIS_STATUS = ["analyzed", "insufficient_detail", "excluded"]


def infer_work_mode(text):
    """Map free-text work arrangements (EN/FR/ES) to one of WORK_MODES."""
    t = norm(text)
    if not t or t in ("not stated", "not verified", "unknown"):
        return "Unknown"
    if any(w in t for w in ["hybrid", "hybride", "hibrido"]):
        return "Hybrid"
    if any(w in t for w in ["remote", "teletravail", "a distance", "remoto", "teletrabajo"]):
        return "Remote"
    if any(w in t for w in ["on site", "onsite", "in office", "office based", "in person",
                            "presencial", "sur place", "au bureau"]):
        return "In person"
    return "Unknown"

CONTACT_TYPES = ["confirmed_poster", "relevant_contact", "added_by_you"]
MAX_RELEVANT_PER_COMPANY = 3

LEVEL_BANDS = ["manager_plus", "analyst"]
ANALYST_LEVELS = ["Analyst", "Senior Analyst", "Specialist", "Coordinator"]
ANALYST_COUNTRIES = ["Canada", "Colombia"]


# Which level bands each country tab shows. Written to meta.json by the 2026-10-26 migration so
# the dashboard reads the rule from the data instead of hard-coding it.
COUNTRY_TAB_BANDS = {"Canada": ["manager_plus"], "Colombia": ["manager_plus", "analyst"],
                     "United States": ["manager_plus"], "Global remote": ["manager_plus"]}
# Which bands send phone alerts (only Canada and Colombia ever alert). Add "analyst" to the
# Colombia list to start getting alerts for Colombian analyst-level roles.
ALERT_BANDS = {"Canada": ["manager_plus"], "Colombia": ["manager_plus"]}

# Out of scope everywhere: freight forwarding / cargo quoting, costing, solution design.
# Matched against norm(title), so accents are already stripped.
OUT_OF_SCOPE_TITLE = re.compile(
    r"\bagente de carga\b|\bcarga internacional\b|\bfreight forward|\bforwarder\b|\bnvocc\b"
    r"|\bcostos?\b|\bcosting\b|\bcost (analyst|accountant|controller|engineer|specialist)\b"
    r"|\bdiseno de soluciones\b|\bsolutions? design\b")

# Analyst-level roles must name pricing explicitly in the title ("pricing strict").
PRICING_TITLE = re.compile(
    r"\bpricing\b|\bprecios?\b|\btarif|\bmonetiz|\bmonetis|\brevenue management\b|\brevenue growth\b"
    r"|\brgm\b|\bgestion de ingresos\b|\bgestion des revenus\b|\byield management\b")

_MANAGER_WORDS = re.compile(
    r"\b(manager|gerente|jefe|jefa|director|directora|directeur|directrice|head|lead|lider|vp|"
    r"vice president|gestionnaire|chef|responsable|principal|staff)\b")
_ANALYST_LEVEL_WORDS = [
    (r"\b(senior|sr) (pricing |revenue |rgm )?(analyst|analista|analyste)\b|\b(analista|analyste) (senior|sr)\b", "Senior Analyst"),
    (r"\b(analyst|analista|analyste|profesional)\b", "Analyst"),
    (r"\b(specialist|especialista|specialiste|conseiller|conseillere)\b", "Specialist"),
    (r"\b(coordinator|coordinador|coordinadora|coordonnateur|coordonnatrice)\b", "Coordinator"),
]


def analyst_level(title):
    """Analyst-level title (Analyst, Specialist, Coordinator...) -> its level; None for Manager+."""
    t = norm(title)
    if not t or _MANAGER_WORDS.search(t):
        return None
    for pattern, level in _ANALYST_LEVEL_WORDS:
        if re.search(pattern, t):
            return level
    return None


def out_of_scope(title):
    return bool(OUT_OF_SCOPE_TITLE.search(norm(title)))


def is_confidential(company):
    """True when the employer is not named (e.g. 'Confidential employer', 'Empresa confidencial')."""
    t = norm(company)
    return not t or any(w in t for w in ["confidential", "confidencial", "confidentiel", "undisclosed", "anonymous", "anonima"])
