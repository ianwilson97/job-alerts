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


def apple(cfg):
    """cfg: {"query": "new grad software engineer"} -> jobs.apple.com (Playwright)

    Paginates URL-based (?page=N) until a page returns 0 job links.
    Caps at 10 pages (200 jobs) so CI doesn't hang on broad queries.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise RuntimeError(
            "playwright not installed; run: pip install playwright && "
            "python -m playwright install chromium"
        )
    from urllib.parse import quote as _quote

    query = cfg.get("query", "new grad software engineer")
    out = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 900},
            locale="en-US",
        )
        page = ctx.new_page()

        for page_num in range(1, 11):
            page.goto(
                f"https://jobs.apple.com/en-us/search?sort=newest&page={page_num}"
                f"&key={_quote(query)}",
                timeout=30000,
                wait_until="domcontentloaded",
            )
            page.wait_for_timeout(7000)

            jobs = page.evaluate("""() => {
                const seen = new Set();
                const result = [];
                document.querySelectorAll('a[href*="/en-us/details/"]').forEach(a => {
                    const m = a.href.match(/details[/]([0-9]+)/);
                    if (!m || seen.has(m[1])) return;
                    seen.add(m[1]);
                    const card = a.closest('[class*="accordion"]') || a.parentElement;
                    const text = card ? card.innerText : '';
                    const loc = text.match(/Location\\n([^\\n]+)/);
                    result.push({
                        id: m[1],
                        title: a.innerText.trim(),
                        url: 'https://jobs.apple.com/en-us/details/' + m[1],
                        location: loc ? loc[1].trim() : '',
                    });
                });
                return result;
            }""")

            if not jobs:
                break
            out.extend(jobs)

        browser.close()

    return out


def meta(cfg):
    """cfg: {"query": "software engineer new grad"} -> metacareers.com (Playwright)

    Note: metacareers.com 429s aggressively from the same IP. In CI (fresh IP each
    run) this usually succeeds. If it fails, monitor.py logs a warning and skips.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise RuntimeError(
            "playwright not installed; run: pip install playwright && "
            "python -m playwright install chromium"
        )
    from urllib.parse import quote as _quote

    query = cfg.get("query", "software engineer new grad")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 900},
            locale="en-US",
        )
        page = ctx.new_page()
        page.goto(
            f"https://www.metacareers.com/jobs?q={_quote(query)}",
            timeout=30000,
            wait_until="load",
        )
        page.wait_for_timeout(10000)

        body_len, jobs = page.evaluate("""() => {
            const seen = new Set();
            const result = [];
            document.querySelectorAll('a[href]').forEach(a => {
                const m = a.href.match(/metacareers\\.com[/]jobs[/]([0-9]+)/);
                if (!m || seen.has(m[1])) return;
                seen.add(m[1]);
                const lines = a.innerText.trim().split('\\n')
                    .map(l => l.trim()).filter(Boolean);
                result.push({
                    id: m[1],
                    title: lines[0] || '',
                    url: 'https://www.metacareers.com/jobs/' + m[1] + '/',
                    location: lines.slice(1).join(', '),
                });
            });
            return [document.body ? document.body.innerHTML.length : 0, result];
        }""")

        browser.close()

    # Empty results on a real page load = scraper broken or rate-limited.
    # Raise so monitor.py logs WARN and preserves prior seen state.
    if not jobs and body_len < 5000:
        raise RuntimeError(f"Meta: page body too short ({body_len} bytes) — likely 429 or block")
    if not jobs and body_len >= 5000:
        raise RuntimeError("Meta: page loaded but no job links found — selector may be stale")

    return jobs


# Registry: name -> fetcher function. companies.py references these by name.
ADAPTERS = {
    "greenhouse": greenhouse,
    "ashby": ashby,
    "lever": lever,
    "amazon": amazon,
    "eightfold": eightfold,
    "workday": workday,
    "apple": apple,
    "meta": meta,
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
