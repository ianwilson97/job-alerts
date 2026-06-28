# job-alerts

Emails `ian_job_alerts@outlook.com` when MAANG+ companies open **new-grad SWE**
roles. Hits each company's JSON jobs API, filters titles, diffs against
`seen.json`, emails anything new. Runs free on GitHub Actions every 6h — no
server.

## How it works

```
monitor.py → adapters.py (per-ATS fetch) → filter.py (title match)
           → diff vs seen.json → notify.py (Outlook SMTP) → commit seen.json
```

- `companies.py` — the watch list. One dict per company.
- `adapters.py` — one fetcher per ATS (Greenhouse, Ashby, Lever, Amazon,
  Eightfold, Workday). Each returns `{id, title, url, location}`.
- `filter.py` — `is_new_grad_swe(title)`. Tune the term lists here.
- `seen.json` — state, committed back by the Action each run.

## Setup

1. Push this repo to GitHub.
2. Get an Outlook **app password** (not your login password):
   Outlook → Security → Advanced security → App passwords.
3. Repo → Settings → Secrets and variables → Actions → add:
   - `SMTP_USER` = `ian_job_alerts@outlook.com`
   - `SMTP_PASS` = the app password
   - `SMTP_TO` = `ian_job_alerts@outlook.com` (optional; defaults to SMTP_USER)
4. Actions tab → **job-check** → Run workflow. First run seeds `seen.json`
   silently (no email). Later runs email only new roles.

## Local run

```bash
pip install -r requirements.txt
export SMTP_USER=ian_job_alerts@outlook.com SMTP_PASS=app-password
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

- **Meta, Apple, Google** — career sites sit behind JS-rendered / protected
  APIs that block plain HTTP. Not included (would need a headless browser,
  against the no-server design).
- **Microsoft, NVIDIA, Bloomberg** — Workday configs are best-guess and marked
  `TODO: verify` in `companies.py`. Confirm each tenant/site from the careers
  site's devtools (`/wday/cxs/<tenant>/<site>/jobs`). If wrong, `monitor.py`
  logs a WARN and skips — it won't crash the run.
- **Uber** — uses a custom API; needs its own adapter. Left out.
