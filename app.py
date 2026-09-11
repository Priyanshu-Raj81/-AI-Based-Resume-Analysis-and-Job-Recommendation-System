import os
import base64
import streamlit as st
import streamlit.components.v1 as components
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


def render_top_masthead():
    """
    Persistent top header bar — hamburger + logo together in one row,
    fixed across the full viewport width, same pattern as YouTube's
    masthead: the header never moves, and the hamburger toggles the
    sidebar (YouTube's "guide") independently underneath it.

    Streamlit has no public Python API to open/close the sidebar, so the
    hamburger works by finding and clicking Streamlit's own internal
    toggle button inside the parent document (this widget renders in an
    iframe, and `window.parent.document` reaches the real page). The
    default native control is hidden via CSS so there's only one visible
    toggle, and the sidebar's own duplicate logo/title (previously
    rendered separately inside `st.sidebar`) has been removed — the
    masthead is now the single, consistent place brand shows up, instead
    of two disconnected-looking headers stacked on top of each other.
    """
    logo_data_uri = ""
    if os.path.exists(_logo_path):
        with open(_logo_path, "rb") as f:
            logo_data_uri = "data:image/png;base64," + base64.b64encode(f.read()).decode()

    logo_img_tag = (
        f"<img src='{logo_data_uri}' style='width:28px;height:28px;border-radius:6px;' />"
        if logo_data_uri else ""
    )

    components.html(
        f"""
        <script>
        (function() {{
            const doc = window.parent.document;

            // Hide Streamlit's built-in collapse controls — ours is the
            // only visible toggle. Only inject this once.
            if (!doc.getElementById('jf-toggle-style')) {{
                const style = doc.createElement('style');
                style.id = 'jf-toggle-style';
                style.textContent = `
                    [data-testid="stSidebarCollapseButton"],
                    [data-testid="stSidebarCollapsedControl"] {{ display: none !important; }}
                `;
                doc.head.appendChild(style);
            }}

            if (doc.getElementById('jf-masthead')) return;  // already injected

            const header = doc.createElement('div');
            header.id = 'jf-masthead';
            header.style.cssText = `
                position: fixed; top: 0; left: 0; width: 100%; height: 56px;
                z-index: 999999; display: flex; align-items: center; gap: 14px;
                padding: 0 16px; box-sizing: border-box;
                background: rgba(8,10,20,0.85); backdrop-filter: blur(14px);
                border-bottom: 1px solid rgba(255,255,255,0.08);
            `;

            const btn = doc.createElement('button');
            btn.id = 'jf-sidebar-toggle';
            btn.title = 'Toggle navigation menu';
            btn.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path d="M2.5 5h15M2.5 10h15M2.5 15h15" stroke="#e8ecf6"
                          stroke-width="1.6" stroke-linecap="round"/>
                </svg>
            `;
            btn.style.cssText = `
                width: 40px; height: 40px; border-radius: 50%; border: none;
                background: transparent; cursor: pointer; flex: none;
                display: flex; align-items: center; justify-content: center;
                transition: background 0.15s ease;
            `;
            btn.onmouseenter = function() {{ btn.style.background = 'rgba(255,255,255,0.08)'; }};
            btn.onmouseleave = function() {{ btn.style.background = 'transparent'; }};
            btn.onclick = function() {{
                const selectors = [
                    '[data-testid="stSidebarCollapseButton"] button',
                    '[data-testid="stSidebarCollapseButton"]',
                    '[data-testid="stSidebarCollapsedControl"] button',
                    '[data-testid="stSidebarCollapsedControl"]',
                    'section[data-testid="stSidebar"] button[kind="header"]',
                    'button[aria-label="Close sidebar"]',
                    'button[aria-label="Open sidebar"]',
                ];
                for (const sel of selectors) {{
                    const el = doc.querySelector(sel);
                    if (el) {{ el.click(); return; }}
                }}
            }};

            const brand = doc.createElement('div');
            brand.style.cssText = `
                display: flex; align-items: center; gap: 8px;
                font-family: 'Inter', sans-serif; user-select: none;
            `;
            brand.innerHTML = `
                {logo_img_tag}
                <span style="font-weight:800; font-size:15px;
                    background:linear-gradient(90deg,#93c5fd,#34d399);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                    {APP_NAME}
                </span>
            `;

            header.appendChild(btn);
            header.appendChild(brand);
            doc.body.appendChild(header);
        }})();
        </script>
        """,
        height=1,
        width=1,
    )


# ── Sidebar ──────────────────────────────────────────────────────
render_top_masthead()

with st.sidebar:
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