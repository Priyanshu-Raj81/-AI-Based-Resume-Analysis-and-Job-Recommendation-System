import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

CSV_PATH = "dataset/career_trends.csv"
REQUIRED_COLUMNS = ["role", "growth_rate", "avg_salary_lpa", "job_openings", "skill", "skill_score"]


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH)
    df.columns = [c.strip().lower() for c in df.columns]
    for col in ["growth_rate", "avg_salary_lpa", "job_openings", "skill_score"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "role" in df.columns:
        df["role"] = df["role"].astype(str).str.strip()
    if "skill" in df.columns:
        df["skill"] = df["skill"].astype(str).str.strip()
    return df.dropna(subset=[c for c in REQUIRED_COLUMNS if c in df.columns])


@st.cache_data(show_spinner=False)
def role_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("role")
        .agg(
            growth_rate=("growth_rate", "max"),
            avg_salary_lpa=("avg_salary_lpa", "max"),
            job_openings=("job_openings", "max"),
        )
        .reset_index()
        .sort_values("growth_rate", ascending=False)
        .reset_index(drop=True)
    )


@st.cache_data(show_spinner=False)
def role_skills(df: pd.DataFrame, role: str) -> pd.DataFrame:
    return (
        df[df["role"] == role][["skill", "skill_score"]]
        .sort_values("skill_score", ascending=False)
        .reset_index(drop=True)
    )


@st.cache_data(show_spinner=False)
def top_emerging_skills(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    return (
        df.groupby("skill")["skill_score"].mean()
        .reset_index()
        .sort_values("skill_score", ascending=False)
        .head(n)
        .reset_index(drop=True)
    )


@st.cache_data(show_spinner=False)
def build_insight(df: pd.DataFrame, role: str) -> str:
    skills = role_skills(df, role)["skill"].tolist()
    if not skills:
        return f"{role} is an emerging role in the current market."
    top = skills[:5]
    joined = top[0] if len(top) == 1 else ", ".join(top[:-1]) + f", and {top[-1]}"
    return f"{role} demand is primarily driven by {joined} expertise."


def init_state(roles):
    if "active_role" not in st.session_state or st.session_state["active_role"] not in roles:
        st.session_state["active_role"] = roles[0]


def hero():
    import os, base64, io
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")

    # ── Hero banner ──────────────────────────────────────────────
    st.markdown("""
    <style>
    .jf-hero {
        position: relative;
        border-radius: 28px;
        padding: 56px 44px 48px;
        overflow: hidden;
        background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 40%, #0ea5e9 70%, #10b981 100%);
        background-size: 200% 200%;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 0 12px 48px rgba(37,99,235,0.35);
    }
    .jf-hero h1 {
        font-size: 3rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0 0 12px;
        letter-spacing: -1.5px;
        text-shadow: 0 2px 16px rgba(0,0,0,0.18);
    }
    .jf-hero p {
        font-size: 1.1rem;
        color: rgba(255,255,255,0.88);
        margin: 0 auto;
        font-weight: 300;
        max-width: 600px;
        line-height: 1.6;
        letter-spacing: 0.2px;
    }
    .jf-tagline-dot { opacity: 0.6; margin: 0 6px; }
    </style>
    """, unsafe_allow_html=True)

    # Build logo img tag safely (no f-string with b64 to avoid brace issues)
    logo_tag = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        src = "data:image/png;base64," + b64
        logo_tag = (
            '<img src="' + src + '"'
            ' style="width:72px;height:72px;object-fit:contain;' 
            ' background:rgba(255,255,255,0.15);border-radius:16px;' 
            ' padding:10px;margin-bottom:18px;' 
            ' box-shadow:0 4px 20px rgba(0,0,0,0.20);" alt="JobFit AI">' 
        )

    hero_html = (
        '<div class="jf-hero fade-up">' +
        logo_tag +
        '<h1>JobFit AI</h1>' +
        '<p>Analyze Resume' + ' &rarr; ' + 'Match Jobs' + ' &rarr; ' + 
        'Build Skills' + ' &rarr; ' + 'Crack Interviews</p>' +
        '</div>'
    )
    st.markdown(hero_html, unsafe_allow_html=True)

    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)
    _, c, _ = st.columns([1.4, 1, 1.4])
    with c:
        if st.button("Analyze Resume", use_container_width=True):
            st.session_state["goto_page"] = "Resume Analyzer"
            st.rerun()


def kpis(df: pd.DataFrame):
    summary = role_summary(df)
    cards = [
        (int(df["skill"].nunique()), 0, "", "", "TOTAL SKILLS"),
        (int(df["role"].nunique()), 0, "", "", "CAREER PATHS"),
        (float(summary["avg_salary_lpa"].mean()), 1, "₹", " LPA", "AVG SALARY"),
        (int(summary["job_openings"].sum()), 0, "", "", "JOB OPENINGS"),
    ]
    boxes = "".join(
        f"""<div class="kpi glass">
                <div class="num" data-target="{val}" data-dec="{dec}" data-pre="{pre}" data-suf="{suf}">0</div>
                <div class="lbl">{lbl}</div>
            </div>"""
        for val, dec, pre, suf, lbl in cards
    )
    components.html(
        f"""
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap" rel="stylesheet">
        <style>
        body {{ margin:0; font-family:'Inter',sans-serif; }}
        .kpi-grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:20px; }}
        @media (max-width:900px) {{ .kpi-grid {{ grid-template-columns:repeat(2,1fr); }} }}
        .kpi {{ padding:28px 24px; border-radius:20px; text-align:center; transition:transform .3s ease, box-shadow .3s ease;
            background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.10); backdrop-filter:blur(16px);
            box-shadow:0 8px 40px rgba(0,0,0,0.35); }}
        .kpi:hover {{ transform:translateY(-8px); box-shadow:0 0 34px rgba(37,99,235,0.55); }}
        .num {{ font-size:2.3rem; font-weight:800; background:linear-gradient(90deg,#93c5fd,#34d399);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
        .lbl {{ color:#9aa4c4; font-size:.88rem; margin-top:8px; letter-spacing:.6px; }}
        </style>
        <div class="kpi-grid">{boxes}</div>
        <script>
        document.querySelectorAll('.num').forEach(function(el) {{
            const target = parseFloat(el.dataset.target);
            const dec = parseInt(el.dataset.dec);
            const pre = el.dataset.pre, suf = el.dataset.suf;
            const dur = 1400; const start = performance.now();
            function tick(now) {{
                let p = Math.min((now - start) / dur, 1);
                p = 1 - Math.pow(1 - p, 3);
                let cur = (target * p).toFixed(dec);
                el.textContent = pre + Number(cur).toLocaleString(undefined,
                    {{minimumFractionDigits:dec, maximumFractionDigits:dec}}) + suf;
                if (p < 1) requestAnimationFrame(tick);
            }}
            requestAnimationFrame(tick);
        }});
        </script>
        """,
        height=170,
    )


def skill_bars(skills: pd.DataFrame):
    for _, r in skills.iterrows():
        pct = max(0.0, min(100.0, float(r["skill_score"])))
        st.markdown(
            f"""
            <div class="skill-row">
                <div class="skill-head"><span>{r['skill']}</span><span class="pct">{pct:.0f}%</span></div>
                <div class="bar-bg"><div class="bar-fill" style="width:{pct}%"></div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def leaderboard(df: pd.DataFrame):
    summary = role_summary(df).head(10).reset_index(drop=True)

    st.markdown('<div class="section-title">Fastest Growing Roles</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Click a role to explore its market intelligence. Live from the dataset.</div>', unsafe_allow_html=True)

    left, right = st.columns([1, 1.2])

    with left:
        medals = {}
        active = st.session_state["active_role"]
        for i, r in summary.iterrows():
            mark = medals.get(i, "")
            prefix = f"{mark}  " if mark else ""
            label = f"{prefix}{r['role']}\u2002\u2002·\u2002\u2002+{r['growth_rate']:.0f}%"
            cls = "lb-active" if r["role"] == active else "lb-item"
            st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
            if st.button(label, key=f"lb_{r['role']}", use_container_width=True):
                st.session_state["active_role"] = r["role"]
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    with right:
        role = st.session_state["active_role"]
        info = summary[summary["role"] == role].iloc[0]

        st.markdown(f'<div class="detail-head">{role}</div>', unsafe_allow_html=True)
        st.markdown(f"""<div class="stat-pill"><span>Growth Rate</span><span class="v">+{info['growth_rate']:.0f}%</span></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="stat-pill"><span>Average Salary</span><span class="v">₹{info['avg_salary_lpa']:.0f} LPA</span></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="stat-pill"><span>Job Openings</span><span class="v">{int(info['job_openings']):,}</span></div>""", unsafe_allow_html=True)

        st.markdown("#### Skills Driving Demand")
        skill_bars(role_skills(df, role))
        st.markdown(f"""<div class="insight">{build_insight(df, role)}</div>""", unsafe_allow_html=True)


def market_insights(df: pd.DataFrame):
    summary = role_summary(df)
    top_skill = top_emerging_skills(df, 1).iloc[0]
    hg = summary.sort_values("growth_rate", ascending=False).iloc[0]
    hs = summary.sort_values("avg_salary_lpa", ascending=False).iloc[0]
    ho = summary.sort_values("job_openings", ascending=False).iloc[0]

    st.markdown('<div class="section-title">AI Market Insights</div>', unsafe_allow_html=True)
    st.markdown("""
    <style>
    .mi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 18px;
        margin-top: 14px;
    }
    .mi-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 18px;
        padding: 24px 20px;
        backdrop-filter: blur(16px);
        box-shadow: 0 8px 40px rgba(0,0,0,0.30);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }
    .mi-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 0 28px rgba(37,99,235,0.40);
        border-color: rgba(147,197,253,0.40);
    }
    .mi-label {
        color: #93c5fd;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .mi-name {
        color: #e8ecf6;
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 8px;
        line-height: 1.3;
    }
    .mi-val {
        background: linear-gradient(90deg, #93c5fd, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.4rem;
        font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)

    data = [
        ("Highest Growth", hg["role"], f"+{hg['growth_rate']:.0f}%"),
        ("Highest Salary", hs["role"], f"₹{hs['avg_salary_lpa']:.0f} LPA"),
        ("Most Openings", ho["role"], f"{int(ho['job_openings']):,}"),
        ("Most Demanded Skill", top_skill["skill"], f"{top_skill['skill_score']:.0f} avg"),
    ]

    cards_html = "".join(
        f'''<div class="mi-card">
            <div class="mi-label">{lbl}</div>
            <div class="mi-name">{name}</div>
            <div class="mi-val">{val}</div>
        </div>'''
        for lbl, name, val in data
    )
    st.markdown(f'<div class="mi-grid">{cards_html}</div>', unsafe_allow_html=True)


def skill_intelligence(df: pd.DataFrame):
    st.markdown('<div class="section-title">Top Emerging Skills</div>', unsafe_allow_html=True)
    skill_bars(top_emerging_skills(df, 5))


def learning_paths(df: pd.DataFrame):
    st.markdown('<div class="section-title">Learning Paths</div>', unsafe_allow_html=True)
    summary = role_summary(df).head(6)
    cols_per_row = 3
    rows = [summary.iloc[i:i + cols_per_row] for i in range(0, len(summary), cols_per_row)]
    for chunk in rows:
        cols = st.columns(cols_per_row)
        for col, (_, r) in zip(cols, chunk.iterrows()):
            chips = "".join(f"<span class='chip'>{s}</span>" for s in role_skills(df, r["role"])["skill"].head(4))
            col.markdown(
                f"""<div class="glass" style="padding:22px; min-height:180px; margin-bottom:18px;">
                        <div style="font-weight:700;font-size:1.15rem;">{r['role']}</div>
                        <div style="margin:10px 0;">{chips}</div>
                        <div style="color:#34d399;font-weight:700;font-size:.9rem;">+ {r['growth_rate']:.0f}% growth</div>
                        <div style="color:#9aa4c4;margin-top:6px;">₹{r['avg_salary_lpa']:.0f} LPA · {int(r['job_openings']):,} openings</div>
                    </div>""",
                unsafe_allow_html=True,
            )


def why_jobfit():
    st.markdown('<div class="section-title">Why JobFit AI?</div>', unsafe_allow_html=True)
    features = [
        ("", "Resume Analysis", "Extract structured information from resumes using AI-powered parsing."),
        ("", "ATS Score", "Evaluate resume compatibility with Applicant Tracking Systems."),
        ("", "Job Match", "Recommend the most suitable job opportunities based on resume skills."),
        ("", "Skill Gap Analysis", "Identify missing in-demand skills required for target roles."),
        ("", "Personalized Learning Path", "Generate a customized roadmap for career growth."),
        ("", "Interview Preparation", "Practice technical interviews using AI-powered guidance."),
    ]
    for row_start in range(0, len(features), 3):
        cols = st.columns(3)
        for col, (icon, title, desc) in zip(cols, features[row_start:row_start + 3]):
            col.markdown(
                f"""<div class="feature-card glass">
                        <div class="feature-title">{title}</div>
                        <div class="feature-desc">{desc}</div>
                    </div>""",
                unsafe_allow_html=True,
            )


def render_home():

    try:
        df = load_data()
    except FileNotFoundError:
        st.error(f"`{CSV_PATH}` not found. Add the dataset and reload.")
        return

    roles = role_summary(df)["role"].tolist()
    if not roles:
        st.error("No valid data available in career_trends.csv.")
        return
    init_state(roles)

    hero(); st.markdown("<br>", unsafe_allow_html=True)
    kpis(df); st.markdown("<br>", unsafe_allow_html=True)
    leaderboard(df); st.markdown("<br>", unsafe_allow_html=True)
    market_insights(df); st.markdown("<br>", unsafe_allow_html=True)
    skill_intelligence(df); st.markdown("<br>", unsafe_allow_html=True)
    learning_paths(df); st.markdown("<br>", unsafe_allow_html=True)
    why_jobfit()


if __name__ == "__main__":
    render_home()