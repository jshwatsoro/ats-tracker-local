from typing import Dict, List, Tuple
from rapidfuzz import fuzz


def must_have_coverage(must_haves: List[str], resume_text: str) -> Tuple[float, List[Dict]]:
    """
    Returns:
    - coverage ratio (0 to 1)
    - per-item results with evidence (best matching snippet)
    """
    text = resume_text.lower()

    results = []
    hits = 0

    # Split resume into rough "snippets" (lines) for evidence search
    snippets = [s.strip() for s in resume_text.split("\n") if len(s.strip()) > 20]

    for req in must_haves:
        req_clean = req.strip()
        req_lower = req_clean.lower()

        # Quick exact containment
        met = req_lower in text

        best_snip = ""
        best_score = 0

        # Fuzzy match against resume snippets to find evidence
        for snip in snippets[:400]:  # limit for speed
            score = fuzz.partial_ratio(req_lower, snip.lower())
            if score > best_score:
                best_score = score
                best_snip = snip

        # Decide met based on fuzzy threshold if not exact
        if not met and best_score >= 80:
            met = True

        if met:
            hits += 1

        results.append({
            "requirement": req_clean,
            "met": met,
            "evidence": best_snip if met else ""
        })

    ratio = hits / len(must_haves) if must_haves else 0.0
    return ratio, results


def skills_coverage(jd_skills: set, resume_skills: set) -> float:
    if not jd_skills:
        return 0.0
    return len(jd_skills.intersection(resume_skills)) / len(jd_skills)


def final_score(must_ratio: float, skills_ratio: float) -> Dict:
    """
    Weighted score, returns breakdown + total score (0 to 100).
    """
    must_weight = 0.50
    skills_weight = 0.35
    # keyword relevance weight will be added next
    total = (must_ratio * must_weight) + (skills_ratio * skills_weight)

    # Scale to 0-100, but only based on included weights
    max_possible = must_weight + skills_weight
    scaled = (total / max_possible) * 100 if max_possible else 0.0

    return {
        "score": round(scaled, 1),
        "must_have_pct": round(must_ratio * 100, 1),
        "skills_pct": round(skills_ratio * 100, 1),
    }
