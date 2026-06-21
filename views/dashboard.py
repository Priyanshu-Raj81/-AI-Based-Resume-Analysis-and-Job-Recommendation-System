# import streamlit as st
# import plotly.express as px
# import pandas as pd

# def render_dashboard():
#     st.title("📊 Your Analytics Dashboard")
#     st.markdown("---")
    
#     # Top Metrics
#     col1, col2, col3 = st.columns(3)
#     with col1:
#         st.metric(label="Resumes Analyzed", value="3", delta="1 this week")
#     with col2:
#         st.metric(label="Average ATS Score", value="72%", delta="5% improvement")
#     with col3:
#         st.metric(label="Top Matching Roles", value="Software Eng.", delta="High Demand", delta_color="normal")
        
#     st.markdown("<br>", unsafe_allow_html=True)
    
#     # Charts Section
#     col_chart1, col_chart2 = st.columns(2)
    
#     with col_chart1:
#         st.subheader("ATS Score History")
#         # Dummy data for chart
#         history_data = pd.DataFrame({
#             "Attempt": ["Resume v1", "Resume v2", "Resume v3"],
#             "Score": [45, 60, 78]
#         })
#         fig1 = px.line(history_data, x="Attempt", y="Score", markers=True, color_discrete_sequence=["#4ade80"])
#         fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#8b93ac'))
#         st.plotly_chart(fig1, use_container_width=True)
        
#     with col_chart2:
#         st.subheader("Your Skill Distribution")
#         skills_data = pd.DataFrame({
#             "Category": ["Programming", "Cloud", "Tools", "Soft Skills"],
#             "Proficiency": [80, 40, 60, 90]
#         })
#         fig2 = px.bar(skills_data, x="Category", y="Proficiency", color="Category", template="plotly_dark")
#         fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
#         st.plotly_chart(fig2, use_container_width=True)

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

    # --- Top Metrics ---
    avg_score = round(sum(h["ats_score"] for h in history) / len(history))
    latest_score = history[-1]["ats_score"]
    score_delta = latest_score - history[0]["ats_score"] if len(history) > 1 else None

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Resumes Analyzed", len(history))
    with col2:
        st.metric("Latest ATS Score", f"{latest_score}%",
                  delta=f"{score_delta}% overall" if score_delta is not None else None)
    with col3:
        st.metric("Last Analyzed Role", latest["role"] if latest else "N/A")

    st.markdown("<br>", unsafe_allow_html=True)

    col_chart1, col_chart2 = st.columns(2)

    # --- ATS Score History Chart ---
    with col_chart1:
        st.subheader("📈 ATS Score History")
        
        history_df = pd.DataFrame({
            "Attempt": [h["attempt"] for h in history],
            "Score": [h["ats_score"] for h in history]
        })
        
        if len(history) == 1:
            # Sirf 1 resume — bar chart dikhao, line nahi
            fig1 = px.bar(history_df, x="Attempt", y="Score",
                         color_discrete_sequence=["#4ade80"],
                         text="Score")
            fig1.update_traces(textposition='outside')
        else:
            # Multiple resumes — line chart
            fig1 = px.line(history_df, x="Attempt", y="Score",
                          markers=True, color_discrete_sequence=["#4ade80"],
                          text="Score")
            fig1.update_traces(textposition='top center')
        
        fig1.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#8b93ac'),
            yaxis=dict(range=[0, 100], title="ATS Score (%)"),
            xaxis=dict(title="Resume Attempt")
        )
        st.plotly_chart(fig1, use_container_width=True)

    # --- Skill Distribution Chart ---
    with col_chart2:
        st.subheader("🛠️ Skill Distribution")
        
        if latest and latest["skills"]:
            skill_list = [s.lower() for s in latest["skills"]]

            categories = {
                "Programming": ['python', 'java', 'c++', 'c#', 'javascript', 'typescript', 'sql', 'r'],
                "Web/Framework": ['html', 'css', 'react', 'angular', 'node.js', 'django', 'flask', 'fastapi'],
                "AI/ML": ['machine learning', 'deep learning', 'nlp', 'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch'],
                "Cloud/DevOps": ['aws', 'gcp', 'azure', 'docker', 'kubernetes', 'git', 'linux', 'cloud'],
                "Mobile": ['flutter', 'dart', 'firebase', 'android studio'],
                "Security": ['cybersecurity', 'cryptography', 'information security'],
            }

            cat_counts = {}
            for cat, keywords in categories.items():
                count = sum(1 for s in skill_list if any(k in s for k in keywords))
                if count > 0:
                    cat_counts[cat] = count

            if cat_counts:
                skills_df = pd.DataFrame({
                    "Category": list(cat_counts.keys()),
                    "Count": list(cat_counts.values())
                })
                fig2 = px.bar(skills_df, x="Category", y="Count",
                             color="Category", template="plotly_dark",
                             text="Count")
                fig2.update_traces(textposition='outside')
                fig2.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    showlegend=False
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Skills detected but categories couldn't be matched.")

    # --- Found Skills Section ---
    if latest and latest["skills"]:
        st.markdown("---")
        st.subheader("✅ Skills Found in Resume")
        cols = st.columns(4)
        for i, skill in enumerate(sorted(latest["skills"])):
            with cols[i % 4]:
                st.success(f"✓ {skill}")

    # --- Missing Skills Section ---
    if latest and latest["missing"]:
        st.markdown("---")
        st.subheader("⚠️ Missing Skills to Learn")
        cols = st.columns(3)
        for i, skill in enumerate(latest["missing"]):
            with cols[i % 3]:
                st.error(f"❌ {skill}")