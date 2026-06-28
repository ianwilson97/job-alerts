"""Send the new-jobs digest via Outlook SMTP. Reads creds from env:

    SMTP_USER  - ian_job_alerts@outlook.com (also the To: address)
    SMTP_PASS  - an Outlook app password (not your login password)
    SMTP_TO    - optional override for recipient (defaults to SMTP_USER)
"""

import os
import smtplib
from email.message import EmailMessage

SMTP_HOST = "smtp-mail.outlook.com"
SMTP_PORT = 587


def send_email(jobs):
    """jobs: list of {company, title, location, url}. No-op if empty."""
    if not jobs:
        return
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASS"]
    to = os.environ.get("SMTP_TO", user)

    lines = [f"{len(jobs)} new new-grad SWE posting(s):\n"]
    for j in jobs:
        lines.append(f"• {j['title']} — {j['company']}")
        if j.get("location"):
            lines.append(f"  {j['location']}")
        lines.append(f"  {j['url']}\n")

    msg = EmailMessage()
    msg["Subject"] = f"[Job Alert] {len(jobs)} new new-grad SWE role(s)"
    msg["From"] = user
    msg["To"] = to
    msg.set_content("\n".join(lines))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.starttls()
        s.login(user, password)
        s.send_message(msg)
    print(f"Emailed {len(jobs)} job(s) to {to}")
