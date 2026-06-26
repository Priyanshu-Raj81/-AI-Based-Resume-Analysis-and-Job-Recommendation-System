import plotly.graph_objects as go
import streamlit as st

from utils.theme import render_empty_state, render_hero, section_heading, spacer


def _score_tone(score):
    if score >= 70:
        return "#4ade80", "Strong", "rm-chip-success"
    if score >= 40:
        return "#facc15", "Moderate", "rm-chip-warning"
    return "#f87171", "Needs Work", "rm-chip-danger"


def _render_stat_card(label, value):
    st.markdown(
        f"""
        <div class="rm-stat fade-up">
            <div class="rm-stat-label">{label}</div>
            <div class="rm-stat-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_skill_bar(label, score):
    st.markdown(
        f"""
        <div class="rm-skill-row">
            <div class="rm-skill-head">
                <span>{label}</span>
                <span class="pct">{score}%</span>
            </div>
            <div class="rm-bar-bg">
                <div class="rm-bar-fill" style="width:{score}%"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_match_card(role, pct):
    _, label, chip_class = _score_tone(pct)
    st.markdown(
        f"""
        <div class="rm-stat fade-up">
            <div class="rm-stat-value">{pct}%</div>
            <div class="rm-stat-label">{role}</div>
            <span class="rm-chip {chip_class}">{label} Match</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_skill_chips(skills, chip_class=""):
    chips = "".join(
        f'<span class="rm-chip {chip_class}">{skill}</span>'
        for skill in skills
    )
    st.markdown(chips, unsafe_allow_html=True)


def _render_missing_skill(skill, label, chip_class):
    st.markdown(
        f"""
        <div class="rm-stat-pill">
            <span>❌ {skill}</span>
            <span class="rm-chip {chip_class}">{label}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_action_card(action):
    st.markdown(
        f"""
        <div class="rm-job-card fade-up">
            <div class="rm-job-head">
                <div class="rm-job-title">{action["icon"]} {action["tag"]}</div>
                <span class="rm-chip">{action["label"]}</span>
            </div>
            <div class="rm-job-meta" style="margin-top:10px;">{action["text"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard():
    render_hero(
        "Your Analytics Dashboard",
        "Track resume strength, career fit, skill gaps, and next actions from your latest analysis.",
    )
    spacer()

    history = st.session_state.get("resume_history", [])
    latest = st.session_state.get("latest_analysis", None)

    if not history:
        render_empty_state(
            "📄",
            "No Resume Analyzed Yet",
            "Go to Resume Analyzer, upload your resume, then return here for your analytics.",
            "Analyze Resume",
            "Resume Analyzer",
        )
        return

    latest_score = history[-1]["ats_score"]
    top_role = latest["role"] if latest else "N/A"
    experience_level = latest.get("experience_level", "Fresher") if latest else "Fresher"

    section_heading("Overview", "Your latest resume analysis at a glance.")
    metric_cols = st.columns(4)
    metrics = [
        ("Resumes Analyzed", len(history)),
        ("Latest ATS Score", f"{latest_score}%"),
        ("Target Role", top_role),
        ("Experience Level", experience_level),
    ]
    for col, (label, value) in zip(metric_cols, metrics):
        with col:
            _render_stat_card(label, value)

    spacer(28)
    col_gauge, col_breakdown = st.columns(2)

    with col_gauge:
        section_heading("Resume Strength Meter", "ATS compatibility based on your latest resume.")
        color, label, chip_class = _score_tone(latest_score)

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=latest_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={
                'text': f"ATS Match - <b>{label}</b>",
                'font': {'color': '#9aa4c4', 'size': 15}
            },
            number={
                'suffix': "%",
                'font': {'color': color, 'size': 44, 'family': 'Arial Black'}
            },
            gauge={
                'axis': {
                    'range': [0, 100],
                    'tickcolor': '#475569',
                    'tickwidth': 1,
                    'tickfont': {'color': '#8b95b8', 'size': 10},
                    'nticks': 6,
                },
                'bar': {'color': color, 'thickness': 0.25},
                'bgcolor': 'rgba(0,0,0,0)',
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 40], 'color': 'rgba(248,113,113,0.15)'},
                    {'range': [40, 70], 'color': 'rgba(250,204,21,0.15)'},
                    {'range': [70, 100], 'color': 'rgba(74,222,128,0.15)'}
                ],
                'threshold': {
                    'line': {'color': color, 'width': 3},
                    'thickness': 0.85,
                    'value': latest_score
                }
            }
        ))
        fig_gauge.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': '#9aa4c4', 'family': 'Arial'},
            height=280,
            margin=dict(t=60, b=10, l=30, r=30),
            transition={'duration': 1500, 'easing': 'cubic-in-out'},
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
        _render_skill_bar(f"{latest_score}% ATS Match", latest_score)
        st.markdown(
            f'<span class="rm-chip {chip_class}">0-40 Needs Work</span>'
            '<span class="rm-chip rm-chip-warning">40-70 Moderate</span>'
            '<span class="rm-chip rm-chip-success">70+ Strong</span>',
            unsafe_allow_html=True,
        )

    with col_breakdown:
        section_heading("Resume Score Breakdown", "Signals contributing to your dashboard score.")

        if latest and latest["skills"]:
            skill_list = [s.lower() for s in latest["skills"]]
            total_skills = len(skill_list)
            missing_count = len(latest.get("missing", []))

            skill_score = min(round((total_skills / (total_skills + missing_count + 1)) * 100), 100) if total_skills else 0
            keyword_score = min(latest_score, 100)
            exp_score = {"Fresher": 60, "Mid-Level (1-3 years)": 75, "Senior (3+ years)": 90}.get(experience_level, 60)
            education_score = 70

            breakdown = {
                "🔑 Skills Match": skill_score,
                "🎯 ATS Keywords": keyword_score,
                "💼 Experience Level": exp_score,
                "🎓 Education": education_score,
            }

            for lbl, score in breakdown.items():
                _render_skill_bar(lbl, score)

    spacer(28)
    section_heading("Top Career Matches", "Roles aligned with the skills found in your resume.")

    if latest and latest["skills"]:
        skill_list = [s.lower() for s in latest["skills"]]

        from utils.scorer import ROLE_SKILLS
        role_matches = []
        for role, required in ROLE_SKILLS.items():
            matched = sum(1 for s in required if s.lower() in skill_list)
            match_pct = round((matched / len(required)) * 100)
            role_matches.append((role.title(), match_pct))

        top_roles = [
            (r, p) for r, p in
            sorted(role_matches, key=lambda x: x[1], reverse=True)
            if p >= 40
        ][:4]

        if top_roles:
            cols = st.columns(len(top_roles))
            for col, (role, pct) in zip(cols, top_roles):
                with col:
                    _render_match_card(role, pct)
        else:
            st.markdown(
                '<div class="rm-info">No strong career matches found. Try uploading an updated resume.</div>',
                unsafe_allow_html=True,
            )

    spacer(28)
    col_s1, col_s2 = st.columns(2)

    with col_s1:
        section_heading("Skills Found in Resume", "Detected capabilities from your latest upload.")
        if latest and latest["skills"]:
            _render_skill_chips(sorted(latest["skills"]), "rm-chip-success")
        else:
            st.markdown('<div class="rm-info">No skills detected yet.</div>', unsafe_allow_html=True)

    with col_s2:
        section_heading("Missing Skills to Learn", "Prioritized gaps for stronger matches.")
        if latest and latest.get("missing"):
            priority_labels = {0: "High", 1: "Medium", 2: "Low"}
            priority_classes = {0: "rm-chip-danger", 1: "rm-chip-warning", 2: "rm-chip-success"}

            for i, skill in enumerate(latest["missing"]):
                priority = min(i // 2, 2)
                _render_missing_skill(skill, priority_labels[priority], priority_classes[priority])
        else:
            st.markdown(
                '<div class="rm-success-card">🎉 No major skill gaps found.</div>',
                unsafe_allow_html=True,
            )

    spacer(28)
    section_heading("Quick Action Items", "Your most impactful next steps to get shortlisted faster.")

    if latest:
        missing = latest.get("missing", [])
        actions = []

        for skill in missing[:2]:
            actions.append({
                "icon": "📚",
                "text": f"Learn <b>{skill}</b> - add it to your resume Skills section",
                "tag": "High Priority",
                "label": "Skill Gap",
            })

        actions.append({
            "icon": "🎯",
            "text": f"Build a project specifically for <b>{top_role}</b> role",
            "tag": "Important",
            "label": "Project",
        })
        actions.append({
            "icon": "📝",
            "text": f"Rewrite your Resume Summary targeting <b>{top_role}</b> position",
            "tag": "Quick Win",
            "label": "Resume",
        })
        actions.append({
            "icon": "🤖",
            "text": "Try <b>Mock Interview Coach</b> in Interview Prep section",
            "tag": "Practice",
            "label": "Interview",
        })

        cols = st.columns(2)
        for i, action in enumerate(actions):
            with cols[i % 2]:
                _render_action_card(action)
