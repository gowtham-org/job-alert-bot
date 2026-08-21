# Job Alert Bot

Checks ~130 companies' public job boards across **Greenhouse, Lever,
Ashby, SmartRecruiters, and Workday**, plus the Remotive remote-jobs API,
every 30 minutes. Filters for DevOps / SRE / Cloud / Platform /
Infrastructure / MLOps / AIOps titles and emails you the new ones. Runs
for free on GitHub Actions -- no server needed.

## A note on accuracy per ATS

- **Greenhouse, Lever, Ashby, SmartRecruiters**: the slug/company-id can
  usually be read straight off the company's careers URL, so these are
  reasonably reliable guesses.
- **Workday** is different -- it needs three values (tenant, data center,
  site name) that are NOT visible in the plain careers URL. The Workday
  entries in `companies.py` are best-effort placeholders and most will
  need to be corrected (see "Fixing a Workday entry" below).

## Setup (takes ~10 minutes, one time)

### 1. Create the repo and push these files

First, unzip this folder locally, then go to https://github.com/new and
create a new **empty** repository (private is fine, no README/gitignore
needed since we already have files). Copy the repo URL it gives you
(looks like `https://github.com/<your-username>/job-alert-bot.git`).

Then, from inside the unzipped `job-alert-bot` folder, run:

```bash
cd job-alert-bot
git init
git add .
git commit -m "Initial commit: job alert bot"
git branch -M main
git remote add origin https://github.com/<your-username>/job-alert-bot.git
git push -u origin main
```

(Replace the URL with the one GitHub gave you. If it asks for
credentials, use a Personal Access Token as the password -- GitHub
stopped accepting regular passwords for git operations. Create one at
https://github.com/settings/tokens if you don't have one, with "repo"
scope checked.)

**Keep the folder structure exactly as-is** when you push --
`.github/workflows/job-alerts.yml` has to stay at that exact path or
GitHub won't pick it up as a workflow.

### 2. Get a Gmail App Password
This lets the bot send email from your Gmail without your real password.

1. Turn on 2-Step Verification on your Google account, if it isn't already:
   https://myaccount.google.com/security
2. Go to https://myaccount.google.com/apppasswords
3. Create a new app password (name it "job-alert-bot"), copy the 16-character
   code it gives you.

### 3. Add secrets to the repo
In your repo: **Settings -> Secrets and variables -> Actions -> New repository secret**

Add two secrets:
- `GMAIL_USER` = your Gmail address (e.g. gowthamchowdam2001@gmail.com)
- `GMAIL_APP_PASSWORD` = the 16-character app password from step 2

(The email it sends TO is already set to gowthamchowdam2001@gmail.com in
the workflow file -- change the `ALERT_TO` line in
`.github/workflows/job-alerts.yml` if you ever want it to go elsewhere.)

### 4. Turn it on
Go to the **Actions** tab of your repo. If prompted, click "I understand my
workflows, enable them." Then click on "Job Alerts" -> "Run workflow" to
fire off a manual test run. Check the logs -- it'll print how many
companies it checked and how many matches it found.

After that, it runs automatically every 30 minutes.

### Optional: do steps 3-4 from your terminal instead of the browser

If you have the GitHub CLI (`gh`) installed and logged in
(`gh auth login`), you can set the secrets and trigger a run without
touching the website:

```bash
gh secret set GMAIL_USER --body "gowthamchowdam2001@gmail.com"
gh secret set GMAIL_APP_PASSWORD --body "<your 16-character app password>"
gh workflow run job-alerts.yml
gh run watch
```

`gh run watch` shows you the live logs of that run so you can confirm it
worked.

## Fixing a Workday entry

1. Open the company's careers page and click into any job listing.
2. Open your browser's DevTools (F12) -> Network tab, then refresh the page.
3. Look for a request to a URL like:
   `https://<tenant>.<dc>.myworkdayjobs.com/wday/cxs/<tenant>/<site>/jobs`
4. Pull the three values out of that URL and update the matching entry in
   `companies.py`, e.g.:
   ```python
   {"name": "Shell", "ats": "workday", "tenant": "shell", "dc": "wd3", "site": "SHELL_CAREERS"}
   ```
If you can't find that request, the company likely isn't on Workday, or
uses a heavily customized setup -- just delete that entry.

## Things to know

- **Some company tokens will fail** -- I guessed a lot of them based on
  common naming patterns. A failed one just gets skipped and logged; it
  won't break anything. Check the Action run logs occasionally
  (they print a list of failed companies) and fix or remove the wrong ones.
  To find the correct token: go to the company's careers page, click
  through to their job listing, and check the URL -- it'll show
  `boards.greenhouse.io/<token>` or `jobs.lever.co/<token>`.
- **It only alerts on NEW postings**, tracked via `seen_jobs.json` in the
  repo. The first run will likely email you a big batch since everything
  is "new" -- that's expected, after that it's just genuinely new postings.
- **It doesn't check visa sponsorship or filter location** -- still your
  job to vet each one before applying (cross-check with h1bdata.info /
  myvisajobs.com like you already do).
- **GitHub disables scheduled workflows after 60 days of repo
  inactivity.** As long as the bot is committing `seen_jobs.json` every
  30 min, this won't happen -- but if you ever pause it for a while, you
  may need to manually re-enable it from the Actions tab.
- Add or remove companies any time by editing `companies.py`.
