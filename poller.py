"""
Job alert poller.

Checks each company in companies.py across 5 ATS platforms
(Greenhouse, Lever, Ashby, SmartRecruiters, Workday) plus the Remotive
aggregator API. Pipeline for each posting:

  1. Title matches a DevOps/SRE/Cloud/Platform/Infra/MLOps/AIOps keyword
  2. Location looks US-based
  3. Posting is not older than MAX_POSTING_AGE_HOURS (based on the ATS's own
     posted/updated date field, when available)
  4. Full job description does NOT contain any excluded citizenship /
     clearance / export-control phrase
  5. Full job description does not ask for more than MAX_YEARS_EXPERIENCE
  6. Not already emailed in a previous run (tracked in seen_jobs.json)

Step 3 matters because "new to the bot" (never-before-seen job ID) is not
the same thing as "recently posted" -- e.g. the first time a company is
added or a broken token gets fixed, every currently-open posting on that
board looks brand new to seen_jobs.json even if it's been live for months.
The age check catches that.

Steps 4-5 require fetching each job's full description, which is only
done for postings that already passed steps 1-3, to keep the number of
extra requests small.

Run via GitHub Actions on a schedule. seen_jobs.json is committed back to
the repo after each run so state persists between runs.
"""

import datetime
import json
import os
import re
import smtplib
import urllib.error
import urllib.parse
import urllib.request
from email.mime.text import MIMEText
from pathlib import Path

from companies import COMPANIES

TIMEOUT = 15
MAX_YEARS_EXPERIENCE = 4
MAX_POSTING_AGE_HOURS = 0.50
# Postings older than this (by the ATS's own posted/updated date, when we
# can determine it) are dropped even if their ID is new to seen_jobs.json.
# When a posting's age can't be determined at all, it's kept rather than
# guessed away -- see is_recent_enough() below.
#
# IMPORTANT LIMITATION: Workday only reports day-level granularity
# ("Posted Today", "Posted 3 Days Ago"), never hours or minutes. A Workday
# posting from 20 hours ago and one from 5 minutes ago both show as
# "Posted Today" and will both pass a 2-hour filter -- there's no way to
# tell them apart with the data Workday exposes. This only affects the 2
# Workday companies in companies.py (Adobe, Target); every other platform
# (Greenhouse, Lever, Ashby, SmartRecruiters, Remotive) gives exact
# timestamps and this filter works precisely for those.
STATE_FILE = Path(__file__).parent / "seen_jobs.json"

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

# --- US location filtering -------------------------------------------------

US_STATE_ABBRS = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID",
    "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS",
    "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK",
    "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV",
    "WI", "WY", "DC",
}

US_PHRASES = ["united states", "usa", "u.s.a", "u.s.", "remote - us", "remote (us)", "remote, us"]

NON_US_KEYWORDS = [
    "india", "bangalore", "bengaluru", "hyderabad", "pune", "mumbai", "chennai", "gurgaon", "gurugram",
    "united kingdom", " uk ", "u.k.", "london", "england",
    "canada", "toronto", "vancouver", "montreal",
    "germany", "berlin", "munich",
    "poland", "warsaw", "krakow",
    "ireland", "dublin",
    "netherlands", "amsterdam",
    "singapore",
    "australia", "sydney", "melbourne",
    "france", "paris",
    "spain", "madrid", "barcelona",
    "portugal", "lisbon",
    "brazil", "sao paulo",
    "mexico",
    "philippines", "manila",
    "romania", "bucharest",
    "ukraine", "kyiv",
    "israel", "tel aviv",
    "japan", "tokyo",
    "china", "shanghai", "beijing",
    "vietnam",
    "argentina",
    "colombia", "bogota",
    "emea", "apac", "latam",
]


def is_us_location(location: str) -> bool:
    if not location:
        return True  # no info -- can't tell, default to include
    loc_lower = location.lower()
    if any(p in loc_lower for p in US_PHRASES):
        return True
    tokens = re.split(r"[,/()\s]+", location)
    for t in tokens:
        tu = t.upper().strip(".")
        if tu in US_STATE_ABBRS or tu == "US":
            return True
    if any(k in loc_lower for k in NON_US_KEYWORDS):
        return False
    return True  # ambiguous -- default to include


def matches_keywords(title: str) -> bool:
    t = title.lower()
    return any(k in t for k in KEYWORDS)


# --- Posting age / recency -------------------------------------------------
# Each ATS reports "when was this posted" differently. These helpers
# normalize whatever's available into a UTC datetime, or None if it can't
# be determined -- in which case the posting is kept rather than guessed
# away (see is_recent_enough).

def _parse_iso(value) -> "datetime.datetime | None":
    if not value:
        return None
    try:
        return datetime.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception:
        return None


def _parse_epoch_ms(value) -> "datetime.datetime | None":
    if value is None:
        return None
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, tz=datetime.timezone.utc)
    except Exception:
        return None


def _parse_workday_relative(text) -> "datetime.datetime | None":
    # Workday search results give relative text like "Posted Today",
    # "Posted 3 Days Ago", or "Posted 30+ Days Ago" instead of a real date.
    # This is inherently approximate -- "30+" is treated as exactly 30,
    # which is a floor, not the true age.
    if not text:
        return None
    t = text.lower()
    now = datetime.datetime.now(datetime.timezone.utc)
    if "today" in t:
        return now
    if "yesterday" in t:
        return now - datetime.timedelta(days=1)
    m = re.search(r"(\d+)\+?\s*day", t)
    if m:
        return now - datetime.timedelta(days=int(m.group(1)))
    return None


def is_recent_enough(posted_dt, max_age_hours: int = MAX_POSTING_AGE_HOURS) -> bool:
    if posted_dt is None:
        return True  # unknown age -- don't hide it, can't verify
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=max_age_hours)
    return posted_dt >= cutoff


# --- Citizenship / clearance / export-control exclusion --------------------
# Word-boundary patterns for short acronyms (avoids false hits like "year"
# matching "ear"), substring patterns for longer phrases.

EXCLUSION_PATTERNS = [
    r"u\.?s\.?\s*citizens?\s*only",
    r"\bu\.?s\.?\s*citizen\b",
    r"\bpermanent resident\b",
    r"\bgreen card\b",
    r"\bitar\b",
    r"\bear\b",
    r"\bexport control(?:led)?\b",
    r"\bexport administration regulations?\b",
    r"\bfederal security clearance\b",
    r"\bsecret clearance\b",
    r"\btop secret clearance\b",
    r"\bpublic trust\b",
    r"\bdod clearance\b",
    r"\bts\s*/\s*sci\b",
    r"\bcitizenship required\b",
    r"\bu\.?s\.?\s*person\b",
]
EXCLUSION_RE = re.compile("|".join(EXCLUSION_PATTERNS), re.IGNORECASE)


def has_excluded_terms(text: str) -> bool:
    return bool(EXCLUSION_RE.search(text or ""))


# --- Experience cap filter (heuristic) --------------------------------------
# Looks for phrasing like "5+ years of experience" or "6 years experience".
# This is text pattern matching, not true comprehension, so it can miss
# unusual phrasing or misread ranges like "3-8 years" (reads the 3, not
# the 8). Treat it as a helpful filter, not a perfect one.

EXP_RE = re.compile(
    r"(\d{1,2})\+?\s*(?:-|to)?\s*\d{0,2}\+?\s*years?\s*(?:of\s+)?(?:experience|exp\b)",
    re.IGNORECASE,
)


def exceeds_experience_cap(text: str, cap: int = MAX_YEARS_EXPERIENCE) -> bool:
    for m in EXP_RE.finditer(text or ""):
        years = int(m.group(1))
        if years > cap:
            return True
    return False


def strip_html(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html or "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fetch_json(url: str, data: bytes = None, method: str = "GET"):
    headers = {"User-Agent": "job-alert-bot/1.0"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


# --- Per-ATS job list fetchers ----------------------------------------------
# Each returns dicts with: id, title, location, url, and enough info
# (_desc, or _fetch_desc callable-equivalent fields) to get a full
# description later for jobs that pass the first filter pass.

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
                "posted_dt": _parse_iso(j.get("first_published") or j.get("updated_at")),
                "_desc_kind": "greenhouse",
                "_desc_ref": (token, j["id"]),
            }
        )
    return jobs


def fetch_greenhouse_description(token, job_id) -> str:
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs/{job_id}"
    data = fetch_json(url)
    return strip_html(data.get("content", ""))


def fetch_lever(token: str):
    url = f"https://api.lever.co/v0/postings/{token}?mode=json"
    data = fetch_json(url)
    jobs = []
    for j in data:
        lists_text = " ".join(
            strip_html(item.get("content", "")) for item in (j.get("lists") or [])
        )
        desc = strip_html(j.get("descriptionPlain") or j.get("description") or "")
        full_desc = f"{desc} {lists_text}".strip()
        jobs.append(
            {
                "id": f"lever-{token}-{j.get('id')}",
                "title": j.get("text", ""),
                "location": (j.get("categories") or {}).get("location", ""),
                "url": j.get("hostedUrl", ""),
                "posted_dt": _parse_epoch_ms(j.get("createdAt")),
                "_desc_kind": "inline",
                "_desc_text": full_desc,
            }
        )
    return jobs


def fetch_ashby(token: str):
    url = f"https://api.ashbyhq.com/posting-api/job-board/{token}"
    data = fetch_json(url)
    jobs = []
    for j in data.get("jobs", []):
        desc = strip_html(j.get("descriptionHtml", "") or j.get("descriptionPlain", ""))
        jobs.append(
            {
                "id": f"ashby-{token}-{j.get('id')}",
                "title": j.get("title", ""),
                "location": j.get("location") or j.get("locationName", "") or "",
                "url": j.get("jobUrl") or j.get("applyUrl", ""),
                "posted_dt": _parse_iso(j.get("publishedAt")),
                "_desc_kind": "inline",
                "_desc_text": desc,
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
                "posted_dt": _parse_iso(j.get("releasedDate")),
                "_desc_kind": "smartrecruiters",
                "_desc_ref": (company, j.get("id")),
            }
        )
    return jobs


def fetch_smartrecruiters_description(company, job_id) -> str:
    url = f"https://api.smartrecruiters.com/v1/companies/{company}/postings/{job_id}"
    data = fetch_json(url)
    sections = (data.get("jobAd") or {}).get("sections") or {}
    parts = []
    for key in ("jobDescription", "qualifications", "additionalInformation"):
        text = (sections.get(key) or {}).get("text", "")
        if text:
            parts.append(strip_html(text))
    return " ".join(parts)


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
                "posted_dt": _parse_workday_relative(j.get("postedOn")),
                "_desc_kind": "workday",
                "_desc_ref": (tenant, dc, site, path),
            }
        )
    return jobs


def fetch_workday_description(tenant, dc, site, path) -> str:
    # Best-effort: Workday's detail endpoint shape varies more than the
    # other ATSs. If this fails, the job is kept (see get_description),
    # so citizenship/clearance/experience filtering is less reliable for
    # Workday postings specifically -- double check those manually.
    url = f"https://{tenant}.{dc}.myworkdayjobs.com/wday/cxs/{tenant}/{site}{path}"
    data = fetch_json(url)
    info = data.get("jobPostingInfo", {}) or {}
    return strip_html(info.get("jobDescription", ""))


def get_description(job: dict) -> str | None:
    """Returns the full description text for a job, or None if it
    couldn't be fetched (caller should treat None as 'unknown, don't
    exclude based on it')."""
    kind = job.get("_desc_kind")
    try:
        if kind == "inline":
            return job.get("_desc_text", "")
        if kind == "greenhouse":
            token, job_id = job["_desc_ref"]
            return fetch_greenhouse_description(token, job_id)
        if kind == "smartrecruiters":
            company, job_id = job["_desc_ref"]
            return fetch_smartrecruiters_description(company, job_id)
        if kind == "workday":
            tenant, dc, site, path = job["_desc_ref"]
            return fetch_workday_description(tenant, dc, site, path)
    except Exception as e:
        print(f"[description fetch failed] {job.get('company')} - {job.get('title')}: {e}")
        return None
    return None


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
                    "posted_dt": _parse_iso(j.get("publication_date")),
                    "_desc_kind": "inline",
                    "_desc_text": strip_html(j.get("description", "")),
                }
            )
    return jobs


SEEN_RETENTION_DAYS = 60
# How long a job ID stays remembered before it's eligible to be pruned from
# seen_jobs.json. A posting that's been gone from a company's board for this
# long is no longer at any real risk of reappearing with the same ID, so
# there's no downside to letting it drop off -- this just keeps the file
# from growing forever.


def load_seen() -> dict:
    """Returns {job_id: iso_timestamp_first_seen}. Transparently upgrades
    the old flat-list format (from before retention was added) by treating
    every existing ID as 'seen right now'."""
    if not STATE_FILE.exists():
        return {}
    try:
        data = json.loads(STATE_FILE.read_text())
    except Exception:
        return {}
    if isinstance(data, list):
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return {job_id: now for job_id in data}
    return data


def save_seen(seen: dict) -> None:
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=SEEN_RETENTION_DAYS)
    pruned = {}
    for job_id, ts in seen.items():
        try:
            when = datetime.datetime.fromisoformat(ts)
        except Exception:
            # Unparsable timestamp -- keep it rather than risk losing state.
            pruned[job_id] = ts
            continue
        if when >= cutoff:
            pruned[job_id] = ts
    STATE_FILE.write_text(json.dumps(pruned, sort_keys=True))


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
    msg["Subject"] = f"[Job Alert] {len(new_jobs)} new US DevOps/SRE/Cloud posting(s)"
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

    # Pass 1: cheap filters using only title + location + posted date --
    # no extra network requests needed for any of these.
    stage1 = [
        j for j in all_jobs
        if matches_keywords(j["title"])
        and is_us_location(j.get("location", ""))
        and is_recent_enough(j.get("posted_dt"))
    ]

    # Only fetch descriptions for jobs already flagged as new (skip the
    # extra network calls for ones we've already processed before).
    to_check = [j for j in stage1 if j["id"] not in seen]

    excluded_citizenship = 0
    excluded_experience = 0
    final_jobs = []
    for j in to_check:
        desc = get_description(j)
        combined = f"{j['title']} {desc or ''}"
        if has_excluded_terms(combined):
            excluded_citizenship += 1
            continue
        if desc is not None and exceeds_experience_cap(combined):
            excluded_experience += 1
            continue
        final_jobs.append(j)

    print(
        f"Checked {len(COMPANIES)} companies + Remotive. "
        f"{len(stage1)} matched keyword+US location+within {MAX_POSTING_AGE_HOURS}h, "
        f"{len(to_check)} were new, "
        f"{excluded_citizenship} dropped for citizenship/clearance terms, "
        f"{excluded_experience} dropped for exceeding {MAX_YEARS_EXPERIENCE}+ years experience, "
        f"{len(final_jobs)} passed everything and will be emailed."
    )

    if final_jobs:
        send_email(final_jobs)

    # Mark everything we evaluated as seen, whether it passed or was
    # excluded, so we don't re-fetch/re-check it every run. save_seen()
    # also prunes anything older than SEEN_RETENTION_DAYS.
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for j in to_check:
        seen[j["id"]] = now_iso
    save_seen(seen)


if __name__ == "__main__":
    main()