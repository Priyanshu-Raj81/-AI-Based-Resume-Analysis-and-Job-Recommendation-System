import streamlit as st
from streamlit_option_menu import option_menu

from utils.theme import apply_custom_css


APP_NAME = "JobFit AI"
APP_TAGLINE = "AI-Powered Career Intelligence"
MENU_OPTIONS = [
    "Home",
    "Resume Analyzer",
    "Dashboard",
    "Job Recommendation",
    "Learning Path",
    "Interview Preparation",
]
MENU_ICONS = [
    "house-door",
    "file-earmark-text",
    "bar-chart-fill",
    "briefcase",
    "map",
    "mic-fill",
]


st.set_page_config(
    page_title=APP_NAME,
    page_icon=" ",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_custom_css()


from views import analyzer, career, dashboard, home, learning


def render_sidebar_brand():
    st.markdown(
        f"""
        <div style="text-align:center; padding:10px 0 4px;">
            <div class="rm-grad-heading" style="margin-bottom:4px;"> {APP_NAME}</div>
            <div style="color:var(--rm-text-2); font-size:.75rem; letter-spacing:.5px;">
                {APP_TAGLINE}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_analysis_status():
    data = st.session_state["latest_analysis"]
    role = data.get("role", "N/A")
    score = data.get("ats_score", 0)
    st.markdown(
        f"""
        <div class="rm-info" style="margin-bottom:12px;">
            <b>✅ Resume Analyzed</b><br>
            <span style="color:var(--rm-text); font-weight:600;">{role}</span><br>
            <span style="color:var(--rm-text-2); font-size:.82rem;">ATS Score: {score}%</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_footer():
    st.markdown(
        f"""
        <div style="color:#6b7280; font-size:.72rem; text-align:center; padding:8px 0; margin-top:8px;">
            {APP_NAME} v1.0<br>{APP_TAGLINE}
        </div>
        """,
        unsafe_allow_html=True,
    )


with st.sidebar:
    render_sidebar_brand()
    st.markdown("---")

    # Navigation fix: option_menu manages its own internal state via key="main_menu".
    # Simply setting st.session_state["main_menu"] doesn't work because option_menu
    # overrides it with its own cached value on render.
    # Fix: delete the widget's internal state key first, then set new value —
    # this forces option_menu to re-initialize and pick up our target page.
    if "goto_page" in st.session_state:
        target = st.session_state.pop("goto_page")
        if "main_menu" in st.session_state:
            del st.session_state["main_menu"]
        st.session_state["main_menu"] = target

    # Dynamic default_index — ensures correct item is highlighted
    # even on programmatic navigation via goto_page
    _current = st.session_state.get("main_menu", "Home")
    _default_idx = MENU_OPTIONS.index(_current) if _current in MENU_OPTIONS else 0

    selected_page = option_menu(
        menu_title=None,
        options=MENU_OPTIONS,
        icons=MENU_ICONS,
        menu_icon="cast",
        default_index=_default_idx,
        key="main_menu",
        styles={
            "container": {
                "padding": "0!important",
                "background-color": "transparent",
            },
            "icon": {"color": "#8b93ac", "font-size": "16px"},
            "nav-link": {
                "font-size": "15px",
                "text-align": "left",
                "margin": "4px 0px",
                "--hover-color": "rgba(99,102,241,0.15)",
                "transition": "all 0.25s ease",
                "border-radius": "14px",
            },
            "nav-link-selected": {
                "background": "linear-gradient(90deg,#4f46e5,#7c3aed,#db2777)",
                "color": "white",
                "font-weight": "700",
                "box-shadow": "0 0 26px rgba(124,58,237,0.55)",
                "border-radius": "14px",
            },
        },
    )

    st.markdown("---")

    if "latest_analysis" in st.session_state:
        render_analysis_status()

    render_sidebar_footer()


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
elif selected_page == "Interview Preparation":
    from views import interview

    interview.render_interview()
else:
    st.title(selected_page)
    st.info("🚧 Module under development.")