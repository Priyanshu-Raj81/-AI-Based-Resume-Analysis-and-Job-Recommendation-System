import streamlit as st

from utils.recommender import load_job_data, recommend_jobs
from utils.theme import (
    render_empty_state, render_hero, render_job_card, render_job_chip,
    section_heading, spacer,
)

POPULAR_SKILLS = ["Python", "Machine Learning", "SQL", "Power BI", "Deep Learning"]


def _score_style(score: int):
    if score >= 70:
        return "#4ade80", "Strong Match"
    if score >= 40:
        return "#facc15", "Good Match"
    return "#f87171", "Partial Match"


def _split_skills(raw_skills):
    return [
        s.strip()
        for s in str(raw_skills).replace("|", ",").split(",")
        if s.strip()
    ]


def _missing_required_skills(required_skills, user_skills, limit=5):
    user_skill_text = " ".join(user_skills).lower()
    return [s for s in required_skills if s.lower() not in user_skill_text][:limit]


def _growth_outlook(score):
    if score >= 70:
        return "Strong fit based on current skill alignment."
    if score >= 40:
        return "Good growth opportunity with focused skill improvement."
    return "Early fit; broaden core skills before targeting this role."


def _build_insight(job_title, required_skills, user_skills):
    req_lower = str(required_skills).lower()
    matched = [s for s in user_skills if s and s.lower() in req_lower]
    base = (
        f"Your {', '.join(matched[:3])} skills closely align with this role."
        if matched
        else "This role broadly matches your profile based on overall skill similarity."
    )
    return f"{base} Strengthening additional in-demand skills would further improve your match for {job_title}."


def _render_recommendation_card(rank, row, user_skills, best_score):
    score = int(row["Match_Score"])
    color, badge = _score_style(score)
    is_best = score == best_score and rank == 1

    required_skills = _split_skills(row["Key Skills"])
    missing_skills  = _missing_required_skills(required_skills, user_skills)

    salary     = row.get("Job Salary", "N/A")
    salary_txt = salary if str(salary) not in ("nan", "N/A") else "Not Disclosed by Recruiter"
    location   = str(row.get("Location", "N/A"))
    job_title  = str(row["Job Title"])
    insight    = _build_insight(job_title, row["Key Skills"], user_skills)
    growth     = _growth_outlook(score)

    # Build chip strings using theme helper
    required_chips = "".join(render_job_chip(s) for s in required_skills[:8]) \
                     or render_job_chip("N/A")
    missing_chips  = "".join(render_job_chip(s, "warning") for s in missing_skills) \
                     or render_job_chip("No major gaps", "success")

    # Delegate all rendering to theme.py
    render_job_card(
        rank=rank,
        job_title=job_title,
        location=location,
        salary_txt=salary_txt,
        growth=growth,
        score=score,
        color=color,
        badge=badge,
        is_best=is_best,
        required_chips=required_chips,
        missing_chips=missing_chips,
        insight=insight,
    )


def render_career():
    render_hero(
        "AI Job Recommendation Engine",
        "Discover the most suitable career opportunities based on your skills, "
        "resume insights, and AI-powered matching.",
    )
    spacer()

    auto_skills = ""
    if "latest_analysis" in st.session_state:
        skills_list = st.session_state["latest_analysis"].get("skills", [])
        auto_skills = ", ".join(skills_list)
        st.markdown(
            '<div class="rm-success-card">✅ Skills auto-loaded from your resume analysis.</div>',
            unsafe_allow_html=True,
        )

    section_heading("Search Jobs", "Tune your skill list and role filter to explore suitable opportunities.")
    st.markdown('<div class="rm-section-sub">Popular skills</div>', unsafe_allow_html=True)
    st.markdown(
        "".join(render_job_chip(s) for s in POPULAR_SKILLS),
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        user_skills_input = st.text_input(
            "🔑 Your Skills (comma-separated):",
            value=auto_skills or "Python, Machine Learning, Data Analysis",
            help="These are auto-filled from your resume. You can edit them.",
        )
    with col2:
        top_n = st.selectbox("Show Top:", [3, 5, 10], index=1)

    role_filter = st.text_input(
        "🎯 Filter by Role (optional):",
        placeholder="e.g. Data Scientist, Flutter Developer, Software Engineer",
    )

    if st.button("🚀 Find Matching Jobs", type="primary"):
        if not user_skills_input.strip():
            st.warning("Please enter at least one skill!")
            return

        progress = st.progress(0, text="Analyzing Skills...")
        with st.spinner("Scanning job market..."):
            user_skills = [s.strip() for s in user_skills_input.split(",")]
            progress.progress(25, text="Matching Job Profiles...")
            df = load_job_data()

            if role_filter.strip() and not df.empty:
                filtered_df = df[
                    df["Job Title"].str.contains(role_filter.strip(), case=False, na=False)
                ]
                if filtered_df.empty:
                    st.warning(f"No jobs found for '{role_filter}'. Searching all roles instead.")
                    filtered_df = df
            else:
                filtered_df = df

            progress.progress(60, text="Calculating Compatibility...")
            recommended = recommend_jobs(user_skills, filtered_df, top_n=top_n) if not filtered_df.empty else None
            progress.progress(100, text="Generating Recommendations...")
        progress.empty()

        if filtered_df.empty:
            render_empty_state("📂", "Dataset not found", "Please ensure the CSV is in the dataset folder.")
            return
        if recommended is None or recommended.empty:
            render_empty_state("🔍", "No matching jobs found", "Try different or broader skills.")
            return

        section_heading(
            f"Top {len(recommended)} Matches Found",
            "Ranked opportunities based on your entered skills.",
        )
        best_score = int(recommended["Match_Score"].max())

        for rank, (_, row) in enumerate(recommended.iterrows(), 1):
            _render_recommendation_card(rank, row, user_skills, best_score)

        spacer(16)
        avg_match  = round(recommended["Match_Score"].mean())
        best_match = int(recommended["Match_Score"].max())

        cols = st.columns(3)
        for col, (label, value) in zip(cols, [
            ("Jobs Found",      len(recommended)),
            ("Best Match",      f"{best_match}%"),
            ("Avg Match Score", f"{avg_match}%"),
        ]):
            with col:
                st.markdown(
                    f'''<div class="rm-stat fade-up">
                        <div class="rm-stat-label">{label}</div>
                        <div class="rm-stat-value">{value}</div>
                    </div>''',
                    unsafe_allow_html=True,
                )

    if "latest_analysis" in st.session_state:
        missing = st.session_state["latest_analysis"].get("missing", [])
        if missing:
            spacer(28)
            section_heading("Skills You Should Learn for Better Matches")
            st.markdown(
                "".join(render_job_chip(f"➕ {s}", "warning") for s in missing),
                unsafe_allow_html=True,
            )