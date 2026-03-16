# ATS Match Tracker (Local)

A privacy-first, local ATS-style resume screening tool that simulates how recruiters evaluate resumes against job descriptions.

This project was built to understand how Applicant Tracking Systems (ATS) work behind the scenes and to translate recruiter screening logic into transparent, explainable decisions.

No AI models.  
No subscriptions.  
No data storage.

---

## Why I Built This

Many candidates don’t understand why their resumes get rejected by ATS systems.  
At the same time, recruiters rely on rule-based screening, not magic.

I built this project to:
- Learn how ATS-style screening actually works
- Practice HR systems thinking
- Create a transparent, ethical alternative to black-box resume screening
- Translate recruiter decision logic into clear feedback

---

## What This Tool Does

- Parses a job description into:
  - Required / Minimum Qualifications (Must-Have)
  - Preferred / Bonus Qualifications (Nice-to-Have)
- Extracts and compares skills from the job description and resume
- Checks resume parseability (ATS readability)
- Applies knockout screening rules:
  - Years of experience
  - Degree requirements
  - Required HR tools or platforms
- Produces a recruiter-style decision:
  - Shortlist
  - Review
  - Reject
- Provides candidate-facing guidance on how to improve a resume
- Generates a downloadable PDF screening report

All processing runs locally on your machine.

---

## Recruiter Mode vs Candidate Mode

### Recruiter Mode
Designed to mirror recruiter workflows:
- Screening decision (Shortlist / Review / Reject)
- Knockout flags
- Must-have evidence mapping
- Neutral, audit-friendly summaries

### Candidate Mode
Designed for resume improvement:
- Priority gaps
- Missing qualifications and skills
- Where to add keywords ethically
- ATS-friendly formatting checklist
- Actionable improvement summary

---

## How the Decision Is Made (High-Level)

1. Resume text is extracted from the PDF
2. Parseability is evaluated (can ATS read it?)
3. Required and preferred qualifications are parsed from the job description
4. Skills and tools are compared
5. Knockout rules are applied
6. A recruiter-style decision is produced with clear reasons

This mirrors real-world recruiter screening logic without proprietary algorithms.

---

## Tech Stack

- Python
- Streamlit (local UI)
- Rule-based parsing and scoring
- No external APIs
- No AI or machine learning models

---

## How to Run Locally

1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies
4. Run the app

Example:

One Liner:
cd ~/Desktop/ats-tracker-local && source .venv/bin/activate && streamlit run app.py

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
