# New Update 
"""
theme.py
--------
Unified Design System for JobFit AI.

Single source of truth for the entire application's visual identity.
Every page calls `apply_custom_css()` once (via app.py) — no per-page CSS.

To change the app's appearance globally, edit only this file.

Sections:
    1. Design Tokens          — CSS custom properties
    2. Global Base            — Background, layout, sidebar
    3. Typography             — Font imports, heading hierarchy
    4. Animations             — Shared keyframes and utility classes
    5. Hero Component         — Full-width gradient banner
    6. Card Components        — Glass, stat, feature, job, question
    7. Section Headings       — Consistent title + subtitle
    8. Chips & Badges         — Inline tags for skills, difficulty, type
    9. Banners                — Info, success, warning, error
   10. Empty State            — No-data placeholder with CTA
   11. Next Step CTA          — Workflow navigation banner
   12. Skill Bars             — Horizontal progress indicators
   13. Leaderboard            — Interactive role list (Home)
   14. Timeline & Stepper     — Week-based roadmap (Learning)
   15. Interview Components   — Question cards, answer/feedback boxes
   16. Streamlit Overrides    — Buttons, inputs, tabs, metrics, progress
"""

import streamlit as st


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PUBLIC HELPERS — Reusable UI functions called by view pages
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def render_job_chip(text: str, variant: str = "default") -> str:
    """Return an HTML chip string for a skill tag.

    Args:
        text:    Skill or label text.
        variant: "default" | "warning" | "success"

    Returns:
        HTML string — combine multiple and pass to st.markdown().
    """
    cls = {
        "warning": "rm-chip rm-chip-warning",
        "success": "rm-chip rm-chip-success",
        "danger":  "rm-chip rm-chip-danger",
    }.get(variant, "rm-chip")
    return f'<span class="{cls}">{text}</span>'


def render_job_card(rank: int, job_title: str, location: str, salary_txt: str,
                    growth: str, score: int, color: str, badge: str,
                    is_best: bool, required_chips: str, missing_chips: str,
                    insight: str, apply_link: str = "", description: str = ""):
    """Render a single job recommendation card.

    All HTML is built inside theme.py so career.py stays logic-only.
    CSS classes are guaranteed to be injected (via apply_custom_css in app.py).

    Args:
        rank:           Job rank number (1, 2, 3 ...)
        job_title:      Job title string
        location:       Location string
        salary_txt:     Salary display string
        growth:         Growth outlook text
        score:          Match score (int 0-100)
        color:          Score color hex string
        badge:          Badge label ("Good Match" etc.)
        is_best:        True if this is the #1 best match
        required_chips: Pre-built HTML string of required skill chips
        missing_chips:  Pre-built HTML string of missing skill chips
        insight:        AI recommendation text
        apply_link:     Job apply URL (optional)
        description:    Short job description (optional)
    """
    card_class   = "rm-job-card best" if is_best else "rm-job-card"
    best_badge   = '<div class="rm-best-badge">🏆 Best Match</div>' if is_best else ""

    safe_title   = job_title.replace('"', '&quot;').replace("'", "&#39;")
    safe_insight = insight.replace('"', '&quot;').replace("'", "&#39;")
    safe_desc    = description.replace('"', '&quot;').replace("'", "&#39;") if description else ""

    # Apply button HTML
    apply_html = (
        f'<a href="{apply_link}" target="_blank" style="' +
        'display:inline-block;margin-top:14px;padding:8px 20px;' +
        'background:linear-gradient(90deg,#1d4ed8,#2563eb);color:#fff;' +
        'border-radius:20px;font-size:.85rem;font-weight:700;' +
        'text-decoration:none;border:1px solid rgba(147,197,253,0.4);">' +
        '🚀 Apply Now</a>'
    ) if apply_link else ""

    # Description HTML
    desc_html = (
        f'<div style="color:#9aa4c4;font-size:.88rem;line-height:1.5;' +
        f'margin-top:10px;padding:10px 14px;background:rgba(255,255,255,0.03);' +
        f'border-radius:8px;border:1px solid rgba(255,255,255,0.07);">' +
        f'📄 {safe_desc}</div>'
    ) if safe_desc else ""

    html = (
        f'<div class="{card_class}">' +
        best_badge +
        f'<div class="rm-job-head">' +
        f'<div style="flex:1;min-width:240px;">' +
        f'<div class="rm-job-title"><span class="rm-job-rank">{rank}.</span> {safe_title}</div>' +
        f'<div class="rm-job-meta">📍 <b>Location:</b> {location}</div>' +
        f'<div class="rm-job-meta">💰 <b>Salary:</b> {salary_txt}</div>' +
        f'<div class="rm-job-meta">📈 <b>Growth Outlook:</b> {growth}</div>' +
        f'</div>' +
        f'<div class="rm-score-box">' +
        f'<div class="rm-score-num" style="color:{color};">{score}%</div>' +
        f'<div class="rm-score-badge" style="color:{color};">{badge}</div>' +
        f'<div class="rm-score-track"><div class="rm-score-fill" style="width:{score}%;background:{color};"></div></div>' +
        f'</div>' +
        f'</div>' +
        desc_html +
        f'<div class="rm-job-meta" style="margin-top:14px;"><b>Required Skills:</b></div>' +
        f'<div style="margin:8px 0;">{required_chips}</div>' +
        f'<div class="rm-job-meta" style="margin-top:12px;"><b>Missing Skills:</b></div>' +
        f'<div style="margin:8px 0;">{missing_chips}</div>' +
        f'<div class="rm-info">💡 <b>AI Recommendation:</b> {safe_insight}</div>' +
        apply_html +
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_iv_band(level: str):
    """Render a difficulty band header (Easy / Medium / Hard)."""
    level_lower = level.lower()
    if "hard" in level_lower:
        cls, emoji = "rm-iv-band-hard", "🔴"
    elif "medium" in level_lower:
        cls, emoji = "rm-iv-band-medium", "🟡"
    else:
        cls, emoji = "rm-iv-band-easy", "🟢"
    st.markdown(
        f'<div class="rm-iv-band {cls}">{emoji} {level.upper()} QUESTIONS</div>',
        unsafe_allow_html=True,
    )


def render_iv_question_card(q_num: str, q_text: str, q_diff: str,
                             q_type: str, answer: str, tip: str):
    """Render a single interview question card with answer and tip.

    Args:
        q_num:  Question number label e.g. "Q1"
        q_text: The question text
        q_diff: Difficulty string e.g. "Easy", "Medium", "Hard"
        q_type: Type string e.g. "Technical", "HR", "Conceptual"
        answer: Answer text (empty string if none)
        tip:    Tip text (empty string if none)
    """
    # Difficulty badge
    dl = q_diff.lower()
    if "hard" in dl:
        diff_cls, card_border = "rm-iv-badge-hard", "#f87171"
    elif "medium" in dl:
        diff_cls, card_border = "rm-iv-badge-medium", "#f59e0b"
    else:
        diff_cls, card_border = "rm-iv-badge-easy", "#22c55e"

    # Type badge
    tl = q_type.lower()
    if "technical" in tl:
        type_cls = "rm-iv-badge-tech"
    elif "hr" in tl or "behavioral" in tl:
        type_cls = "rm-iv-badge-hr"
    else:
        type_cls = "rm-iv-badge-concept"

    diff_badge = f'<span class="rm-iv-badge {diff_cls}">{q_diff}</span>' if q_diff else ""
    type_badge = f'<span class="rm-iv-badge {type_cls}">{q_type}</span>' if q_type else ""

    answer_html = (
        f'<div class="rm-iv-answer">' +
        f'<div class="rm-iv-answer-label">✅ ANSWER</div>' +
        f'<div class="rm-iv-answer-text">{answer}</div>' +
        f'</div>'
    ) if answer.strip() else ""

    tip_html = (
        f'<div class="rm-iv-tip">' +
        f'<span style="font-size:14px;flex:none;">💡</span>' +
        f'<div class="rm-iv-tip-text">{tip}</div>' +
        f'</div>'
    ) if tip.strip() else ""

    html = (
        f'<div class="rm-iv-qcard" style="border-left-color:{card_border};">' +
        f'<div class="rm-iv-qnum">{q_num}</div>' +
        f'<div class="rm-iv-qtext">{q_text}</div>' +
        f'<div class="rm-iv-badges">{diff_badge}{type_badge}</div>' +
        answer_html +
        tip_html +
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_iv_panel(icon_html: str, title: str, desc: str):
    """Render an interview type info panel."""
    st.markdown(
        f'<div class="rm-iv-panel">' +
        f'<div class="rm-iv-panel-title">{icon_html} {title}</div>' +
        f'<div class="rm-iv-panel-desc">{desc}</div>' +
        f'</div>',
        unsafe_allow_html=True,
    )


def render_iv_page_header(icon_html: str, title: str, subtitle: str):
    """Render the Interview Preparation page header."""
    st.markdown(
        f'<div class="rm-iv-page-header">' +
        f'<div class="hicon">{icon_html}</div>' +
        f'<div><h1>{title}</h1><p>{subtitle}</p></div>' +
        f'</div>',
        unsafe_allow_html=True,
    )


def render_iv_stat_row(stats: list):
    """Render a row of stat boxes for resume info display.

    Args:
        stats: list of (key_label, value) tuples
    """
    boxes = "".join(
        f'<div class="rm-iv-statbox"><div class="k">{k}</div><div class="v">{v}</div></div>'
        for k, v in stats
    )
    st.markdown(
        f'<div class="rm-iv-statrow">{boxes}</div>',
        unsafe_allow_html=True,
    )

def apply_custom_css():
    """Inject the global design system CSS. Called once in app.py."""
    st.markdown(_CSS, unsafe_allow_html=True)


def render_hero(title: str, subtitle: str = "", particles: bool = False):
    """Render a consistent hero banner.

    Args:
        title:     Main heading (supports HTML/emoji).
        subtitle:  Description text below the heading.
        particles: Show floating particle decorations (Home page only).
    """
    particle_html = ""
    if particles:
        particle_html = (
            '<div class="particle p1"></div><div class="particle p2"></div>'
            '<div class="particle p3"></div><div class="particle p4"></div>'
            '<div class="particle p5"></div>'
        )
    st.markdown(
        f'<div class="rm-hero fade-up">{particle_html}'
        f'<h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def render_empty_state(icon: str, title: str, description: str,
                       cta_label: str = "", cta_page: str = ""):
    """Render a premium empty-state placeholder with optional CTA.

    Args:
        icon:        Emoji displayed prominently.
        title:       Bold heading.
        description: Explanatory text.
        cta_label:   Button text (omit to skip button).
        cta_page:    Navigation target page name.
    """
    st.markdown(
        f'<div class="rm-empty">'
        f'<div class="rm-empty-icon">{icon}</div>'
        f'<div class="rm-empty-title">{title}</div>'
        f'<div class="rm-empty-desc">{description}</div></div>',
        unsafe_allow_html=True,
    )
    if cta_label and cta_page:
        if st.button(f"🚀 {cta_label}", key=f"empty_{cta_page}", type="primary"):
            st.session_state["goto_page"] = cta_page
            st.rerun()


def render_next_step(emoji: str, label: str, target_page: str,
                     description: str = ""):
    """Render a workflow CTA banner guiding the user to the next step.

    Args:
        emoji:       Icon for the banner.
        label:       Name of the next page/step.
        target_page: Exact page name for navigation routing.
        description: Brief explanation of what the next step does.
    """
    st.markdown(
        f'<div class="rm-next-step">'
        f'<div class="rm-next-inner">'
        f'<span class="rm-next-icon">{emoji}</span>'
        f'<div><div class="rm-next-label">Next Step → {label}</div>'
        f'<div class="rm-next-desc">{description}</div></div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )
    if st.button(f"Continue to {label} →", key=f"next_{target_page}", type="primary"):
        st.session_state["goto_page"] = target_page
        st.rerun()


def section_heading(title: str, subtitle: str = ""):
    """Render a consistent section heading with optional subtitle."""
    html = f'<div class="rm-section-title">{title}</div>'
    if subtitle:
        html += f'<div class="rm-section-sub">{subtitle}</div>'
    st.markdown(html, unsafe_allow_html=True)


def spacer(height: int = 18):
    """Insert vertical whitespace between sections."""
    st.markdown(f"<div style='height:{height}px'></div>", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CSS — Single stylesheet for the entire application
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_CSS = """<style>

/* ================================================================
   1. DESIGN TOKENS
   ================================================================ */
:root {
    /* ── Backgrounds ─────────────────────────────────────────── */
    --rm-bg:           #05060f;
    --rm-surface:      rgba(255,255,255,0.04);
    --rm-surface-2:    rgba(255,255,255,0.06);

    /* ── Borders ─────────────────────────────────────────────── */
    --rm-border:       rgba(255,255,255,0.10);
    --rm-border-hover: rgba(147,197,253,0.60);

    /* ── Brand Colors ────────────────────────────────────────── */
    --rm-indigo:       #2563eb;
    --rm-purple:       #1d4ed8;
    --rm-pink:         #10b981;

    /* ── Gradients ───────────────────────────────────────────── */
    --rm-grad:         linear-gradient(120deg, #1d4ed8, #2563eb, #10b981, #1d4ed8);
    --rm-grad-text:    linear-gradient(90deg, #93c5fd, #34d399);
    --rm-grad-bar:     linear-gradient(90deg, #2563eb, #10b981);

    /* ── Text ────────────────────────────────────────────────── */
    --rm-text:         #e8ecf6;
    --rm-text-2:       #9aa4c4;
    --rm-text-3:       #8b95b8;

    /* ── Semantic Colors ─────────────────────────────────────── */
    --rm-success:      #4ade80;
    --rm-success-bg:   rgba(74,222,128,0.12);
    --rm-warning:      #facc15;
    --rm-warning-bg:   rgba(250,204,21,0.10);
    --rm-danger:       #f87171;
    --rm-danger-bg:    rgba(248,113,113,0.10);

    /* ── Spacing ─────────────────────────────────────────────── */
    --rm-space-xs:     4px;
    --rm-space-sm:     8px;
    --rm-space-md:     16px;
    --rm-space-lg:     24px;
    --rm-space-xl:     32px;

    /* ── Radius ──────────────────────────────────────────────── */
    --rm-radius-sm:    8px;
    --rm-radius-md:    14px;
    --rm-radius-lg:    20px;
    --rm-radius-xl:    28px;

    /* ── Shadows ─────────────────────────────────────────────── */
    --rm-shadow:       0 8px 40px rgba(0,0,0,0.35);
    --rm-glow:         0 0 34px rgba(37,99,235,0.55);
}


/* ================================================================
   2. GLOBAL BASE
   ================================================================ */
.stApp {
    background:
        radial-gradient(1200px 600px at 10% -10%, rgba(37,99,235,0.18), transparent 60%),
        radial-gradient(1000px 500px at 100% 0%,  rgba(16,185,129,0.14), transparent 55%),
        linear-gradient(160deg, #05060f 0%, #05111f 45%, #070b18 100%);
    color: var(--rm-text);
}
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding-top: 2.8rem;
    padding-bottom: 3rem;
    max-width: 1320px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0c0e1a 0%, #0a0c17 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}


/* ================================================================
   3. TYPOGRAPHY
   ================================================================ */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.rm-grad-heading {
    font-size: 1.5rem; font-weight: 800; margin-bottom: 14px;
    background: var(--rm-grad-text);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}


/* ================================================================
   4. ANIMATIONS
   ================================================================ */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(22px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes floatY {
    0%, 100% { transform: translateY(0); }
    50%      { transform: translateY(-16px); }
}
@keyframes gradientMove {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes glowPulse {
    0%, 100% { box-shadow: 0 0 18px rgba(37,99,235,0.35); }
    50%      { box-shadow: 0 0 38px rgba(37,99,235,0.65); }
}
@keyframes fillBar { from { width: 0%; } }

.fade-up { animation: fadeUp .65s ease both; }


/* ================================================================
   5. HERO COMPONENT
   ================================================================ */
.rm-hero {
    position: relative; overflow: hidden; text-align: center;
    border-radius: var(--rm-radius-xl);
    padding: 60px 44px; margin-bottom: 10px;
    background: var(--rm-grad); background-size: 300% 300%;
    animation: gradientMove 12s ease infinite, glowPulse 4s ease-in-out infinite;
}
.rm-hero h1 {
    font-size: 3rem; font-weight: 800; margin: 0;
    background: linear-gradient(90deg, #fff, #d1fae5);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -1.5px;
}
.rm-hero p {
    font-size: 1.15rem; color: #eef0ff; margin: 14px auto 0;
    font-weight: 300; max-width: 760px; line-height: 1.6;
}
/* Home hero variant — larger for landing page */
.rm-hero-lg { padding: 84px 40px; }
.rm-hero-lg h1 { font-size: 4.2rem; letter-spacing: -2px; }
.rm-hero-lg p  { font-size: 1.4rem; }
/* Floating particles (used in Home hero) */
.rm-hero .particle {
    position: absolute; border-radius: 50%;
    background: rgba(255,255,255,0.40);
    animation: floatY 6s ease-in-out infinite;
}
.rm-hero .p1 { width:14px; height:14px; left:8%;  top:30%; }
.rm-hero .p2 { width:10px; height:10px; left:25%; top:70%; animation-delay:1s; }
.rm-hero .p3 { width:18px; height:18px; left:70%; top:25%; animation-delay:2s; }
.rm-hero .p4 { width:8px;  height:8px;  left:85%; top:65%; animation-delay:1.5s; }
.rm-hero .p5 { width:12px; height:12px; left:50%; top:15%; animation-delay:.5s; }


/* ================================================================
   6. CARD COMPONENTS
   ================================================================ */

/* ── 6a. Glass Card — universal container ────────────────────── */
.rm-glass {
    background: var(--rm-surface);
    border: 1px solid var(--rm-border);
    backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
    border-radius: var(--rm-radius-lg);
    box-shadow: var(--rm-shadow);
    padding: 22px 24px;
    transition: transform .3s ease, box-shadow .3s ease, border-color .3s ease;
}
.rm-glass:hover {
    transform: translateY(-6px);
    box-shadow: var(--rm-glow);
    border-color: var(--rm-border-hover);
}

/* ── 6b. Stat Card — KPI display ─────────────────────────────── */
.rm-stat {
    background: var(--rm-surface);
    border: 1px solid var(--rm-border);
    backdrop-filter: blur(16px);
    border-radius: var(--rm-radius-lg);
    padding: 20px 22px;
    box-shadow: var(--rm-shadow);
    transition: transform .3s ease, box-shadow .3s ease, border-color .3s ease;
}
.rm-stat:hover {
    transform: translateY(-6px);
    box-shadow: var(--rm-glow);
    border-color: var(--rm-border-hover);
}
.rm-stat-label {
    color: var(--rm-text-2); font-size: .78rem;
    text-transform: uppercase; letter-spacing: .06em;
    margin-bottom: 6px;
}
.rm-stat-value {
    font-size: 1.3rem; font-weight: 800;
    background: var(--rm-grad-text);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}

/* ── 6c. Stat Pill — inline key-value row ────────────────────── */
.rm-stat-pill {
    display: flex; justify-content: space-between;
    padding: 16px 18px; border-radius: var(--rm-radius-md);
    background: var(--rm-surface);
    border: 1px solid var(--rm-border);
    margin-bottom: 12px;
}
.rm-stat-pill .v { font-weight: 800; color: #34d399; }

/* ── 6d. Feature Card — icon + title + description ───────────── */
.rm-feature-card {
    padding: 26px 22px; border-radius: var(--rm-radius-lg);
    min-height: 200px; margin-bottom: 18px;
    transition: transform .3s ease, box-shadow .3s ease, border-color .3s ease;
}
.rm-feature-card:hover {
    transform: translateY(-8px);
    box-shadow: var(--rm-glow);
    border-color: var(--rm-border-hover);
}
.rm-feature-icon  { font-size: 2.2rem; margin-bottom: 12px; }
.rm-feature-title { font-weight: 700; font-size: 1.15rem; margin-bottom: 8px; color: #eef0ff; }
.rm-feature-desc  { color: var(--rm-text-2); font-size: .92rem; line-height: 1.5; }

/* ── 6e. Job Card — career recommendation result ─────────────── */
.rm-job-card {
    padding: 24px 26px; border-radius: var(--rm-radius-lg); margin-bottom: 18px;
    background: var(--rm-surface); border: 1px solid var(--rm-border);
    backdrop-filter: blur(16px); box-shadow: var(--rm-shadow);
    transition: transform .3s ease, box-shadow .3s ease, border-color .3s ease;
}
.rm-job-card:hover {
    transform: translateY(-6px);
    box-shadow: var(--rm-glow);
    border-color: var(--rm-border-hover);
}
.rm-job-card.best {
    border-color: rgba(251,191,36,0.6);
    box-shadow: 0 0 30px rgba(251,191,36,0.25);
}
.rm-job-head  { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; flex-wrap: wrap; }
.rm-job-title { font-size: 1.3rem; font-weight: 800; color: #eef0ff; }
.rm-job-rank  { color: var(--rm-text-3); font-weight: 700; margin-right: 8px; }
.rm-job-meta  { color: var(--rm-text-2); font-size: .92rem; margin: 4px 0; }
.rm-job-meta b { color: #cfd6ee; }
.rm-best-badge {
    display: inline-block; font-weight: 800; font-size: .78rem;
    padding: 4px 12px; border-radius: 20px; margin-bottom: 8px;
    background: linear-gradient(90deg, #fbbf24, #f59e0b); color: #1a1206;
    box-shadow: 0 0 16px rgba(251,191,36,0.5);
}
.rm-score-box   { text-align: center; min-width: 130px; }
.rm-score-num   { font-size: 2rem; font-weight: 800; line-height: 1; }
.rm-score-badge { font-size: .78rem; font-weight: 700; margin-top: 2px; }
.rm-score-track { background: rgba(255,255,255,0.08); border-radius: 8px; height: 9px; overflow: hidden; margin-top: 8px; }
.rm-score-fill  { height: 100%; border-radius: 8px; animation: fillBar 1.1s cubic-bezier(.22,1,.36,1) both; }

/* ── 6f. Insight Card — metric highlight (Home) ──────────────── */
.rm-insight-card {
    padding: 22px; border-radius: var(--rm-radius-lg);
    text-align: center;
    transition: transform .3s ease, box-shadow .3s ease;
}
.rm-insight-card:hover { transform: translateY(-8px); box-shadow: var(--rm-glow); }
.rm-insight-card .lbl  { color: var(--rm-text-2); font-size: .9rem; letter-spacing: .5px; }
.rm-insight-card .name { font-weight: 700; font-size: 1.1rem; margin: 6px 0; }
.rm-insight-card .val  {
    font-size: 1.35rem; font-weight: 800;
    background: var(--rm-grad-text);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}


/* ================================================================
   7. SECTION HEADINGS
   ================================================================ */
.rm-section-title {
    font-size: 1.25rem; font-weight: 700;
    margin: 8px 0 12px; color: var(--rm-text);
}
.rm-section-sub {
    color: var(--rm-text-2); margin-bottom: 18px; font-size: .92rem;
}


/* ================================================================
   8. CHIPS & BADGES
   ================================================================ */

/* Chip — used for skills, tags, keywords */
.rm-chip {
    display: inline-block; padding: 6px 14px;
    border-radius: 20px; margin: 4px;
    font-size: .85rem; font-weight: 600;
    background: rgba(37,99,235,0.22); color: #dfe4f5;
    border: 1px solid rgba(147,197,253,0.25);
    transition: all .2s ease;
}
.rm-chip:hover { background: rgba(37,99,235,0.38); transform: translateY(-2px); }
.rm-chip-danger  { background: var(--rm-danger-bg);  color: #fda4af; border-color: rgba(244,63,94,0.30); }
.rm-chip-success { background: var(--rm-success-bg); color: var(--rm-success); border-color: rgba(74,222,128,0.30); }
.rm-chip-warning { background: var(--rm-warning-bg); color: var(--rm-warning); border-color: rgba(250,204,21,0.30); }

/* Badge — small inline label (interview difficulty/type) */
.rm-badge {
    display: inline-block; padding: 3px 10px;
    border-radius: 20px; font-size: .72rem; font-weight: 600;
    border: 1px solid currentColor;
}
.badge-row     { display: flex; gap: 8px; margin: 8px 0 0; flex-wrap: wrap; }
.badge-easy    { color: #22c55e; background: rgba(22,163,74,.12); }
.badge-medium  { color: #f59e0b; background: rgba(217,119,6,.12); }
.badge-hard    { color: #f87171; background: rgba(220,38,38,.12); }
.badge-tech    { color: #818cf8; background: rgba(129,140,248,.12); }
.badge-hr      { color: #34d399; background: rgba(52,211,153,.12); }
.badge-concept { color: #fb923c; background: rgba(251,146,60,.12); }


/* ================================================================
   9. BANNERS (Info / Success / Warning / Error)
   ================================================================ */
.rm-info {
    padding: 16px 20px; border-radius: var(--rm-radius-md); margin: 10px 0;
    background: rgba(37,99,235,0.10); border-left: 4px solid #818cf8;
    color: #dfe4f5; font-size: .95rem;
}
.rm-info b { color: #93c5fd; }

.rm-success-card {
    padding: 16px 20px; border-radius: var(--rm-radius-md); margin: 10px 0;
    background: linear-gradient(120deg, rgba(16,185,129,0.14), rgba(37,99,235,0.10));
    border: 1px solid rgba(52,211,153,0.35);
    color: #34d399; font-weight: 700;
}

.rm-warning-card {
    padding: 16px 20px; border-radius: var(--rm-radius-md); margin: 10px 0;
    background: var(--rm-warning-bg);
    border: 1px solid rgba(250,204,21,0.30);
    color: var(--rm-warning); font-weight: 600;
}

.rm-error-card {
    padding: 16px 20px; border-radius: var(--rm-radius-md); margin: 10px 0;
    background: var(--rm-danger-bg);
    border: 1px solid rgba(248,113,113,0.30);
    color: var(--rm-danger); font-weight: 600;
}


/* ================================================================
   10. EMPTY STATE
   ================================================================ */
.rm-empty {
    padding: 52px 36px; border-radius: var(--rm-radius-xl);
    text-align: center; margin: 16px 0;
    background: var(--rm-surface); border: 1px solid var(--rm-border);
    backdrop-filter: blur(16px); box-shadow: var(--rm-shadow);
    animation: fadeUp .65s ease both;
}
.rm-empty-icon  { font-size: 3.2rem; margin-bottom: 14px; }
.rm-empty-title { font-weight: 800; font-size: 1.35rem; color: var(--rm-text); margin-bottom: 8px; }
.rm-empty-desc  { color: var(--rm-text-2); font-size: .95rem; line-height: 1.6; }


/* ================================================================
   11. NEXT STEP CTA
   ================================================================ */
.rm-next-step {
    margin: 28px 0 10px; padding: 20px 24px;
    border-radius: var(--rm-radius-lg);
    background: linear-gradient(120deg, rgba(29,78,216,0.12), rgba(16,185,129,0.08));
    border: 1px solid rgba(147,197,253,0.30);
    transition: all .3s ease;
}
.rm-next-step:hover { border-color: var(--rm-border-hover); box-shadow: 0 0 24px rgba(37,99,235,0.3); }
.rm-next-inner { display: flex; align-items: center; gap: 16px; }
.rm-next-icon  { font-size: 1.8rem; flex: none; }
.rm-next-label { font-weight: 700; font-size: 1.05rem; color: var(--rm-text); }
.rm-next-desc  { color: var(--rm-text-2); font-size: .88rem; margin-top: 2px; }


/* ================================================================
   12. SKILL BARS
   ================================================================ */
.rm-skill-row  { margin-bottom: 14px; }
.rm-skill-head { display: flex; justify-content: space-between; font-size: .92rem; margin-bottom: 5px; }
.rm-skill-head .pct { color: #93c5fd; font-weight: 700; }
.rm-bar-bg   { background: rgba(255,255,255,0.07); border-radius: 10px; height: 12px; overflow: hidden; }
.rm-bar-fill {
    height: 100%; border-radius: 10px;
    background: var(--rm-grad-bar);
    animation: fillBar 1.2s cubic-bezier(.22,1,.36,1) both;
    box-shadow: 0 0 14px rgba(37,99,235,0.6);
}


/* ================================================================
   13. LEADERBOARD (Home page role list)
   ================================================================ */
.lb-item .stButton > button,
.lb-active .stButton > button {
    width: 100%; text-align: left; justify-content: flex-start;
    border-radius: var(--rm-radius-md); padding: 16px 18px; margin-bottom: 10px;
    font-weight: 700; font-size: 1rem; letter-spacing: .2px;
    transition: all .25s ease; white-space: nowrap;
}
.lb-item .stButton > button {
    background: var(--rm-surface);
    border: 1px solid var(--rm-border); color: #dfe4f5;
}
.lb-item .stButton > button:hover {
    transform: translateX(6px);
    border-color: rgba(37,99,235,0.55);
    box-shadow: 0 0 20px rgba(37,99,235,0.35);
    background: var(--rm-surface-2);
}
.lb-active .stButton > button {
    background: linear-gradient(120deg, rgba(29,78,216,0.45), rgba(16,185,129,0.30));
    border: 1px solid rgba(147,197,253,0.85); color: #fff;
    box-shadow: 0 0 26px rgba(37,99,235,0.55);
    transform: translateX(4px);
}


/* ================================================================
   14. TIMELINE & STEPPER (Learning page)
   ================================================================ */

/* Stepper dots */
.rm-stepper   { display: flex; align-items: center; justify-content: center; gap: 0; margin: 8px 0 26px; flex-wrap: wrap; }
.rm-step      { display: flex; flex-direction: column; align-items: center; min-width: 90px; }
.rm-step .dot {
    width: 42px; height: 42px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; color: #fff;
    background: linear-gradient(120deg, #2563eb, #0ea5e9);
    box-shadow: 0 0 18px rgba(37,99,235,0.6);
}
.rm-step .nm    { color: #cfd6ee; font-size: .82rem; margin-top: 8px; font-weight: 600; }
.rm-step-line   { height: 3px; width: 48px; background: var(--rm-grad-bar); border-radius: 3px; margin: 0 -2px 26px; }

/* Vertical timeline */
.rm-tl-week { position: relative; padding-left: 42px; margin-bottom: 24px; }
.rm-tl-week:before {
    content: ''; position: absolute; left: 18px; top: 38px; bottom: -24px;
    width: 2px; background: linear-gradient(180deg, #2563eb, #0ea5e9);
}
.rm-tl-week:last-child:before { display: none; }
.rm-tl-head { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.rm-tl-badge {
    position: absolute; left: 0; width: 38px; height: 38px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; color: #fff;
    background: linear-gradient(120deg, #2563eb, #0ea5e9);
    box-shadow: 0 0 18px rgba(37,99,235,0.6);
}
.rm-tl-title {
    font-size: 1.2rem; font-weight: 800;
    background: var(--rm-grad-text);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.rm-tl-body {
    padding: 20px 24px; border-radius: 18px;
    transition: transform .3s ease, box-shadow .3s ease;
}
.rm-tl-body:hover   { transform: translateY(-4px); box-shadow: 0 0 30px rgba(37,99,235,0.45); }
.rm-tl-body h3      { color: #93c5fd; font-size: 1.02rem; margin-top: 14px; }
.rm-tl-body strong  { color: #c4b5fd; }
.rm-tl-body a       { color: #818cf8; }

/* Roadmap fallback (when weekly parsing fails) */
.rm-roadmap-wrap { padding: 26px 30px; border-radius: 22px; margin-top: 6px; }
.rm-roadmap-wrap h2 {
    border-left: 4px solid #818cf8; padding-left: 12px; margin-top: 22px;
    background: var(--rm-grad-text);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.rm-roadmap-wrap strong { color: #93c5fd; }


/* ================================================================
   15. INTERVIEW COMPONENTS
   ================================================================ */

/* Page header */
.rm-iv-header {
    background: var(--rm-surface); border: 1px solid var(--rm-border);
    border-radius: var(--rm-radius-lg); padding: 28px 30px; margin-bottom: 18px;
    display: flex; align-items: center; gap: 16px;
    animation: fadeUp .65s ease both;
}
.rm-iv-header .icon {
    width: 48px; height: 48px; border-radius: 12px; flex: none;
    display: flex; align-items: center; justify-content: center;
    background: rgba(29,78,216,0.12); color: var(--rm-indigo);
}
.rm-iv-header h1 { color: var(--rm-text); margin: 0; font-size: 1.5rem; font-weight: 700; letter-spacing: -.01em; }
.rm-iv-header p  { color: var(--rm-text-2); margin: 4px 0 0; font-size: .92rem; }

/* Stat row */
.rm-iv-stat {
    background: var(--rm-surface); border: 1px solid var(--rm-border);
    border-radius: var(--rm-radius-lg); padding: 16px 18px;
    transition: border-color .18s ease, transform .18s ease;
}
.rm-iv-stat:hover { border-color: var(--rm-indigo); transform: translateY(-2px); }
.rm-iv-stat .k {
    display: flex; align-items: center; gap: 6px; color: var(--rm-text-2);
    font-size: .72rem; text-transform: uppercase; letter-spacing: .06em;
}
.rm-iv-stat .v { color: var(--rm-text); font-size: 1.25rem; font-weight: 700; margin-top: 6px; }

/* Info box */
.rm-iv-info {
    background: var(--rm-surface); border: 1px solid var(--rm-border);
    border-left: 3px solid var(--rm-indigo);
    border-radius: var(--rm-radius-md); padding: 16px 18px; margin: 8px 0;
}
.rm-iv-info .t { display: flex; align-items: center; gap: 8px; color: var(--rm-text); font-weight: 600; }
.rm-iv-info .d { color: var(--rm-text-2); font-size: .88rem; margin-top: 4px; }

/* Difficulty bands */
.rm-band { border-radius: 10px; padding: 12px 16px; margin: 20px 0 8px; font-weight: 700; font-size: 1rem; }
.band-easy   { background: rgba(22,163,74,.12);  color: #22c55e; border-left: 4px solid #22c55e; }
.band-medium { background: rgba(217,119,6,.12);  color: #f59e0b; border-left: 4px solid #f59e0b; }
.band-hard   { background: rgba(220,38,38,.12);  color: #f87171; border-left: 4px solid #f87171; }

/* Question card */
.rm-q-card {
    background: var(--rm-surface-2); border: 1px solid var(--rm-border);
    border-left: 4px solid var(--rm-indigo);
    border-radius: var(--rm-radius-md); padding: 16px 18px; margin: 10px 0 4px;
    animation: fadeUp .5s ease both;
}
.rm-q-number { color: var(--rm-indigo); font-size: .8rem; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; margin-bottom: 4px; }
.rm-q-text   { color: var(--rm-text); font-size: 1rem; font-weight: 600; line-height: 1.5; }

/* Answer box */
.rm-answer-box {
    background: rgba(22,163,74,.06); border: 1px solid rgba(22,163,74,.2);
    border-radius: var(--rm-radius-sm); padding: 12px 16px; margin: 10px 0 6px;
}
.rm-answer-label { color: #22c55e; font-size: .75rem; font-weight: 700; letter-spacing: .04em; margin-bottom: 6px; }
.rm-answer-text  { color: #d1fae5; font-size: .92rem; line-height: 1.7; }

/* Tip box */
.rm-tip-box {
    background: rgba(251,191,36,.06); border: 1px solid rgba(251,191,36,.2);
    border-radius: var(--rm-radius-sm); padding: 10px 14px; margin: 4px 0 8px;
    display: flex; gap: 8px; align-items: flex-start;
}
.rm-tip-icon { color: #fbbf24; font-size: 14px; flex: none; margin-top: 1px; }
.rm-tip-text { color: #fde68a; font-size: .88rem; line-height: 1.6; }

/* Feedback box */
.rm-fb-box {
    background: var(--rm-surface-2); border: 1px solid var(--rm-border);
    border-left: 4px solid var(--rm-indigo);
    border-radius: var(--rm-radius-md); padding: 14px 16px; margin: 10px 0;
}
.rm-fb-text { color: var(--rm-text); font-size: .92rem; line-height: 1.6; }


/* ================================================================
   17. INTERVIEW QUESTION CARDS
   ================================================================ */

/* Difficulty band headers */
.rm-iv-band {
    border-radius: 10px; padding: 12px 18px;
    margin: 24px 0 12px; font-weight: 700; font-size: 1rem;
    display: flex; align-items: center; gap: 8px;
}
.rm-iv-band-easy   { background: rgba(22,163,74,.12);  color: #22c55e; border-left: 4px solid #22c55e; }
.rm-iv-band-medium { background: rgba(217,119,6,.12);  color: #f59e0b; border-left: 4px solid #f59e0b; }
.rm-iv-band-hard   { background: rgba(220,38,38,.12);  color: #f87171; border-left: 4px solid #f87171; }

/* Individual question card */
.rm-iv-qcard {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.10);
    border-left: 4px solid #2563eb;
    border-radius: 14px; padding: 20px 22px;
    margin: 10px 0 6px;
    animation: fadeUp .4s ease both;
}
.rm-iv-qnum {
    color: #2563eb; font-size: .78rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: .06em; margin-bottom: 6px;
}
.rm-iv-qtext {
    color: #e8ecf6; font-size: 1rem; font-weight: 600;
    line-height: 1.5; margin-bottom: 10px;
}
.rm-iv-badges { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px; }
.rm-iv-badge {
    display: inline-block; padding: 3px 10px;
    border-radius: 20px; font-size: .72rem; font-weight: 600;
    border: 1px solid currentColor;
}
.rm-iv-badge-easy    { color: #22c55e; background: rgba(22,163,74,.12); }
.rm-iv-badge-medium  { color: #f59e0b; background: rgba(217,119,6,.12); }
.rm-iv-badge-hard    { color: #f87171; background: rgba(220,38,38,.12); }
.rm-iv-badge-tech    { color: #818cf8; background: rgba(129,140,248,.12); }
.rm-iv-badge-hr      { color: #34d399; background: rgba(52,211,153,.12); }
.rm-iv-badge-concept { color: #fb923c; background: rgba(251,146,60,.12); }

/* Answer box */
.rm-iv-answer {
    background: rgba(22,163,74,.06);
    border: 1px solid rgba(22,163,74,.20);
    border-radius: 10px; padding: 14px 16px; margin-top: 10px;
}
.rm-iv-answer-label {
    color: #22c55e; font-size: .74rem; font-weight: 700;
    letter-spacing: .05em; margin-bottom: 6px;
}
.rm-iv-answer-text { color: #d1fae5; font-size: .9rem; line-height: 1.7; }

/* Tip box */
.rm-iv-tip {
    background: rgba(251,191,36,.06);
    border: 1px solid rgba(251,191,36,.18);
    border-radius: 10px; padding: 10px 14px;
    margin-top: 8px; display: flex; gap: 8px; align-items: flex-start;
}
.rm-iv-tip-text { color: #fde68a; font-size: .88rem; line-height: 1.6; }

/* Info panel (interview type description) */
.rm-iv-panel {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.10);
    border-left: 3px solid #2563eb;
    border-radius: 12px; padding: 16px 18px; margin: 8px 0;
}
.rm-iv-panel-title { display: flex; align-items: center; gap: 8px; color: #e8ecf6; font-weight: 600; }
.rm-iv-panel-desc  { color: #9aa4c4; font-size: .88rem; margin-top: 4px; }

/* Page header */
.rm-iv-page-header {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 16px; padding: 28px 30px; margin-bottom: 18px;
    display: flex; align-items: center; gap: 16px;
}
.rm-iv-page-header .hicon {
    width: 48px; height: 48px; border-radius: 12px; flex: none;
    display: flex; align-items: center; justify-content: center;
    background: rgba(37,99,235,0.15); color: #2563eb;
}
.rm-iv-page-header h1 { color: #e8ecf6; margin: 0; font-size: 1.5rem; font-weight: 700; }
.rm-iv-page-header p  { color: #9aa4c4; margin: 4px 0 0; font-size: .92rem; }

/* Resume stat row */
.rm-iv-statrow { display: flex; gap: 14px; margin: 8px 0 4px; flex-wrap: wrap; }
.rm-iv-statbox {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.10);
    border-radius: 12px; padding: 14px 18px; flex: 1; min-width: 120px;
    transition: border-color .18s ease;
}
.rm-iv-statbox:hover { border-color: #2563eb; }
.rm-iv-statbox .k { color: #9aa4c4; font-size: .72rem; text-transform: uppercase; letter-spacing: .06em; }
.rm-iv-statbox .v { color: #e8ecf6; font-size: 1.2rem; font-weight: 700; margin-top: 4px; }

/* ================================================================
   18. HOME PAGE COMPONENTS
   ================================================================ */

/* Hero — large landing variant */
.hero {
    position: relative; border-radius: 28px; padding: 84px 40px; overflow: hidden;
    background: var(--rm-grad); background-size: 300% 300%;
    animation: gradientMove 12s ease infinite, glowPulse 4s ease-in-out infinite;
    text-align: center; margin-top: 8px;
}
.hero h1 {
    font-size: 4.2rem; font-weight: 800; margin: 0;
    background: linear-gradient(90deg, #fff, #d1fae5);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -2px;
}
.hero p { font-size: 1.4rem; color: #eef0ff; margin-top: 16px; font-weight: 300; }

/* Glass utility */
.glass {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.10);
    backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
    border-radius: 20px; box-shadow: var(--rm-shadow);
}

/* Section titles */
.section-title { font-size: 1.7rem; font-weight: 700; margin: 22px 0 4px; }
.section-sub   { color: var(--rm-text-3); margin-bottom: 20px; }

/* Skill bars */
.skill-row  { margin-bottom: 14px; }
.skill-head { display: flex; justify-content: space-between; font-size: .92rem; margin-bottom: 5px; }
.skill-head .pct { color: #93c5fd; font-weight: 700; }
.bar-bg   { background: rgba(255,255,255,0.07); border-radius: 10px; height: 12px; overflow: hidden; }
.bar-fill {
    height: 100%; border-radius: 10px; background: var(--rm-grad-bar);
    animation: fillBar 1.2s cubic-bezier(.22,1,.36,1) both;
    box-shadow: 0 0 14px rgba(37,99,235,0.6);
}

/* Insight banner */
.insight {
    padding: 18px 22px; border-radius: 16px; margin-top: 16px;
    background: rgba(37,99,235,0.10);
    border-left: 4px solid #818cf8;
    font-size: 1rem; color: #dfe4f5;
}

/* Stat pill */
.stat-pill {
    display: flex; justify-content: space-between;
    padding: 16px 18px; border-radius: 14px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 12px;
}
.stat-pill .v { font-weight: 800; color: #34d399; }

/* Detail heading */
.detail-head {
    font-size: 1.5rem; font-weight: 800; margin-bottom: 14px;
    background: var(--rm-grad-text);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}

/* Feature cards (Why JobFit section) */
.feature-card {
    padding: 26px 22px; border-radius: 20px; min-height: 200px; margin-bottom: 20px;
    transition: transform .3s ease, box-shadow .3s ease, border-color .3s ease;
}
.feature-card:hover {
    transform: translateY(-8px);
    box-shadow: var(--rm-glow);
    border-color: var(--rm-border-hover);
}
.feature-icon  { font-size: 2.2rem; margin-bottom: 12px; }
.feature-title { font-weight: 700; font-size: 1.15rem; margin-bottom: 8px; color: #eef0ff; }
.feature-desc  { color: var(--rm-text-2); font-size: .92rem; line-height: 1.5; }


/* ================================================================
   16. STREAMLIT WIDGET OVERRIDES
   ================================================================ */

/* ── Buttons: Primary ────────────────────────────────────────── */
.stButton > button[kind="primary"],
.stButton > button[type="primary"] {
    width: 100%; border-radius: var(--rm-radius-md);
    padding: .85rem 1.4rem; font-weight: 800; font-size: 1.02rem;
    border: 1px solid rgba(255,255,255,0.15); color: #fff;
    background: linear-gradient(90deg, #1d4ed8, #2563eb, #10b981);
    background-size: 200% 200%; transition: all .25s ease;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[type="primary"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 0 32px rgba(37,99,235,0.65);
    border-color: #93c5fd;
}

/* ── Buttons: Secondary ──────────────────────────────────────── */
.stButton > button:not([kind="primary"]):not([type="primary"]) {
    border-radius: var(--rm-radius-md);
    padding: .7rem 1.4rem; font-weight: 700;
    border: 1px solid rgba(255,255,255,0.15);
    background: linear-gradient(90deg, #1d4ed8, #2563eb); color: #fff;
    transition: all .25s ease;
}
.stButton > button:not([kind="primary"]):not([type="primary"]):hover {
    transform: translateY(-3px);
    box-shadow: 0 0 26px rgba(37,99,235,0.6);
    border-color: #93c5fd;
}

/* ── Download Button ─────────────────────────────────────────── */
.stDownloadButton > button {
    border-radius: var(--rm-radius-md);
    padding: .7rem 1.4rem; font-weight: 700;
    background: var(--rm-surface);
    border: 1px solid rgba(147,197,253,0.40); color: var(--rm-text);
    transition: all .25s ease;
}
.stDownloadButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 0 24px rgba(37,99,235,0.5);
    border-color: #93c5fd;
}

/* ── Text Inputs / Selects / Text Areas ──────────────────────── */
.stSelectbox div[data-baseweb="select"] > div,
.stTextArea textarea,
.stTextInput input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
    color: var(--rm-text) !important;
}

/* ── Radio Pills ─────────────────────────────────────────────── */
div[role="radiogroup"] { gap: 14px; }
div[role="radiogroup"] label {
    background: var(--rm-surface); border: 1px solid var(--rm-border);
    padding: 14px 22px; border-radius: var(--rm-radius-md);
    transition: all .25s ease; font-weight: 600;
}
div[role="radiogroup"] label:hover {
    transform: translateY(-3px);
    border-color: rgba(37,99,235,0.5);
    box-shadow: 0 0 18px rgba(37,99,235,0.3);
}
div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(120deg, rgba(29,78,216,0.45), rgba(16,185,129,0.30));
    border: 1px solid rgba(147,197,253,0.85);
    box-shadow: 0 0 26px rgba(37,99,235,0.55);
}

/* ── File Uploader ───────────────────────────────────────────── */
[data-testid="stFileUploader"] section {
    background: rgba(255,255,255,0.03);
    border: 1.5px dashed rgba(147,197,253,0.40);
    border-radius: 16px; padding: 18px; transition: all .25s ease;
}
[data-testid="stFileUploader"] section:hover {
    border-color: rgba(147,197,253,0.85);
    box-shadow: 0 0 24px rgba(37,99,235,0.3);
}

/* ── Tabs ────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] {
    background: var(--rm-surface); border: 1px solid var(--rm-border);
    border-radius: 12px; padding: 6px 16px; color: #cfd6ee;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(120deg, rgba(29,78,216,0.4), rgba(16,185,129,0.25)) !important;
    border: 1px solid rgba(147,197,253,0.7) !important; color: #fff !important;
}

/* ── Metrics ─────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--rm-surface); border: 1px solid var(--rm-border);
    border-radius: var(--rm-radius-lg); padding: 18px 22px;
    box-shadow: var(--rm-shadow);
}

/* ── Progress Bar ────────────────────────────────────────────── */
.stProgress > div > div > div > div {
    background: var(--rm-grad-bar) !important;
    border-radius: 10px;
}

/* ── Divider ─────────────────────────────────────────────────── */
hr { border-color: rgba(255,255,255,0.06) !important; }

/* ── Hide sidebar collapse/expand arrows ────────────────────── */
/* Prevents users from accidentally collapsing the sidebar       */
[data-testid="collapsedControl"] { display: none !important; }
button[data-testid="baseButton-header"] { display: none !important; }


/* ================================================================
   13. LEARNING PATH COMPONENTS
   ================================================================ */

/* Summary cards (Target Role / Experience / Missing Skills) */
.lp-sum-card {
    padding: 20px 22px; border-radius: var(--rm-radius-lg);
    transition: transform .3s ease, box-shadow .3s ease;
    background: var(--rm-surface); border: 1px solid var(--rm-border);
    backdrop-filter: blur(16px); box-shadow: var(--rm-shadow);
}
.lp-sum-card:hover {
    transform: translateY(-8px); box-shadow: var(--rm-glow);
    border-color: var(--rm-border-hover);
}
.lp-sum-card .ic { font-size: 1.6rem; }
.lp-sum-card .lbl { color: var(--rm-text-2); font-size: .85rem; margin-top: 6px; letter-spacing: .4px; }
.lp-sum-card .val {
    font-weight: 800; font-size: 1.15rem; margin-top: 4px;
    background: var(--rm-grad-text);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}

/* Recommended skills card */
.lp-rec-card {
    padding: 20px 22px; border-radius: var(--rm-radius-lg); margin-top: 10px;
    background: rgba(37,99,235,0.08); border: 1px solid rgba(147,197,253,0.25);
}
.lp-rec-title { font-weight: 700; color: #a5b4fc; margin-bottom: 12px; font-size: 1.05rem; }
.lp-skill-chip {
    display: inline-block; background: rgba(37,99,235,0.22); color: var(--rm-text);
    padding: 7px 16px; border-radius: 20px; margin: 5px; font-size: .88rem; font-weight: 600;
    border: 1px solid rgba(165,180,252,0.25); transition: all .2s ease;
}
.lp-skill-chip:hover { background: rgba(37,99,235,0.4); transform: translateY(-2px); }

/* Success confirmation card */
.lp-succ-card {
    padding: 18px 22px; border-radius: var(--rm-radius-md); margin-top: 14px;
    background: linear-gradient(120deg, var(--rm-success-bg), rgba(37,99,235,0.10));
    border: 1px solid rgba(74,222,128,0.35);
}
.lp-succ-card .t { font-weight: 700; color: var(--rm-success); }
.lp-succ-card .d { color: var(--rm-text-2); font-size: .9rem; margin-top: 4px; }

/* Section title (local alias of rm-section-title for this page) */
.lp-section-title { font-size: 1.25rem; font-weight: 700; margin: 8px 0 12px; color: var(--rm-text); }

/* Hero variant for Learning Path (reuses .rm-hero, no extra rules needed) */

/* Segmented radio (mode selector) */
div[role="radiogroup"] { gap: 14px; }
div[role="radiogroup"] label {
    background: var(--rm-surface); border: 1px solid var(--rm-border);
    padding: 14px 22px; border-radius: var(--rm-radius-md); transition: all .25s ease; font-weight: 600;
}
div[role="radiogroup"] label:hover {
    transform: translateY(-3px); border-color: rgba(37,99,235,0.5); box-shadow: 0 0 18px rgba(37,99,235,0.3);
}
div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(120deg, rgba(29,78,216,0.45), rgba(16,185,129,0.30));
    border: 1px solid var(--rm-border-hover); box-shadow: var(--rm-glow);
}

/* Roadmap stepper */
.lp-stepper { display: flex; align-items: center; justify-content: center; gap: 0; margin: 8px 0 26px; flex-wrap: wrap; }
.lp-step { display: flex; flex-direction: column; align-items: center; min-width: 90px; }
.lp-step .dot {
    width: 42px; height: 42px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-weight: 800; color: #fff; background: var(--rm-grad-bar); box-shadow: var(--rm-glow);
}
.lp-step .nm { color: var(--rm-text); font-size: .82rem; margin-top: 8px; font-weight: 600; }
.lp-step-line { height: 3px; width: 48px; background: var(--rm-grad-bar); border-radius: 3px; margin: 0 -2px 26px; }

/* Roadmap fallback container (used with .glass) */
.lp-roadmap-wrap { padding: 26px 30px; border-radius: var(--rm-radius-xl); margin-top: 6px; }
.lp-roadmap-wrap h2 {
    border-left: 4px solid #818cf8; padding-left: 12px; margin-top: 22px;
    background: var(--rm-grad-text);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.lp-roadmap-wrap strong { color: #a5b4fc; }

/* Roadmap vertical timeline */
.lp-tl-week { position: relative; padding-left: 42px; margin-bottom: 24px; }
.lp-tl-week:before {
    content: ''; position: absolute; left: 18px; top: 38px; bottom: -24px;
    width: 2px; background: var(--rm-grad-bar);
}
.lp-tl-week:last-child:before { display: none; }
.lp-tl-badge {
    position: absolute; left: 0; width: 38px; height: 38px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center; font-weight: 800; color: #fff;
    background: var(--rm-grad-bar); box-shadow: var(--rm-glow);
}
.lp-tl-week-title {
    font-size: 1.15rem; font-weight: 800; margin-bottom: 12px;
    background: var(--rm-grad-text);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.lp-tl-week-body {
    background: var(--rm-surface); border: 1px solid var(--rm-border);
    backdrop-filter: blur(16px); border-radius: var(--rm-radius-lg);
    padding: 22px 26px; box-shadow: var(--rm-shadow); transition: transform .3s ease;
}
.lp-tl-week-body h3, .lp-tl-week-body h4 { color: #a5b4fc; margin: 14px 0 6px; }
.lp-tl-week-body strong { color: #c4b5fd; }
.lp-tl-week-body a { color: #818cf8; }
.lp-tl-week-body p, .lp-tl-week-body li { color: var(--rm-text-2); line-height: 1.6; }
.lp-tl-connector { margin-left: 60px; width: 2px; height: 24px; background: var(--rm-grad-bar); }

/* Real resource cards (YouTube / course results fetched via live API) */
.lp-res-wrap { margin-top: 14px; display: flex; flex-direction: column; gap: 8px; }
.lp-res-card {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 14px; border-radius: var(--rm-radius-sm);
    background: var(--rm-surface-2); border: 1px solid var(--rm-border);
    text-decoration: none; transition: all .2s ease;
}
.lp-res-card:hover { border-color: var(--rm-border-hover); box-shadow: var(--rm-glow); transform: translateX(3px); }
.lp-res-card .tag {
    flex-shrink: 0; font-size: .7rem; font-weight: 800; letter-spacing: .4px;
    padding: 3px 9px; border-radius: 8px; text-transform: uppercase;
}
.lp-res-card .tag.yt { background: rgba(248,113,113,0.18); color: #fca5a5; }  /* YouTube Playlist */
.lp-res-card .tag.course { background: rgba(37,99,235,0.20); color: #93c5fd; }
.lp-res-card .info { min-width: 0; }
.lp-res-card .title {
    color: var(--rm-text); font-weight: 600; font-size: .9rem;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block;
}
.lp-res-card .src { color: var(--rm-text-3); font-size: .76rem; }
.lp-res-empty { color: var(--rm-text-3); font-size: .85rem; font-style: italic; margin-top: 8px; }

</style>
"""