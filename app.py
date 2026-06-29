import os
import base64
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

# Keys to clear on New Analysis
RESET_KEYS = [
    "latest_analysis",
    "resume_history",
    "interview_questions",
    "coach_state",
    "_nav_target",
    "main_menu",
    "_career_searched",
    "_analysis_rendered",
]


# ── Browser tab logo ─────────────────────────────────────────────
_logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
_page_icon = _logo_path if os.path.exists(_logo_path) else "💼"

st.set_page_config(
    page_title=APP_NAME,
    page_icon=_page_icon,
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_custom_css()

# ── Global CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
/* Remove white box around sidebar logo */
section[data-testid="stSidebar"] [data-testid="stImage"],
section[data-testid="stSidebar"] [data-testid="stImage"] > div,
section[data-testid="stSidebar"] img {
    background: transparent !important;
    box-shadow: none !important;
    border: none !important;
}

/* New Analysis button styling */
.new-analysis-btn button {
    width: 100% !important;
    background: transparent !important;
    border: 1px solid rgba(37,99,235,0.50) !important;
    color: #93c5fd !important;
    border-radius: 10px !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.4px !important;
    padding: 6px 12px !important;
    margin-top: 8px !important;
    transition: all 0.2s ease !important;
}
.new-analysis-btn button:hover {
    background: rgba(37,99,235,0.15) !important;
    border-color: #2563eb !important;
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)


from views import analyzer, career, dashboard, home, learning


# ── Helpers ──────────────────────────────────────────────────────
def reset_session():
    """Clear all analysis-related session state and go to Resume Analyzer."""
    for key in RESET_KEYS:
        st.session_state.pop(key, None)
    st.session_state["goto_page"] = "Resume Analyzer"


def render_sidebar_brand():
    if os.path.exists(_logo_path):
        from PIL import Image
        img = Image.open(_logo_path).convert("RGBA")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(img, width=90)
    st.markdown(
        f"""
        <div style="text-align:center; padding:4px 0 6px;">
            <div style="font-size:1.15rem; font-weight:800;
                        background:linear-gradient(90deg,#93c5fd,#34d399);
                        -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                {APP_NAME}
            </div>
            <div style="color:#9aa4c4; font-size:.72rem; letter-spacing:.5px; margin-top:2px;">
                {APP_TAGLINE}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_analysis_status():
    data  = st.session_state["latest_analysis"]
    role  = data.get("role", "N/A")
    score = data.get("ats_score", 0)

    # Status card only (button is rendered separately in sidebar)
    st.markdown(
        f"""
        <div class="rm-info" style="margin-bottom:8px;">
            <b>Resume Analyzed</b><br>
            <span style="color:var(--rm-text); font-weight:600;">{role}</span><br>
            <span style="color:var(--rm-text-2); font-size:.82rem;">ATS Score: {score}%</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_footer():
    st.markdown(
        f"""
        <div style="color:#6b7280; font-size:.72rem; text-align:center;
                    padding:8px 0; margin-top:8px;">
            {APP_NAME} v1.0 &nbsp;·&nbsp; {APP_TAGLINE}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Sidebar ──────────────────────────────────────────────────────
with st.sidebar:
    render_sidebar_brand()
    st.markdown("---")

    _manual_select = None
    if "goto_page" in st.session_state:
        target = st.session_state.pop("goto_page")
        st.session_state["_nav_target"] = target

    if "_nav_target" in st.session_state:
        _nav_target = st.session_state["_nav_target"]
        if _nav_target in MENU_OPTIONS:
            _manual_select = MENU_OPTIONS.index(_nav_target)

    selected_page = option_menu(
        menu_title=None,
        options=MENU_OPTIONS,
        icons=MENU_ICONS,
        menu_icon="cast",
        default_index=0,
        manual_select=_manual_select,
        key="main_menu",
        styles={
            "container":         {"padding": "0!important", "background-color": "transparent"},
            "icon":              {"color": "#8b93ac", "font-size": "16px"},
            "nav-link": {
                "font-size":     "15px",
                "text-align":    "left",
                "margin":        "4px 0px",
                "--hover-color": "rgba(37,99,235,0.15)",
                "transition":    "all 0.25s ease",
                "border-radius": "14px",
            },
            "nav-link-selected": {
                "background":    "linear-gradient(90deg,#1d4ed8,#2563eb,#10b981)",
                "color":         "white",
                "font-weight":   "700",
                "box-shadow":    "0 0 26px rgba(37,99,235,0.45)",
                "border-radius": "14px",
            },
        },
    )

    # Override selected_page with programmatic target if set
    if "_nav_target" in st.session_state:
        selected_page = st.session_state.pop("_nav_target")

    # ── New Analysis button — right after nav, always visible once analyzed ──
    if "latest_analysis" in st.session_state:
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        st.markdown('<div class="new-analysis-btn">', unsafe_allow_html=True)
        if st.button("+ New Analysis", key="btn_new_analysis", use_container_width=True):
            reset_session()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    if "latest_analysis" in st.session_state:
        render_analysis_status()

    render_sidebar_footer()


# ── Page routing ─────────────────────────────────────────────────
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
    st.info("Module under development.")