import streamlit as st

from utils.job_api import is_configured, search_live_jobs
from utils.nlp_extractor import extract_skills
from utils.recommender import load_job_data, recommend_jobs, get_job_missing_skills
from utils.theme import (
    render_empty_state, render_hero, render_job_card, render_job_chip,
    section_heading, spacer,
)

POPULAR_SKILLS = ["Python", "Machine Learning", "SQL", "Power BI", "Deep Learning"]


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
        is_best=is_best,
        required_chips=required_chips,
        missing_chips=missing_chips,
        insight=insight,
        apply_link=apply_link,
        description=description,
    )


def _score_live_job(job_skills, user_skills, min_skills=3):
    """
    Overlap-based match: % of the job's real extracted skills the candidate has.

    Returns None when fewer than `min_skills` were extracted from the
    description — Adzuna descriptions are often short/truncated snippets,
    so with only 1-2 detected skills a single match/mismatch swings the
    score between 0% and 100%, which is misleading rather than informative.
    """
    if len(job_skills) < min_skills:
        return None
    user_lower = {s.lower() for s in user_skills}
    matched = [s for s in job_skills if s.lower() in user_lower]
    return round(len(matched) / len(job_skills) * 100)


def _render_live_job_card(rank, job, user_skills, best_score):
    # Real skills extracted from the REAL job description via spaCy PhraseMatcher —
    # not a guessed/curated mapping, since this is an actual live posting.
    job_skills = extract_skills(job["description"])
    score = _score_live_job(job_skills, user_skills)
    is_best = score is not None and score == best_score and rank == 1

    user_lower = {s.lower() for s in user_skills}
    missing_skills = [s for s in job_skills if s.lower() not in user_lower][:5]

    if job["salary_min"] and job["salary_max"]:
        salary_txt = f"₹{int(job['salary_min']):,} - ₹{int(job['salary_max']):,} /yr"
    else:
        salary_txt = "Not Disclosed by Recruiter"

    required_chips = "".join(render_job_chip(s) for s in job_skills[:8]) or render_job_chip("N/A")
    missing_chips = "".join(render_job_chip(s, "warning") for s in missing_skills) \
        or render_job_chip("No major gaps", "success")

    if score is None:
        insight = (
            f"Live listing from {job['company']}. The job description was too short to "
            f"reliably extract required skills — check the full posting before applying."
        )
        growth = "Check full posting for details."
    else:
        insight = (
            f"Live listing from {job['company']}. Skills below were extracted directly "
            f"from the actual job description."
        )
        growth = _growth_outlook(score)

    render_job_card(
        rank=rank,
        job_title=f"{job['title']} — {job['company']}",
        location=job["location"],
        salary_txt=salary_txt,
        growth=growth,
        is_best=is_best,
        required_chips=required_chips,
        missing_chips=missing_chips,
        insight=insight,
        apply_link=job["apply_link"],
        description=job["description"][:400],
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

    location_input = st.text_input("Location", value="India")

    if not is_configured():
        st.info(
            "💡 Add `ADZUNA_APP_ID` and `ADZUNA_APP_KEY` to your `.env` file to search "
            "live, real job listings. Showing the local sample dataset for now."
        )

    # Auto-trigger search if coming from resume analysis
    auto_search = has_analysis and not st.session_state.get("_career_searched")
    run_search  = st.button("Find Matching Jobs", type="primary") or auto_search

    if run_search:
        st.session_state["_career_searched"] = True

        if not user_skills_input.strip():
            st.warning("Please enter at least one skill!")
            return

        user_skills = [s.strip() for s in user_skills_input.split(",")]
        active_role = role_filter.strip() or auto_role.strip()

        # ── LIVE MODE (automatic, default): real Adzuna listings, real skills
        #    extracted from real text. Falls back to the local dataset only
        #    if Adzuna isn't configured or the request fails. ──────────────
        if is_configured():
            with st.spinner("Fetching live job listings..."):
                result = search_live_jobs(
                    role=active_role or "Software Engineer",
                    location=location_input,
                )

            if result["ok"] and result["jobs"]:
                live_jobs = result["jobs"][:top_n]
                scored_pairs = [
                    (job, _score_live_job(extract_skills(job["description"]), user_skills))
                    for job in live_jobs
                ]
                # None (insufficient data) sorts last, not first
                scored_pairs.sort(key=lambda p: p[1] if p[1] is not None else -1, reverse=True)
                valid_scores = [s for _, s in scored_pairs if s is not None]
                best_score = max(valid_scores) if valid_scores else None

                section_heading(
                    f"Top {len(scored_pairs)} Live Matches Found",
                    f"Real, currently-open listings for {active_role or 'your profile'} — via Adzuna.",
                )
                for rank, (job, _) in enumerate(scored_pairs, 1):
                    _render_live_job_card(rank, job, user_skills, best_score)
                return

            # Live search attempted but failed/empty — fall through to local dataset
            st.info(f"Live search unavailable ({result.get('error') or 'no results'}). Showing local dataset instead.")


        with st.spinner("Scanning job market..."):
            df = load_job_data()

            # Role-based filtering — use auto_role if role_filter empty
            if active_role and not df.empty:
                filtered_df = df[
                    df["Job Title"].str.contains(active_role, case=False, na=False)
                ]
                if filtered_df.empty:
                    st.info(f"No exact matches for '{active_role}'. Showing closest skill-based matches.")
                    filtered_df = df
            else:
                filtered_df = df

            recommended = recommend_jobs(user_skills, filtered_df, top_n=top_n) if not filtered_df.empty else None

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
        st.markdown(
            f'''<div class="rm-stat fade-up" style="max-width:220px;">
                <div class="rm-stat-label">Jobs Found</div>
                <div class="rm-stat-value">{len(recommended)}</div>
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