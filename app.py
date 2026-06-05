import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.pdf_parser import extract_text_from_pdf
from utils.nlp_extractor import extract_skills, extract_education, extract_experience, extract_name
from utils.scorer import calculate_score, get_grade, get_missing_skills
from utils.recommender import load_jobs, add_manual_job, recommend_jobs
from utils.ai_suggestions import get_ai_suggestions, get_resume_score_feedback

# ─── PAGE CONFIG ───────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🤖",
    layout="wide"
)

# ─── CUSTOM CSS ────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background: #1e1e2e;
        border-radius: 12px;
        padding: 1.2rem;
        border: 1px solid #333;
        text-align: center;
    }
    .skill-badge {
        display: inline-block;
        background: #667eea;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        margin: 3px;
        font-size: 0.85rem;
    }
    .missing-badge {
        display: inline-block;
        background: #e74c3c;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        margin: 3px;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── HEADER ────────────────────────────────────────────
st.markdown('<p class="main-header">🤖 AI Resume Analyzer & Job Recommender</p>', unsafe_allow_html=True)
st.markdown("---")

# ─── SIDEBAR ───────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    job_role_filter = st.text_input("🎯 Target Job Role", placeholder="e.g. Data Scientist")
    top_n_jobs = st.slider("📋 Number of Job Recommendations", 3, 10, 5)
    show_ai = st.toggle("🤖 Enable AI Suggestions (OpenAI)", value=True)
    st.markdown("---")
    st.info("Upload your resume PDF and click Analyze!")

# ─── FILE UPLOAD ───────────────────────────────────────
uploaded_file = st.file_uploader("📄 Upload Your Resume (PDF)", type=["pdf"])

if uploaded_file:
    with st.spinner("🔍 Analyzing your resume..."):

        # Extract text
        resume_text = extract_text_from_pdf(uploaded_file)

        # Extract info
        name = extract_name(resume_text)
        skills = extract_skills(resume_text)
        education = extract_education(resume_text)
        experience = extract_experience(resume_text)

        # Load jobs & recommend
        jobs_df = load_jobs()
        recommended_jobs = recommend_jobs(resume_text, jobs_df, top_n=top_n_jobs)

        # Score against top job
        if not recommended_jobs.empty:
            skill_col = None
            for col in ['Skills Required', 'skills', 'description', 'Job Description', 'key_skills']:
                if col in recommended_jobs.columns:
                    skill_col = col
                    break
            top_job_desc = recommended_jobs.iloc[0][skill_col] if skill_col else ""
            top_job_title = recommended_jobs.iloc[0].get('Job Title',
                           recommended_jobs.iloc[0].get('job_title', 'Top Role'))
            score = calculate_score(resume_text, str(top_job_desc))
        else:
            score = 0
            top_job_title = job_role_filter or "General"

        grade, grade_label = get_grade(score)

        # Missing skills
        required_skills_text = str(top_job_desc) if not recommended_jobs.empty else ""
        required_skills_list = required_skills_text.lower().split()
        missing = get_missing_skills(skills, required_skills_list[:10])

    st.success(f"✅ Analysis Complete for **{name}**!")
    st.markdown("---")

    # ─── METRICS ROW ───────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👤 Candidate", name)
    with col2:
        st.metric("📊 Match Score", f"{score}%")
    with col3:
        st.metric("🎓 Grade", f"{grade} — {grade_label}")
    with col4:
        st.metric("💼 Experience", f"{experience} Years")

    st.markdown("---")

    # ─── TABS ──────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "🧠 Skills Analysis",
        "💼 Job Recommendations",
        "🤖 AI Suggestions",
        "📈 Score Breakdown"
    ])

    # TAB 1 — Skills
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("✅ Skills Found in Resume")
            if skills:
                skill_html = " ".join([f'<span class="skill-badge">{s}</span>' for s in skills])
                st.markdown(skill_html, unsafe_allow_html=True)
            else:
                st.warning("No skills detected. Make sure your resume has a skills section.")

        with col2:
            st.subheader("❌ Missing Skills for Top Role")
            if missing:
                missing_html = " ".join([f'<span class="missing-badge">{s}</span>' for s in missing[:10]])
                st.markdown(missing_html, unsafe_allow_html=True)
            else:
                st.success("Great! You have most required skills.")

        st.markdown("---")
        st.subheader("🎓 Education Detected")
        if education:
            st.write(", ".join(education))
        else:
            st.write("No education info detected.")

    # TAB 2 — Job Recommendations
    with tab2:
        st.subheader(f"🏆 Top {top_n_jobs} Job Recommendations For You")
        if not recommended_jobs.empty:
            display_cols = ['Job Title', 'Match Score']
            for col in ['Location', 'Experience Required', 'job_title', 'location']:
                if col in recommended_jobs.columns:
                    display_cols.append(col)
            display_cols = list(dict.fromkeys(display_cols))
            available_cols = [c for c in display_cols if c in recommended_jobs.columns]
            st.dataframe(recommended_jobs[available_cols], use_container_width=True)

            # Bar chart
            fig = px.bar(
                recommended_jobs,
                x='Match Score',
                y=recommended_jobs.get('Job Title', recommended_jobs.columns[0]),
                orientation='h',
                color='Match Score',
                color_continuous_scale='viridis',
                title="Job Match Scores"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No job recommendations found. Check your dataset file.")

    # TAB 3 — AI Suggestions
    with tab3:
        st.subheader("🤖 AI-Powered Career Suggestions")
        if show_ai:
            with st.spinner("🧠 Generating AI suggestions..."):
                feedback = get_resume_score_feedback(score, grade, name)
                suggestions = get_ai_suggestions(resume_text, missing, top_job_title)

            st.info(f"💬 **Score Feedback:** {feedback}")
            st.markdown("---")
            st.markdown(suggestions)
        else:
            st.info("Enable AI Suggestions from the sidebar to get personalized advice.")

    # TAB 4 — Score Breakdown
    with tab4:
        st.subheader("📊 Detailed Score Analysis")
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=score,
            title={'text': "Resume Match Score"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#667eea"},
                'steps': [
                    {'range': [0, 25], 'color': "#e74c3c"},
                    {'range': [25, 50], 'color': "#f39c12"},
                    {'range': [50, 75], 'color': "#3498db"},
                    {'range': [75, 100], 'color': "#2ecc71"}
                ],
                'threshold': {'line': {'color': "white", 'width': 4}, 'value': score}
            }
        ))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=400)
        st.plotly_chart(fig, use_container_width=True)

        # Skills pie chart
        if skills:
            skill_categories = {
                "Programming": ["Python", "Java", "Javascript", "C++", "R", "Matlab"],
                "ML/AI": ["Machine Learning", "Deep Learning", "Nlp", "Tensorflow", "Pytorch"],
                "Data": ["Sql", "Pandas", "Numpy", "Excel", "Power Bi", "Tableau"],
                "Web": ["Html", "Css", "React", "Node.Js", "Flask", "Django"],
                "DevOps/Cloud": ["Docker", "Kubernetes", "Aws", "Azure", "Git"]
            }
            category_counts = {}
            for cat, cat_skills in skill_categories.items():
                count = sum(1 for s in skills if s in cat_skills)
                if count > 0:
                    category_counts[cat] = count

            if category_counts:
                fig2 = px.pie(
                    names=list(category_counts.keys()),
                    values=list(category_counts.values()),
                    title="Your Skills by Category",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig2, use_container_width=True)

else:
    # Landing screen
    st.markdown("""
    <div style="text-align: center; padding: 3rem;">
        <h2>👆 Upload your Resume to Get Started!</h2>
        <p style="color: #888; font-size: 1.1rem;">
            Get instant AI-powered analysis, job recommendations,<br>
            skill gap detection, and personalized career suggestions.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 📄 Resume Parsing\nAutomatic extraction of skills, education & experience")
    with col2:
        st.markdown("### 💼 Job Matching\nTop job recommendations based on your profile")
    with col3:
        st.markdown("### 🤖 AI Suggestions\nPersonalized career advice powered by OpenAI")