import streamlit as st
from streamlit_option_menu import option_menu  # Import the new premium menu
from utils.theme import apply_custom_css

# --- Page Config ---
st.set_page_config(page_title="Resumatch AI", page_icon="🎯", layout="wide", initial_sidebar_state="expanded")
apply_custom_css()

# --- Import Views ---
from views import home, analyzer, learning, dashboard, career, compare, market, skills

# --- Premium Animated Sidebar Navigation ---
with st.sidebar:
    st.markdown("### 🤖 Resumatch App")
    st.markdown("---")
    
    # The magical animated menu
    selected_page = option_menu(
        menu_title=None,  # Leave empty because we have the markdown title above
        options=["Home", "Dashboard", "Resume Analyzer", "Job Recommendation", "Learning Path","Skills"],  #Market, compare
        # Bootstrap icons for each tab
        icons=["house-door", "bar-chart-fill", "file-earmark-text", "briefcase", "map", "graph-up-arrow", "bullseye", "arrow-left-right"],
        menu_icon="cast", 
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#8b93ac", "font-size": "16px"}, 
            "nav-link": {
                "font-size": "15px", 
                "text-align": "left", 
                "margin": "4px 0px", 
                "--hover-color": "rgba(59,130,246,0.15)", # Light blue hover effect
                "transition": "all 0.3s ease-in-out", # Smooth animation
                "border-radius": "8px"
            },
            "nav-link-selected": {
                "background-color": "#3b82f6", 
                "color": "white", 
                "font-weight": "600",
                "box-shadow": "0 4px 10px rgba(59,130,246,0.4)", # Glowing effect for active tab
                "border-radius": "8px"
            },
        }
    )
    
    st.markdown("---")
    st.info("Developed for your remote internship project. 🚀")

# --- Routing Logic ---
if selected_page == "Home": 
    home.render_home()
elif selected_page == "Dashboard": 
    dashboard.render_dashboard()
elif selected_page == "Resume Analyzer": 
    analyzer.render_analyzer()
elif selected_page == "Job Recommendation": 
    career.render_career()
elif selected_page == "Learning Path": 
    learning.render_learning()
elif selected_page == "Market": 
    market.render_market()
elif selected_page == "Skills": 
    skills.render_skills()
elif selected_page == "Compare": 
    compare.render_compare()
else: 
    st.title(selected_page)
    st.info("🚧 Module under development.")