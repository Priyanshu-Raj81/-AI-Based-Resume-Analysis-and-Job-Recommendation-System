import streamlit as st
from utils.pdf_parser import parse_resume
from utils.nlp_extractor import extract_skills
from utils.recommender import load_job_data, get_role_ats_score, recommend_jobs
from utils.scorer import calculate_similarity_score
from utils.ai_suggestions import generate_resume_suggestions

def render_analyzer():
    st.title("🎯 AI Resume Analyzer")
    st.markdown("---")

    uploaded_file = st.file_uploader("1. Upload your PDF or DOCX resume", type=["pdf", "docx"])

    st.subheader("2. Choose Analysis Mode")
    mode = st.radio("Mode:", ["Target Job Role", "Paste Job Description (JD)"], horizontal=True)

    target_role = ""
    job_desc = ""

    if mode == "Target Job Role":
        target_role = st.selectbox("Target Job Role:", [
    # Software Development
    "Software Developer", "Backend Developer", "Frontend Developer",
    "Full Stack Developer", "Flutter Developer", "Android Developer", "iOS Developer",
    "Mobile App Developer",
    # Data & AI
    "Data Scientist", "Data Analyst", "Data Engineer", "ML Engineer",
    "AI Engineer", "Business Analyst", "NLP Engineer", "Prompt Engineer",
    # Cloud & DevOps
    "DevOps Engineer", "Cloud Engineer", "Site Reliability Engineer",
    # Security
    "Information Security Analyst", "Cybersecurity Engineer", "Ethical Hacker",
    # Management
    "Product Manager", "Project Manager",
    # Design
    "UI UX Designer", "Graphic Designer",
    # Emerging
    "Blockchain Developer", "Game Developer", "AR VR Developer",
])
    else:
        job_desc = st.text_area("Paste JD here:", height=150)

    # ✅ Experience Level added
    experience_level = st.selectbox(
        "3. Your Experience Level:",
        ["Fresher", "Mid-Level (1-3 years)", "Senior (3+ years)"],
        help="AI will tailor suggestions based on your experience level"
    )

    if st.button("🚀 Analyze Now", type="primary"):
        if not uploaded_file:
            st.warning("Please upload a resume!")
            return

        with st.spinner("Analyzing..."):
            resume_text = parse_resume(uploaded_file)
            extracted_skills = extract_skills(resume_text)
            df = load_job_data()

            if mode == "Target Job Role":
                ats_score, missing_skills = get_role_ats_score(extracted_skills, target_role, df)
            else:
                jd_skills = extract_skills(job_desc)
                ats_score, missing_skills = calculate_similarity_score(extracted_skills, " ".join(jd_skills))

        # ✅ Session state mein save
        if "resume_history" not in st.session_state:
            st.session_state.resume_history = []

        attempt_number = len(st.session_state.resume_history) + 1
        st.session_state.resume_history.append({
            "attempt": f"Resume v{attempt_number}",
            "ats_score": ats_score,
            "role": target_role if mode == "Target Job Role" else "Custom JD",
            "skills": extracted_skills,
            "missing": missing_skills
        })

        st.session_state.latest_analysis = {
            "ats_score": ats_score,
            "role": target_role if mode == "Target Job Role" else "Custom JD",
            "skills": extracted_skills,
            "missing": missing_skills,
            "job_desc": job_desc,
            "mode": mode,
            "experience_level": experience_level  # ✅ Save kiya
        }

        st.success("✅ Analysis Complete!")

        tab1, tab2, tab3, tab4 = st.tabs(["📊 Score", "⚠️ Skill Gap", "💼 Matches", "🤖 AI Suggestions"])

        with tab1:
            st.metric("ATS Match Score", f"{ats_score}%")
            st.progress(ats_score / 100)
            st.write("**Found Skills:**", ", ".join(extracted_skills))

        with tab2:
            st.write("### Missing Skills")
            if missing_skills:
                for s in missing_skills:
                    st.write(f"❌ {s}")
            else:
                st.success("🎉 No major skill gaps found!")

        with tab3:
            if mode == "Target Job Role" and not df.empty:
                recommended = recommend_jobs(extracted_skills, df)
                st.dataframe(recommended)
            else:
                st.info("Matches available only in 'Target Job Role' mode.")

        with tab4:
            st.subheader("🤖 AI-Powered Resume Suggestions")
            st.write(f"Personalized recommendations for **{target_role}** at **{experience_level}** level.")
            st.markdown("---")

            with st.spinner("🧠 AI analyzing your resume... please wait"):
                suggestions = generate_resume_suggestions(
                    target_role=target_role if mode == "Target Job Role" else "Custom JD Role",
                    extracted_skills=extracted_skills,
                    missing_skills=missing_skills,
                    job_desc=job_desc if mode == "Paste Job Description (JD)" else "",
                    experience_level=experience_level  # ✅ Pass kiya
                )

            st.markdown(suggestions)

            st.download_button(
                label="📥 Download AI Suggestions",
                data=suggestions,
                file_name=f"resume_suggestions_{target_role}_{experience_level}.txt",
                mime="text/plain"
            )

    # ✅ Page refresh fix
    elif "latest_analysis" in st.session_state:
        data = st.session_state.latest_analysis
        st.info(f"📋 Showing last analysis for: **{data['role']}** | Level: **{data.get('experience_level', 'Fresher')}**")

        tab1, tab2, tab3 = st.tabs(["📊 Score", "⚠️ Skill Gap", "🤖 AI Suggestions"])

        with tab1:
            st.metric("ATS Match Score", f"{data['ats_score']}%")
            st.progress(data['ats_score'] / 100)
            st.write("**Found Skills:**", ", ".join(data['skills']))

        with tab2:
            if data['missing']:
                for s in data['missing']:
                    st.write(f"❌ {s}")
            else:
                st.success("🎉 No major skill gaps found!")

        with tab3:
            st.subheader("🤖 AI-Powered Resume Suggestions")
            st.markdown("---")

            with st.spinner("🧠 AI analyzing your resume..."):
                suggestions = generate_resume_suggestions(
                    target_role=data['role'],
                    extracted_skills=data['skills'],
                    missing_skills=data['missing'],
                    job_desc=data.get('job_desc', ''),
                    experience_level=data.get('experience_level', 'Fresher')  # ✅ Pass kiya
                )

            st.markdown(suggestions)

            st.download_button(
                label="📥 Download AI Suggestions",
                data=suggestions,
                file_name="resume_suggestions.txt",
                mime="text/plain"
            )