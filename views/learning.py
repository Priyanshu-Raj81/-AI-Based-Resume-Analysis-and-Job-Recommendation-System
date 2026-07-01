# New Update

import re
import streamlit as st
from utils.ai_suggestions import generate_learning_path
from utils.pdf_export import generate_pdf
from utils.theme import render_hero, section_heading, spacer
from utils.resource_search import get_week_resources


def _extract_week_topics(body: str) -> list:
    """Pull the bullet items under '### Topics to Cover:' from a week's body text."""
    lines = body.split("\n")
    topics, capturing = [], False
    for line in lines:
        stripped = line.strip()
        if re.match(r'^#{2,3}\s*topics?\s*to\s*cover', stripped, re.I):
            capturing = True
            continue
        if capturing:
            if stripped.startswith("#"):  # next section started
                break
            if stripped.startswith("-") or stripped.startswith("*"):
                topics.append(stripped.lstrip("-* ").strip())
    return topics


def _resource_card_html(tag: str, title: str, url: str, source: str) -> str:
    tag_class    = "yt" if tag == "YT" else "course"
    tag_label    = "▶ PLAYLIST" if tag == "YT" else "📘 COURSE"
    # Truncate long titles so card stays single-line
    display_title = title[:72] + "…" if len(title) > 72 else title
    return (
        f'<a class="lp-res-card" href="{url}" target="_blank" rel="noopener noreferrer">'
        f'<span class="tag {tag_class}">{tag_label}</span>'
        f'<span class="info"><span class="title">{display_title}</span>'
        f'<span class="src">{source}</span></span></a>'
    )


def _build_resources_html(resources: dict) -> str:
    """
    Build resource cards HTML string — called INSIDE the week card HTML block
    so everything renders in one single st.markdown() call (avoids Streamlit's
    separate-element limitation that caused cards to float outside the week box).
    """
    skill = resources.get("skill", "")
    cards = []

    for v in resources.get("youtube", []):
        cards.append(_resource_card_html("YT", v["title"], v["url"], v["channel"]))
    for c in resources.get("courses", []):
        cards.append(_resource_card_html("COURSE", c["title"], c["url"], c["source"]))

    skill_label = f'<div style="font-size:.8rem;color:var(--rm-text-3);margin-bottom:6px;">📚 Resources for <b style="color:#a5b4fc;">{skill}</b></div>' if skill else '<div style="font-size:.8rem;color:var(--rm-text-3);margin-bottom:6px;">📚 Resources</div>'

    if cards:
        return f'<div class="lp-res-wrap">{skill_label}{"".join(cards)}</div>'

    fb = resources.get("fallback", {})
    return (
        f'<div class="lp-res-wrap">{skill_label}'
        f'<div class="lp-res-empty">No playlist found right now — '
        f'<a href="{fb.get("youtube","#")}" target="_blank">search on YouTube</a> or '
        f'<a href="{fb.get("courses","#")}" target="_blank">search courses</a>.</div></div>'
    )


def _resources_to_markdown(resources: dict) -> str:
    """Render a week's resources as markdown — used for the downloadable PDF."""
    lines = ["### 📚 Resources (live, verified):"]
    for v in resources.get("youtube", []):
        lines.append(f"- **YouTube:** [{v['title']}]({v['url']}) — {v['channel']}")
    for c in resources.get("courses", []):
        lines.append(f"- **Course:** [{c['title']}]({c['url']}) — {c['source']}")
    if len(lines) == 1:
        fb = resources.get("fallback", {})
        lines.append(f"- No exact match found — [search on YouTube]({fb.get('youtube', '')}) "
                      f"or [search courses]({fb.get('courses', '')})")
    return "\n".join(lines)


def _parse_roadmap_weeks(roadmap: str):
    """UI-only parser. Splits the markdown roadmap into week blocks.
    Does NOT modify backend output. Returns list of dicts."""
    if not roadmap:
        return []
    parts = re.split(r'(?m)^##\s*.*?Week\s*\d+[^\n]*', roadmap)
    headers = re.findall(r'(?m)^##\s*.*?(Week\s*\d+\s*:?[^\n]*)', roadmap)
    weeks = []
    bodies = parts[1:] if len(parts) > 1 else []
    for i, body in enumerate(bodies):
        title = headers[i].strip() if i < len(headers) else f"Week {i + 1}"
        body_clean = body.strip()
        # Strip duplicate title line AI sometimes repeats at top of body
        # e.g. ": Fundamentals of Java and Android Basics"
        body_clean = re.sub(r'^\s*:\s*[^\n]+\n', '', body_clean)
        weeks.append({"num": i + 1, "title": title, "body": body_clean.strip()})
    return weeks


def _md_to_html(text: str) -> str:
    """Convert basic markdown to HTML for inline rendering inside st.markdown blocks."""
    # Bold
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # Headings ### and ##
    text = re.sub(r'(?m)^###\s+(.*?)$', r'<h4>\1</h4>', text)
    text = re.sub(r'(?m)^##\s+(.*?)$',  r'<h3>\1</h3>', text)
    # Links [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', text)
    # Bullet lines starting with -
    lines = text.split("\n")
    out, in_ul = [], False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("* "):
            if not in_ul:
                out.append('<ul style="margin:6px 0 10px 18px;padding:0;">')
                in_ul = True
            out.append(f'<li>{stripped[2:]}</li>')
        else:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if stripped:
                out.append(f'<p>{stripped}</p>')
    if in_ul:
        out.append("</ul>")
    return "\n".join(out)


def _render_roadmap_timeline(weeks):
    icons = {1: "📘", 2: "📗", 3: "📙", 4: "📕"}
    connector = '<div class="lp-tl-connector"></div>'
    for idx, w in enumerate(weeks):
        icon = icons.get(w["num"], "📖")
        body_html     = _md_to_html(w["body"])
        resources_html = _build_resources_html(w["resources"]) if w.get("resources") else ""

        # Resources are built INTO the same HTML string — single st.markdown() call
        # so they render inside the week card's rounded box (fixes the "floating
        # outside" bug caused by separate st.markdown() calls).
        card_html = f"""
        <div style="display:flex;gap:16px;align-items:flex-start;margin-bottom:0;">
            <div style="display:flex;flex-direction:column;align-items:center;flex-shrink:0;">
                <div class="lp-tl-badge" style="position:static;">{w["num"]}</div>
            </div>
            <div style="flex:1;min-width:0;">
                <div class="lp-tl-week-title">{icon} {w["title"]}</div>
                <div class="lp-tl-week-body">
                    {body_html}
                    {resources_html}
                </div>
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

        if idx < len(weeks) - 1:
            st.markdown(connector, unsafe_allow_html=True)


def render_learning():
    # ---------- HERO ----------
    render_hero(
        "AI Learning Path Generator",
        "Generate a personalized AI-powered career roadmap based on your resume, target role, and skill gaps.",
    )
    spacer(18)

    # ✅ 3 Modes
    section_heading("Choose Mode")
    mode = st.radio(
        "Choose Mode:",
        ["From My Resume Analysis", "By Job Role", "Custom Input"],
        horizontal=True,
        label_visibility="collapsed",
    )

    target_role = ""
    missing_skills = None
    experience_level = "Fresher"

    spacer(12)

    # --- Mode 1: From Resume ---
    if mode == "From My Resume Analysis":
        if "latest_analysis" in st.session_state:
            data = st.session_state.latest_analysis
            target_role = data.get("role", "")
            missing_skills = data.get("missing", [])
            experience_level = data.get("experience_level", "Fresher")

            # Premium summary cards
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(
                    f"""<div class="lp-sum-card"><div class="ic">🎯</div>
                        <div class="lbl">TARGET ROLE</div><div class="val">{target_role}</div></div>""",
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown(
                    f"""<div class="lp-sum-card"><div class="ic">📊</div>
                        <div class="lbl">EXPERIENCE LEVEL</div><div class="val">{experience_level}</div></div>""",
                    unsafe_allow_html=True,
                )
            with col3:
                st.markdown(
                    f"""<div class="lp-sum-card"><div class="ic">⚠️</div>
                        <div class="lbl">MISSING SKILLS</div><div class="val">{len(missing_skills)} identified</div></div>""",
                    unsafe_allow_html=True,
                )

            if missing_skills:
                chips = "".join(f"<span class='lp-skill-chip'>{s}</span>" for s in missing_skills)
                st.markdown(
                    f"""<div class="lp-rec-card"><div class="lp-rec-title">🔥 Recommended Skills</div>{chips}</div>""",
                    unsafe_allow_html=True,
                )

            st.markdown(
                """<div class="lp-succ-card"><div class="t">✅ Resume successfully analyzed</div>
                    <div class="d">Your roadmap will be generated using resume insights.</div></div>""",
                unsafe_allow_html=True,
            )
        else:
            st.warning("⚠️ No resume analyzed yet!")
            st.info("👉 Go to **Resume Analyzer** first → Upload resume → Come back here!")
            return

    # --- Mode 2: By Job Role ---
    elif mode == "By Job Role":
        st.info("💡 Just select your target role and experience level — AI will decide what to learn!")

        col1, col2 = st.columns(2)
        with col1:
            target_role = st.selectbox("Target Job Role:", [
    # Software Development
    "Software Developer", "Backend Developer", "Frontend Developer",
    "Full Stack Developer", "Flutter Developer", "Android Developer", "iOS Developer",
    "Mobile App Developer",
    # Data & AI
    "Data Scientist", "Data Analyst", "Data Engineer", "ML Engineer",
    "AI Engineer", "Business Analyst", "NLP Engineer", "Prompt Engineer",
    # Cloud & DevOps
    "DevOps Engineer", "Cloud Engineer", "Site Reliability Engineer",
    # Security
    "Information Security Analyst", "Cybersecurity Engineer", "Ethical Hacker",
    # Management
    "Product Manager", "Project Manager",
    # Design
    "UI UX Designer", "Graphic Designer",
    # Emerging
    "Blockchain Developer", "Game Developer", "AR VR Developer",
])
        with col2:
            experience_level = st.selectbox("Experience Level:", [
                "Fresher", "Mid-Level (1-3 years)", "Senior (3+ years)"
            ])
        # missing_skills = None — AI will decide based on role

    # --- Mode 3: Custom ---
    else:
        col1, col2 = st.columns(2)
        with col1:
            target_role = st.text_input("Target Job Role:", placeholder="e.g. Data Scientist")
        with col2:
            experience_level = st.selectbox("Experience Level:", [
                "Fresher", "Mid-Level (1-3 years)", "Senior (3+ years)"
            ])
        missing_input = st.text_input(
            "Skills you want to learn (comma separated):",
            placeholder="e.g. Python, SQL, Machine Learning"
        )
        if missing_input:
            missing_skills = [s.strip() for s in missing_input.split(',')]

    spacer(20)

    # --- Generate Button ---
    if st.button("Generate Learning Roadmap", type="primary"):
        if not target_role:
            st.warning("Please enter or select a Target Job Role!")
            return

        with st.spinner(f"🧠 Creating personalized roadmap for {target_role}..."):
            roadmap = generate_learning_path(
                target_role=target_role,
                experience_level=experience_level,
                missing_skills=missing_skills
            )

        st.success("✅ Your Personalized Roadmap is Ready!")
        spacer(10)

        # ---------- Parse weeks (UI-only) ----------
        weeks = _parse_roadmap_weeks(roadmap)

        # ---------- Fetch REAL resources (live API, not LLM-generated) ----------
        # missing_skills are the ANCHOR for search queries (must-have skills first,
        # then good-to-have). LLM topics used only as context enrichment or fallback
        # when missing_skills list is shorter than the number of weeks.
        with st.spinner("🔎 Finding most-watched playlists and courses for your missing skills..."):
            for i, w in enumerate(weeks):
                topics = _extract_week_topics(w["body"])
                topic_context = topics[0] if topics else w["title"]

                if missing_skills and i < len(missing_skills):
                    # Use actual missing skill as primary query — guaranteed relevant
                    skill = missing_skills[i]
                else:
                    # Week index exceeds missing_skills list → fallback to LLM topic
                    skill = topic_context
                    topic_context = ""

                w["resources"] = get_week_resources(
                    skill=skill,
                    topic_context=topic_context if skill != topic_context else "",
                )

        # ---------- STEPPER ----------
        if len(weeks) >= 2:
            steps_html = '<div class="lp-stepper">'
            for i in range(1, len(weeks) + 1):
                steps_html += f'<div class="lp-step"><div class="dot">{i}</div><div class="nm">Week {i}</div></div>'
                if i < len(weeks):
                    steps_html += '<div class="lp-step-line"></div>'
            steps_html += "</div>"
            section_heading("Learning Progress")
            st.markdown(steps_html, unsafe_allow_html=True)

        # ---------- ROADMAP HEADER ----------
        section_heading(
            "🗺️ Your 4-Week Roadmap",
            f'<b style="color:#a5b4fc;">Role:</b> {target_role} &nbsp;·&nbsp; '
            f'<b style="color:#a5b4fc;">Level:</b> {experience_level}',
        )

        # ---------- ROADMAP BODY ----------
        if weeks:
            _render_roadmap_timeline(weeks)
            # Build enriched markdown (roadmap text + real resource links) for the PDF
            pdf_text = "\n\n".join(
                f"## {w['title']}\n{w['body']}\n\n{_resources_to_markdown(w['resources'])}"
                for w in weeks
            )
        else:
            # Fallback: if week format is not detected, render raw markdown
            st.markdown('<div class="glass lp-roadmap-wrap">', unsafe_allow_html=True)
            st.markdown(roadmap)
            st.markdown('</div>', unsafe_allow_html=True)
            pdf_text = roadmap

        spacer(18)

        # ✅ Download button
        pdf_bytes = generate_pdf(
            text=pdf_text,
            title="AI Learning Roadmap",
            subtitle=f"{target_role}  ·  {experience_level}"
        )
        st.download_button(
            label="📥 Download Roadmap as PDF",
            data=pdf_bytes,
            file_name=f"roadmap_{target_role}_{experience_level}.pdf",
            mime="application/pdf"
        )