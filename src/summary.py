from typing import List, Dict


def _top_n(items: List[str], n: int) -> List[str]:
    return items[:n] if items else []


def build_fix_summary(
    score: float,
    must_results: List[Dict],
    missing_skills: List[str],
    matched_skills: List[str],
) -> str:
    """
    Rule-based recruiter summary. 1–2 short paragraphs.
    No hallucinations. Uses only detected gaps.
    """

    total_must = len(must_results)
    met_must = sum(1 for r in must_results if r.get("met"))
    missing_must = [r["requirement"] for r in must_results if not r.get("met")]

    top_missing_must = _top_n(missing_must, 3)
    top_missing_skills = _top_n(missing_skills, 6)
    top_matched = _top_n(matched_skills, 6)

    # Paragraph 1: overall alignment + strengths + biggest gaps
    if score >= 80:
        level = "strong"
    elif score >= 60:
        level = "moderate"
    else:
        level = "limited"

    strengths_part = ""
    if top_matched:
        strengths_part = f" Strong matches include: {', '.join(top_matched)}."

    gaps_part = ""
    if top_missing_must:
        gaps_part += f" Key must-have gaps: {', '.join(top_missing_must)}."
    if top_missing_skills:
        gaps_part += f" Missing tools/skills mentioned in the JD: {', '.join(top_missing_skills)}."

    p1 = (
        f"Overall alignment is {level} based on this job description. "
        f"The resume meets {met_must} of {total_must} must-have requirements and scored {score:.1f}%."
        f"{strengths_part}{gaps_part}"
    )

    # Paragraph 2: how to fix (actionable, no inventing)
    actions = []

    if top_missing_skills:
        actions.append(
            "Add a short Core Skills/Tools section near the top and include only the missing tools you truly have experience with."
        )

    if top_missing_must:
        actions.append(
            "Rewrite 2–3 bullets to mirror the job’s must-have language, and add 1 line of context that proves you’ve done the work (scope, volume, cadence)."
        )

    actions.append(
        "Quantify impact where possible (e.g., interviews scheduled per week, number of hires supported, onboarding volume, time saved, accuracy improvements)."
    )

    p2 = " ".join(actions)

    # Keep it to 1–2 paragraphs
    return p1 + "\n\n" + p2
