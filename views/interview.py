import streamlit as st
import re
from utils.pdf_export import generate_pdf
from utils.ai_suggestions import (
    generate_interview_questions,
    generate_coach_questions,
    evaluate_answer,
    generate_final_report,
)
from utils import coach_parsing as cp
from utils import coach_state as cs
from utils.theme import (
    render_iv_band,
    render_iv_question_card,
    render_iv_panel,
    render_iv_page_header,
    render_iv_stat_row,
)

ROLES_LIST = [
    "Software Developer", "Backend Developer", "Frontend Developer",
    "Full Stack Developer", "Mobile App Developer", "Flutter Developer",
    "Android Developer", "iOS Developer",
    "Data Scientist", "Data Analyst", "Data Engineer",
    "ML Engineer", "AI Engineer", "NLP Engineer",
    "Prompt Engineer", "Business Analyst",
    "DevOps Engineer", "Cloud Engineer", "Site Reliability Engineer",
    "Information Security Analyst", "Cybersecurity Engineer", "Ethical Hacker",
    "Product Manager", "Project Manager",
    "UI UX Designer", "Graphic Designer",
    "Blockchain Developer", "Game Developer", "AR VR Developer",
]

ICONS = {
    "mic":    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>',
    "target": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
    "chart":  '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
    "tools":  '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a4 4 0 0 0-5.6 5.6L3 18v3h3l6.1-6.1a4 4 0 0 0 5.6-5.6l-2.5 2.5-2-2 2.5-2.5z"/></svg>',
    "brain":  '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.94-.55z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.94-.55z"/></svg>',
    "user":   '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    "layers": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>',
}


def _clean(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*',     r'\1', text)
    text = re.sub(r'#{1,6}\s*',     '',    text)
    text = re.sub(r'`(.*?)`',       r'\1', text)
    return text.strip()


def _badge_cls(label):
    return {
        "Technical": "rm-iv-badge-tech", "HR": "rm-iv-badge-hr",
        "Behavioral": "rm-iv-badge-hr",  "Conceptual": "rm-iv-badge-concept",
        "Easy": "rm-iv-badge-easy",      "Medium": "rm-iv-badge-medium",
        "Hard": "rm-iv-badge-hard",
    }.get(label, "rm-iv-badge-concept")


# =========================================================================== #
# QUESTION BANK — parse AI text → individual cards via theme
# =========================================================================== #
def _parse_and_render_questions(questions_text: str):
    """Parse AI-generated question bank text and render each question
    as a themed card. All rendering delegated to theme.render_iv_question_card."""
    lines       = questions_text.split('\n')
    q_num       = q_text = q_type = q_diff = tip_text = ""
    answer_lines = []
    in_answer   = in_tip = False

    def flush():
        nonlocal q_num, q_text, q_type, q_diff, answer_lines, tip_text, in_answer, in_tip
        if not q_text:
            return
        answer = _clean(' '.join(answer_lines))
        render_iv_question_card(
            q_num   = _clean(q_num),
            q_text  = _clean(q_text),
            q_diff  = _clean(q_diff),
            q_type  = _clean(q_type),
            answer  = answer,
            tip     = _clean(tip_text),
        )
        q_num = q_text = q_type = q_diff = tip_text = ""
        answer_lines.clear()
        in_answer = in_tip = False

    for line in lines:
        s = line.strip()
        if not s:
            continue
        up = s.upper()

        # Difficulty band headers
        if '🟢' in s or ('EASY' in up and 'QUESTION' in up):
            flush(); render_iv_band("Easy"); in_answer = in_tip = False; continue
        if '🟡' in s or ('MEDIUM' in up and 'QUESTION' in up):
            flush(); render_iv_band("Medium"); in_answer = in_tip = False; continue
        if '🔴' in s or ('HARD' in up and 'QUESTION' in up):
            flush(); render_iv_band("Hard"); in_answer = in_tip = False; continue

        # Question number + text
        m = re.match(r'^(\*\*)?(?:###\s*)?(Q\d+)[:\.\)]\s*(.*)', s)
        if m:
            flush()
            q_num = m.group(2); q_text = m.group(3) or ""
            in_answer = in_tip = False; continue

        # Metadata lines
        if re.search(r'\btype\b\s*:', s, re.I):
            q_type = _clean(re.split(r'type\s*:', s, flags=re.I, maxsplit=1)[-1])
            in_answer = in_tip = False; continue
        if re.search(r'\bdifficulty\b\s*:', s, re.I):
            q_diff = _clean(re.split(r'difficulty\s*:', s, flags=re.I, maxsplit=1)[-1])
            in_answer = in_tip = False; continue

        # Answer block
        if re.search(r'✅|answer\s*:', s, re.I):
            in_answer = True; in_tip = False
            val = re.split(r'answer\s*:', s, flags=re.I, maxsplit=1)[-1].replace('✅', '').strip()
            if val:
                answer_lines.append(val)
            continue

        # Tip block
        if re.search(r'💡|tip\s*:', s, re.I):
            in_answer = False; in_tip = True
            tip_text = re.split(r'tip\s*:', s, flags=re.I, maxsplit=1)[-1].replace('💡', '').strip()
            continue

        # Continuation lines
        if in_answer and q_text:
            answer_lines.append(s)
        elif in_tip and q_text:
            tip_text += ' ' + s

    flush()


def render_question_bank(target_role, auto_skills, experience_level):
    if "interview_type_selected" not in st.session_state:
        st.session_state.interview_type_selected = "Full interview"

    st.markdown("##### Interview type")
    col1, col2, col3 = st.columns(3)
    with col1:
        is_full = st.session_state.interview_type_selected == "Full interview"
        if st.button("Full Interview", key="btn_full", use_container_width=True,
                     type="primary" if is_full else "secondary"):
            st.session_state.interview_type_selected = "Full interview"; st.rerun()
    with col2:
        is_tech = st.session_state.interview_type_selected == "Technical only"
        if st.button("Technical Only", key="btn_tech", use_container_width=True,
                     type="primary" if is_tech else "secondary"):
            st.session_state.interview_type_selected = "Technical only"; st.rerun()
    with col3:
        is_hr = st.session_state.interview_type_selected == "HR only"
        if st.button("HR Only", key="btn_hr", use_container_width=True,
                     type="primary" if is_hr else "secondary"):
            st.session_state.interview_type_selected = "HR only"; st.rerun()

    interview_type = st.session_state.interview_type_selected

    type_info = {
        "Full interview": (ICONS["target"], "Full interview",  "Technical, HR and conceptual rounds combined."),
        "Technical only": (ICONS["brain"],  "Technical only",  "Role-specific technical questions only."),
        "HR only":        (ICONS["user"],   "HR only",         "Behavioral and situational questions with STAR answers."),
    }
    icon, title, desc = type_info[interview_type]
    render_iv_panel(icon, title, f"{desc} &nbsp;·&nbsp; 15 Easy · 15 Medium · 10 Hard = 40 questions")

    st.divider()

    if st.button("Generate interview questions", type="primary", key="qbank_gen"):
        with st.spinner(f"Generating 40 questions for {target_role}…"):
            questions = generate_interview_questions(
                target_role=target_role, extracted_skills=auto_skills,
                experience_level=experience_level, interview_type=interview_type)
        st.session_state.qbank_result = questions

    if "qbank_result" in st.session_state:
        questions = st.session_state.qbank_result
        st.success("40 questions with answers are ready.")
        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total", "40"); m2.metric("Easy", "15")
        m3.metric("Medium", "15"); m4.metric("Hard", "10")
        render_iv_panel(
            ICONS["layers"],
            f"{target_role} · {experience_level} · {interview_type}", ""
        )
        st.divider()
        _parse_and_render_questions(questions)
        st.divider()
        pdf_bytes = generate_pdf(
            text=questions,
            title="Interview Questions & Answers",
            subtitle=f"{target_role}  ·  {experience_level}  ·  {interview_type}"
        )
        st.download_button(
            "📥 Download Questions & Answers as PDF",
            data=pdf_bytes,
            file_name=f"interview_{target_role}_{experience_level}.pdf",
            mime="application/pdf",
        )


# =========================================================================== #
# MOCK INTERVIEW COACH MODE
# =========================================================================== #
def _start_coach(target_role, experience_level, interview_type, auto_skills, num_q):
    projects = missing = []
    if "latest_analysis" in st.session_state:
        data     = st.session_state.latest_analysis
        projects = data.get("projects", []) or []
        missing  = data.get("missing_skills", []) or []
    with st.spinner("Preparing your personalized interview…"):
        raw = generate_coach_questions(
            target_role=target_role, extracted_skills=auto_skills,
            experience_level=experience_level, interview_type=interview_type,
            num_questions=num_q, projects=projects, missing_skills=missing)
    questions = cp.parse_questions(raw)
    if not questions:
        st.error("Could not generate questions right now. Please try again.")
        return
    cs.init_session(questions, meta={"role": target_role,
                                     "level": experience_level,
                                     "type": interview_type})
    st.rerun()


def _render_final_report(target_role, experience_level):
    report = cs.get_report()
    if report is None:
        with st.spinner("Compiling your final report…"):
            raw = generate_final_report(target_role, experience_level, cs.build_summary())
        report = cp.parse_report(raw)
        cs.set_report(report)

    if not report.get("ok", True):
        st.warning("The report was generated with limited data.")

    render_iv_page_header(ICONS["layers"], "Interview Report",
                          "Your performance summary and improvement plan.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Overall score",  f"{report['overall_score']}/10")
    c2.metric("Readiness",      f"{report['readiness_percent']}%")
    c3.metric("Recommendation", report["hiring_recommendation"])
    st.progress(min(report["readiness_percent"], 100) / 100)
    st.divider()

    t1, t2, t3, t4 = st.tabs(["Strengths", "Weaknesses", "Improvement plan", "Recommended topics"])
    with t1:
        for s in report["strengths"] or ["No specific strengths captured."]:
            st.markdown(f"- {s}")
    with t2:
        for w in report["weaknesses"] or ["No specific weaknesses captured."]:
            st.markdown(f"- {w}")
        top = cs.top_weaknesses(5)
        if top:
            st.caption("Weak areas by frequency:")
            for cat, cnt in top:
                st.markdown(f"- {cat} ({cnt})")
    with t3:
        for p in report["improvement_plan"] or ["Keep practicing mock interviews."]:
            st.markdown(f"- {p}")
    with t4:
        for topic in report["recommended_topics"] or ["Core fundamentals for your role."]:
            st.markdown(f"- {topic}")

    st.divider()
    if st.button("🔄 Retake interview", type="primary", key="retake"):
        cs.clear_pending(); cs.reset_session(); st.rerun()


def render_coach(target_role, experience_level, auto_skills):
    if not cs.has_session():
        render_iv_panel(ICONS["brain"], "Mock Interview Coach",
                        "A live, resume-aware interview. Answer each question, "
                        "get instant feedback, and receive a final report.")
        itype = st.selectbox("Interview type",
                             ["Full interview", "Technical only", "HR only"], key="coach_type")
        num_q = st.slider("Number of questions", 5, 12, 8, key="coach_numq")
        if st.button("Start mock interview", type="primary", key="coach_start"):
            _start_coach(target_role, experience_level, itype, auto_skills, num_q)
        return

    if cs.is_finished():
        _render_final_report(target_role, experience_level)
        return

    answered = cs.answered_count()
    pending  = cs.get_pending()

    st.progress(cs.progress_fraction())
    pc1, pc2 = st.columns([3, 1])
    pc1.caption(f"Question {answered + 1} of {cs.total_questions()}")
    pc2.metric("Avg score", f"{cs.average_score()}/10")

    q = cs.current_question()
    if q is None:
        s = cs.get_session()
        if s: s["finished"] = True
        st.rerun(); return

    render_iv_question_card(
        q_num  = f"Question {answered + 1}",
        q_text = q["question"],
        q_diff = q["difficulty"],
        q_type = q["type"],
        answer = "",
        tip    = "",
    )

    if pending and pending.get("q_id") == q["id"]:
        evaluation = pending["evaluation"]
        sc = evaluation["scores"]
        st.text_area("Your answer", value=pending["answer"], height=160,
                     key=f"ans_view_{q['id']}", disabled=True)
        st.markdown(
            '<div class="rm-iv-answer" style="border-color:rgba(129,140,248,.3);">'
            '<div class="rm-iv-answer-label" style="color:#818cf8;">FEEDBACK</div>'
            f'<div class="rm-iv-answer-text" style="color:#e0e7ff;">{evaluation["feedback"]}</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        m = st.columns(6)
        m[0].metric("Technical", sc["technical_accuracy"])
        m[1].metric("Comm.",     sc["communication"])
        m[2].metric("Clarity",   sc["clarity"])
        m[3].metric("Confidence",sc["confidence"])
        m[4].metric("Problem",   sc["problem_solving"])
        m[5].metric("Depth",     sc["depth"])
        nb1, nb2 = st.columns([3, 1])
        with nb1:
            if st.button("Next question →", type="primary", key=f"next_{q['id']}"):
                cs.clear_pending(); cs.advance(); st.rerun()
        with nb2:
            if st.button("End interview", key=f"end_eval_{q['id']}"):
                cs.clear_pending()
                s = cs.get_session()
                if s: s["finished"] = True
                st.rerun()
        return

    answer = st.text_area("Your answer", key=f"ans_{q['id']}", height=160,
                          placeholder="Type your answer here…")
    b1, b2, b3 = st.columns([2, 1, 1])
    with b1:
        submit = st.button("Submit answer", type="primary", key=f"sub_{q['id']}")
    with b2:
        skip = st.button("Skip", key=f"skip_{q['id']}")
    with b3:
        end  = st.button("End interview", key=f"end_{q['id']}")

    if submit:
        if not (answer or "").strip():
            st.warning("Please type an answer, or use Skip."); st.stop()
        if (existing := cs.get_pending()) and existing.get("q_id") == q["id"]:
            st.rerun(); return
        with st.spinner("Evaluating your answer…"):
            raw = evaluate_answer(q["question"], answer, target_role)
        evaluation = cp.parse_evaluation(raw)
        cs.record_turn(q, answer, evaluation)
        cs.set_pending(q["id"], answer, evaluation)
        st.rerun()

    if skip: cs.clear_pending(); cs.advance(); st.rerun()
    if end:
        s = cs.get_session()
        if s: s["finished"] = True
        st.rerun()


# =========================================================================== #
# PAGE ENTRY
# =========================================================================== #
def render_interview():
    render_iv_page_header(
        ICONS["mic"],
        "AI Interview Preparation",
        "Practice with a 40-question bank or a live, resume-aware AI coach.",
    )

    auto_role = ""; auto_skills = []; auto_level = "Fresher"

    if "latest_analysis" in st.session_state:
        data       = st.session_state.latest_analysis
        auto_role  = data.get("role", "")
        auto_skills= data.get("skills", [])
        auto_level = data.get("experience_level", "Fresher")
        render_iv_stat_row([
            (f"{ICONS['target']} Target role",    auto_role or "—"),
            (f"{ICONS['chart']} Level",            auto_level),
            (f"{ICONS['tools']} Skills detected",  len(auto_skills)),
        ])
        st.success("Auto-filled from your resume analysis.")
    else:
        st.info("Tip: analyze your resume first to get personalized questions.")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        default_idx = ROLES_LIST.index(auto_role) if auto_role in ROLES_LIST else 0
        target_role = st.selectbox("Target role", ROLES_LIST, index=default_idx)
    with col2:
        levels = ["Fresher", "Mid-Level (1-3 years)", "Senior (3+ years)"]
        default_level = levels.index(auto_level) if auto_level in levels else 0
        experience_level = st.selectbox("Experience level", levels, index=default_level)

    st.divider()
    mode = st.radio("Mode", ["Question Bank", "Mock Interview Coach"],
                    horizontal=True, key="interview_mode")
    st.divider()

    if mode == "Question Bank":
        render_question_bank(target_role, auto_skills, experience_level)
    else:
        render_coach(target_role, experience_level, auto_skills)

    if "latest_analysis" not in st.session_state:
        st.divider()
        st.warning("Your resume has not been analyzed yet.")
        st.info("Upload and analyze your resume in the Resume Analyzer, "
                "then return here for personalized questions.")