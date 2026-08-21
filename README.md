# Job Alert Bot

Checks ~122 companies' public job boards across **Greenhouse, Lever,
Ashby, SmartRecruiters, and Workday**, plus the Remotive remote-jobs API,
every 15 minutes. For each posting it checks, in order:

1. Title matches a DevOps / SRE / Cloud / Platform / Infrastructure /
   MLOps / AIOps keyword
2. Location looks US-based
3. Full job description does **not** contain any citizenship / clearance /
   export-control phrase (see list below)
4. Full job description doesn't ask for more than **4 years** of
   experience
5. It's a posting you haven't already been emailed about

Anything that passes all five gets emailed to you. Runs for free on
GitHub Actions -- no server needed.

## How this actually runs

GitHub Actions doesn't keep a server running 24/7. On the schedule set
in `job-alerts.yml`, GitHub spins up a fresh temporary machine, runs
`poller.py`, sends an email if there's anything new, then shuts the
machine down. It repeats this every 15 minutes indefinitely -- that's
the closest a scheduled job can reliably get to "immediate" (GitHub can
delay a scheduled run by a few extra minutes under load, and going much
below 15 minutes risks skipped runs). Since your repo is public, Actions
minutes are free and unlimited, so running this often costs you nothing.

## The new filters, and how they actually work

**Citizenship / clearance / export-control exclusion.** The bot now
downloads each candidate job's *full description* (not just the title)
and checks it against these phrases: U.S. Citizens Only, U.S. Citizen,
Permanent Resident, Green Card, ITAR, EAR, Export Control, Federal
Security Clearance, Secret Clearance, Top Secret Clearance, Public
Trust, DoD Clearance, TS/SCI, citizenship required, U.S. Person. If any
of these show up anywhere in the description, the job is dropped before
it ever reaches your inbox. This is a straightforward text match on the
description, so it's quite reliable -- if a posting mentions any of
these, it gets caught.

**4-years-experience cap.** The bot also scans the description for
phrasing like "5+ years of experience" or "6-8 years experience" and
drops the posting if the number it finds is over 4. This one is a
heuristic, not perfect comprehension -- it can miss unusual phrasing
(e.g. "half a decade of experience") and on ranges like "3-8 years" it
reads the first number (3), not the ceiling (8). Treat it as a solid
first pass, not a guarantee -- worth a glance at the full posting before
you rule it out or in.

**Fetching full descriptions costs extra requests**, so the bot only
does this for postings that already passed the keyword + US-location
check and that it hasn't evaluated before -- keeps each run fast.

## US-only location filtering

Checks each job's location string for a US state, "United States",
"Remote - US", etc., and drops ones that clearly say another country
(India, UK, Canada, Germany, etc.). A bare "Remote" with no country
listed is kept by default, since most companies on this list are US
headquartered. Not a guarantee -- still glance at the location before
applying. Tune `US_PHRASES` / `NON_US_KEYWORDS` at the top of
`poller.py` if you spot something obviously wrong slipping through.

## A note on accuracy per ATS

- **Greenhouse, Lever, Ashby, SmartRecruiters**: company slugs are
  usually readable straight off the careers URL, so these are reasonably
  reliable, and description-fetching for the exclusion/experience checks
  works cleanly for all four.
- **Workday** is different in two ways:
  1. It needs three values (tenant, data center, site name) that are
     *not* visible in the plain careers URL -- the Workday entries in
     `companies.py` are best-effort placeholders and most will need
     correcting (see below).
  2. Its full-description endpoint is less standardized, so the
     citizenship/clearance/experience filtering is less reliable there
     specifically. This matters because several Workday entries are
     Houston energy majors (Shell, Chevron, Halliburton, SLB, etc.) --
     exactly the kind of companies likely to have citizenship or
     clearance requirements. Double-check those manually rather than
     trusting the filter blindly.

### Fixing a Workday entry

1. Open the company's careers page and click into any job listing.
2. Open DevTools (F12) -> Network tab, refresh the page.
3. Look for a request to:
   `https://<tenant>.<dc>.myworkdayjobs.com/wday/cxs/<tenant>/<site>/jobs`
4. Update the matching entry in `companies.py` with those three values.

If you can't find that request, the company likely isn't on Workday --
just delete that entry.

## Setup (if starting from scratch)

### 1. Create the repo and push these files

Unzip this folder locally, create an empty repo on GitHub, then from
inside the unzipped `job-alert-bot` folder:

```bash
cd job-alert-bot
git init
git add .
git commit -m "Initial commit: job alert bot"
git branch -M main
git remote add origin https://github.com/<your-username>/job-alert-bot.git
git push -u origin main
```

If it asks for a password, use a GitHub Personal Access Token (create
one at https://github.com/settings/tokens with "repo" scope).

**Keep the folder structure exactly as-is** --
`.github/workflows/job-alerts.yml` has to stay at that exact path.

### 2. Get a Gmail App Password

1. Turn on 2-Step Verification: https://myaccount.google.com/security
2. Create an app password: https://myaccount.google.com/apppasswords

### 3. Add secrets to the repo

Settings -> Secrets and variables -> Actions -> New repository secret:
- `GMAIL_USER` = your Gmail address
- `GMAIL_APP_PASSWORD` = the 16-character app password

### 4. Turn it on

Actions tab -> enable workflows if prompted -> "Job Alerts" -> "Run
workflow" for a manual test. Check the logs for the summary line (how
many matched, how many got filtered out and why, how many were emailed).

Or from the terminal with GitHub CLI:

```bash
gh secret set GMAIL_USER --body "your-email@gmail.com"
gh secret set GMAIL_APP_PASSWORD --body "<your app password>"
gh workflow run job-alerts.yml
gh run watch
```

## Updating an already-pushed repo

If you already have this repo running and just want this update (US
filtering + citizenship/clearance exclusion + experience cap + faster
schedule), copy the new `poller.py`, `companies.py`,
`.github/workflows/job-alerts.yml`, and `README.md` into your local
folder, overwriting the old ones, then:

```bash
git add .
git commit -m "Add citizenship/clearance filter, experience cap, faster schedule"
git push
```

No need to touch your secrets.

## Other things to know

- **Some company tokens will fail** -- best-effort guesses based on
  naming patterns. A failed one is skipped and logged, nothing breaks.
  Check the Action logs occasionally and fix or remove ones that keep
  failing.
- **It only alerts on postings it hasn't evaluated before**, tracked via
  `seen_jobs.json`. The first run after this update will re-evaluate
  everything currently open (since the new filters haven't run on them
  yet), so expect a bigger batch of emails, or none, once.
- **It doesn't check visa sponsorship history** -- still cross-check with
  h1bdata.info / myvisajobs.com like you already do; the exclusion filter
  only catches postings that explicitly state citizenship/clearance
  requirements in the text.
- Add or remove companies any time by editing `companies.py`.
