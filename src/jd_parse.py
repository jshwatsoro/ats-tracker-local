import re
from typing import Dict, List


MUST_HAVE_HINTS = [
    "required qualifications",
    "minimum qualifications",
    "minimum requirements",
    "basic qualifications",
    "core qualifications",
    "required",
    "requirements",
    "qualifications",
    "must have",
    "what you bring",
    "knowledge, skills, and abilities",
    "knowledge skills and abilities",
    "ksas",
]

NICE_TO_HAVE_HINTS = [
    "preferred qualifications",
    "preferred requirements",
    "preferred",
    "nice to have",
    "nice-to-have",
    "bonus",
    "desired",
    "additional qualifications",
    "plus",
]


def _clean_lines(text: str) -> List[str]:
    text = text.replace("\r", "\n")
    lines = [ln.strip() for ln in text.split("\n")]
    return [ln for ln in lines if ln]


def _is_bullet(line: str) -> bool:
    return bool(re.match(r"^(\-|\*|•|\u2022|\d+\.|\(\d+\))\s+", line))


def _strip_bullet_prefix(line: str) -> str:
    return re.sub(r"^(\-|\*|•|\u2022|\d+\.|\(\d+\))\s+", "", line).strip()


def parse_job_description(jd_text: str) -> Dict[str, List[str]]:
    """
    Heuristic parser:
    - Detects section headers like Required Qualifications / Preferred Qualifications / KSAs
    - Captures bullets beneath them
    - Everything else goes into other_bullets
    """
    lines = _clean_lines(jd_text)

    must_have: List[str] = []
    nice_to_have: List[str] = []
    other: List[str] = []

    current_section = "other"

    for line in lines:
        lower = line.lower()

        # detect section headers (more forgiving)
        is_short_header = len(line) <= 120
        looks_like_header = line.endswith(":") or is_short_header

        if looks_like_header and any(h in lower for h in MUST_HAVE_HINTS):
            current_section = "must"
            continue

        if looks_like_header and any(h in lower for h in NICE_TO_HAVE_HINTS):
            current_section = "nice"
            continue

        # collect bullets
        if _is_bullet(line):
            item = _strip_bullet_prefix(line)
            if not item:
                continue

            if current_section == "must":
                must_have.append(item)
            elif current_section == "nice":
                nice_to_have.append(item)
            else:
                other.append(item)

    # fallback: if no bullets captured, split by sentences (basic)
    if not must_have and not nice_to_have and not other:
        sentences = re.split(r"(?<=[.!?])\s+", jd_text.strip())
        other = [s.strip() for s in sentences if len(s.strip()) > 20]

    return {
        "must_have": must_have,
        "nice_to_have": nice_to_have,
        "other_bullets": other,
    }
