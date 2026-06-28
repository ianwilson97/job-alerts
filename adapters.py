"""One fetcher per ATS platform. Each returns a list of normalized jobs:

    {"id": str, "title": str, "url": str, "location": str}

Adding a company = a config line in companies.py, not new code here — as long
as it uses one of these ATS platforms.
"""

from urllib.parse import quote

import requests

TIMEOUT = 30
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) job-alerts",
    "Accept": "application/json",
}


def _loc(value) -> str:
    """Greenhouse/Ashby sometimes give a dict, sometimes a string."""
    if isinstance(value, dict):
        return value.get("name") or value.get("locationName") or ""
    return value or ""


def greenhouse(cfg):
    """cfg: {"token": "airbnb"}  -> boards-api.greenhouse.io"""
    token = cfg["token"]
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    out = []
    for j in r.json().get("jobs", []):
        out.append({
            "id": str(j["id"]),
            "title": j.get("title", ""),
            "url": j.get("absolute_url", ""),
            "location": _loc(j.get("location")),
        })
    return out


def ashby(cfg):
    """cfg: {"org": "ramp"}  -> api.ashbyhq.com posting board"""
    org = cfg["org"]
    url = f"https://api.ashbyhq.com/posting-api/job-board/{org}?includeCompensation=false"
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    out = []
    for j in r.json().get("jobs", []):
        if j.get("isListed") is False:
            continue
        out.append({
            "id": str(j["id"]),
            "title": j.get("title", ""),
            "url": j.get("jobUrl") or j.get("applyUrl", ""),
            "location": _loc(j.get("location")),
        })
    return out


def lever(cfg):
    """cfg: {"org": "plaid"}  -> api.lever.co (returns a JSON list)"""
    org = cfg["org"]
    url = f"https://api.lever.co/v0/postings/{org}?mode=json"
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    out = []
    for j in r.json():
        out.append({
            "id": str(j["id"]),
            "title": j.get("text", ""),
            "url": j.get("hostedUrl", ""),
            "location": (j.get("categories") or {}).get("location", ""),
        })
    return out


def amazon(cfg):
    """cfg: {"query": "software engineer"} -> amazon.jobs search.json (paged)"""
    query = cfg.get("query", "software engineer")
    out = []
    offset = 0
    while True:
        url = (
            "https://www.amazon.jobs/en/search.json"
            f"?base_query={quote(query)}"
            f"&result_limit=100&offset={offset}&sort=recent"
        )
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        jobs = data.get("jobs", [])
        if not jobs:
            break
        for j in jobs:
            out.append({
                "id": str(j.get("id_icims") or j["id"]),
                "title": j.get("title", ""),
                "url": "https://www.amazon.jobs" + j.get("job_path", ""),
                "location": j.get("normalized_location") or j.get("location", ""),
            })
        offset += 100
        if offset >= int(data.get("hits", 0)) or offset >= 1000:
            break
    return out


def eightfold(cfg):
    """cfg: {"host": "netflix.eightfold.ai", "domain": "netflix.com",
             "query": "engineer"}  -> Eightfold ATS (paged)"""
    host = cfg["host"]
    domain = cfg["domain"]
    query = cfg.get("query", "engineer")
    out = []
    start = 0
    while True:
        url = (
            f"https://{host}/api/apply/v2/jobs"
            f"?domain={domain}&query={quote(query)}"
            f"&start={start}&num=100&sort_by=relevance"
        )
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        positions = r.json().get("positions", [])
        if not positions:
            break
        for p in positions:
            out.append({
                "id": str(p.get("id") or p.get("display_job_id")),
                "title": p.get("name", ""),
                "url": p.get("canonicalPositionUrl", ""),
                "location": p.get("location", ""),
            })
        start += 100
        if start >= 1000:
            break
    return out


def workday(cfg):
    """cfg: {"host": "nvidia.wd5.myworkdayjobs.com", "tenant": "nvidia",
             "site": "NVIDIAExternalCareerSite",
             "search": "software"}  -> Workday CXS jobs (POST, paged)

    To add a Workday company: open its careers site, find the
    `/wday/cxs/<tenant>/<site>/jobs` POST in devtools, copy host/tenant/site.
    """
    host = cfg["host"]
    site = cfg["site"]
    tenant = cfg["tenant"]
    search = cfg.get("search", "")
    base = f"https://{host}/wday/cxs/{tenant}/{site}"
    out = []
    offset = 0
    while True:
        r = requests.post(
            f"{base}/jobs",
            headers={**HEADERS, "Content-Type": "application/json"},
            json={"limit": 20, "offset": offset, "searchText": search},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()
        postings = data.get("jobPostings", [])
        if not postings:
            break
        for p in postings:
            path = p.get("externalPath", "")
            out.append({
                "id": str(p.get("bulletFields", [p.get("title")])[0] or path),
                "title": p.get("title", ""),
                "url": f"https://{host}{path}",
                "location": p.get("locationsText", ""),
            })
        offset += 20
        if offset >= int(data.get("total", 0)) or offset >= 1000:
            break
    return out


# Registry: name -> fetcher function. companies.py references these by name.
ADAPTERS = {
    "greenhouse": greenhouse,
    "ashby": ashby,
    "lever": lever,
    "amazon": amazon,
    "eightfold": eightfold,
    "workday": workday,
}


def _smoke():
    """Hit a couple of known-live endpoints; confirm they parse."""
    checks = [
        ("greenhouse", {"token": "airbnb"}),
        ("ashby", {"org": "ramp"}),
        ("eightfold", {"host": "netflix.eightfold.ai",
                       "domain": "netflix.com", "query": "engineer"}),
        ("workday", {"host": "nvidia.wd5.myworkdayjobs.com", "tenant": "nvidia",
                     "site": "NVIDIAExternalCareerSite",
                     "search": "software engineer"}),
    ]
    for name, cfg in checks:
        try:
            jobs = ADAPTERS[name](cfg)
            assert jobs, f"{name} returned nothing"
            j = jobs[0]
            assert j["id"] and j["title"], f"{name} job missing id/title"
            print(f"OK {name}: {len(jobs)} jobs, e.g. {j['title']!r}")
        except Exception as e:
            print(f"FAIL {name}: {e}")


if __name__ == "__main__":
    _smoke()
