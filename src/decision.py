from typing import Dict, List


def _count_missing_must(must_results: List[Dict]) -> int:
    return sum(1 for r in must_results if not r.get("met", False))


def _has_tool_risk(knockouts: Dict) -> bool:
    for item in knockouts.get("tools_flags", []):
        if item.get("status") == "Risk":
            return True
    return False


def recruiter_decision(
    parse_info: Dict,
    must_results: List[Dict],
    score_breakdown: Dict,
    knockouts: Dict
) -> Dict:
    """
    Returns:
    - decision: Shortlist / Review / Reject
    - reasons: list of strings (for transparency)
    """

    reasons = []

    must_pct = score_breakdown.get("must_have_pct", 0)
    skills_pct = score_breakdown.get("skills_pct", 0)

    missing_must = _count_missing_must(must_results)

    parse_status = parse_info.get("status", "Needs review")
    years_flag = knockouts.get("years_flag", "N/A")
    degree_flag = knockouts.get("degree_flag", "N/A")
    tool_risk = _has_tool_risk(knockouts)

    # --- Reject rules ---
    if parse_status == "Fail":
        return {
            "decision": "Reject",
            "reasons": ["Resume parseability failed (text extraction too low or unreadable)."]
        }

    if must_pct < 50 and missing_must >= 2:
        reasons.append("Must-have coverage is below 50% with multiple missing requirements.")
        return {"decision": "Reject", "reasons": reasons}

    if tool_risk:
        reasons.append("A tool marked as REQUIRED in the JD appears missing in the resume.")
        # Tool risk is often a hard screen. Keep as Reject to match recruiter reality.
        return {"decision": "Reject", "reasons": reasons}

    # --- Shortlist rules ---
    if parse_status == "Good" and must_pct >= 80 and skills_pct >= 60:
        # Avoid shortlisting if key items are unclear
        if years_flag == "Unclear":
            reasons.append("Years requirement is unclear from resume text.")
            return {"decision": "Review", "reasons": reasons}
        if degree_flag == "Unclear":
            reasons.append("Degree requirement is unclear from resume text.")
            return {"decision": "Review", "reasons": reasons}

        return {
            "decision": "Shortlist",
            "reasons": ["Strong must-have coverage and solid skills/tools match."]
        }

    # --- Default ---
    # Anything not clearly strong or clearly failing goes to Review
    if parse_status != "Good":
        reasons.append("Parseability needs review.")
    if must_pct < 80:
        reasons.append("Must-have coverage is not yet strong.")
    if skills_pct < 60:
        reasons.append("Skills/tools coverage is moderate or low.")
    if years_flag == "Unclear":
        reasons.append("Years requirement is unclear from resume text.")
    if degree_flag == "Unclear":
        reasons.append("Degree requirement is unclear from resume text.")

    return {"decision": "Review", "reasons": reasons}
