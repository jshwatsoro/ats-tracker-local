import re
from typing import Dict, List


def _find_years_required(jd_text: str) -> int:
    """
    Finds minimum years like:
    - "2+ years"
    - "3 years of experience"
    - "minimum 5 years"
    Returns 0 if not found.
    """
    text = jd_text.lower()

    patterns = [
        r"(\d+)\s*\+\s*years",
        r"minimum\s+(\d+)\s+years",
        r"at\s+least\s+(\d+)\s+years",
        r"(\d+)\s+years?\s+of\s+experience",
    ]

    hits = []
    for p in patterns:
        for m in re.finditer(p, text):
            try:
                hits.append(int(m.group(1)))
            except Exception:
                pass

    return min(hits) if hits else 0


def _resume_mentions_years(resume_text: str, years_required: int) -> str:
    """
    Returns: Pass / Unclear
    We do not try to calculate tenure yet (that can be added later).
    """
    if years_required <= 0:
        return "N/A"

    # If resume explicitly mentions years, treat as Pass (simple heuristic)
    text = resume_text.lower()
    if re.search(r"\b(\d+)\s*\+?\s*years\b", text) or "years of experience" in text:
        return "Pass"

    return "Unclear"


def _degree_required(jd_text: str) -> bool:
    text = jd_text.lower()
    # Only flag as required if the JD uses strong language
    required_phrases = [
        "bachelor's degree required",
        "bachelors degree required",
        "degree required",
        "must have a bachelor's",
        "must have a bachelors",
        "required: bachelor",
        "minimum: bachelor",
    ]
    return any(p in text for p in required_phrases)


def _resume_has_degree(resume_text: str) -> str:
    text = resume_text.lower()
    if any(k in text for k in ["bachelor", "b.a.", "b.s.", "ba ", "bs ", "degree"]):
        return "Pass"
    return "Unclear"


def _extract_required_tools(jd_text: str, tool_list: List[str]) -> List[str]:
    """
    Only treat tools as knockouts if JD uses strong language around them.
    Example:
    - "Workday required"
    - "Experience with ADP required"
    """
    text = jd_text.lower()
    required_tools = []

    for tool in tool_list:
        t = tool.lower()
        patterns = [
            rf"{re.escape(t)}\s+required",
            rf"experience\s+with\s+{re.escape(t)}\s+required",
            rf"must\s+have\s+.*{re.escape(t)}",
        ]
        if any(re.search(p, text) for p in patterns):
            required_tools.append(tool)

    return required_tools


def _resume_has_tool(resume_text: str, tool: str) -> bool:
    return tool.lower() in resume_text.lower()


def evaluate_knockouts(jd_text: str, resume_text: str) -> Dict:
    """
    Returns knockout flags designed for recruiter screening.
    Values: Pass / Unclear / Risk / N/A
    """
    years_required = _find_years_required(jd_text)
    years_flag = _resume_mentions_years(resume_text, years_required)

    degree_is_required = _degree_required(jd_text)
    if degree_is_required:
        degree_flag = _resume_has_degree(resume_text)
    else:
        degree_flag = "N/A"

    # Common HR Coordinator tooling (expand later)
    common_tools = [
        "Workday", "ADP", "UKG", "BambooHR", "Rippling",
        "iCIMS", "Greenhouse", "Lever", "Taleo", "SmartRecruiters",
        "Excel", "Google Sheets"
    ]
    required_tools = _extract_required_tools(jd_text, common_tools)

    tools_flags = []
    for t in required_tools:
        tools_flags.append({
            "tool": t,
            "status": "Pass" if _resume_has_tool(resume_text, t) else "Risk"
        })

    return {
        "years_required": years_required,
        "years_flag": years_flag,          # Pass / Unclear / N/A
        "degree_required": degree_is_required,
        "degree_flag": degree_flag,        # Pass / Unclear / N/A
        "required_tools": required_tools,
        "tools_flags": tools_flags,        # list of {tool, status}
    }
