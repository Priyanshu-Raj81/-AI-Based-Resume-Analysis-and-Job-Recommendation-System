# import re
# import streamlit as st
# from utils.ai_suggestions import generate_learning_path
# from utils.pdf_export import generate_pdf


# def _inject_learning_css():
#     st.markdown(
#         """
#         <style>
#         @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
#         html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

#         .stApp {
#             background:
#                 radial-gradient(1200px 600px at 10% -10%, rgba(99,102,241,0.18), transparent 60%),
#                 radial-gradient(1000px 500px at 100% 0%, rgba(236,72,153,0.14), transparent 55%),
#                 linear-gradient(160deg, #05060f 0%, #0a0f24 45%, #070b18 100%);
#             color: #e8ecf6;
#         }
#         #MainMenu, footer, header { visibility: hidden; }
#         .block-container { padding-top: 3.2rem; padding-bottom: 3rem; max-width: 1320px; }

#         @keyframes fadeUp { from {opacity:0; transform:translateY(24px);} to {opacity:1; transform:translateY(0);} }
#         @keyframes gradientMove { 0%{background-position:0% 50%;} 50%{background-position:100% 50%;} 100%{background-position:0% 50%;} }
#         @keyframes glowPulse { 0%,100%{box-shadow:0 0 18px rgba(99,102,241,0.35);} 50%{box-shadow:0 0 38px rgba(99,102,241,0.65);} }
#         .fade-up { animation: fadeUp .7s ease both; }

#         .glass {
#             background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.10);
#             backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
#             border-radius: 20px; box-shadow: 0 8px 40px rgba(0,0,0,0.35);
#         }

#         /* Hero */
#         .lp-hero {
#             position: relative; border-radius: 28px; padding: 56px 44px; overflow: hidden;
#             background: linear-gradient(120deg, #4f46e5, #7c3aed, #db2777, #4f46e5);
#             background-size: 300% 300%;
#             animation: gradientMove 12s ease infinite, glowPulse 4s ease-in-out infinite;
#             text-align: center; margin-bottom: 10px;
#         }
#         .lp-hero h1 {
#             font-size: 3rem; font-weight: 800; margin: 0;
#             background: linear-gradient(90deg,#fff,#e0e7ff);
#             -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -1.5px;
#         }
#         .lp-hero p { font-size: 1.15rem; color: #eef0ff; margin: 14px auto 0; font-weight: 300; max-width: 760px; line-height:1.6; }

#         .lp-section-title { font-size:1.25rem; font-weight:700; margin:8px 0 12px; color:#eef0ff; }

#         /* Summary cards */
#         .sum-card {
#             padding:20px 22px; border-radius:18px; transition: transform .3s ease, box-shadow .3s ease;
#             background: rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.10);
#             backdrop-filter: blur(16px); box-shadow:0 8px 40px rgba(0,0,0,0.35);
#         }
#         .sum-card:hover { transform:translateY(-8px); box-shadow:0 0 34px rgba(124,58,237,0.55); border-color:rgba(165,180,252,0.6); }
#         .sum-card .ic { font-size:1.6rem; }
#         .sum-card .lbl { color:#9aa4c4; font-size:.85rem; margin-top:6px; letter-spacing:.4px; }
#         .sum-card .val { font-weight:800; font-size:1.15rem; margin-top:4px;
#             background:linear-gradient(90deg,#a5b4fc,#f472b6); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }

#         /* Recommended skills card */
#         .rec-card { padding:20px 22px; border-radius:18px; margin-top:10px;
#             background: rgba(99,102,241,0.08); border:1px solid rgba(129,140,248,0.25); }
#         .rec-title { font-weight:700; color:#a5b4fc; margin-bottom:12px; font-size:1.05rem; }
#         .skill-chip {
#             display:inline-block; background:rgba(124,58,237,0.22); color:#dfe4f5;
#             padding:7px 16px; border-radius:20px; margin:5px; font-size:.88rem; font-weight:600;
#             border:1px solid rgba(165,180,252,0.25); transition: all .2s ease;
#         }
#         .skill-chip:hover { background:rgba(124,58,237,0.4); transform:translateY(-2px); }

#         /* Success card */
#         .succ-card {
#             padding:18px 22px; border-radius:16px; margin-top:14px;
#             background: linear-gradient(120deg, rgba(16,185,129,0.14), rgba(124,58,237,0.10));
#             border:1px solid rgba(52,211,153,0.35);
#         }
#         .succ-card .t { font-weight:700; color:#34d399; }
#         .succ-card .d { color:#9aa4c4; font-size:.9rem; margin-top:4px; }

#         /* Segmented radio */
#         div[role="radiogroup"] { gap: 14px; }
#         div[role="radiogroup"] label {
#             background: rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.10);
#             padding: 14px 22px; border-radius: 14px; transition: all .25s ease; font-weight:600;
#         }
#         div[role="radiogroup"] label:hover { transform: translateY(-3px); border-color: rgba(124,58,237,0.5); box-shadow:0 0 18px rgba(124,58,237,0.3); }
#         div[role="radiogroup"] label:has(input:checked) {
#             background: linear-gradient(120deg, rgba(79,70,229,0.45), rgba(219,39,119,0.30));
#             border:1px solid rgba(165,180,252,0.85); box-shadow:0 0 26px rgba(124,58,237,0.55);
#         }

#         /* Inputs */
#         .stSelectbox div[data-baseweb="select"] > div,
#         .stTextInput input {
#             background: rgba(255,255,255,0.05) !important;
#             border: 1px solid rgba(255,255,255,0.12) !important;
#             border-radius: 12px !important; color:#e8ecf6 !important;
#         }

#         /* Primary CTA */
#         .stButton > button[kind="primary"] {
#             width:100%; border-radius:16px; padding:.95rem 1.4rem; font-weight:800; font-size:1.05rem;
#             border:1px solid rgba(255,255,255,0.15); color:#fff;
#             background: linear-gradient(90deg,#4f46e5,#7c3aed,#db2777); background-size:200% 200%;
#             transition: all .25s ease;
#         }
#         .stButton > button[kind="primary"]:hover { transform: translateY(-3px); box-shadow:0 0 32px rgba(124,58,237,0.65); border-color:#a5b4fc; }

#         /* Download button */
#         .stDownloadButton > button {
#             border-radius:14px; padding:.7rem 1.4rem; font-weight:700;
#             background:rgba(255,255,255,0.05); border:1px solid rgba(165,180,252,0.4); color:#e8ecf6;
#             transition: all .25s ease;
#         }
#         .stDownloadButton > button:hover { transform:translateY(-3px); box-shadow:0 0 24px rgba(124,58,237,0.5); border-color:#a5b4fc; }

#         /* Stepper */
#         .stepper { display:flex; align-items:center; justify-content:center; gap:0; margin:8px 0 26px; flex-wrap:wrap; }
#         .step { display:flex; flex-direction:column; align-items:center; min-width:90px; }
#         .step .dot {
#             width:42px; height:42px; border-radius:50%; display:flex; align-items:center; justify-content:center;
#             font-weight:800; color:#fff; background:linear-gradient(120deg,#6366f1,#ec4899);
#             box-shadow:0 0 18px rgba(124,58,237,0.6);
#         }
#         .step .nm { color:#cfd6ee; font-size:.82rem; margin-top:8px; font-weight:600; }
#         .step-line { height:3px; width:48px; background:linear-gradient(90deg,#6366f1,#ec4899); border-radius:3px; margin:0 -2px 26px; }

#         /* Roadmap fallback container */
#         .roadmap-wrap { padding:26px 30px; border-radius:22px; margin-top:6px; }
#         .roadmap-wrap h2 {
#             border-left:4px solid #818cf8; padding-left:12px; margin-top:22px;
#             background:linear-gradient(90deg,#a5b4fc,#f472b6); -webkit-background-clip:text; -webkit-text-fill-color:transparent;
#         }
#         .roadmap-wrap strong { color:#a5b4fc; }

#         /* Roadmap vertical timeline */
#         .tl-week { position:relative; padding-left:42px; margin-bottom:24px; }
#         .tl-week:before {
#             content:''; position:absolute; left:18px; top:38px; bottom:-24px;
#             width:2px; background:linear-gradient(180deg,#6366f1,#ec4899);
#         }
#         .tl-week:last-child:before { display:none; }
#         .tl-week-head { display:flex; align-items:center; gap:12px; margin-bottom:12px; }
#         .tl-badge {
#             position:absolute; left:0; width:38px; height:38px; border-radius:50%;
#             display:flex; align-items:center; justify-content:center; font-weight:800; color:#fff;
#             background:linear-gradient(120deg,#6366f1,#ec4899); box-shadow:0 0 18px rgba(124,58,237,0.6);
#         }
#         .tl-week-title {
#             font-size:1.2rem; font-weight:800;
#             background:linear-gradient(90deg,#a5b4fc,#f472b6);
#             -webkit-background-clip:text; -webkit-text-fill-color:transparent;
#         }
#         .tl-week-body {
#             padding:20px 24px; border-radius:18px; transition:transform .3s ease, box-shadow .3s ease;
#         }
#         .tl-week-body:hover { transform:translateY(-4px); box-shadow:0 0 30px rgba(124,58,237,0.45); }
#         .tl-week-body h3 { color:#a5b4fc; font-size:1.02rem; margin-top:14px; }
#         .tl-week-body strong { color:#c4b5fd; }
#         .tl-week-body a { color:#818cf8; }
#         </style>
#         """,
#         unsafe_allow_html=True,
#     )


# def _parse_roadmap_weeks(roadmap: str):
#     """UI-only parser. Splits the markdown roadmap into week blocks.
#     Does NOT modify backend output. Returns list of dicts."""
#     if not roadmap:
#         return []
#     parts = re.split(r'(?m)^##\s*.*?Week\s*\d+[^\n]*', roadmap)
#     headers = re.findall(r'(?m)^##\s*.*?(Week\s*\d+\s*:?[^\n]*)', roadmap)
#     weeks = []
#     bodies = parts[1:] if len(parts) > 1 else []
#     for i, body in enumerate(bodies):
#         title = headers[i].strip() if i < len(headers) else f"Week {i + 1}"
#         body_clean = body.strip()
#         # Strip duplicate title line AI sometimes repeats at top of body
#         # e.g. ": Fundamentals of Java and Android Basics"
#         body_clean = re.sub(r'^\s*:\s*[^\n]+\n', '', body_clean)
#         weeks.append({"num": i + 1, "title": title, "body": body_clean.strip()})
#     return weeks


# def _md_to_html(text: str) -> str:
#     """Convert basic markdown to HTML for inline rendering inside st.markdown blocks."""
#     # Bold
#     text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
#     # Headings ### and ##
#     text = re.sub(r'(?m)^###\s+(.*?)$', r'<h4 style="color:#a5b4fc;margin:14px 0 6px;">\1</h4>', text)
#     text = re.sub(r'(?m)^##\s+(.*?)$',  r'<h3 style="color:#a5b4fc;margin:16px 0 8px;">\1</h3>', text)
#     # Links [text](url)
#     text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank" style="color:#818cf8;">\1</a>', text)
#     # Bullet lines starting with -
#     lines = text.split("\n")
#     out, in_ul = [], False
#     for line in lines:
#         stripped = line.strip()
#         if stripped.startswith("- ") or stripped.startswith("* "):
#             if not in_ul:
#                 out.append('<ul style="margin:6px 0 10px 18px;padding:0;">')
#                 in_ul = True
#             out.append(f'<li style="color:#cfd6ee;margin:4px 0;line-height:1.6;">{stripped[2:]}</li>')
#         else:
#             if in_ul:
#                 out.append("</ul>")
#                 in_ul = False
#             if stripped:
#                 out.append(f'<p style="color:#cfd6ee;margin:6px 0;line-height:1.6;">{stripped}</p>')
#     if in_ul:
#         out.append("</ul>")
#     return "\n".join(out)


# def _render_roadmap_timeline(weeks):
#     icons = {1: "📘", 2: "📗", 3: "📙", 4: "📕"}
#     connector = (
#         '<div style="margin-left:60px;width:2px;height:24px;'
#         'background:linear-gradient(180deg,#6366f1,#ec4899);"></div>'
#     )
#     for idx, w in enumerate(weeks):
#         icon = icons.get(w["num"], "📖")
#         body_html = _md_to_html(w["body"])

#         card_html = f"""
#         <div style="display:flex;gap:16px;align-items:flex-start;margin-bottom:0;">
#             <!-- Badge + line -->
#             <div style="display:flex;flex-direction:column;align-items:center;flex-shrink:0;">
#                 <div style="width:42px;height:42px;border-radius:50%;display:flex;align-items:center;
#                     justify-content:center;font-weight:800;color:#fff;font-size:1rem;
#                     background:linear-gradient(120deg,#6366f1,#ec4899);
#                     box-shadow:0 0 18px rgba(124,58,237,0.6);">{w["num"]}</div>
#             </div>
#             <!-- Content -->
#             <div style="flex:1;min-width:0;">
#                 <div style="font-size:1.15rem;font-weight:800;margin-bottom:12px;
#                     background:linear-gradient(90deg,#a5b4fc,#f472b6);
#                     -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
#                     {icon} {w["title"]}
#                 </div>
#                 <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.10);
#                     backdrop-filter:blur(16px);border-radius:18px;padding:22px 26px;
#                     box-shadow:0 8px 40px rgba(0,0,0,0.35);transition:transform .3s ease;">
#                     {body_html}
#                 </div>
#             </div>
#         </div>
#         """
#         st.markdown(card_html, unsafe_allow_html=True)

#         # Connector line between weeks (not after last)
#         if idx < len(weeks) - 1:
#             st.markdown(connector, unsafe_allow_html=True)


# def render_learning():
#     _inject_learning_css()

#     # ---------- HERO ----------
#     st.markdown(
#         """
#         <div class="lp-hero fade-up">
#             <h1>AI Learning Path Generator</h1>
#             <p>Generate a personalized AI-powered career roadmap based on your resume, target role, and skill gaps.</p>
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )
#     st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

#     # ✅ 3 Modes
#     st.markdown('<div class="lp-section-title">Choose Mode</div>', unsafe_allow_html=True)
#     mode = st.radio(
#         "Choose Mode:",
#         ["From My Resume Analysis", "By Job Role", "Custom Input"],
#         horizontal=True,
#         label_visibility="collapsed",
#     )

#     target_role = ""
#     missing_skills = None
#     experience_level = "Fresher"

#     st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

#     # --- Mode 1: From Resume ---
#     if mode == "From My Resume Analysis":
#         if "latest_analysis" in st.session_state:
#             data = st.session_state.latest_analysis
#             target_role = data.get("role", "")
#             missing_skills = data.get("missing", [])
#             experience_level = data.get("experience_level", "Fresher")

#             # Premium summary cards
#             col1, col2, col3 = st.columns(3)
#             with col1:
#                 st.markdown(
#                     f"""<div class="sum-card"><div class="ic">🎯</div>
#                         <div class="lbl">TARGET ROLE</div><div class="val">{target_role}</div></div>""",
#                     unsafe_allow_html=True,
#                 )
#             with col2:
#                 st.markdown(
#                     f"""<div class="sum-card"><div class="ic">📊</div>
#                         <div class="lbl">EXPERIENCE LEVEL</div><div class="val">{experience_level}</div></div>""",
#                     unsafe_allow_html=True,
#                 )
#             with col3:
#                 st.markdown(
#                     f"""<div class="sum-card"><div class="ic">⚠️</div>
#                         <div class="lbl">MISSING SKILLS</div><div class="val">{len(missing_skills)} identified</div></div>""",
#                     unsafe_allow_html=True,
#                 )

#             if missing_skills:
#                 chips = "".join(f"<span class='skill-chip'>{s}</span>" for s in missing_skills)
#                 st.markdown(
#                     f"""<div class="rec-card"><div class="rec-title">🔥 Recommended Skills</div>{chips}</div>""",
#                     unsafe_allow_html=True,
#                 )

#             st.markdown(
#                 """<div class="succ-card"><div class="t">✅ Resume successfully analyzed</div>
#                     <div class="d">Your roadmap will be generated using resume insights.</div></div>""",
#                 unsafe_allow_html=True,
#             )
#         else:
#             st.warning("⚠️ No resume analyzed yet!")
#             st.info("👉 Go to **Resume Analyzer** first → Upload resume → Come back here!")
#             return

#     # --- Mode 2: By Job Role ---
#     elif mode == "By Job Role":
#         st.info("💡 Just select your target role and experience level — AI will decide what to learn!")

#         col1, col2 = st.columns(2)
#         with col1:
#             target_role = st.selectbox("Target Job Role:", [
#     # Software Development
#     "Software Developer", "Backend Developer", "Frontend Developer",
#     "Full Stack Developer", "Flutter Developer", "Android Developer", "iOS Developer",
#     "Mobile App Developer",
#     # Data & AI
#     "Data Scientist", "Data Analyst", "Data Engineer", "ML Engineer",
#     "AI Engineer", "Business Analyst", "NLP Engineer", "Prompt Engineer",
#     # Cloud & DevOps
#     "DevOps Engineer", "Cloud Engineer", "Site Reliability Engineer",
#     # Security
#     "Information Security Analyst", "Cybersecurity Engineer", "Ethical Hacker",
#     # Management
#     "Product Manager", "Project Manager",
#     # Design
#     "UI UX Designer", "Graphic Designer",
#     # Emerging
#     "Blockchain Developer", "Game Developer", "AR VR Developer",
# ])
#         with col2:
#             experience_level = st.selectbox("Experience Level:", [
#                 "Fresher", "Mid-Level (1-3 years)", "Senior (3+ years)"
#             ])
#         # missing_skills = None — AI will decide based on role

#     # --- Mode 3: Custom ---
#     else:
#         col1, col2 = st.columns(2)
#         with col1:
#             target_role = st.text_input("Target Job Role:", placeholder="e.g. Data Scientist")
#         with col2:
#             experience_level = st.selectbox("Experience Level:", [
#                 "Fresher", "Mid-Level (1-3 years)", "Senior (3+ years)"
#             ])
#         missing_input = st.text_input(
#             "Skills you want to learn (comma separated):",
#             placeholder="e.g. Python, SQL, Machine Learning"
#         )
#         if missing_input:
#             missing_skills = [s.strip() for s in missing_input.split(',')]

#     st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

#     # --- Generate Button ---
#     if st.button("Generate Learning Roadmap", type="primary"):
#         if not target_role:
#             st.warning("Please enter or select a Target Job Role!")
#             return

#         with st.spinner(f"🧠 Creating personalized roadmap for {target_role}..."):
#             roadmap = generate_learning_path(
#                 target_role=target_role,
#                 experience_level=experience_level,
#                 missing_skills=missing_skills
#             )

#         st.success("✅ Your Personalized Roadmap is Ready!")
#         st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

#         # ---------- Parse weeks (UI-only) ----------
#         weeks = _parse_roadmap_weeks(roadmap)

#         # ---------- STEPPER ----------
#         if len(weeks) >= 2:
#             steps_html = '<div class="stepper">'
#             for i in range(1, len(weeks) + 1):
#                 steps_html += f'<div class="step"><div class="dot">{i}</div><div class="nm">Week {i}</div></div>'
#                 if i < len(weeks):
#                     steps_html += '<div class="step-line"></div>'
#             steps_html += "</div>"
#             st.markdown('<div class="lp-section-title">Learning Progress</div>', unsafe_allow_html=True)
#             st.markdown(steps_html, unsafe_allow_html=True)

#         # ---------- ROADMAP HEADER ----------
#         st.markdown(
#             f"""<div class="lp-section-title" style="font-size:1.5rem;">🗺️ Your 4-Week Roadmap</div>
#                 <div style="color:#9aa4c4; margin-bottom:18px;">
#                     <b style="color:#a5b4fc;">Role:</b> {target_role} &nbsp;·&nbsp;
#                     <b style="color:#a5b4fc;">Level:</b> {experience_level}
#                 </div>""",
#             unsafe_allow_html=True,
#         )

#         # ---------- ROADMAP BODY ----------
#         if weeks:
#             _render_roadmap_timeline(weeks)
#         else:
#             # Fallback: if week format is not detected, render raw markdown
#             st.markdown('<div class="glass roadmap-wrap">', unsafe_allow_html=True)
#             st.markdown(roadmap)
#             st.markdown('</div>', unsafe_allow_html=True)

#         st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

#         # ✅ Download button
#         pdf_bytes = generate_pdf(
#             text=roadmap,
#             title="AI Learning Roadmap",
#             subtitle=f"{target_role}  ·  {experience_level}"
#         )
#         st.download_button(
#             label="📥 Download Roadmap as PDF",
#             data=pdf_bytes,
#             file_name=f"roadmap_{target_role}_{experience_level}.pdf",
#             mime="application/pdf"
#         )


# New Update

import re
import streamlit as st
from utils.ai_suggestions import generate_learning_path
from utils.pdf_export import generate_pdf


def _inject_learning_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

        .stApp {
            background:
                radial-gradient(1200px 600px at 10% -10%, rgba(99,102,241,0.18), transparent 60%),
                radial-gradient(1000px 500px at 100% 0%, rgba(236,72,153,0.14), transparent 55%),
                linear-gradient(160deg, #05060f 0%, #0a0f24 45%, #070b18 100%);
            color: #e8ecf6;
        }
        #MainMenu, footer, header { visibility: hidden; }
        .block-container { padding-top: 3.2rem; padding-bottom: 3rem; max-width: 1320px; }

        @keyframes fadeUp { from {opacity:0; transform:translateY(24px);} to {opacity:1; transform:translateY(0);} }
        @keyframes gradientMove { 0%{background-position:0% 50%;} 50%{background-position:100% 50%;} 100%{background-position:0% 50%;} }
        @keyframes glowPulse { 0%,100%{box-shadow:0 0 18px rgba(99,102,241,0.35);} 50%{box-shadow:0 0 38px rgba(99,102,241,0.65);} }
        .fade-up { animation: fadeUp .7s ease both; }

        .glass {
            background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.10);
            backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
            border-radius: 20px; box-shadow: 0 8px 40px rgba(0,0,0,0.35);
        }

        /* Hero */
        .lp-hero {
            position: relative; border-radius: 28px; padding: 56px 44px; overflow: hidden;
            background: linear-gradient(120deg, #1d4ed8, #2563eb, #10b981, #1d4ed8);
            background-size: 300% 300%;
            animation: gradientMove 12s ease infinite, glowPulse 4s ease-in-out infinite;
            text-align: center; margin-bottom: 10px;
        }
        .lp-hero h1 {
            font-size: 3rem; font-weight: 800; margin: 0;
            background: linear-gradient(90deg,#fff,#e0e7ff);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -1.5px;
        }
        .lp-hero p { font-size: 1.15rem; color: #eef0ff; margin: 14px auto 0; font-weight: 300; max-width: 760px; line-height:1.6; }

        .lp-section-title { font-size:1.25rem; font-weight:700; margin:8px 0 12px; color:#eef0ff; }

        /* Summary cards */
        .sum-card {
            padding:20px 22px; border-radius:18px; transition: transform .3s ease, box-shadow .3s ease;
            background: rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.10);
            backdrop-filter: blur(16px); box-shadow:0 8px 40px rgba(0,0,0,0.35);
        }
        .sum-card:hover { transform:translateY(-8px); box-shadow:0 0 34px rgba(37,99,235,0.55); border-color:rgba(165,180,252,0.6); }
        .sum-card .ic { font-size:1.6rem; }
        .sum-card .lbl { color:#9aa4c4; font-size:.85rem; margin-top:6px; letter-spacing:.4px; }
        .sum-card .val { font-weight:800; font-size:1.15rem; margin-top:4px;
            background:linear-gradient(90deg,#a5b4fc,#f472b6); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }

        /* Recommended skills card */
        .rec-card { padding:20px 22px; border-radius:18px; margin-top:10px;
            background: rgba(99,102,241,0.08); border:1px solid rgba(129,140,248,0.25); }
        .rec-title { font-weight:700; color:#a5b4fc; margin-bottom:12px; font-size:1.05rem; }
        .skill-chip {
            display:inline-block; background:rgba(37,99,235,0.22); color:#dfe4f5;
            padding:7px 16px; border-radius:20px; margin:5px; font-size:.88rem; font-weight:600;
            border:1px solid rgba(165,180,252,0.25); transition: all .2s ease;
        }
        .skill-chip:hover { background:rgba(37,99,235,0.4); transform:translateY(-2px); }

        /* Success card */
        .succ-card {
            padding:18px 22px; border-radius:16px; margin-top:14px;
            background: linear-gradient(120deg, rgba(16,185,129,0.14), rgba(37,99,235,0.10));
            border:1px solid rgba(52,211,153,0.35);
        }
        .succ-card .t { font-weight:700; color:#34d399; }
        .succ-card .d { color:#9aa4c4; font-size:.9rem; margin-top:4px; }

        /* Segmented radio */
        div[role="radiogroup"] { gap: 14px; }
        div[role="radiogroup"] label {
            background: rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.10);
            padding: 14px 22px; border-radius: 14px; transition: all .25s ease; font-weight:600;
        }
        div[role="radiogroup"] label:hover { transform: translateY(-3px); border-color: rgba(37,99,235,0.5); box-shadow:0 0 18px rgba(37,99,235,0.3); }
        div[role="radiogroup"] label:has(input:checked) {
            background: linear-gradient(120deg, rgba(79,70,229,0.45), rgba(219,39,119,0.30));
            border:1px solid rgba(165,180,252,0.85); box-shadow:0 0 26px rgba(37,99,235,0.55);
        }

        /* Inputs */
        .stSelectbox div[data-baseweb="select"] > div,
        .stTextInput input {
            background: rgba(255,255,255,0.05) !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            border-radius: 12px !important; color:#e8ecf6 !important;
        }

        /* Primary CTA */
        .stButton > button[kind="primary"] {
            width:100%; border-radius:16px; padding:.95rem 1.4rem; font-weight:800; font-size:1.05rem;
            border:1px solid rgba(255,255,255,0.15); color:#fff;
            background: linear-gradient(90deg,#1d4ed8,#2563eb,#10b981); background-size:200% 200%;
            transition: all .25s ease;
        }
        .stButton > button[kind="primary"]:hover { transform: translateY(-3px); box-shadow:0 0 32px rgba(37,99,235,0.65); border-color:#a5b4fc; }

        /* Download button */
        .stDownloadButton > button {
            border-radius:14px; padding:.7rem 1.4rem; font-weight:700;
            background:rgba(255,255,255,0.05); border:1px solid rgba(165,180,252,0.4); color:#e8ecf6;
            transition: all .25s ease;
        }
        .stDownloadButton > button:hover { transform:translateY(-3px); box-shadow:0 0 24px rgba(37,99,235,0.5); border-color:#a5b4fc; }

        /* Stepper */
        .stepper { display:flex; align-items:center; justify-content:center; gap:0; margin:8px 0 26px; flex-wrap:wrap; }
        .step { display:flex; flex-direction:column; align-items:center; min-width:90px; }
        .step .dot {
            width:42px; height:42px; border-radius:50%; display:flex; align-items:center; justify-content:center;
            font-weight:800; color:#fff; background:linear-gradient(120deg,#2563eb,#0ea5e9);
            box-shadow:0 0 18px rgba(37,99,235,0.6);
        }
        .step .nm { color:#cfd6ee; font-size:.82rem; margin-top:8px; font-weight:600; }
        .step-line { height:3px; width:48px; background:linear-gradient(90deg,#2563eb,#0ea5e9); border-radius:3px; margin:0 -2px 26px; }

        /* Roadmap fallback container */
        .roadmap-wrap { padding:26px 30px; border-radius:22px; margin-top:6px; }
        .roadmap-wrap h2 {
            border-left:4px solid #818cf8; padding-left:12px; margin-top:22px;
            background:linear-gradient(90deg,#a5b4fc,#f472b6); -webkit-background-clip:text; -webkit-text-fill-color:transparent;
        }
        .roadmap-wrap strong { color:#a5b4fc; }

        /* Roadmap vertical timeline */
        .tl-week { position:relative; padding-left:42px; margin-bottom:24px; }
        .tl-week:before {
            content:''; position:absolute; left:18px; top:38px; bottom:-24px;
            width:2px; background:linear-gradient(180deg,#2563eb,#0ea5e9);
        }
        .tl-week:last-child:before { display:none; }
        .tl-week-head { display:flex; align-items:center; gap:12px; margin-bottom:12px; }
        .tl-badge {
            position:absolute; left:0; width:38px; height:38px; border-radius:50%;
            display:flex; align-items:center; justify-content:center; font-weight:800; color:#fff;
            background:linear-gradient(120deg,#2563eb,#0ea5e9); box-shadow:0 0 18px rgba(37,99,235,0.6);
        }
        .tl-week-title {
            font-size:1.2rem; font-weight:800;
            background:linear-gradient(90deg,#a5b4fc,#f472b6);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent;
        }
        .tl-week-body {
            padding:20px 24px; border-radius:18px; transition:transform .3s ease, box-shadow .3s ease;
        }
        .tl-week-body:hover { transform:translateY(-4px); box-shadow:0 0 30px rgba(37,99,235,0.45); }
        .tl-week-body h3 { color:#a5b4fc; font-size:1.02rem; margin-top:14px; }
        .tl-week-body strong { color:#c4b5fd; }
        .tl-week-body a { color:#818cf8; }
        </style>
        """,
        unsafe_allow_html=True,
    )


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
    text = re.sub(r'(?m)^###\s+(.*?)$', r'<h4 style="color:#a5b4fc;margin:14px 0 6px;">\1</h4>', text)
    text = re.sub(r'(?m)^##\s+(.*?)$',  r'<h3 style="color:#a5b4fc;margin:16px 0 8px;">\1</h3>', text)
    # Links [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank" style="color:#818cf8;">\1</a>', text)
    # Bullet lines starting with -
    lines = text.split("\n")
    out, in_ul = [], False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("* "):
            if not in_ul:
                out.append('<ul style="margin:6px 0 10px 18px;padding:0;">')
                in_ul = True
            out.append(f'<li style="color:#cfd6ee;margin:4px 0;line-height:1.6;">{stripped[2:]}</li>')
        else:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if stripped:
                out.append(f'<p style="color:#cfd6ee;margin:6px 0;line-height:1.6;">{stripped}</p>')
    if in_ul:
        out.append("</ul>")
    return "\n".join(out)


def _render_roadmap_timeline(weeks):
    icons = {1: "📘", 2: "📗", 3: "📙", 4: "📕"}
    connector = (
        '<div style="margin-left:60px;width:2px;height:24px;'
        'background:linear-gradient(180deg,#2563eb,#0ea5e9);"></div>'
    )
    for idx, w in enumerate(weeks):
        icon = icons.get(w["num"], "📖")
        body_html = _md_to_html(w["body"])

        card_html = f"""
        <div style="display:flex;gap:16px;align-items:flex-start;margin-bottom:0;">
            <!-- Badge + line -->
            <div style="display:flex;flex-direction:column;align-items:center;flex-shrink:0;">
                <div style="width:42px;height:42px;border-radius:50%;display:flex;align-items:center;
                    justify-content:center;font-weight:800;color:#fff;font-size:1rem;
                    background:linear-gradient(120deg,#2563eb,#0ea5e9);
                    box-shadow:0 0 18px rgba(37,99,235,0.6);">{w["num"]}</div>
            </div>
            <!-- Content -->
            <div style="flex:1;min-width:0;">
                <div style="font-size:1.15rem;font-weight:800;margin-bottom:12px;
                    background:linear-gradient(90deg,#a5b4fc,#f472b6);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                    {icon} {w["title"]}
                </div>
                <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.10);
                    backdrop-filter:blur(16px);border-radius:18px;padding:22px 26px;
                    box-shadow:0 8px 40px rgba(0,0,0,0.35);transition:transform .3s ease;">
                    {body_html}
                </div>
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

        # Connector line between weeks (not after last)
        if idx < len(weeks) - 1:
            st.markdown(connector, unsafe_allow_html=True)


def render_learning():
    _inject_learning_css()

    # ---------- HERO ----------
    st.markdown(
        """
        <div class="lp-hero fade-up">
            <h1>AI Learning Path Generator</h1>
            <p>Generate a personalized AI-powered career roadmap based on your resume, target role, and skill gaps.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

    # ✅ 3 Modes
    st.markdown('<div class="lp-section-title">Choose Mode</div>', unsafe_allow_html=True)
    mode = st.radio(
        "Choose Mode:",
        ["From My Resume Analysis", "By Job Role", "Custom Input"],
        horizontal=True,
        label_visibility="collapsed",
    )

    target_role = ""
    missing_skills = None
    experience_level = "Fresher"

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

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
                    f"""<div class="sum-card"><div class="ic">🎯</div>
                        <div class="lbl">TARGET ROLE</div><div class="val">{target_role}</div></div>""",
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown(
                    f"""<div class="sum-card"><div class="ic">📊</div>
                        <div class="lbl">EXPERIENCE LEVEL</div><div class="val">{experience_level}</div></div>""",
                    unsafe_allow_html=True,
                )
            with col3:
                st.markdown(
                    f"""<div class="sum-card"><div class="ic">⚠️</div>
                        <div class="lbl">MISSING SKILLS</div><div class="val">{len(missing_skills)} identified</div></div>""",
                    unsafe_allow_html=True,
                )

            if missing_skills:
                chips = "".join(f"<span class='skill-chip'>{s}</span>" for s in missing_skills)
                st.markdown(
                    f"""<div class="rec-card"><div class="rec-title">🔥 Recommended Skills</div>{chips}</div>""",
                    unsafe_allow_html=True,
                )

            st.markdown(
                """<div class="succ-card"><div class="t">✅ Resume successfully analyzed</div>
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

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

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
        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

        # ---------- Parse weeks (UI-only) ----------
        weeks = _parse_roadmap_weeks(roadmap)

        # ---------- STEPPER ----------
        if len(weeks) >= 2:
            steps_html = '<div class="stepper">'
            for i in range(1, len(weeks) + 1):
                steps_html += f'<div class="step"><div class="dot">{i}</div><div class="nm">Week {i}</div></div>'
                if i < len(weeks):
                    steps_html += '<div class="step-line"></div>'
            steps_html += "</div>"
            st.markdown('<div class="lp-section-title">Learning Progress</div>', unsafe_allow_html=True)
            st.markdown(steps_html, unsafe_allow_html=True)

        # ---------- ROADMAP HEADER ----------
        st.markdown(
            f"""<div class="lp-section-title" style="font-size:1.5rem;">🗺️ Your 4-Week Roadmap</div>
                <div style="color:#9aa4c4; margin-bottom:18px;">
                    <b style="color:#a5b4fc;">Role:</b> {target_role} &nbsp;·&nbsp;
                    <b style="color:#a5b4fc;">Level:</b> {experience_level}
                </div>""",
            unsafe_allow_html=True,
        )

        # ---------- ROADMAP BODY ----------
        if weeks:
            _render_roadmap_timeline(weeks)
        else:
            # Fallback: if week format is not detected, render raw markdown
            st.markdown('<div class="glass roadmap-wrap">', unsafe_allow_html=True)
            st.markdown(roadmap)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

        # ✅ Download button
        pdf_bytes = generate_pdf(
            text=roadmap,
            title="AI Learning Roadmap",
            subtitle=f"{target_role}  ·  {experience_level}"
        )
        st.download_button(
            label="📥 Download Roadmap as PDF",
            data=pdf_bytes,
            file_name=f"roadmap_{target_role}_{experience_level}.pdf",
            mime="application/pdf"
        ) 
