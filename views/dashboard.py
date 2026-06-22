import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def render_dashboard():
    st.title("📊 Your Analytics Dashboard")
    st.markdown("---")

    history = st.session_state.get("resume_history", [])
    latest = st.session_state.get("latest_analysis", None)

    if not history:
        st.warning("⚠️ No resume analyzed yet!")
        st.info("👉 Go to **Resume Analyzer** → Upload resume → Come back here!")
        return

    latest_score = history[-1]["ats_score"]
    top_role = latest["role"] if latest else "N/A"
    experience_level = latest.get("experience_level", "Fresher") if latest else "Fresher"

    # ============================================================
    # --- TOP METRICS ---
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
    # --- ROW 1: Resume Strength Gauge + Skill Distribution Donut ---
    # ============================================================
    col_chart1, col_chart2 = st.columns(2)

    # ✅ Resume Strength Gauge (ATS History hataya)
    with col_chart1:
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
            mode="gauge+number+delta",
            value=latest_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"ATS Match — {label}", 'font': {'color': '#8b93ac', 'size': 16}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': '#8b93ac'},
                'bar': {'color': color},
                'bgcolor': 'rgba(0,0,0,0)',
                'steps': [
                    {'range': [0, 40], 'color': 'rgba(248,113,113,0.2)'},
                    {'range': [40, 70], 'color': 'rgba(250,204,21,0.2)'},
                    {'range': [70, 100], 'color': 'rgba(74,222,128,0.2)'}
                ],
                'threshold': {
                    'line': {'color': color, 'width': 4},
                    'thickness': 0.75,
                    'value': latest_score
                }
            },
            number={'suffix': "%", 'font': {'color': color, 'size': 40}}
        ))
        fig_gauge.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': '#8b93ac'},
            height=300,
            margin=dict(t=50, b=10, l=30, r=30)
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    # ✅ Skill Distribution — Donut Chart
    with col_chart2:
        st.subheader("🍩 Skill Distribution")

        if latest and latest["skills"]:
            skill_list = [s.lower() for s in latest["skills"]]

            categories = {
                "Programming": ['python', 'java', 'c++', 'c#', 'javascript', 'typescript', 'r', 'kotlin', 'swift', 'dart'],
                "Web/Framework": ['html', 'css', 'react', 'angular', 'node.js', 'django', 'flask', 'fastapi', 'bootstrap'],
                "AI/ML": ['machine learning', 'deep learning', 'nlp', 'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'tableau'],
                "Cloud/DevOps": ['aws', 'gcp', 'azure', 'docker', 'kubernetes', 'linux', 'cloud', 'git', 'jenkins'],
                "Database": ['sql', 'mysql', 'mongodb', 'postgresql', 'redis', 'sqlite', 'firebase'],
                "Soft Skills": ['communication', 'leadership', 'agile', 'project management', 'teamwork', 'scrum'],
            }

            cat_counts = {}
            for cat, keywords in categories.items():
                count = sum(1 for s in skill_list if any(k in s for k in keywords))
                if count > 0:
                    cat_counts[cat] = count

            if cat_counts:
                fig_donut = go.Figure(go.Pie(
                    labels=list(cat_counts.keys()),
                    values=list(cat_counts.values()),
                    hole=0.5,
                    textinfo='label+percent',
                    textfont=dict(color='white', size=12),
                    marker=dict(colors=['#3b82f6', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444'])
                ))
                fig_donut.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#8b93ac'),
                    height=300,
                    showlegend=True,
                    legend=dict(font=dict(color='#8b93ac')),
                    margin=dict(t=20, b=20, l=20, r=20)
                )
                st.plotly_chart(fig_donut, use_container_width=True)

    st.markdown("---")

    # ============================================================
    # --- ROW 2: Resume Score Breakdown + Career Match Cards ---
    # ============================================================
    col_left, col_right = st.columns(2)

    # ✅ Resume Score Breakdown
    with col_left:
        st.subheader("📋 Resume Score Breakdown")

        if latest and latest["skills"]:
            skill_list = [s.lower() for s in latest["skills"]]
            total_skills = len(skill_list)
            missing_count = len(latest.get("missing", []))

            # Score components calculate karo
            skill_score = min(round((total_skills / (total_skills + missing_count + 1)) * 100), 100) if total_skills else 0
            keyword_score = min(latest_score, 100)
            exp_score = {"Fresher": 60, "Mid-Level (1-3 years)": 75, "Senior (3+ years)": 90}.get(experience_level, 60)
            education_score = 70  # Static for now

            breakdown = {
                "🔑 Skills Match": skill_score,
                "🎯 ATS Keywords": keyword_score,
                "💼 Experience Level": exp_score,
                "🎓 Education": education_score,
            }

            for label, score in breakdown.items():
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    color = "#4ade80" if score >= 70 else "#facc15" if score >= 40 else "#f87171"
                    st.markdown(f"**{label}**")
                    st.progress(score / 100)
                with col_b:
                    st.markdown(f"<h4 style='color:{color}; margin-top:20px;'>{score}%</h4>", unsafe_allow_html=True)

    # ✅ Career Match Cards
    with col_right:
        st.subheader("💼 Top Career Matches")

        if latest and latest["skills"]:
            skill_list = [s.lower() for s in latest["skills"]]

            # Role match logic
            from utils.scorer import ROLE_SKILLS
            role_matches = []
            for role, required in ROLE_SKILLS.items():
                matched = sum(1 for s in required if s.lower() in skill_list)
                match_pct = round((matched / len(required)) * 100)
                if match_pct > 0:
                    role_matches.append((role.title(), match_pct))

            # Top 3 roles
            top_roles = sorted(role_matches, key=lambda x: x[1], reverse=True)[:3]

            for role, pct in top_roles:
                if pct >= 70:
                    color = "#4ade80"
                    badge = "🔥 Strong Match"
                elif pct >= 40:
                    color = "#facc15"
                    badge = "⚡ Good Match"
                else:
                    color = "#f87171"
                    badge = "📌 Partial Match"

                st.markdown(
                    f"""<div style='border:1px solid {color}; border-radius:10px; padding:12px; margin-bottom:10px;'>
                    <span style='color:{color}; font-size:18px; font-weight:bold;'>{role}</span>
                    <span style='float:right; color:{color};'>{pct}% {badge}</span>
                    </div>""",
                    unsafe_allow_html=True
                )

    st.markdown("---")

    # ============================================================
    # --- ROW 3: Skills Found + Missing Skills ---
    # ============================================================
    col_s1, col_s2 = st.columns(2)

    with col_s1:
        st.subheader("✅ Skills Found in Resume")
        if latest and latest["skills"]:
            cols = st.columns(3)
            for i, skill in enumerate(sorted(latest["skills"])):
                with cols[i % 3]:
                    st.success(f"✓ {skill}")

    with col_s2:
        st.subheader("⚠️ Missing Skills to Learn")
        if latest and latest.get("missing"):
            for skill in latest["missing"]:
                st.error(f"❌ {skill}")
        else:
            st.success("🎉 No major skill gaps found!")

    st.markdown("---")

    # ============================================================
    # --- ROW 4: Quick Action Items ---
    # ============================================================
    st.subheader("⚡ Quick Action Items")
    st.write("These are your most impactful next steps:")

    if latest:
        missing = latest.get("missing", [])
        actions = []

        # Missing skills se actions banao
        for skill in missing[:3]:
            actions.append(f"📚 Learn **{skill}** — add it to your resume Skills section")

        # Role-specific action
        actions.append(f"🎯 Build a project specifically for **{top_role}** role")
        actions.append(f"📝 Rewrite your Resume Summary targeting **{top_role}** position")

        col1, col2 = st.columns(2)
        for i, action in enumerate(actions):
            with col1 if i % 2 == 0 else col2:
                st.info(action)