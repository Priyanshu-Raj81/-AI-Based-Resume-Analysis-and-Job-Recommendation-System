import streamlit as st

from utils.recommender import load_job_data, recommend_jobs, get_job_missing_skills
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
    score   = int(row["Match_Score"])
    color, badge = _score_style(score)
    is_best = score == best_score and rank == 1

    # Use pre-computed dataset-based skills (accurate 2026 market data)
    required_skills = _split_skills(row["Key Skills"])
    missing_skills  = row.get("Missing_Skills") or []
    # Fallback if Missing_Skills column not present
    if not isinstance(missing_skills, list):
        missing_skills = _missing_required_skills(required_skills, user_skills)

    salary     = row.get("Job Salary", "N/A")
    salary_txt = salary if str(salary) not in ("nan", "N/A") else "Not Disclosed by Recruiter"
    location   = str(row.get("Location", "N/A"))
    job_title  = str(row["Job Title"])
    insight    = _build_insight(job_title, row["Key Skills"], user_skills)
    growth     = _growth_outlook(score)

    # Build chip strings — required from dataset, missing from dataset comparison
    required_chips = "".join(render_job_chip(s) for s in required_skills[:8]) \
                     or render_job_chip("N/A")
    missing_chips  = "".join(render_job_chip(s, "warning") for s in missing_skills) \
                     or render_job_chip("No major gaps", "success")

    apply_link  = str(row.get("Apply Link",  "") or "")
    description = str(row.get("Description", "") or "")

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
        apply_link=apply_link,
        description=description,
    )


def render_career():
    render_hero(
        "AI Job Recommendation Engine",
        "Discover the most suitable career opportunities based on your skills, "
        "resume insights, and AI-powered matching.",
    )
    spacer()

    # ── Auto-load from session ────────────────────────────────────
    auto_skills  = ""
    auto_role    = ""
    has_analysis = "latest_analysis" in st.session_state

    if has_analysis:
        analysis    = st.session_state["latest_analysis"]
        skills_list = analysis.get("skills", [])
        auto_skills = ", ".join(skills_list)
        auto_role   = analysis.get("role", "")
        st.markdown(
            '<div class="rm-success-card">Skills auto-loaded from your resume analysis.</div>',
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
            "Your Skills (comma-separated):",
            value=auto_skills or "Python, Machine Learning, Data Analysis",
            help="These are auto-filled from your resume. You can edit them.",
        )
    with col2:
        top_n = st.selectbox("Show Top:", [3, 5, 10], index=1)

    # Role field — auto-filled from resume analysis, NOT optional if analysis exists
    role_filter = st.text_input(
        "Filter by Role:" if has_analysis else "Filter by Role (optional):",
        value=auto_role,
        placeholder="e.g. Data Scientist, Flutter Developer, Software Engineer",
        help="Auto-filled from your resume analysis. You can change it." if has_analysis else "Filter jobs by a specific role.",
    )

    # Auto-trigger search if coming from resume analysis
    auto_search = has_analysis and not st.session_state.get("_career_searched")
    run_search  = st.button("Find Matching Jobs", type="primary") or auto_search

    if run_search:
        st.session_state["_career_searched"] = True

        if not user_skills_input.strip():
            st.warning("Please enter at least one skill!")
            return

        progress = st.progress(0, text="Analyzing Skills...")
        with st.spinner("Scanning job market..."):
            user_skills = [s.strip() for s in user_skills_input.split(",")]
            progress.progress(25, text="Matching Job Profiles...")
            df = load_job_data()

            # Role-based filtering — use auto_role if role_filter empty
            active_role = role_filter.strip() or auto_role.strip()
            if active_role and not df.empty:
                filtered_df = df[
                    df["Job Title"].str.contains(active_role, case=False, na=False)
                ]
                if filtered_df.empty:
                    st.info(f"No exact matches for '{active_role}'. Showing closest skill-based matches.")
                    filtered_df = df
            else:
                filtered_df = df

            progress.progress(60, text="Calculating Compatibility...")
            recommended = recommend_jobs(user_skills, filtered_df, top_n=top_n) if not filtered_df.empty else None
            progress.progress(100, text="Generating Recommendations...")
        progress.empty()

        if filtered_df.empty:
            render_empty_state("No Dataset", "Dataset not found", "Please ensure the CSV is in the dataset folder.")
            return
        if recommended is None or recommended.empty:
            render_empty_state("No Jobs", "No matching jobs found", "Try different or broader skills.")
            return

        section_heading(
            f"Top {len(recommended)} Matches Found",
            f"Ranked opportunities for {role_filter.strip() or auto_role or 'your profile'}.",
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

    if has_analysis:
        missing = st.session_state["latest_analysis"].get("missing", [])
        if missing:
            spacer(28)
            section_heading("Skills You Should Learn for Better Matches")
            st.markdown(
                "".join(render_job_chip(f"+ {s}", "warning") for s in missing),
                unsafe_allow_html=True,
            )