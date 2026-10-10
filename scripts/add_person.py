"""Add a contact you found yourself, for example from LinkedIn's "Meet the hiring team" box.

Example:
  python3 scripts/add_person.py --name "Jane Doe" --title "Director, Pricing" --company "Autodesk" \\
      --job JOB-0009 --relationship "Hiring manager" --linkedin "https://www.linkedin.com/in/janedoe"
Then commit and push (or let tonight's run do it).
"""
import argparse
import common as c

ap = argparse.ArgumentParser()
ap.add_argument("--name", required=True)
ap.add_argument("--title", required=True)
ap.add_argument("--company", required=True)
ap.add_argument("--job", help="Tracker ID of the role, e.g. JOB-0009")
ap.add_argument("--relationship", default="Hiring team (seen on LinkedIn)")
ap.add_argument("--linkedin", help="Profile URL (linkedin.com/in/...)")
ap.add_argument("--note")
a = ap.parse_args()

people = c.load("people.json")
jobs = {j["id"] for j in c.load("opportunities.json")}
if a.job and a.job not in jobs:
    raise SystemExit("Unknown job ID %s" % a.job)
if a.linkedin and "linkedin.com/in/" not in a.linkedin:
    raise SystemExit("The LinkedIn link must be a profile link (linkedin.com/in/...)")
if any(c.norm(p["name"]) == c.norm(a.name) and c.norm(p["company"]) == c.norm(a.company) for p in people):
    raise SystemExit("%s at %s is already listed" % (a.name, a.company))
pid = c.next_id([p["id"] for p in people], "PERSON-")
people.append(dict(id=pid, name=a.name.strip(), title=a.title.strip(), company=a.company.strip(), contact_type="added_by_you",
                   relationship=a.relationship, relevance=None, opportunity_id=a.job, linkedin_profile=a.linkedin,
                   verification="Added by you", evidence_url=a.linkedin, found_via="You", first_seen=c.today(), notes=a.note))
c.save("people.json", people)
print("Added %s %s (%s)" % (pid, a.name, a.company))
