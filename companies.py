# List of companies to poll for new job postings, across 5 ATS platforms.
#
# Each entry needs "name", "ats", and then ATS-specific fields:
#
#   greenhouse:      {"token": "<slug>"}
#       -> from careers URL like boards.greenhouse.io/<slug>
#   lever:           {"token": "<slug>"}
#       -> from careers URL like jobs.lever.co/<slug>
#   ashby:           {"token": "<slug>"}
#       -> from careers URL like jobs.ashbyhq.com/<slug>
#   smartrecruiters: {"company": "<id>"}
#       -> from careers URL like jobs.smartrecruiters.com/<id>
#   workday:         {"tenant": "...", "dc": "...", "site": "..."}
#       -> NOT guessable from the careers URL alone. See README for how
#          to find these 3 values (they require checking your browser's
#          network tab). The Workday entries below are placeholders /
#          best-effort guesses and will likely need correcting.
#
# Wrong/failed entries are skipped and logged, not fatal.

COMPANIES = [
    # ============== GREENHOUSE ==============
    {"name": "HashiCorp", "ats": "greenhouse", "token": "hashicorp"},
    {"name": "Datadog", "ats": "greenhouse", "token": "datadog"},
    {"name": "Grafana Labs", "ats": "greenhouse", "token": "grafanalabs"},
    {"name": "Elastic", "ats": "greenhouse", "token": "elastic"},
    {"name": "MongoDB", "ats": "greenhouse", "token": "mongodb"},
    {"name": "Confluent", "ats": "greenhouse", "token": "confluent"},
    {"name": "Cloudflare", "ats": "greenhouse", "token": "cloudflare"},
    {"name": "Fastly", "ats": "greenhouse", "token": "fastly"},
    {"name": "PagerDuty", "ats": "greenhouse", "token": "pagerduty"},
    {"name": "New Relic", "ats": "greenhouse", "token": "newrelic"},
    {"name": "Sysdig", "ats": "greenhouse", "token": "sysdig"},
    {"name": "JFrog", "ats": "greenhouse", "token": "jfrog"},
    {"name": "Cribl", "ats": "greenhouse", "token": "cribl"},
    {"name": "Chronosphere", "ats": "greenhouse", "token": "chronosphere"},
    {"name": "DigitalOcean", "ats": "greenhouse", "token": "digitalocean"},
    {"name": "Docker", "ats": "greenhouse", "token": "docker"},
    {"name": "Temporal Technologies", "ats": "greenhouse", "token": "temporaltechnologies"},
    {"name": "LaunchDarkly", "ats": "greenhouse", "token": "launchdarkly"},
    {"name": "Rapid7", "ats": "greenhouse", "token": "rapid7"},
    {"name": "Tenable", "ats": "greenhouse", "token": "tenable"},
    {"name": "CircleCI", "ats": "greenhouse", "token": "circleci"},
    {"name": "GitLab", "ats": "greenhouse", "token": "gitlab"},
    {"name": "Equinix", "ats": "greenhouse", "token": "equinix"},
    {"name": "Stripe", "ats": "greenhouse", "token": "stripe"},
    {"name": "Plaid", "ats": "greenhouse", "token": "plaid"},
    {"name": "Robinhood", "ats": "greenhouse", "token": "robinhood"},
    {"name": "Coinbase", "ats": "greenhouse", "token": "coinbase"},
    {"name": "Chime", "ats": "greenhouse", "token": "chime"},
    {"name": "Affirm", "ats": "greenhouse", "token": "affirm"},
    {"name": "Brex", "ats": "greenhouse", "token": "brex"},
    {"name": "Marqeta", "ats": "greenhouse", "token": "marqeta"},
    {"name": "Klarna", "ats": "greenhouse", "token": "klarna"},
    {"name": "Databricks", "ats": "greenhouse", "token": "databricks"},
    {"name": "Scale AI", "ats": "greenhouse", "token": "scaleai"},
    {"name": "DataRobot", "ats": "greenhouse", "token": "datarobot"},
    {"name": "Anyscale", "ats": "greenhouse", "token": "anyscale"},
    {"name": "Anthropic", "ats": "greenhouse", "token": "anthropic"},
    {"name": "Hugging Face", "ats": "greenhouse", "token": "huggingface"},
    {"name": "Asana", "ats": "greenhouse", "token": "asana"},
    {"name": "Figma", "ats": "greenhouse", "token": "figma"},
    {"name": "Airtable", "ats": "greenhouse", "token": "airtable"},
    {"name": "Miro", "ats": "greenhouse", "token": "miro"},
    {"name": "Postman", "ats": "greenhouse", "token": "postman"},
    {"name": "HubSpot", "ats": "greenhouse", "token": "hubspot"},
    {"name": "Webflow", "ats": "greenhouse", "token": "webflow"},
    {"name": "Loom", "ats": "greenhouse", "token": "loom"},
    {"name": "Grammarly", "ats": "greenhouse", "token": "grammarly"},
    {"name": "DoorDash", "ats": "greenhouse", "token": "doordash"},
    {"name": "Instacart", "ats": "greenhouse", "token": "instacart"},
    {"name": "Reddit", "ats": "greenhouse", "token": "reddit"},
    {"name": "Lyft", "ats": "greenhouse", "token": "lyft"},
    {"name": "Pinterest", "ats": "greenhouse", "token": "pinterest"},
    {"name": "Faire", "ats": "greenhouse", "token": "faire"},
    {"name": "Thumbtack", "ats": "greenhouse", "token": "thumbtack"},
    {"name": "Zillow", "ats": "greenhouse", "token": "zillow"},
    {"name": "Compass", "ats": "greenhouse", "token": "compass"},
    {"name": "Oscar Health", "ats": "greenhouse", "token": "oscarhealth"},
    {"name": "Devoted Health", "ats": "greenhouse", "token": "devotedhealth"},
    {"name": "Ro", "ats": "greenhouse", "token": "ro"},
    {"name": "Included Health", "ats": "greenhouse", "token": "includedhealth"},
    {"name": "SentinelOne", "ats": "greenhouse", "token": "sentinelone"},
    {"name": "Abnormal Security", "ats": "greenhouse", "token": "abnormalsecurity"},
    {"name": "Samsara", "ats": "greenhouse", "token": "samsara"},
    {"name": "Gusto", "ats": "greenhouse", "token": "gusto"},
    {"name": "Rippling", "ats": "greenhouse", "token": "rippling"},
    {"name": "Deel", "ats": "greenhouse", "token": "deel"},
    {"name": "Carta", "ats": "greenhouse", "token": "carta"},
    {"name": "Benchling", "ats": "greenhouse", "token": "benchling"},
    {"name": "Attentive", "ats": "greenhouse", "token": "attentive"},
    {"name": "Braze", "ats": "greenhouse", "token": "braze"},
    {"name": "Amplitude", "ats": "greenhouse", "token": "amplitude"},
    {"name": "Mixpanel", "ats": "greenhouse", "token": "mixpanel"},
    {"name": "Segment", "ats": "greenhouse", "token": "segment"},
    {"name": "Klaviyo", "ats": "greenhouse", "token": "klaviyo"},
    {"name": "Toast", "ats": "greenhouse", "token": "toast"},
    {"name": "Squarespace", "ats": "greenhouse", "token": "squarespace"},
    {"name": "Discord", "ats": "greenhouse", "token": "discord"},
    {"name": "Duolingo", "ats": "greenhouse", "token": "duolingo"},
    {"name": "Coursera", "ats": "greenhouse", "token": "coursera"},
    {"name": "Flexport", "ats": "greenhouse", "token": "flexport"},
    {"name": "Turo", "ats": "greenhouse", "token": "turo"},
    {"name": "GoodRx", "ats": "greenhouse", "token": "goodrx"},

    # ============== LEVER ==============
    {"name": "Render", "ats": "lever", "token": "render"},
    {"name": "Sourcegraph", "ats": "lever", "token": "sourcegraph"},
    {"name": "Buildkite", "ats": "lever", "token": "buildkite"},
    {"name": "Cedar", "ats": "lever", "token": "cedar"},
    {"name": "Zscaler", "ats": "lever", "token": "zscaler"},
    {"name": "Netskope", "ats": "lever", "token": "netskope"},
    {"name": "1Password", "ats": "lever", "token": "1password"},

    # ============== ASHBY ==============
    {"name": "Linear", "ats": "ashby", "token": "linear"},
    {"name": "Retool", "ats": "ashby", "token": "retool"},
    {"name": "Mercury", "ats": "ashby", "token": "mercury"},
    {"name": "Modal", "ats": "ashby", "token": "modal"},
    {"name": "Replit", "ats": "ashby", "token": "replit"},
    {"name": "Vanta", "ats": "ashby", "token": "vanta"},
    {"name": "Ramp", "ats": "ashby", "token": "ramp"},
    {"name": "ElevenLabs", "ats": "ashby", "token": "elevenlabs"},
    {"name": "Together AI", "ats": "ashby", "token": "togetherai"},
    {"name": "Weights & Biases", "ats": "ashby", "token": "wandb"},
    {"name": "Cohere", "ats": "ashby", "token": "cohere"},
    {"name": "Runway", "ats": "ashby", "token": "runwayml"},
    {"name": "Perplexity", "ats": "ashby", "token": "perplexityai"},
    {"name": "Vercel", "ats": "ashby", "token": "vercel"},
    {"name": "Notion", "ats": "ashby", "token": "notion"},

    # ============== SMARTRECRUITERS ==============
    {"name": "Visa", "ats": "smartrecruiters", "company": "Visa"},
    {"name": "Yelp", "ats": "smartrecruiters", "company": "Yelp"},
    {"name": "Bosch", "ats": "smartrecruiters", "company": "BoschGroup"},
    {"name": "IKEA", "ats": "smartrecruiters", "company": "IKEA"},
    {"name": "LegalZoom", "ats": "smartrecruiters", "company": "LegalZoom"},
    {"name": "Poshmark", "ats": "smartrecruiters", "company": "Poshmark"},

    # ============== WORKDAY ==============
    # LOW CONFIDENCE -- these tenant/dc/site values are best-effort guesses.
    # Verify and fix using the steps in README.md before relying on them.
    # Included because several are Houston-area energy majors that hire
    # a lot of cloud/DevOps/infra roles.
    {"name": "Shell", "ats": "workday", "tenant": "shell", "dc": "wd3", "site": "SHELL_CAREERS"},
    {"name": "Chevron", "ats": "workday", "tenant": "chevron", "dc": "wd5", "site": "Chevron_Careers"},
    {"name": "ConocoPhillips", "ats": "workday", "tenant": "conocophillips", "dc": "wd1", "site": "ConocoPhillips_Careers"},
    {"name": "Halliburton", "ats": "workday", "tenant": "halliburton", "dc": "wd1", "site": "Halliburton_Careers"},
    {"name": "SLB", "ats": "workday", "tenant": "slb", "dc": "wd3", "site": "SLB_Careers"},
    {"name": "Phillips 66", "ats": "workday", "tenant": "phillips66", "dc": "wd1", "site": "Phillips66_Careers"},
    {"name": "Marathon Petroleum", "ats": "workday", "tenant": "marathonpetroleum", "dc": "wd1", "site": "Marathon_Careers"},
    {"name": "ExxonMobil", "ats": "workday", "tenant": "exxonmobil", "dc": "wd1", "site": "ExxonMobil_Careers"},
    {"name": "ServiceNow", "ats": "workday", "tenant": "servicenow", "dc": "wd1", "site": "Careers"},
    {"name": "Salesforce", "ats": "workday", "tenant": "salesforce", "dc": "wd1", "site": "External_Career_Site"},
    {"name": "Adobe", "ats": "workday", "tenant": "adobe", "dc": "wd5", "site": "external_experienced"},
    {"name": "Target", "ats": "workday", "tenant": "target", "dc": "wd5", "site": "targetcareers"},
]
