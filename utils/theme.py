import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
        .stProgress .st-bo { background-color: #4CAF50; }
        .score-card { background: #1a2035; border: 1px solid #2a3352; border-radius: 12px; padding: 20px; text-align: center; }
        .score-val { font-size: 36px; font-weight: bold; color: #4ade80; }
        .roadmap-container { background-color: #1a2035; padding: 25px; border-radius: 10px; border: 1px solid #2a3352; }
    </style>
    """, unsafe_allow_html=True)