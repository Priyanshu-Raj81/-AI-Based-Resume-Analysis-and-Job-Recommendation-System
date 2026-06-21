import streamlit as st
import plotly.express as px
import pandas as pd

def render_skills():
    st.title("🔍 Skill Analysis")
    st.write("Visualize your strengths and identify areas for growth.")
    st.markdown("---")
    
    st.write("Rate your proficiency in different categories to generate your Skill Radar.")
    
    col1, col2 = st.columns(2)
    with col1:
        frontend = st.slider("Frontend / UI", 0, 100, 70)
        backend = st.slider("Backend / APIs", 0, 100, 80)
        database = st.slider("Databases", 0, 100, 60)
    with col2:
        ai_ml = st.slider("AI / Machine Learning", 0, 100, 50)
        devops = st.slider("DevOps / Cloud", 0, 100, 40)
        security = st.slider("Information Security", 0, 100, 65)
        
    if st.button("Generate Radar Chart", type="primary"):
        df = pd.DataFrame(dict(
            r=[frontend, backend, database, ai_ml, devops, security],
            theta=['Frontend', 'Backend', 'Databases', 'AI/ML', 'DevOps/Cloud', 'Security']
        ))
        
        fig = px.line_polar(df, r='r', theta='theta', line_close=True, template="plotly_dark")
        fig.update_traces(fill='toself', line_color='#8b5cf6')
        st.plotly_chart(fig, use_container_width=True)