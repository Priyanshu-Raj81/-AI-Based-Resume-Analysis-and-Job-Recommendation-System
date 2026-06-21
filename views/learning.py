import streamlit as st
from utils.ai_suggestions import generate_learning_path

def render_learning():
    st.title("📚 AI Learning Path Generator")
    st.write("Get a personalized 4-week roadmap to land your dream job!")
    st.markdown("---")

    # ✅ 3 Modes
    mode = st.radio(
        "Choose Mode:",
        ["🎯 From My Resume Analysis", "💼 By Job Role", "✍️ Custom Input"],
        horizontal=True
    )

    target_role = ""
    missing_skills = None
    experience_level = "Fresher"

    # --- Mode 1: From Resume ---
    if mode == "🎯 From My Resume Analysis":
        if "latest_analysis" in st.session_state:
            data = st.session_state.latest_analysis
            target_role = data.get("role", "")
            missing_skills = data.get("missing", [])
            experience_level = data.get("experience_level", "Fresher")

            # Info cards
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"🎯 **Role:** {target_role}")
            with col2:
                st.info(f"📊 **Level:** {experience_level}")
            with col3:
                st.info(f"⚠️ **Missing Skills:** {len(missing_skills)} identified")

            if missing_skills:
                st.warning(f"**Skills to learn:** {', '.join(missing_skills)}")

            st.success("✅ All details auto-filled from your resume analysis!")
        else:
            st.warning("⚠️ No resume analyzed yet!")
            st.info("👉 Go to **Resume Analyzer** first → Upload resume → Come back here!")
            return

    # --- Mode 2: By Job Role ---
    elif mode == "💼 By Job Role":
        st.info("💡 Just select your target role and experience level — AI will decide what to learn!")

        col1, col2 = st.columns(2)
        with col1:
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
        with col2:
            experience_level = st.selectbox("Experience Level:", [
                "Fresher", "Mid-Level (1-3 years)", "Senior (3+ years)"
            ])
        # missing_skills = None — AI khud decide karega

    # --- Mode 3: Custom ---
    else:
        col1, col2 = st.columns(2)
        with col1:
            target_role = st.text_input("Target Job Role:", placeholder="e.g. Data Scientist")
        with col2:
            experience_level = st.selectbox("Experience Level:", [
                "Fresher", "Mid-Level (1-3 years)", "Senior (3+ years)"
            ])
        missing_input = st.text_input(
            "Skills you want to learn (comma separated):",
            placeholder="e.g. Python, SQL, Machine Learning"
        )
        if missing_input:
            missing_skills = [s.strip() for s in missing_input.split(',')]

    st.markdown("---")

    # --- Generate Button ---
    if st.button("✨ Generate My Roadmap", type="primary"):
        if not target_role:
            st.warning("Please enter or select a Target Job Role!")
            return

        with st.spinner(f"🧠 Creating personalized roadmap for {target_role}..."):
            roadmap = generate_learning_path(
                target_role=target_role,
                experience_level=experience_level,
                missing_skills=missing_skills
            )

        st.success("✅ Your Personalized Roadmap is Ready!")
        st.markdown("---")

        # ✅ Better display
        st.markdown(f"## 🗺️ Your 4-Week Roadmap")
        st.markdown(f"**Role:** {target_role} | **Level:** {experience_level}")
        st.markdown("---")
        st.markdown(roadmap)

        st.markdown("---")

        # ✅ Download button
        st.download_button(
            label="📥 Download Roadmap",
            data=roadmap,
            file_name=f"roadmap_{target_role}_{experience_level}.txt",
            mime="text/plain"
        )