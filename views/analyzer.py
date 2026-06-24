import streamlit as st
from utils.pdf_parser import parse_resume
from utils.nlp_extractor import extract_skills, extract_projects
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
            "Software Developer", "Backend Developer", "Frontend Developer",
            "Full Stack Developer", "Flutter Developer", "Android Developer", "iOS Developer",
            "Mobile App Developer",
            "Data Scientist", "Data Analyst", "Data Engineer", "ML Engineer",
            "AI Engineer", "Business Analyst", "NLP Engineer", "Prompt Engineer",
            "DevOps Engineer", "Cloud Engineer", "Site Reliability Engineer",
            "Information Security Analyst", "Cybersecurity Engineer", "Ethical Hacker",
            "Product Manager", "Project Manager",
            "UI UX Designer", "Graphic Designer",
            "Blockchain Developer", "Game Developer", "AR VR Developer",
        ])
    else:
        job_desc = st.text_area("Paste JD here:", height=150)

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
            extracted_projects = extract_projects(resume_text)
            df = load_job_data()

            if mode == "Target Job Role":
                ats_score, missing_skills = get_role_ats_score(extracted_skills, target_role, df)
            else:
                jd_skills = extract_skills(job_desc)
                ats_score, missing_skills = calculate_similarity_score(
                    extracted_skills, " ".join(jd_skills))

        # ✅ Session state save
        if "resume_history" not in st.session_state:
            st.session_state.resume_history = []

        attempt_number = len(st.session_state.resume_history) + 1
        st.session_state.resume_history.append({
            "attempt": f"Resume v{attempt_number}",
            "ats_score": ats_score,
            "role": target_role if mode == "Target Job Role" else "Custom JD",
            "skills": extracted_skills,
            "missing": missing_skills,
            "projects": extracted_projects,
        })

        st.session_state.latest_analysis = {
            "ats_score": ats_score,
            "role": target_role if mode == "Target Job Role" else "Custom JD",
            "skills": extracted_skills,
            "missing": missing_skills,
            "missing_skills": missing_skills,
            "projects": extracted_projects,
            "job_desc": job_desc,
            "mode": mode,
            "experience_level": experience_level
        }

        st.success("✅ Analysis Complete!")

        tab1, tab2, tab3, tab4 = st.tabs(["📊 Score", "⚠️ Skill Gap", "💼 Matches", "🤖 AI Suggestions"])

        with tab1:
            st.metric("ATS Match Score", f"{ats_score}%")
            st.progress(ats_score / 100)
            st.write("**Found Skills:**", ", ".join(extracted_skills))

            # ✅ Projects — sirf clean message
            if extracted_projects:
                st.markdown("""
                    <div style='background:rgba(79,70,229,0.1); border-left:3px solid #4f46e5;
                                border-radius:8px; padding:12px 16px; margin-top:12px;'>
                        <span style='color:#818cf8; font-weight:700;'>✅ Projects Analyzed</span>
                        <br><br>
                        <span style='color:#9aa1b1; font-size:13px;'>
                            Your projects have been analyzed successfully. Visit
                            <b style='color:#4f46e5;'>Interview Prep → 🎤 Mock Interview Coach</b>
                            to get personalized questions based on your projects!
                        </span>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div style='background:rgba(250,204,21,0.08); border-left:3px solid #facc15;
                                border-radius:8px; padding:12px 16px; margin-top:12px;'>
                        <span style='color:#facc15; font-weight:700;'>💡 No Projects Found</span>
                        <br><br>
                        <span style='color:#9aa1b1; font-size:13px;'>
                            No projects section detected in your resume.
                            Add a <b style='color:#facc15;'>Projects</b> section to get
                            project-based interview questions in the AI Coach!
                        </span>
                    </div>
                """, unsafe_allow_html=True)

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
                    experience_level=experience_level
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

            # ✅ Projects — sirf clean message
            if data.get("projects"):
                st.markdown("""
                    <div style='background:rgba(79,70,229,0.1); border-left:3px solid #4f46e5;
                                border-radius:8px; padding:12px 16px; margin-top:12px;'>
                        <span style='color:#818cf8; font-weight:700;'>✅ Projects Analyzed</span>
                        <br><br>
                        <span style='color:#9aa1b1; font-size:13px;'>
                            Your projects have been analyzed successfully. Visit
                            <b style='color:#4f46e5;'>Interview Prep → 🎤 Mock Interview Coach</b>
                            to get personalized questions based on your projects!
                        </span>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div style='background:rgba(250,204,21,0.08); border-left:3px solid #facc15;
                                border-radius:8px; padding:12px 16px; margin-top:12px;'>
                        <span style='color:#facc15; font-weight:700;'>💡 No Projects Found</span>
                        <br><br>
                        <span style='color:#9aa1b1; font-size:13px;'>
                            No projects section detected in your resume.
                            Add a <b style='color:#facc15;'>Projects</b> section to get
                            project-based interview questions in the AI Coach!
                        </span>
                    </div>
                """, unsafe_allow_html=True)

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
                    experience_level=data.get('experience_level', 'Fresher')
                )
            st.markdown(suggestions)
            st.download_button(
                label="📥 Download AI Suggestions",
                data=suggestions,
                file_name="resume_suggestions.txt",
                mime="text/plain"
            )