"""Entry point. For each company: fetch jobs, keep the new-grad SWE ones, diff
against seen.json, email anything new, then persist the updated seen set.

First run (no seen.json) seeds state silently — no 200-job email blast.

Run:  python monitor.py
Env:  SMTP_USER, SMTP_PASS  (see notify.py)
"""

import json
import os
import sys

from adapters import ADAPTERS
from companies import COMPANIES
from filter import is_new_grad_swe
from notify import send_email

SEEN_FILE = os.path.join(os.path.dirname(__file__), "seen.json")


def load_seen():
    if not os.path.exists(SEEN_FILE):
        return None  # signals first run
    with open(SEEN_FILE) as f:
        return json.load(f)


def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(seen, f, indent=2, sort_keys=True)


def main():
    seen = load_seen()
    first_run = seen is None
    if first_run:
        seen = {}
        print("First run: seeding seen.json, no email will be sent.")

    new_jobs = []
    updated = {}

    for company in COMPANIES:
        name = company["name"]
        fetch = ADAPTERS[company["adapter"]]
        try:
            jobs = fetch(company["config"])
        except Exception as e:
            print(f"WARN {name}: fetch failed ({e}); keeping prior seen set")
            # Preserve old IDs so a transient outage doesn't re-alert later.
            updated[name] = seen.get(name, [])
            continue

        matched = {j["id"]: j for j in jobs if is_new_grad_swe(j["title"])}
        prior = set(seen.get(name, []))
        fresh_ids = set(matched) - prior

        if not first_run:
            for jid in fresh_ids:
                j = matched[jid]
                new_jobs.append({"company": name, **j})

        # Persist union: matched now + anything seen before still relevant.
        updated[name] = sorted(set(matched) | prior)
        print(f"{name}: {len(matched)} matched, {len(fresh_ids)} new")

    save_seen(updated)

    if new_jobs:
        send_email(new_jobs)
    elif not first_run:
        print("No new jobs.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
