import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from utils.pdf_parser import extract_text_from_pdf
from utils.nlp_extractor import extract_skills, extract_education, extract_experience, extract_name
from utils.scorer import calculate_score, get_grade, get_missing_skills
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
    show_ai = st.toggle("🤖 Enable AI Suggestions (OpenAI)", value=True)
    st.markdown("---")
    st.info("1️⃣ Upload your resume PDF\n\n2️⃣ Paste the Job Description\n\n3️⃣ Click **Analyze** to get results!")

# ─── MAIN INPUT SECTION ────────────────────────────────
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("📄 Upload Your Resume (PDF)")
    uploaded_file = st.file_uploader("", type=["pdf"])

with col_right:
    st.subheader("📋 Paste Job Description")
    job_description = st.text_area(
        "",
        height=200,
        placeholder="Paste the full job description here...\n\nExample:\nWe are looking for a Data Scientist with experience in Python, Machine Learning, SQL, TensorFlow...",
        key="jd_input"
    )
    job_title_input = st.text_input("🎯 Job Title (optional)", placeholder="e.g. Data Scientist at Google")

st.markdown("---")

# ─── ANALYZE BUTTON ────────────────────────────────────
analyze_clicked = st.button("🔍 Analyze Resume", type="primary", use_container_width=True)

# ─── ANALYSIS LOGIC ────────────────────────────────────
if analyze_clicked:
    if not uploaded_file:
        st.error("❌ Please upload your resume PDF first!")
    elif not job_description.strip():
        st.error("❌ Please paste a Job Description to analyze against!")
    else:
        with st.spinner("🔍 Analyzing your resume against the job description..."):

            # Extract resume text
            resume_text = extract_text_from_pdf(uploaded_file)

            # Extract info from resume
            name       = extract_name(resume_text)
            skills     = extract_skills(resume_text)
            education  = extract_education(resume_text)
            experience = extract_experience(resume_text)

            # Score against manually entered JD
            score = calculate_score(resume_text, job_description)
            grade, grade_label = get_grade(score)

            # Missing skills — scorer.py KNOWN_SKILLS se filter hoga automatically
            missing = get_missing_skills(skills, job_description, resume_text)

            # Job title for display
            top_job_title = job_title_input.strip() if job_title_input.strip() else "This Role"

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
            "📋 JD vs Resume",
            "🤖 AI Suggestions",
            "📈 Score Breakdown"
        ])

        # ── TAB 1 — Skills ──────────────────────────────────
        with tab1:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("✅ Skills Found in Your Resume")
                if skills:
                    skill_html = " ".join([f'<span class="skill-badge">{s}</span>' for s in skills])
                    st.markdown(skill_html, unsafe_allow_html=True)
                else:
                    st.warning("No skills detected. Make sure your resume has a skills section.")

            with col2:
                st.subheader("❌ Missing Skills for This Role")
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

        # ── TAB 2 — JD vs Resume ────────────────────────────
        with tab2:
            st.subheader(f"📋 Job Description Analysis: {top_job_title}")

            col_jd, col_res = st.columns(2)

            with col_jd:
                st.markdown("**🗒️ Job Description (you entered)**")
                st.text_area("", value=job_description, height=300, disabled=True, key="jd_display")

            with col_res:
                st.markdown("**📄 Extracted Resume Summary**")
                resume_summary = f"""Candidate: {name}
Experience: {experience} Years
Education: {', '.join(education) if education else 'Not detected'}

Skills:
{', '.join(skills) if skills else 'Not detected'}
"""
                st.text_area("", value=resume_summary, height=300, disabled=True, key="res_display")

            st.markdown("---")
            st.markdown(f"**🎯 Overall Match with '{top_job_title}': `{score}%` ({grade} — {grade_label})**")

            # Score progress bar
            progress_color = (
                "#2ecc71" if score >= 75 else
                "#3498db" if score >= 50 else
                "#f39c12" if score >= 25 else
                "#e74c3c"
            )
            st.markdown(f"""
            <div style="background:#333; border-radius:8px; height:20px; width:100%;">
                <div style="background:{progress_color}; border-radius:8px; height:20px; width:{score}%;"></div>
            </div>
            <p style="color:#888; font-size:0.85rem; margin-top:4px;">0% ————————————————————— 100%</p>
            """, unsafe_allow_html=True)

        # ── TAB 3 — AI Suggestions ───────────────────────────
        with tab3:
            st.subheader("🤖 AI-Powered Career Suggestions")
            if show_ai:
                with st.spinner("🧠 Generating AI suggestions..."):
                    feedback    = get_resume_score_feedback(score, grade, name, top_job_title)
                    suggestions = get_ai_suggestions(resume_text, missing, top_job_title, job_description)
                st.info(f"💬 **Score Feedback:** {feedback}")
                st.markdown("---")
                st.markdown(suggestions)
            else:
                st.info("Enable AI Suggestions from the sidebar to get personalized advice.")

        # ── TAB 4 — Score Breakdown ──────────────────────────
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
                        {'range': [0, 25],   'color': "#e74c3c"},
                        {'range': [25, 50],  'color': "#f39c12"},
                        {'range': [50, 75],  'color': "#3498db"},
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
                    "Programming":  ["Python", "Java", "Javascript", "C++", "R", "Matlab"],
                    "ML/AI":        ["Machine Learning", "Deep Learning", "Nlp", "Tensorflow", "Pytorch"],
                    "Data":         ["Sql", "Pandas", "Numpy", "Excel", "Power Bi", "Tableau"],
                    "Web":          ["Html", "Css", "React", "Node.Js", "Flask", "Django"],
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

# ─── LANDING SCREEN ────────────────────────────────────
else:
    st.markdown("""
    <div style="text-align: center; padding: 3rem;">
        <h2>👆 Upload Resume + Paste Job Description → Click Analyze!</h2>
        <p style="color: #888; font-size: 1.1rem;">
            Get instant AI-powered analysis of how well your resume<br>
            matches any specific job you're applying for.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 📄 Resume Parsing\nAutomatic extraction of skills, education & experience")
    with col2:
        st.markdown("### 🎯 JD Matching\nScore your resume against any job description you paste")
    with col3:
        st.markdown("### 🤖 AI Suggestions\nPersonalized career advice based on skill gaps")