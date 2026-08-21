# List of companies to poll for new job postings, across ATS platforms.
#
# This list was trimmed from an original ~122 guessed entries down to the
# ones CONFIRMED working from an actual GitHub Actions run (checked
# 2026-08-21), plus 3 entries fixed after verifying their real tokens:
#   - DoorDash:   doordash -> doordashusa
#   - SentinelOne: sentinelone -> sentinellabs
#   - Segment:    now posts under Twilio's board (acquired), token "twilio"
#
# HashiCorp was removed entirely -- confirmed to have moved off Greenhouse
# with no easy replacement found.
#
# NOTE: every guessed Lever token failed in the real run, so there are
# currently NO Lever companies in this list. If you want Lever coverage,
# ask for specific companies to be looked up and verified properly rather
# than guessed -- guessing on Lever specifically had a 0% hit rate here.
#
# Each entry needs "name", "ats", and then ATS-specific fields:
#   greenhouse:      {"token": "<slug>"}
#   lever:           {"token": "<slug>"}
#   ashby:           {"token": "<slug>"}
#   smartrecruiters: {"company": "<id>"}
#   workday:         {"tenant": "...", "dc": "...", "site": "..."}
#
# Failed entries are skipped and logged, not fatal -- but this list should
# now run clean with few or no failures.

COMPANIES = [
    # ============== GREENHOUSE (confirmed working) ==============
    {"name": "Datadog", "ats": "greenhouse", "token": "datadog"},
    {"name": "Grafana Labs", "ats": "greenhouse", "token": "grafanalabs"},
    {"name": "Elastic", "ats": "greenhouse", "token": "elastic"},
    {"name": "MongoDB", "ats": "greenhouse", "token": "mongodb"},
    {"name": "Cloudflare", "ats": "greenhouse", "token": "cloudflare"},
    {"name": "Fastly", "ats": "greenhouse", "token": "fastly"},
    {"name": "PagerDuty", "ats": "greenhouse", "token": "pagerduty"},
    {"name": "New Relic", "ats": "greenhouse", "token": "newrelic"},
    {"name": "JFrog", "ats": "greenhouse", "token": "jfrog"},
    {"name": "Cribl", "ats": "greenhouse", "token": "cribl"},
    {"name": "Temporal Technologies", "ats": "greenhouse", "token": "temporaltechnologies"},
    {"name": "LaunchDarkly", "ats": "greenhouse", "token": "launchdarkly"},
    {"name": "CircleCI", "ats": "greenhouse", "token": "circleci"},
    {"name": "GitLab", "ats": "greenhouse", "token": "gitlab"},
    {"name": "Stripe", "ats": "greenhouse", "token": "stripe"},
    {"name": "Robinhood", "ats": "greenhouse", "token": "robinhood"},
    {"name": "Coinbase", "ats": "greenhouse", "token": "coinbase"},
    {"name": "Chime", "ats": "greenhouse", "token": "chime"},
    {"name": "Affirm", "ats": "greenhouse", "token": "affirm"},
    {"name": "Brex", "ats": "greenhouse", "token": "brex"},
    {"name": "Marqeta", "ats": "greenhouse", "token": "marqeta"},
    {"name": "Databricks", "ats": "greenhouse", "token": "databricks"},
    {"name": "Scale AI", "ats": "greenhouse", "token": "scaleai"},
    {"name": "Anthropic", "ats": "greenhouse", "token": "anthropic"},
    {"name": "Asana", "ats": "greenhouse", "token": "asana"},
    {"name": "Figma", "ats": "greenhouse", "token": "figma"},
    {"name": "Airtable", "ats": "greenhouse", "token": "airtable"},
    {"name": "Postman", "ats": "greenhouse", "token": "postman"},
    {"name": "HubSpot", "ats": "greenhouse", "token": "hubspot"},
    {"name": "Webflow", "ats": "greenhouse", "token": "webflow"},
    {"name": "Instacart", "ats": "greenhouse", "token": "instacart"},
    {"name": "Reddit", "ats": "greenhouse", "token": "reddit"},
    {"name": "Lyft", "ats": "greenhouse", "token": "lyft"},
    {"name": "Pinterest", "ats": "greenhouse", "token": "pinterest"},
    {"name": "Faire", "ats": "greenhouse", "token": "faire"},
    {"name": "Abnormal Security", "ats": "greenhouse", "token": "abnormalsecurity"},
    {"name": "Samsara", "ats": "greenhouse", "token": "samsara"},
    {"name": "Gusto", "ats": "greenhouse", "token": "gusto"},
    {"name": "Carta", "ats": "greenhouse", "token": "carta"},
    {"name": "Attentive", "ats": "greenhouse", "token": "attentive"},
    {"name": "Braze", "ats": "greenhouse", "token": "braze"},
    {"name": "Amplitude", "ats": "greenhouse", "token": "amplitude"},
    {"name": "Mixpanel", "ats": "greenhouse", "token": "mixpanel"},
    {"name": "Klaviyo", "ats": "greenhouse", "token": "klaviyo"},
    {"name": "Toast", "ats": "greenhouse", "token": "toast"},
    {"name": "Squarespace", "ats": "greenhouse", "token": "squarespace"},
    {"name": "Discord", "ats": "greenhouse", "token": "discord"},
    {"name": "Duolingo", "ats": "greenhouse", "token": "duolingo"},
    {"name": "Coursera", "ats": "greenhouse", "token": "coursera"},
    {"name": "Flexport", "ats": "greenhouse", "token": "flexport"},

    # ============== GREENHOUSE (verified from Gowtham's 200-company target list) ==============
    {"name": "Block (Square)", "ats": "greenhouse", "token": "block"},
    {"name": "dbt Labs", "ats": "greenhouse", "token": "dbtlabsinc"},
    {"name": "Pulumi", "ats": "greenhouse", "token": "pulumicorporation"},
    {"name": "Wiz", "ats": "greenhouse", "token": "wizinc"},

    # ============== GREENHOUSE (fixed this round, now verified) ==============
    {"name": "DoorDash", "ats": "greenhouse", "token": "doordashusa"},
    {"name": "SentinelOne", "ats": "greenhouse", "token": "sentinellabs"},
    {"name": "Twilio (Segment)", "ats": "greenhouse", "token": "twilio"},
    {"name": "Okta", "ats": "greenhouse", "token": "okta"},

    # ============== LEVER (verified from Gowtham's 200-company target list) ==============
    {"name": "Palantir", "ats": "lever", "token": "palantir"},
    {"name": "Bumble", "ats": "lever", "token": "bumbleinc"},

    # ============== ASHBY (confirmed working) ==============
    {"name": "Linear", "ats": "ashby", "token": "linear"},
    {"name": "Mercury", "ats": "ashby", "token": "mercury"},
    {"name": "Modal", "ats": "ashby", "token": "modal"},
    {"name": "Replit", "ats": "ashby", "token": "replit"},
    {"name": "Vanta", "ats": "ashby", "token": "vanta"},
    {"name": "Ramp", "ats": "ashby", "token": "ramp"},
    {"name": "ElevenLabs", "ats": "ashby", "token": "elevenlabs"},
    {"name": "Cohere", "ats": "ashby", "token": "cohere"},
    {"name": "Vercel", "ats": "ashby", "token": "vercel"},
    {"name": "Notion", "ats": "ashby", "token": "notion"},
    {"name": "Confluent", "ats": "ashby", "token": "confluent"},

    # ============== SMARTRECRUITERS (confirmed working) ==============
    {"name": "Visa", "ats": "smartrecruiters", "company": "Visa"},
    {"name": "Yelp", "ats": "smartrecruiters", "company": "Yelp"},
    {"name": "Bosch", "ats": "smartrecruiters", "company": "BoschGroup"},
    {"name": "IKEA", "ats": "smartrecruiters", "company": "IKEA"},
    {"name": "LegalZoom", "ats": "smartrecruiters", "company": "LegalZoom"},
    {"name": "Poshmark", "ats": "smartrecruiters", "company": "Poshmark"},

    # ============== WORKDAY (confirmed working -- didn't error, but
    # double-check these actually surface real job data, since a wrong
    # site name can sometimes return 200 with zero/odd results) ==============
    {"name": "Adobe", "ats": "workday", "tenant": "adobe", "dc": "wd5", "site": "external_experienced"},
    {"name": "Target", "ats": "workday", "tenant": "target", "dc": "wd5", "site": "targetcareers"},
]