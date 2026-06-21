import streamlit as st
from utils.recommender import load_job_data, recommend_jobs

def render_career():
    st.title("💼 Job Recommendations")
    st.write("Discover the best-matching roles based on your skillset.")
    st.markdown("---")

    # ✅ Resume analyzer se skills auto-load
    auto_skills = ""
    if "latest_analysis" in st.session_state:
        skills_list = st.session_state["latest_analysis"].get("skills", [])
        auto_skills = ", ".join(skills_list)
        st.success(f"✅ Skills auto-loaded from your resume analysis!")

    # --- Input Section ---
    col1, col2 = st.columns([3, 1])
    with col1:
        user_skills_input = st.text_input(
            "🔑 Your Skills (comma-separated):",
            value=auto_skills if auto_skills else "Python, Machine Learning, Data Analysis",
            help="These are auto-filled from your resume. You can edit them."
        )
    with col2:
        top_n = st.selectbox("Show Top:", [3, 5, 10], index=1)

    # --- Role Filter (optional) ---
    role_filter = st.text_input(
        "🎯 Filter by Role (optional):",
        placeholder="e.g. Data Scientist, Flutter Developer, Software Engineer"
    )

    if st.button("🔍 Find Matching Jobs", type="primary"):
        if not user_skills_input.strip():
            st.warning("Please enter at least one skill!")
            return

        with st.spinner("Scanning job market..."):
            user_skills = [s.strip() for s in user_skills_input.split(',')]
            df = load_job_data()

            # Role filter apply karo
            if role_filter.strip() and not df.empty:
                filtered_df = df[df['Job Title'].str.contains(role_filter.strip(), case=False, na=False)]
                if filtered_df.empty:
                    st.warning(f"No jobs found for '{role_filter}'. Searching all roles instead.")
                    filtered_df = df
            else:
                filtered_df = df

            if not filtered_df.empty:
                recommended = recommend_jobs(user_skills, filtered_df, top_n=top_n)

                if not recommended.empty:
                    st.markdown(f"### 🎯 Top {len(recommended)} Matches Found")
                    st.markdown("---")

                    for rank, (i, row) in enumerate(recommended.iterrows(), 1):
                        # Score color
                        score = int(row['Match_Score'])
                        if score >= 70:
                            score_color = "#4ade80"  # Green
                            badge = "🔥 Strong Match"
                        elif score >= 40:
                            score_color = "#facc15"  # Yellow
                            badge = "⚡ Good Match"
                        else:
                            score_color = "#f87171"  # Red
                            badge = "📌 Partial Match"

                        with st.container(border=True):
                            col_title, col_score = st.columns([4, 1])

                            with col_title:
                                st.markdown(f"### #{rank} {row['Job Title']}")
                                
                                info_col1, info_col2 = st.columns(2)
                                with info_col1:
                                    st.write(f"📍 **Location:** {row.get('Location', 'N/A')}")
                                with info_col2:
                                    salary = row.get('Job Salary', 'N/A')
                                    st.write(f"💰 **Salary:** {salary if salary != 'nan' else 'Not disclosed'}")

                                # Skills preview
                                skills_preview = str(row['Key Skills'])[:150]
                                st.write(f"🔑 **Required Skills:** {skills_preview}...")

                            with col_score:
                                st.markdown(
                                    f"<div style='text-align:center; padding:10px;'>"
                                    f"<h2 style='color:{score_color}; margin:0;'>{score}%</h2>"
                                    f"<p style='color:{score_color}; font-size:12px; margin:0;'>{badge}</p>"
                                    f"</div>",
                                    unsafe_allow_html=True
                                )

                        st.markdown("<br>", unsafe_allow_html=True)

                    # --- Summary Stats ---
                    st.markdown("---")
                    avg_match = round(recommended['Match_Score'].mean())
                    best_match = int(recommended['Match_Score'].max())

                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.metric("Jobs Found", len(recommended))
                    with m2:
                        st.metric("Best Match", f"{best_match}%")
                    with m3:
                        st.metric("Avg Match Score", f"{avg_match}%")

                else:
                    st.warning("No matches found. Try different or broader skills!")
            else:
                st.error("❌ Dataset not found. Please ensure CSV is in the dataset folder.")

    # --- Agar resume analyzed hai toh missing skills bhi dikhao ---
    if "latest_analysis" in st.session_state:
        missing = st.session_state["latest_analysis"].get("missing", [])
        if missing:
            st.markdown("---")
            st.subheader("📚 Skills You Should Learn for Better Matches")
            cols = st.columns(3)
            for i, skill in enumerate(missing):
                with cols[i % 3]:
                    st.warning(f"➕ {skill}")