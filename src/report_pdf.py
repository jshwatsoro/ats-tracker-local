from io import BytesIO
from datetime import datetime
from typing import List, Dict

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


FONT_BODY = ("Helvetica", 10)
FONT_H1 = ("Helvetica-Bold", 16)
FONT_H2 = ("Helvetica-Bold", 12)
FONT_LABEL = ("Helvetica-Bold", 10)
FONT_NOTE = ("Helvetica-Oblique", 9)

LINE_H = 13
PARA_GAP = 8
SECTION_GAP = 14


def _new_page(c, width, height, margin) -> float:
    c.showPage()
    # Reset font after page break (ReportLab resets state)
    c.setFont(*FONT_BODY)
    return height - margin


def _ensure_space(c, y, needed, width, height, margin) -> float:
    if y - needed < margin:
        return _new_page(c, width, height, margin)
    return y


def _wrap_lines(c, text: str, max_width: float) -> List[str]:
    words = text.split()
    lines = []
    line = ""

    for w in words:
        test = (line + " " + w).strip()
        if c.stringWidth(test, FONT_BODY[0], FONT_BODY[1]) <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = w

    if line:
        lines.append(line)

    return lines


def _draw_paragraph(c, text: str, x: float, y: float, max_width: float, width, height, margin) -> float:
    lines = _wrap_lines(c, text, max_width)
    needed = (len(lines) * LINE_H) + PARA_GAP
    y = _ensure_space(c, y, needed, width, height, margin)

    for ln in lines:
        c.drawString(x, y, ln)
        y -= LINE_H

    y -= PARA_GAP
    return y


def _draw_section_title(c, title: str, x: float, y: float, width, height, margin) -> float:
    y = _ensure_space(c, y, 30, width, height, margin)
    c.setFont(*FONT_H2)
    c.drawString(x, y, title)
    y -= 16
    c.setFont(*FONT_BODY)
    return y


def build_pdf_report(
    role_title: str,
    score_breakdown: Dict,
    matched_skills: List[str],
    missing_skills: List[str],
    must_results: List[Dict],
    summary_text: str
) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    margin = 0.75 * inch
    x = margin
    y = height - margin
    max_width = width - 2 * margin

    # Header
    c.setFont(*FONT_H1)
    c.drawString(x, y, "ATS Match Tracker Report (Local)")
    y -= 22

    c.setFont(*FONT_BODY)
    c.drawString(x, y, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    y -= 14
    c.drawString(x, y, f"Role: {role_title or 'N/A'}")
    y -= SECTION_GAP

    # Score Breakdown
    y = _draw_section_title(c, "Score Breakdown", x, y, width, height, margin)

    score = score_breakdown.get("score", 0)
    must_pct = score_breakdown.get("must_have_pct", 0)
    skills_pct = score_breakdown.get("skills_pct", 0)

    c.setFont(*FONT_LABEL)
    c.drawString(x, y, "Match Score:")
    c.setFont(*FONT_BODY)
    c.drawString(x + 95, y, f"{score}%")
    y -= 14

    c.setFont(*FONT_LABEL)
    c.drawString(x, y, "Must-Haves Met:")
    c.setFont(*FONT_BODY)
    c.drawString(x + 95, y, f"{must_pct}%")
    y -= 14

    c.setFont(*FONT_LABEL)
    c.drawString(x, y, "Skills/Tools Match:")
    c.setFont(*FONT_BODY)
    c.drawString(x + 110, y, f"{skills_pct}%")
    y -= SECTION_GAP

    # Summary
    y = _draw_section_title(c, "Recruiter Summary (What to Fix)", x, y, width, height, margin)
    for para in summary_text.split("\n\n"):
        y = _draw_paragraph(c, para, x, y, max_width, width, height, margin)

    y -= SECTION_GAP - PARA_GAP

    # Skills / Tools
    y = _draw_section_title(c, "Skills/Tools", x, y, width, height, margin)

    c.setFont(*FONT_LABEL)
    c.drawString(x, y, "Matched:")
    y -= 14
    c.setFont(*FONT_BODY)
    y = _draw_paragraph(c, ", ".join(matched_skills) if matched_skills else "None", x, y, max_width, width, height, margin)

    c.setFont(*FONT_LABEL)
    c.drawString(x, y, "Missing (from JD):")
    y -= 14
    c.setFont(*FONT_BODY)
    y = _draw_paragraph(c, ", ".join(missing_skills) if missing_skills else "None", x, y, max_width, width, height, margin)

    # Must-Have Evidence
    y = _draw_section_title(c, "Must-Have Evidence", x, y, width, height, margin)

    for item in must_results:
        req = item.get("requirement", "").strip()
        met = bool(item.get("met", False))
        evidence = item.get("evidence", "").strip()

        status = "MET" if met else "NOT MET"
        title = f"{status}: {req}"

        # Ensure enough space for title + at least 2 lines
        y = _ensure_space(c, y, 50, width, height, margin)

        c.setFont(*FONT_LABEL)
        y = _draw_paragraph(c, title, x, y, max_width, width, height, margin)

        c.setFont(*FONT_BODY)
        if met and evidence:
            y = _draw_paragraph(c, f"Evidence: {evidence}", x, y, max_width, width, height, margin)
        else:
            y = _draw_paragraph(c, "Evidence: None found in resume text.", x, y, max_width, width, height, margin)

        y -= 4  # small gap between items

    # Disclaimer at bottom of last page
    y = _ensure_space(c, y, 30, width, height, margin)
    c.setFont(*FONT_NOTE)
    c.drawString(x, margin, "Disclaimer: This is a heuristic alignment score, not an official ATS ranking.")
    c.save()

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
