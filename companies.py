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

    # --- Workday (verified live) ---
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

    # --- Not included ---
    # Microsoft: migrated to apply.careers.microsoft.com on Eightfold, but its
    #   public job API returns 403 (auth-gated). Old gcsservices/widgets
    #   endpoints are dead (404/302). No clean unauthenticated JSON -> dropped.
    # Uber: custom API, not Lever — needs a dedicated adapter.
    # Meta, Apple, Google: JS-rendered behind protected APIs that block plain
    #   HTTP. Out of scope for the no-server design.
]
