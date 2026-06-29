"""Which companies to monitor, and how to reach each one's jobs API.

Add a company = add one dict here. `adapter` must be a key in
adapters.ADAPTERS; `config` is passed straight to that adapter function.

VERIFIED live during build (sandbox could reach these):
  Amazon, Netflix, Airbnb, Stripe, Databricks, Ramp, + extra Greenhouse cos.

UNVERIFIED (endpoints unreachable from build sandbox or need a token/site
discovered from devtools). Left in but marked. If one errors at runtime,
monitor.py logs it and keeps going — fix the config when convenient.
"""

COMPANIES = [
    # --- Verified ---
    {"name": "Amazon", "adapter": "amazon",
     "config": {"query": "software engineer new grad"}},
    {"name": "Netflix", "adapter": "eightfold",
     "config": {"host": "netflix.eightfold.ai", "domain": "netflix.com",
                "query": "software engineer"}},
    {"name": "Airbnb", "adapter": "greenhouse", "config": {"token": "airbnb"}},
    {"name": "Stripe", "adapter": "greenhouse", "config": {"token": "stripe"}},
    {"name": "Databricks", "adapter": "greenhouse",
     "config": {"token": "databricks"}},
    {"name": "Ramp", "adapter": "ashby", "config": {"org": "ramp"}},
    # Extra Greenhouse companies confirmed live (drop any you don't want):
    {"name": "Coinbase", "adapter": "greenhouse", "config": {"token": "coinbase"}},
    {"name": "Robinhood", "adapter": "greenhouse", "config": {"token": "robinhood"}},
    {"name": "Pinterest", "adapter": "greenhouse", "config": {"token": "pinterest"}},
    {"name": "Dropbox", "adapter": "greenhouse", "config": {"token": "dropbox"}},
    {"name": "Reddit", "adapter": "greenhouse", "config": {"token": "reddit"}},
    {"name": "Figma", "adapter": "greenhouse", "config": {"token": "figma"}},
    {"name": "Brex", "adapter": "greenhouse", "config": {"token": "brex"}},
    {"name": "Block", "adapter": "greenhouse", "config": {"token": "block"}},
    {"name": "Asana", "adapter": "greenhouse", "config": {"token": "asana"}},
    {"name": "Datadog", "adapter": "greenhouse", "config": {"token": "datadog"}},
    {"name": "The Trade Desk", "adapter": "greenhouse",
     "config": {"token": "thetradedesk"}},
    {"name": "Lyft", "adapter": "greenhouse", "config": {"token": "lyft"}},
    {"name": "Twitch", "adapter": "greenhouse", "config": {"token": "twitch"}},
    {"name": "Discord", "adapter": "greenhouse", "config": {"token": "discord"}},
    {"name": "Cloudflare", "adapter": "greenhouse",
     "config": {"token": "cloudflare"}},
    {"name": "DoorDash", "adapter": "greenhouse",
     "config": {"token": "doordashusa"}},
    {"name": "Coupang", "adapter": "greenhouse", "config": {"token": "coupang"}},
    {"name": "Roblox", "adapter": "greenhouse", "config": {"token": "roblox"}},
    {"name": "Affirm", "adapter": "greenhouse", "config": {"token": "affirm"}},
    # Block = Square (same Greenhouse board after rebrand).

    # --- Lever (verified live) ---
    {"name": "Palantir", "adapter": "lever", "config": {"org": "palantir"}},
    {"name": "Spotify", "adapter": "lever", "config": {"org": "spotify"}},

    # --- Ashby (verified live) ---
    {"name": "Notion", "adapter": "ashby", "config": {"org": "Notion"}},
    {"name": "OpenAI", "adapter": "ashby", "config": {"org": "openai"}},
    {"name": "Plaid", "adapter": "ashby", "config": {"org": "plaid"}},

    # --- Workday (verified live) ---
    {"name": "PayPal", "adapter": "workday",
     "config": {"host": "paypal.wd1.myworkdayjobs.com",
                "tenant": "paypal", "site": "jobs",
                "search": "software engineer"}},
    {"name": "Adobe", "adapter": "workday",
     "config": {"host": "adobe.wd5.myworkdayjobs.com",
                "tenant": "adobe", "site": "external_experienced",
                "search": "software engineer"}},
    {"name": "eBay", "adapter": "workday",
     "config": {"host": "ebay.wd5.myworkdayjobs.com",
                "tenant": "ebay", "site": "apply",
                "search": "software engineer"}},
    {"name": "Salesforce", "adapter": "workday",
     "config": {"host": "salesforce.wd12.myworkdayjobs.com",
                "tenant": "salesforce", "site": "External_Career_Site",
                "search": "software engineer"}},
    {"name": "NVIDIA", "adapter": "workday",
     "config": {"host": "nvidia.wd5.myworkdayjobs.com",
                "tenant": "nvidia", "site": "NVIDIAExternalCareerSite",
                "search": "software engineer"}},
    {"name": "Bloomberg", "adapter": "workday",
     "config": {"host": "bloomberg.wd1.myworkdayjobs.com",
                "tenant": "bloomberg",
                "site": "Bloombergindustrygroup_External_Career_Site",
                "search": "software engineer"}},
    # Bloomberg's Workday tenant is Bloomberg Industry Group (formerly BNA);
    # core Bloomberg LP roles live on Avature/careers.bloomberg.com (no JSON
    # API). The INDG board still surfaces engineering new-grad roles.

    # --- Not included (no clean public JSON API found) ---
    # Microsoft: Eightfold, public API 403 (auth-gated); old endpoints dead.
    # Meta, Apple, Google: /api/v1/search requires Apple ID login (401); Google/Meta
    #   fully JS-rendered behind protected APIs.
    # Uber: custom API, not Lever — would need a dedicated adapter.
    # Tesla, Salesforce(non-eng): Workday tenants returned 422 on guessed sites.
    # ByteDance, LinkedIn, Oracle, Blackstone: proprietary or Taleo ATS, no public JSON.
    # GitHub, Snap, Atlassian, HashiCorp, X/Twitter, Codeium: no Greenhouse/Lever/Ashby
    #   board at obvious tokens (all 404). HashiCorp acquired by IBM 2024; Codeium
    #   acquired by Google 2025 — boards likely dead. To add others: open careers page,
    #   find the ATS XHR in devtools, drop a config line above.
]
