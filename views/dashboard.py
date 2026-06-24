import streamlit as st
import plotly.graph_objects as go
import pandas as pd


def render_dashboard():
    st.title("📊 Your Analytics Dashboard")
    st.markdown("---")

    history = st.session_state.get("resume_history", [])
    latest = st.session_state.get("latest_analysis", None)

    if not history:
        st.markdown("""
            <div style='background:#171a23; border:1px solid #2a2f3a; border-radius:12px;
                        padding:40px; text-align:center; margin:20px 0;'>
                <div style='font-size:48px; margin-bottom:16px;'>📄</div>
                <h3 style='color:#e6e8ee; margin:0 0 8px;'>No Resume Analyzed Yet</h3>
                <p style='color:#9aa1b1; margin:0;'>
                    Go to <b style='color:#4f46e5;'>Resume Analyzer</b> →
                    Upload your resume → Come back here!
                </p>
            </div>
        """, unsafe_allow_html=True)
        return

    latest_score = history[-1]["ats_score"]
    top_role = latest["role"] if latest else "N/A"
    experience_level = latest.get("experience_level", "Fresher") if latest else "Fresher"

    # ============================================================
    # TOP METRICS — 4 KPI Cards
    # ============================================================
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Resumes Analyzed", len(history))
    with col2:
        st.metric("Latest ATS Score", f"{latest_score}%")
    with col3:
        st.metric("Target Role", top_role)
    with col4:
        st.metric("Experience Level", experience_level)

    st.markdown("<br>", unsafe_allow_html=True)

    # ============================================================
    # ROW 1: Gauge (full width) — Skill Distribution hataya
    # ============================================================
    col_gauge, col_breakdown = st.columns(2)

    with col_gauge:
        st.subheader("🎯 Resume Strength Meter")

        if latest_score >= 70:
            color = "#4ade80"
            label = "Strong"
        elif latest_score >= 40:
            color = "#facc15"
            label = "Moderate"
        else:
            color = "#f87171"
            label = "Needs Work"

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=latest_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={
                'text': f"ATS Match — <b>{label}</b>",
                'font': {'color': '#8b93ac', 'size': 15}
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
                    'tickfont': {'color': '#475569', 'size': 10},
                    'nticks': 6,
                },
                'bar': {'color': color, 'thickness': 0.25},
                'bgcolor': 'rgba(0,0,0,0)',
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 40],   'color': 'rgba(248,113,113,0.15)'},
                    {'range': [40, 70],  'color': 'rgba(250,204,21,0.15)'},
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
            font={'color': '#8b93ac', 'family': 'Arial'},
            height=280,
            margin=dict(t=60, b=10, l=30, r=30),
            transition={'duration': 1500, 'easing': 'cubic-in-out'},
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        # ✅ Animated progress bar
        st.markdown(f"""
            <style>
            @keyframes barGrow {{
                from {{ width: 0%; }}
                to   {{ width: {latest_score}%;
                       box-shadow: 0 0 10px {color}80; }}
            }}
            .anim-bar {{ animation: barGrow 1.5s cubic-bezier(.4,0,.2,1) forwards; width:0%; }}
            </style>
            <div style='margin-top:4px;'>
                <div style='display:flex; justify-content:space-between; margin-bottom:6px;'>
                    <span style='color:#475569; font-size:11px;'>0%</span>
                    <span style='color:{color}; font-size:12px; font-weight:700;'>
                        {latest_score}% ATS Match
                    </span>
                    <span style='color:#475569; font-size:11px;'>100%</span>
                </div>
                <div style='background:#1e293b; border-radius:999px; height:8px; overflow:hidden;'>
                    <div class='anim-bar'
                         style='height:100%; background:{color}; border-radius:999px;'></div>
                </div>
                <div style='display:flex; justify-content:space-between; margin-top:10px;'>
                    <span style='font-size:11px; color:#f87171;'>● 0-40 Needs Work</span>
                    <span style='font-size:11px; color:#facc15;'>● 40-70 Moderate</span>
                    <span style='font-size:11px; color:#4ade80;'>● 70+ Strong</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # ============================================================
    # ROW 1 RIGHT: Score Breakdown
    # ============================================================
    with col_breakdown:
        st.subheader("📋 Resume Score Breakdown")

        if latest and latest["skills"]:
            skill_list = [s.lower() for s in latest["skills"]]
            total_skills = len(skill_list)
            missing_count = len(latest.get("missing", []))

            skill_score = min(round((total_skills / (total_skills + missing_count + 1)) * 100), 100) if total_skills else 0
            keyword_score = min(latest_score, 100)
            exp_score = {"Fresher": 60, "Mid-Level (1-3 years)": 75, "Senior (3+ years)": 90}.get(experience_level, 60)
            education_score = 70

            breakdown = {
                "🔑 Skills Match":    skill_score,
                "🎯 ATS Keywords":    keyword_score,
                "💼 Experience Level": exp_score,
                "🎓 Education":       education_score,
            }

            for lbl, score in breakdown.items():
                clr = "#4ade80" if score >= 70 else "#facc15" if score >= 40 else "#f87171"
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"**{lbl}**")
                    st.progress(score / 100)
                with col_b:
                    st.markdown(
                        f"<h4 style='color:{clr}; margin-top:20px;'>{score}%</h4>",
                        unsafe_allow_html=True
                    )

    st.markdown("---")

    # ============================================================
    # ROW 2: Career Matches (full width styled)
    # ============================================================
    st.subheader("💼 Top Career Matches")

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
            for idx, (role, pct) in enumerate(top_roles):
                if pct >= 70:
                    clr = "#4ade80"
                    badge = "🔥 Strong"
                    bg = "rgba(74,222,128,0.08)"
                    border = "rgba(74,222,128,0.3)"
                elif pct >= 40:
                    clr = "#facc15"
                    badge = "⚡ Good"
                    bg = "rgba(250,204,21,0.08)"
                    border = "rgba(250,204,21,0.3)"
                else:
                    clr = "#f87171"
                    badge = "📌 Partial"
                    bg = "rgba(248,113,113,0.08)"
                    border = "rgba(248,113,113,0.3)"

                with cols[idx]:
                    st.markdown(f"""
                        <div style='background:{bg}; border:1px solid {border};
                                    border-radius:12px; padding:18px 14px;
                                    text-align:center;'>
                            <div style='color:{clr}; font-size:26px;
                                        font-weight:800; margin-bottom:4px;'>
                                {pct}%
                            </div>
                            <div style='color:#e6e8ee; font-size:13px;
                                        font-weight:600; margin-bottom:6px;'>
                                {role}
                            </div>
                            <span style='color:{clr}; font-size:11px;
                                         font-weight:600;'>{badge}</span>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No strong career matches found. Try uploading an updated resume!")

    st.markdown("---")

    # ============================================================
    # ROW 3: Skills Found + Missing Skills
    # ============================================================
    col_s1, col_s2 = st.columns(2)

    with col_s1:
        st.subheader("✅ Skills Found in Resume")
        if latest and latest["skills"]:
            cols = st.columns(3)
            for i, skill in enumerate(sorted(latest["skills"])):
                with cols[i % 3]:
                    st.success(f"✓ {skill}")
        else:
            st.info("No skills detected yet.")

    with col_s2:
        st.subheader("⚠️ Missing Skills to Learn")
        if latest and latest.get("missing"):
            priority_colors = {0: "#f87171", 1: "#facc15", 2: "#4ade80"}
            priority_labels = {0: "🔴 High", 1: "🟡 Medium", 2: "🟢 Low"}

            for i, skill in enumerate(latest["missing"]):
                priority = min(i // 2, 2)
                clr = priority_colors[priority]
                lbl = priority_labels[priority]
                st.markdown(f"""
                    <div style='background:#0f172a; border:1px solid {clr}40;
                                border-left:3px solid {clr};
                                border-radius:8px; padding:10px 14px; margin:5px 0;
                                display:flex; justify-content:space-between;
                                align-items:center;'>
                        <span style='color:#e6e8ee; font-size:14px;'>❌ {skill}</span>
                        <span style='color:{clr}; font-size:11px;
                                    font-weight:700;'>{lbl}</span>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.success("🎉 No major skill gaps found!")

    st.markdown("---")

    # ============================================================
    # ROW 4: Quick Action Items
    # ============================================================
    st.subheader("⚡ Quick Action Items")
    st.caption("Your most impactful next steps to get shortlisted faster:")

    if latest:
        missing = latest.get("missing", [])
        actions = []

        for skill in missing[:2]:
            actions.append({
                "icon": "📚",
                "color": "#f87171",
                "text": f"Learn <b>{skill}</b> — add it to your resume Skills section",
                "tag": "High Priority"
            })

        actions.append({
            "icon": "🎯",
            "color": "#4f46e5",
            "text": f"Build a project specifically for <b>{top_role}</b> role",
            "tag": "Important"
        })
        actions.append({
            "icon": "📝",
            "color": "#10b981",
            "text": f"Rewrite your Resume Summary targeting <b>{top_role}</b> position",
            "tag": "Quick Win"
        })
        actions.append({
            "icon": "🤖",
            "color": "#8b5cf6",
            "text": "Try <b>Mock Interview Coach</b> in Interview Prep section",
            "tag": "Practice"
        })

        cols = st.columns(2)
        for i, action in enumerate(actions):
            with cols[i % 2]:
                st.markdown(f"""
                    <div style='background:#0f172a; border:1px solid #2a2f3a;
                                border-left:3px solid {action["color"]};
                                border-radius:10px; padding:14px 16px; margin:6px 0;'>
                        <div style='display:flex; justify-content:space-between;
                                    align-items:flex-start;'>
                            <span style='font-size:20px;'>{action["icon"]}</span>
                            <span style='color:{action["color"]}; font-size:10px;
                                        font-weight:700; background:{action["color"]}20;
                                        padding:2px 8px; border-radius:20px;'>
                                {action["tag"]}
                            </span>
                        </div>
                        <p style='color:#cbd5e1; font-size:13px;
                                  margin:8px 0 0; line-height:1.5;'>
                            {action["text"]}
                        </p>
                    </div>
                """, unsafe_allow_html=True)