import streamlit as st

from utils.ai_suggestions import generate_resume_suggestions
from utils.nlp_extractor import extract_projects, extract_skills
from utils.pdf_parser import parse_resume
from utils.recommender import get_role_ats_score, load_job_data
from utils.scorer import calculate_similarity_score
from utils.theme import render_hero, section_heading, spacer


TARGET_ROLES = [
    "Software Developer", "Backend Developer", "Frontend Developer",
    "Full Stack Developer", "Flutter Developer", "Android Developer", "iOS Developer",
    "Mobile App Developer",
    "Data Scientist", "Data Analyst", "Data Engineer", "ML Engineer",
    "AI Engineer", "Business Analyst", "NLP Engineer", "Prompt Engineer",
    "DevOps Engineer", "Cloud Engineer", "Site Reliability Engineer",
    "Information Security Analyst", "Cybersecurity Engineer", "Ethical Hacker",
    "Product Manager", "Project Manager",
    "UI UX Designer", "Graphic Designer",
    "Blockchain Developer", "Game Developer", "AR VR Developer",
]


def _render_score(score):
    st.markdown(
        f"""
        <div class="rm-stat fade-up">
            <div class="rm-stat-label">ATS Match Score</div>
            <div class="rm-stat-value">{score}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(score / 100)


def _render_chips(items, chip_class="", empty_text="No items found."):
    if not items:
        st.markdown(f'<div class="rm-info">{empty_text}</div>', unsafe_allow_html=True)
        return

    st.markdown(
        "".join(f'<span class="rm-chip {chip_class}">{item}</span>' for item in items),
        unsafe_allow_html=True,
    )


def _render_project_status(projects):
    if projects:
        st.markdown(
            """
            <div class="rm-success-card">
                ✅ Projects Analyzed<br>
                <span style="color:var(--rm-text-2); font-weight:500;">
                    Your projects have been analyzed successfully. Visit
                    <b>Interview Prep → Mock Interview Coach</b>
                    to get personalized questions based on your projects.
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        """
        <div class="rm-warning-card">
            💡 No Projects Found<br>
            <span style="color:var(--rm-text-2); font-weight:500;">
                No projects section detected in your resume. Add a
                <b>Projects</b> section to get project-based interview questions in the AI Coach.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_analysis_summary(role, experience_level):
    st.markdown(
        f"""
        <div class="rm-info">
            <b>📋 Showing last analysis</b><br>
            <span style="color:var(--rm-text); font-weight:600;">{role}</span>
            <span style="color:var(--rm-text-2);"> · Level: {experience_level}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_suggestions(target_role, extracted_skills, missing_skills,
                        job_desc="", experience_level="Fresher",
                        download_name="resume_suggestions.txt"):
    section_heading("AI-Powered Resume Suggestions", "Personalized recommendations for your target role.")
    with st.spinner("AI analyzing your resume..."):
        suggestions = generate_resume_suggestions(
            target_role=target_role,
            extracted_skills=extracted_skills,
            missing_skills=missing_skills,
            job_desc=job_desc,
            experience_level=experience_level
        )
    st.markdown(suggestions)
    st.download_button(
        label="📥 Download AI Suggestions",
        data=suggestions,
        file_name=download_name,
        mime="text/plain"
    )


def _render_score_tab(score, skills, projects):
    _render_score(score)
    spacer(14)
    section_heading("Found Skills", "Skills detected from your resume.")
    _render_chips(skills, empty_text="No skills detected.")
    spacer(14)
    _render_project_status(projects)


def _render_missing_tab(missing_skills):
    section_heading("Missing Skills", "Skill gaps to improve your ATS match.")
    if missing_skills:
        _render_chips([f"❌ {skill}" for skill in missing_skills], "rm-chip-danger")
    else:
        st.markdown(
            '<div class="rm-success-card">🎉 No major skill gaps found.</div>',
            unsafe_allow_html=True,
        )


def render_analyzer():
    render_hero(
        "AI Resume Analyzer",
        "Upload your resume, analyze ATS compatibility, discover skill gaps, and receive AI-powered career recommendations.",
    )
    spacer()

    section_heading("Upload Resume", "Supported formats: PDF and DOCX. Maximum size: 200 MB.")
    uploaded_file = st.file_uploader("1. Upload your PDF or DOCX resume", type=["pdf", "docx"])

    spacer()
    section_heading("Choose Analysis Mode", "Compare your resume against a role or a custom job description.")
    mode = st.radio("Mode:", ["Target Job Role", "Paste Job Description (JD)"], horizontal=True, label_visibility="collapsed")

    target_role = ""
    job_desc = ""

    if mode == "Target Job Role":
        target_role = st.selectbox("Target Job Role:", TARGET_ROLES)
    else:
        job_desc = st.text_area("Paste JD here:", height=150)

    experience_level = st.selectbox(
        "3. Your Experience Level:",
        ["Fresher", "Mid-Level (1-3 years)", "Senior (3+ years)"],
        help="AI will tailor suggestions based on your experience level"
    )

    spacer()

    if st.button("Analyze Resume", type="primary"):
        if not uploaded_file:
            st.warning("Please upload a resume!")
            return

        progress = st.progress(0, text="Parsing Resume...")
        with st.spinner("Analyzing..."):
            resume_text = parse_resume(uploaded_file)
            progress.progress(20, text="Extracting Skills...")
            extracted_skills = extract_skills(resume_text)
            progress.progress(45, text="Analyzing Projects...")
            extracted_projects = extract_projects(resume_text)
            progress.progress(65, text="Calculating ATS Score...")
            df = load_job_data()

            if mode == "Target Job Role":
                ats_score, missing_skills = get_role_ats_score(extracted_skills, target_role, df)
            else:
                jd_skills = extract_skills(job_desc)
                ats_score, missing_skills = calculate_similarity_score(
                    extracted_skills, " ".join(jd_skills))
            progress.progress(90, text="Generating Recommendations...")
        progress.progress(100, text="Done!")
        progress.empty()

        if "resume_history" not in st.session_state:
            st.session_state.resume_history = []
        st.session_state["_analysis_rendered"] = False  # reset for next rerun

        attempt_number = len(st.session_state.resume_history) + 1
        st.session_state.resume_history.append({
            "attempt": f"Resume v{attempt_number}",
            "ats_score": ats_score,
            "role": target_role if mode == "Target Job Role" else "Custom JD",
            "skills": extracted_skills,
            "missing": missing_skills,
            "projects": extracted_projects,
        })

        st.session_state.latest_analysis = {
            "ats_score": ats_score,
            "role": target_role if mode == "Target Job Role" else "Custom JD",
            "skills": extracted_skills,
            "missing": missing_skills,
            "missing_skills": missing_skills,
            "projects": extracted_projects,
            "job_desc": job_desc,
            "mode": mode,
            "experience_level": experience_level
        }

        st.markdown('<div class="rm-success-card">✅ Analysis Complete!</div>', unsafe_allow_html=True)

        # Rerun once so sidebar immediately shows "New Analysis" button
        if not st.session_state.get("_analysis_rendered"):
            st.session_state["_analysis_rendered"] = True
            st.rerun()

        tab1, tab2, tab3 = st.tabs(["Score", "Skill Gap", "AI Suggestions"])

        with tab1:
            _render_score_tab(ats_score, extracted_skills, extracted_projects)

        with tab2:
            _render_missing_tab(missing_skills)

        with tab3:
            _render_suggestions(
                target_role=target_role if mode == "Target Job Role" else "Custom JD Role",
                extracted_skills=extracted_skills,
                missing_skills=missing_skills,
                job_desc=job_desc if mode == "Paste Job Description (JD)" else "",
                experience_level=experience_level,
                download_name=f"resume_suggestions_{target_role}_{experience_level}.txt",
            )

    elif "latest_analysis" in st.session_state:
        data = st.session_state.latest_analysis
        _render_analysis_summary(data['role'], data.get('experience_level', 'Fresher'))

        tab1, tab2, tab3 = st.tabs(["Score", "Skill Gap", "AI Suggestions"])

        with tab1:
            _render_score_tab(data['ats_score'], data['skills'], data.get("projects"))

        with tab2:
            _render_missing_tab(data['missing'])

        with tab3:
            _render_suggestions(
                target_role=data['role'],
                extracted_skills=data['skills'],
                missing_skills=data['missing'],
                job_desc=data.get('job_desc', ''),
                experience_level=data.get('experience_level', 'Fresher'),
            )