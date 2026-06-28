"""Title matching: is this a new-grad software/engineering role?

This is the one piece worth tuning. Edit the term lists below to widen or
narrow what triggers an alert. Run `python filter.py` to check the logic.
"""

NEW_GRAD_TERMS = [
    "new grad",
    "new graduate",
    "university grad",
    "university graduate",
    "early career",
    "early in career",
    "entry level",
    "entry-level",
    "campus",
    "recent graduate",
]

# A role must ALSO look like software/engineering.
ENGINEERING_TERMS = [
    "software engineer",
    "software developer",
    "swe",
    "engineer",
    "developer",
    "programmer",
]

# Hard excludes: senior/lead roles, internships, management, non-eng "engineers".
EXCLUDE_TERMS = [
    "senior",
    "sr.",
    "staff",
    "principal",
    "lead ",
    "intern",
    "manager",
    "director",
    "head of",
    "sales engineer",
    "solutions engineer",
    "support engineer",
    "engineering manager",
]


def is_new_grad_swe(title: str) -> bool:
    """True when title reads like a new-grad software/engineering role."""
    if not title:
        return False
    t = title.lower()
    if any(x in t for x in EXCLUDE_TERMS):
        return False
    if not any(x in t for x in ENGINEERING_TERMS):
        return False
    return any(x in t for x in NEW_GRAD_TERMS)


def demo():
    should_pass = [
        "Software Engineer, New Grad",
        "New Graduate Software Engineer (2026)",
        "University Graduate, Software Engineer",
        "Early Career Software Developer",
        "Entry-Level Software Engineer",
        "Campus Engineer - Backend",
    ]
    should_fail = [
        "Senior Software Engineer",
        "Software Engineer Intern",
        "Staff Software Engineer, New Grad",  # senior wins
        "Engineering Manager",
        "New Grad Product Manager",  # not engineering
        "Sales Engineer, University Program",  # excluded role
        "Software Engineer",  # not flagged new grad
        "Account Executive",
    ]
    for title in should_pass:
        assert is_new_grad_swe(title), f"should PASS: {title!r}"
    for title in should_fail:
        assert not is_new_grad_swe(title), f"should FAIL: {title!r}"
    print(f"OK: {len(should_pass)} pass, {len(should_fail)} fail cases correct")


if __name__ == "__main__":
    demo()
