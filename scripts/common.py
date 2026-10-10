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
COUNTRIES = ["Canada", "Colombia", "Global remote"]
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
