import streamlit as st
import pandas as pd
import plotly.express as px

def render_market():
    st.title("📈 Market Insights")
    st.write("Stay ahead of the curve by understanding industry trends and skill demands.")
    st.markdown("---")
    
    st.subheader("🔥 Top Trending Tech Skills in 2026")
    
    # Market Data
    market_data = pd.DataFrame({
        "Skill": ['Generative AI', 'Cloud Computing (AWS/GCP)', 'Python/FastAPI', 'React/Next.js', 'Cybersecurity', 'Flutter/Dart'],
        "Demand Index": [98, 92, 88, 85, 82, 80]
    })
    
    fig = px.bar(market_data, x="Demand Index", y="Skill", orientation='h', color="Demand Index", color_continuous_scale="Blues")
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.info("💡 **Insight:** AI and LLM integration skills have seen a 300% surge in job postings over the last year.")
    with col2:
        st.info("💡 **Insight:** Cross-platform mobile development remains highly stable, with steady demand.")