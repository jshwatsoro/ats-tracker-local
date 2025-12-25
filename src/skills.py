from typing import List, Set


# You will expand this over time
SKILL_KEYWORDS = {
    # Recruiting & HR
    "recruiting",
    "sourcing",
    "interview scheduling",
    "interview coordination",
    "candidate screening",
    "phone screens",
    "onboarding",
    "offer coordination",
    "background checks",

    # ATS / HRIS
    "ats",
    "greenhouse",
    "lever",
    "workday",
    "icims",
    "adp",
    "paychex",

    # Tools
    "google sheets",
    "google calendar",
    "excel",
    "outlook",
    "slack",
    "zoom",
    "linkedin recruiter",
    "indeed",
    "ziprecruiter",

    # Metrics & ops
    "time to fill",
    "pipeline",
    "headcount",
    "compliance",
    "eeo",
}


def extract_skills(text: str) -> Set[str]:
    """
    Extract known skills/tools from text using keyword matching.
    """
    text_lower = text.lower()
    found = set()

    for skill in SKILL_KEYWORDS:
        if skill in text_lower:
            found.add(skill)

    return found
