# job-alerts

Emails new-grad SWE postings from 40+ companies (MAANG+ and beyond) to a
Gmail address. Hits each company's JSON jobs API (or, for a few, a headless
browser), filters titles, diffs against `seen.json`, emails anything new.
Runs free on GitHub Actions every 6h — no server.

## How it works

```
monitor.py → adapters.py (per-ATS fetch / Playwright) → filter.py (title match)
           → diff vs seen.json → notify.py (Gmail SMTP) → commit seen.json
```

- `companies.py` — the watch list. One dict per company.
- `adapters.py` — one fetcher per ATS (Greenhouse, Ashby, Lever, Amazon,
  Eightfold, Workday) plus Playwright-based adapters for Apple and Meta.
  Each returns `{id, title, url, location}`.
- `filter.py` — `is_new_grad_swe(title)`. Tune the term lists here.
- `seen.json` — state, committed back by the Action each run.

## Setup

1. Fork this repo (or clone it into a new repo of your own) — GitHub Actions
   only runs under a repo you control.
2. Get a Gmail [**app password**](https://myaccount.google.com/apppasswords) for the account you want alerts sent
   from (not your login password):
   Google Account → Security → 2-Step Verification → App passwords.
3. On your repo → Settings → Secrets and variables → Actions → add:
   - `SMTP_USER` = your Gmail address
   - `SMTP_PASS` = the app password
   - `SMTP_TO` = where to send alerts (optional; defaults to SMTP_USER)
4. Actions tab → **job-check** → Run workflow. First run seeds `seen.json`
   silently (no email). Later runs email only new roles.

## Local run

```bash
pip install -r requirements.txt
python -m playwright install --with-deps chromium   # only needed for Apple/Meta
export SMTP_USER=your.name@gmail.com SMTP_PASS=app-password
python monitor.py
```

## Tests

```bash
python filter.py     # title-matching self-check
python adapters.py   # smoke-test live endpoints
```

## Adding a company

One line in `companies.py`, if it uses a supported ATS:

```python
{"name": "Acme", "adapter": "greenhouse", "config": {"token": "acme"}},
```

Find the token: open the company's job board, view-source / network tab, look
for `boards-api.greenhouse.io/v1/boards/<token>` (or the matching ATS URL).

## Known gaps

- **Apple, Meta** — covered via Playwright (headless Chromium), not a JSON
  API. Slower (~30s each) and more fragile — Meta rate-limits (429) from
  repeated runs off the same IP; the adapter raises so `monitor.py` logs a
  WARN and preserves prior state instead of wiping `seen.json`.
- **Google** — bot detection blocks headless rendering entirely. Not
  included.
- **Microsoft, GitHub, Snap, Atlassian, Uber, ByteDance, LinkedIn, Oracle** —
  no public Greenhouse/Lever/Ashby board or clean JSON API found. See
  comments at the bottom of `companies.py` for what was tried.
