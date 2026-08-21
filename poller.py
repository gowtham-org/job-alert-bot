"""
Job alert poller.

Checks each company in companies.py across 5 ATS platforms
(Greenhouse, Lever, Ashby, SmartRecruiters, Workday) plus the Remotive
aggregator API, filters postings by keyword, and emails any NEW matches
(ones not seen in a previous run) to ALERT_TO.

Run via GitHub Actions on a schedule. State (which jobs have already been
emailed) is kept in seen_jobs.json, which the workflow commits back to the
repo after each run so it persists between runs.
"""

import json
import os
import smtplib
import urllib.error
import urllib.parse
import urllib.request
from email.mime.text import MIMEText
from pathlib import Path

from companies import COMPANIES

KEYWORDS = [
    "devops",
    "site reliability",
    "sre",
    "cloud engineer",
    "cloud infrastructure",
    "platform engineer",
    "infrastructure engineer",
    "mlops",
    "aiops",
    "reliability engineer",
    "cloud operations",
    "release engineer",
]

REMOTIVE_SEARCH_TERMS = [
    "devops",
    "site reliability",
    "cloud engineer",
    "platform engineer",
    "mlops",
]

STATE_FILE = Path(__file__).parent / "seen_jobs.json"
TIMEOUT = 15


def matches_keywords(title: str) -> bool:
    t = title.lower()
    return any(k in t for k in KEYWORDS)


def fetch_json(url: str, data: bytes = None, method: str = "GET"):
    headers = {"User-Agent": "job-alert-bot/1.0"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_greenhouse(token: str):
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=false"
    data = fetch_json(url)
    jobs = []
    for j in data.get("jobs", []):
        jobs.append(
            {
                "id": f"greenhouse-{token}-{j['id']}",
                "title": j.get("title", ""),
                "location": (j.get("location") or {}).get("name", ""),
                "url": j.get("absolute_url", ""),
            }
        )
    return jobs


def fetch_lever(token: str):
    url = f"https://api.lever.co/v0/postings/{token}?mode=json"
    data = fetch_json(url)
    jobs = []
    for j in data:
        jobs.append(
            {
                "id": f"lever-{token}-{j.get('id')}",
                "title": j.get("text", ""),
                "location": (j.get("categories") or {}).get("location", ""),
                "url": j.get("hostedUrl", ""),
            }
        )
    return jobs


def fetch_ashby(token: str):
    url = f"https://api.ashbyhq.com/posting-api/job-board/{token}"
    data = fetch_json(url)
    jobs = []
    for j in data.get("jobs", []):
        jobs.append(
            {
                "id": f"ashby-{token}-{j.get('id')}",
                "title": j.get("title", ""),
                "location": j.get("location") or j.get("locationName", "") or "",
                "url": j.get("jobUrl") or j.get("applyUrl", ""),
            }
        )
    return jobs


def fetch_smartrecruiters(company: str):
    url = f"https://api.smartrecruiters.com/v1/companies/{company}/postings?limit=100"
    data = fetch_json(url)
    jobs = []
    for j in data.get("content", []):
        loc = j.get("location", {}) or {}
        loc_str = ", ".join(filter(None, [loc.get("city"), loc.get("region"), loc.get("country")]))
        jobs.append(
            {
                "id": f"smartrecruiters-{company}-{j.get('id')}",
                "title": j.get("name", ""),
                "location": loc_str,
                "url": f"https://jobs.smartrecruiters.com/{company}/{j.get('id')}",
            }
        )
    return jobs


def fetch_workday(cfg: dict):
    tenant, dc, site = cfg["tenant"], cfg["dc"], cfg["site"]
    url = f"https://{tenant}.{dc}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"
    body = json.dumps({"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": ""}).encode()
    data = fetch_json(url, data=body, method="POST")
    jobs = []
    for j in data.get("jobPostings", []):
        path = j.get("externalPath", "")
        jobs.append(
            {
                "id": f"workday-{tenant}-{path}",
                "title": j.get("title", ""),
                "location": j.get("locationsText", ""),
                "url": f"https://{tenant}.{dc}.myworkdayjobs.com/{site}{path}",
            }
        )
    return jobs


def fetch_remotive():
    jobs = []
    for kw in REMOTIVE_SEARCH_TERMS:
        url = f"https://remotive.com/api/remote-jobs?search={urllib.parse.quote(kw)}"
        try:
            data = fetch_json(url)
        except Exception as e:
            print(f"[remotive] error for '{kw}': {e}")
            continue
        for j in data.get("jobs", []):
            jobs.append(
                {
                    "id": f"remotive-{j.get('id')}",
                    "title": j.get("title", ""),
                    "location": j.get("candidate_required_location", ""),
                    "url": j.get("url", ""),
                    "company": j.get("company_name", ""),
                }
            )
    return jobs


def load_seen() -> set:
    if STATE_FILE.exists():
        return set(json.loads(STATE_FILE.read_text()))
    return set()


def save_seen(seen: set) -> None:
    STATE_FILE.write_text(json.dumps(sorted(seen)))


def send_email(new_jobs) -> None:
    user = os.environ["GMAIL_USER"]
    pw = os.environ["GMAIL_APP_PASSWORD"]
    to_addr = os.environ.get("ALERT_TO", user)

    lines = []
    for j in new_jobs:
        company = j.get("company", "")
        loc = j.get("location", "")
        lines.append(f"{j['title']}\n{company} — {loc}\n{j['url']}\n")
    body = "\n".join(lines)

    msg = MIMEText(body)
    msg["Subject"] = f"[Job Alert] {len(new_jobs)} new DevOps/SRE/Cloud posting(s)"
    msg["From"] = user
    msg["To"] = to_addr

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(user, pw)
        server.sendmail(user, [to_addr], msg.as_string())


def main() -> None:
    seen = load_seen()
    all_jobs = []
    failed = []

    for c in COMPANIES:
        try:
            ats = c["ats"]
            if ats == "greenhouse":
                jobs = fetch_greenhouse(c["token"])
            elif ats == "lever":
                jobs = fetch_lever(c["token"])
            elif ats == "ashby":
                jobs = fetch_ashby(c["token"])
            elif ats == "smartrecruiters":
                jobs = fetch_smartrecruiters(c["company"])
            elif ats == "workday":
                jobs = fetch_workday(c)
            else:
                continue
            for j in jobs:
                j["company"] = c["name"]
            all_jobs.extend(jobs)
        except urllib.error.HTTPError as e:
            failed.append(f"{c['name']} ({c['ats']}): HTTP {e.code}")
        except Exception as e:
            failed.append(f"{c['name']} ({c['ats']}): {e}")

    try:
        all_jobs.extend(fetch_remotive())
    except Exception as e:
        print(f"[remotive] error: {e}")

    if failed:
        print(f"{len(failed)} companies failed to fetch (likely wrong token/config or different ATS):")
        for f in failed:
            print(f"  - {f}")

    matched = [j for j in all_jobs if matches_keywords(j["title"])]
    new_jobs = [j for j in matched if j["id"] not in seen]

    print(
        f"Checked {len(COMPANIES)} companies + Remotive. "
        f"{len(matched)} matching postings total, {len(new_jobs)} new since last run."
    )

    if new_jobs:
        send_email(new_jobs)
        seen.update(j["id"] for j in new_jobs)
        save_seen(seen)


if __name__ == "__main__":
    main()
