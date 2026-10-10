"""One-time (2026-10-10): label existing contacts and add the first pass of relevant contacts
found in public sources. Safe to run more than once."""
import common as c

T = "2026-10-10"
ADD = [
 dict(name="Ben Cochran", title="VP of Developer Enablement, Autodesk Platform Services", company="Autodesk", job="JOB-0009",
      relevance="Leads the developer platform whose API business model this role puts into practice.",
      source="https://aps.autodesk.com/blog/autodesk-devcon-2026-highlights", via="Autodesk DevCon 2026 keynote (Apr 16, 2026)"),
 dict(name="Raji Arasu", title="EVP of Platform Services & Emerging Technology and CTO", company="Autodesk", job="JOB-0009",
      relevance="Executive over Autodesk Platform Services, where API monetization sits.",
      source="https://aps.autodesk.com/blog/autodesk-devcon-2026-highlights", via="Autodesk DevCon 2026 keynote (Apr 16, 2026)"),
 dict(name="Hans Werner", title="General Manager, Andean Market (Colombia, Peru, Ecuador)", company="Natura", job="JOB-0018",
      relevance="Runs the integrated Colombia, Peru and Ecuador business that the RGM role supports.",
      source="https://www.valoraanalitik.com/?p=566911", via="Valora Analitik (Mar 26, 2026)"),
]
people = c.load("people.json")
for p in people:
    p.setdefault("contact_type", "confirmed_poster")
    p.setdefault("relevance", None)
    p.setdefault("found_via", "Job posting")
for a in ADD:
    if any(c.norm(p["name"]) == c.norm(a["name"]) and c.norm(p["company"]) == c.norm(a["company"]) for p in people):
        continue
    pid = c.next_id([p["id"] for p in people], "PERSON-")
    people.append(dict(id=pid, name=a["name"], title=a["title"], company=a["company"], contact_type="relevant_contact",
                       relationship="Relevant leader (not confirmed as poster)", relevance=a["relevance"],
                       opportunity_id=a["job"], linkedin_profile=None, verification="Named in public source",
                       evidence_url=a["source"], found_via=a["via"], first_seen=T,
                       notes="Profile not looked up; LinkedIn is not opened automatically."))
    print("added", pid, a["name"])
c.save("people.json", people)
