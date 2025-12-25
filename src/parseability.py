import re
from typing import Dict, List


EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)

PHONE_RE = re.compile(
    r"(\+?1[\s\-\.]?)?(\(?\d{3}\)?[\s\-\.]?)\d{3}[\s\-\.]?\d{4}"
)

DATE_RE = re.compile(
    r"\b(0?[1-9]|1[0-2])\/(\d{4})\b|\b(20\d{2}|19\d{2})\b"
)

HEADINGS = [
    "experience",
    "work experience",
    "professional experience",
    "education",
    "skills",
    "certifications",
    "summary",
]


def check_parseability(resume_text: str) -> Dict:
    text = (resume_text or "").strip()
    lower = text.lower()

    has_text = len(text) >= 200
    text_length = len(text)

    has_email = bool(EMAIL_RE.search(text))
    has_phone = bool(PHONE_RE.search(text))

    found_headings: List[str] = []
    for h in HEADINGS:
        if h in lower:
            found_headings.append(h)

    has_headings = len(found_headings) >= 2
    has_dates = bool(DATE_RE.search(text))

    points = 0
    points += 1 if has_text else 0
    points += 1 if has_email else 0
    points += 1 if has_phone else 0
    points += 1 if has_headings else 0
    points += 1 if has_dates else 0

    if not has_text:
        status = "Fail"
    elif points >= 4:
        status = "Good"
    else:
        status = "Needs review"

    return {
        "status": status,
        "points": points,
        "text_length": text_length,
        "has_email": has_email,
        "has_phone": has_phone,
        "has_headings": has_headings,
        "found_headings": found_headings,
        "has_dates": has_dates,
    }
