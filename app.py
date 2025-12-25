import streamlit as st

from src.pdf_extract import extract_text_from_pdf
from src.jd_parse import parse_job_description
from src.skills import extract_skills
from src.scoring import must_have_coverage, skills_coverage, final_score
from src.summary import build_fix_summary
from src.report_pdf import build_pdf_report
from src.parseability import check_parseability
from src.knockouts import evaluate_knockouts
from src.decision import recruiter_decision


# ==================================================
# PSEUDOCODE (High-level flow)
# ==================================================
# 1) User inputs: paste job description + upload resume PDF
# 2) On Analyze:
#    - Extract resume text from PDF
#    - Check parseability (can ATS read it?)
#    - Parse JD into required (must-have) and preferred (nice-to-have)
#    - Extract skills from JD + resume
#    - Score:
#        must-have coverage + skills coverage -> final score breakdown
#    - Build recruiter/candidate summary text
#    - Evaluate knockouts (years/degree/required tools)
#    - Compute recruiter decision (Shortlist/Review/Reject)
# 3) UI switches by Mode:
#    - Recruiter Mode: decision + knockouts + evidence
#    - Candidate Mode: prioritized gaps + where to add keywords + format checklist
# 4) Export PDF report


# --------------------------------------------------
# Page setup
# --------------------------------------------------
st.set_page_config(
    page_title="ATS Match Tracker (Local)",
    page_icon="📄",
    layout="wide"
)

st.title("ATS Match Tracker (Local)")
st.caption("Privacy-first. Runs locally. No storage.")

# --------------------------------------------------
# Mode toggle
# --------------------------------------------------
mode = st.radio(
    "Mode",
    ["Recruiter Mode", "Candidate Mode"],
    horizontal=True
)

# --------------------------------------------------
# Inputs
# --------------------------------------------------
left, right = st.columns(2, gap="large")

with left:
    st.subheader("Job Description")
    jd_text = st.text_area(
        "Paste the job description here",
        height=300,
        placeholder="Paste the full job description..."
    )

with right:
    st.subheader("Resume PDF")
    resume_file = st.file_uploader(
        "Upload a resume PDF",
        type=["pdf"]
    )

st.divider()

# --------------------------------------------------
# Buttons
# --------------------------------------------------
b1, b2 = st.columns(2, gap="large")

with b1:
    analyze = st.button("Analyze", type="primary", use_container_width=True)

with b2:
    clear = st.button("Clear", use_container_width=True)

if clear:
    st.session_state.clear()
    st.rerun()


# ==================================================
# Analyze
# ==================================================
if analyze:
    if not jd_text.strip():
        st.error("Please paste a job description.")
    elif resume_file is None:
        st.error("Please upload a resume PDF.")
    else:
        # ------------------------------------------
        # PSEUDOCODE (Data prep)
        # ------------------------------------------
        # resume_text = extract_text_from_pdf(file)
        # parse_info = check_parseability(resume_text)
        # jd_parsed = parse_job_description(jd_text)
        # jd_skills, resume_skills = extract_skills(...)
        # must_results = must_have_coverage(jd_parsed["must_have"], resume_text)
        # score_breakdown = final_score(...)
        # summary_text = build_fix_summary(...)
        # knockouts = evaluate_knockouts(...)
        # decision_info = recruiter_decision(...)

        # 1) Extract resume text
        resume_bytes = resume_file.read()
        resume_text = extract_text_from_pdf(resume_bytes)

        # 2) Parseability checks (ATS-readability)
        parse_info = check_parseability(resume_text)

        # 3) Parse JD into required/preferred (your updated jd_parse.py handles this)
        jd_parsed = parse_job_description(jd_text)

        # 4) Skills extraction
        jd_skills = extract_skills(jd_text)
        resume_skills = extract_skills(resume_text)

        matched_skills = sorted(list(jd_skills.intersection(resume_skills)))
        missing_skills = sorted(list(jd_skills.difference(resume_skills)))

        # 5) Scoring + evidence mapping
        must_ratio, must_results = must_have_coverage(
            jd_parsed["must_have"],
            resume_text
        )
        skills_ratio = skills_coverage(jd_skills, resume_skills)
        score_breakdown = final_score(must_ratio, skills_ratio)

        # 6) Summary text (rule-based)
        summary_text = build_fix_summary(
            score=score_breakdown["score"],
            must_results=must_results,
            missing_skills=missing_skills,
            matched_skills=matched_skills
        )

        # 7) Knockouts (years/degree/required tools)
        knockouts = evaluate_knockouts(jd_text, resume_text)

        # 8) Recruiter decision badge
        decision_info = recruiter_decision(
            parse_info,
            must_results,
            score_breakdown,
            knockouts
        )

        st.success("Resume text extracted and job description analyzed.")

        # ------------------------------------------
        # Metrics row (shared)
        # ------------------------------------------
        m1, m2, m3, m4 = st.columns(4, gap="large")

        with m1:
            st.metric("Match Score", f"{score_breakdown['score']}%")
        with m2:
            st.metric("Must-Haves Met", f"{score_breakdown['must_have_pct']}%")
        with m3:
            st.metric("Skills / Tools Match", f"{score_breakdown['skills_pct']}%")
        with m4:
            st.metric("Parseability", parse_info["status"])

        # ------------------------------------------
        # Parseability details (shared)
        # ------------------------------------------
        with st.expander("Parseability details"):
            checks = [
                ("Email detected", parse_info["has_email"]),
                ("Phone detected", parse_info["has_phone"]),
                ("Standard headings detected", parse_info["has_headings"]),
                ("Dates detected", parse_info["has_dates"]),
                ("Text length OK", parse_info["text_length"] >= 200),
            ]
            for label, ok in checks:
                st.write(("✅ " if ok else "⚠️ ") + label)

            if parse_info["found_headings"]:
                st.caption("Headings found: " + ", ".join(parse_info["found_headings"]))
            st.caption(f"Extracted text length: {parse_info['text_length']} characters")

        # ==================================================
        # Mode: Recruiter
        # ==================================================
        if mode == "Recruiter Mode":
            st.divider()
            st.subheader("Recruiter Decision")

            decision = decision_info["decision"]
            reasons = decision_info["reasons"]

            if decision == "Shortlist":
                st.success("Shortlist")
            elif decision == "Reject":
                st.error("Reject")
            else:
                st.warning("Review")

            if reasons:
                st.caption("Reasons:")
                for r in reasons:
                    st.write(f"- {r}")

            # ------------------------------------------
            # Knockout flags
            # ------------------------------------------
            st.divider()
            st.subheader("Knockout Flags")

            k1, k2, k3 = st.columns(3, gap="large")

            with k1:
                if knockouts["years_required"] > 0:
                    st.metric("Years Required", str(knockouts["years_required"]))
                    st.write(f"Status: **{knockouts['years_flag']}**")
                else:
                    st.metric("Years Required", "N/A")
                    st.write("Status: **N/A**")

            with k2:
                st.metric("Degree Required", "Yes" if knockouts["degree_required"] else "No")
                st.write(f"Status: **{knockouts['degree_flag']}**")

            with k3:
                if knockouts["required_tools"]:
                    st.metric("Required Tools", str(len(knockouts["required_tools"])))
                    for item in knockouts["tools_flags"]:
                        st.write(f"- {item['tool']}: **{item['status']}**")
                else:
                    st.metric("Required Tools", "0")
                    st.write("Status: **N/A**")

            # ------------------------------------------
            # Recruiter summary (neutral)
            # ------------------------------------------
            st.divider()
            st.subheader("Recruiter Summary (What to Fix)")
            st.write(summary_text)

            # ------------------------------------------
            # Must-have evidence (recruiter view)
            # ------------------------------------------
            st.divider()
            st.subheader("Must-Have Evidence (Recruiter View)")

            if must_results:
                for item in must_results:
                    status = "✅ Met" if item.get("met") else "❌ Not Met"
                    with st.expander(f"{status}: {item.get('requirement', '')}"):
                        if item.get("met") and item.get("evidence"):
                            st.write("**Evidence from resume:**")
                            st.write(item["evidence"])
                        else:
                            st.write("No clear evidence found.")
            else:
                st.info("No must-have requirements to score.")

        # ==================================================
        # Mode: Candidate
        # ==================================================
        if mode == "Candidate Mode":
            st.divider()
            st.subheader("Top Gaps (Priority)")

            missing_must = [r["requirement"] for r in must_results if not r.get("met")]
            if missing_must:
                st.write("**Missing required qualifications (top 3):**")
                for req in missing_must[:3]:
                    st.write(f"- {req}")
            else:
                st.write("**Missing required qualifications:** None detected.")

            if missing_skills:
                st.write("**Missing skills/tools (top 8):**")
                for sk in missing_skills[:8]:
                    st.write(f"- {sk}")
            else:
                st.write("**Missing skills/tools:** None detected.")

            st.divider()
            st.subheader("Where to Add Keywords")

            st.write("- Add tools and platforms in your **Skills** section (HRIS, ATS, Excel, scheduling tools).")
            st.write("- Add required qualifications in your **most recent role bullets** using proof and metrics.")
            st.write("- Mirror key wording from the JD only when it matches your real experience.")

            st.divider()
            st.subheader("Formatting Checklist (ATS Friendly)")

            format_checks = [
                ("Use a single-column layout", True),
                ("Avoid tables and text boxes", True),
                ("Use standard headings (Experience, Education, Skills)", parse_info["has_headings"]),
                ("Include email and phone as text (not icons)", parse_info["has_email"] and parse_info["has_phone"]),
                ("Keep dates consistent (MM/YYYY format)", parse_info["has_dates"]),
            ]
            for label, ok in format_checks:
                st.write(("✅ " if ok else "⚠️ ") + label)

            st.divider()
            st.subheader("Candidate Summary (How to Improve)")
            st.write(summary_text)

        # ------------------------------------------
        # JD sections (shared)
        # ------------------------------------------
        st.divider()
        c1, c2 = st.columns(2, gap="large")

        with c1:
            st.subheader("Required / Minimum Qualifications (Must-Have)")
            if jd_parsed["must_have"]:
                st.write(jd_parsed["must_have"])
            else:
                st.info("No required qualifications detected.")

        with c2:
            st.subheader("Preferred / Bonus Qualifications (Nice-to-Have)")
            if jd_parsed["nice_to_have"]:
                st.write(jd_parsed["nice_to_have"])
            else:
                st.info("No preferred qualifications detected.")

        # ------------------------------------------
        # Skills matched/missing (shared)
        # ------------------------------------------
        st.divider()
        s1, s2 = st.columns(2, gap="large")

        with s1:
            st.subheader("Matched Skills / Tools")
            if matched_skills:
                st.write(matched_skills)
            else:
                st.warning("No matched skills found.")

        with s2:
            st.subheader("Missing Skills / Tools (from JD)")
            if missing_skills:
                st.write(missing_skills)
            else:
                st.success("No missing skills detected.")

        # ------------------------------------------
        # PDF report (shared)
        # ------------------------------------------
        role_title = jd_text.strip().split("\n")[0].strip() if jd_text.strip() else ""

        pdf_bytes = build_pdf_report(
            role_title=role_title,
            score_breakdown=score_breakdown,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            must_results=must_results,
            summary_text=summary_text
        )

        st.download_button(
            label="Download PDF Report",
            data=pdf_bytes,
            file_name="ats_match_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )
