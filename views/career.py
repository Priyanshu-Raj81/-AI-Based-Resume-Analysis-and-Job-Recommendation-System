import streamlit as st

from utils.recommender import load_job_data, recommend_jobs
from utils.theme import render_empty_state, render_hero, section_heading, spacer


POPULAR_SKILLS = ["Python", "Machine Learning", "SQL", "Power BI", "Deep Learning"]


def _score_style(score: int):
    if score >= 70:
        return "#4ade80", "Strong Match", "rm-chip-success"
    if score >= 40:
        return "#facc15", "Good Match", "rm-chip-warning"
    return "#f87171", "Partial Match", "rm-chip-danger"


def _split_skills(raw_skills):
    return [
        skill.strip()
        for skill in str(raw_skills).replace('|', ',').split(',')
        if skill.strip()
    ]


def _missing_required_skills(required_skills, user_skills, limit=5):
    user_skill_text = " ".join(user_skills).lower()
    return [
        skill for skill in required_skills
        if skill.lower() not in user_skill_text
    ][:limit]


def _growth_outlook(score):
    if score >= 70:
        return "Strong fit based on current skill alignment."
    if score >= 40:
        return "Good growth opportunity with focused skill improvement."
    return "Early fit; broaden core skills before targeting this role."


def _build_insight(job_title, required_skills, user_skills):
    req_lower = str(required_skills).lower()
    matched = [s for s in user_skills if s and s.lower() in req_lower]
    if matched:
        base = f"Your {', '.join(matched[:3])} skills closely align with this role."
    else:
        base = "This role broadly matches your profile based on overall skill similarity."
    return f"{base} Strengthening additional in-demand skills would further improve your match for {job_title}."


def _render_chip_list(items, chip_class=""):
    if not items:
        st.markdown('<span class="rm-chip rm-chip-success">No major gaps</span>', unsafe_allow_html=True)
        return

    st.markdown(
        "".join(f'<span class="rm-chip {chip_class}">{item}</span>' for item in items),
        unsafe_allow_html=True,
    )


def _render_summary_metric(label, value):
    st.markdown(
        f"""
        <div class="rm-stat fade-up">
            <div class="rm-stat-label">{label}</div>
            <div class="rm-stat-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_recommendation_card(rank, row, user_skills, best_score):
    score = int(row['Match_Score'])
    color, badge, _ = _score_style(score)
    is_best = score == best_score and rank == 1
    required_skills = _split_skills(row['Key Skills'])
    missing_skills = _missing_required_skills(required_skills, user_skills)
    salary = row.get('Job Salary', 'N/A')
    salary_txt = salary if str(salary) != 'nan' else 'Not disclosed'
    location = row.get('Location', 'N/A')
    insight = _build_insight(row['Job Title'], row['Key Skills'], user_skills)
    best_badge = '<div class="rm-best-badge">🏆 Best Match</div>' if is_best else ''
    required_chips = "".join(
        f'<span class="rm-chip">{skill}</span>'
        for skill in required_skills[:8]
    )
    missing_chips = "".join(
        f'<span class="rm-chip rm-chip-warning">{skill}</span>'
        for skill in missing_skills
    ) or '<span class="rm-chip rm-chip-success">No major gaps</span>'

    st.markdown(
        f"""
        <div class="rm-job-card {'best' if is_best else ''}">
            <div class="rm-job-head">
                <div style="flex:1; min-width:240px;">
                    {best_badge}
                    <div class="rm-job-title"><span class="rm-job-rank">#{rank}</span>{row['Job Title']}</div>
                    <div class="rm-job-meta">📍 <b>Location:</b> {location}</div>
                    <div class="rm-job-meta">💰 <b>Salary:</b> {salary_txt}</div>
                    <div class="rm-job-meta">📈 <b>Growth Outlook:</b> {_growth_outlook(score)}</div>
                </div>
                <div class="rm-score-box">
                    <div class="rm-score-num" style="color:{color};">{score}%</div>
                    <div class="rm-score-badge" style="color:{color};">{badge}</div>
                    <div class="rm-score-track">
                        <div class="rm-score-fill" style="width:{score}%; background:{color};"></div>
                    </div>
                </div>
            </div>
            <div class="rm-job-meta" style="margin-top:14px;"><b>Required Skills:</b></div>
            <div>{required_chips}</div>
            <div class="rm-job-meta" style="margin-top:12px;"><b>Missing Skills:</b></div>
            <div>{missing_chips}</div>
            <div class="rm-info">💡 <b>AI Recommendation:</b> {insight}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_career():
    render_hero(
        "AI Job Recommendation Engine",
        "Discover the most suitable career opportunities based on your skills, resume insights, and AI-powered matching.",
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
    _render_chip_list(POPULAR_SKILLS)

    col1, col2 = st.columns([3, 1])
    with col1:
        user_skills_input = st.text_input(
            "🔑 Your Skills (comma-separated):",
            value=auto_skills if auto_skills else "Python, Machine Learning, Data Analysis",
            help="These are auto-filled from your resume. You can edit them."
        )
    with col2:
        top_n = st.selectbox("Show Top:", [3, 5, 10], index=1)

    role_filter = st.text_input(
        "🎯 Filter by Role (optional):",
        placeholder="e.g. Data Scientist, Flutter Developer, Software Engineer"
    )

    if st.button("🚀 Find Matching Jobs", type="primary"):
        if not user_skills_input.strip():
            st.warning("Please enter at least one skill!")
            return

        progress = st.progress(0, text="Analyzing Skills...")
        with st.spinner("Scanning job market..."):
            user_skills = [s.strip() for s in user_skills_input.split(',')]
            progress.progress(25, text="Matching Job Profiles...")
            df = load_job_data()

            if role_filter.strip() and not df.empty:
                filtered_df = df[df['Job Title'].str.contains(role_filter.strip(), case=False, na=False)]
                if filtered_df.empty:
                    st.warning(f"No jobs found for '{role_filter}'. Searching all roles instead.")
                    filtered_df = df
            else:
                filtered_df = df

            progress.progress(60, text="Calculating Compatibility...")

            if not filtered_df.empty:
                recommended = recommend_jobs(user_skills, filtered_df, top_n=top_n)
                progress.progress(90, text="Ranking Opportunities...")
            else:
                recommended = None
            progress.progress(100, text="Generating Recommendations...")
        progress.empty()

        if filtered_df.empty:
            render_empty_state(
                "📂",
                "Dataset not found",
                "Please ensure the CSV is in the dataset folder.",
            )
            return

        if recommended is None or recommended.empty:
            render_empty_state(
                "🔍",
                "No matching jobs found",
                "Try different or broader skills to discover more opportunities.",
            )
            return

        section_heading(f"Top {len(recommended)} Matches Found", "Ranked opportunities based on your entered skills.")
        best_score = int(recommended['Match_Score'].max())

        for rank, (_, row) in enumerate(recommended.iterrows(), 1):
            _render_recommendation_card(rank, row, user_skills, best_score)

        avg_match = round(recommended['Match_Score'].mean())
        best_match = int(recommended['Match_Score'].max())

        cols = st.columns(3)
        for col, (label, value) in zip(cols, [
            ("Jobs Found", len(recommended)),
            ("Best Match", f"{best_match}%"),
            ("Avg Match Score", f"{avg_match}%"),
        ]):
            with col:
                _render_summary_metric(label, value)

    if "latest_analysis" in st.session_state:
        missing = st.session_state["latest_analysis"].get("missing", [])
        if missing:
            spacer(28)
            section_heading("Skills You Should Learn for Better Matches")
            _render_chip_list([f"➕ {skill}" for skill in missing], "rm-chip-warning")
