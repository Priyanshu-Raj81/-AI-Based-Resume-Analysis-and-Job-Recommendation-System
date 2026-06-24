import streamlit as st
import re
from utils.ai_suggestions import (
    generate_interview_questions,
    generate_coach_questions,
    evaluate_answer,
    generate_final_report,
)
from utils import coach_parsing as cp
from utils import coach_state as cs

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
    "mic":   '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>',
    "target":'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
    "chart": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
    "tools": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a4 4 0 0 0-5.6 5.6L3 18v3h3l6.1-6.1a4 4 0 0 0 5.6-5.6l-2.5 2.5-2-2 2.5-2.5z"/></svg>',
    "brain": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.94-.55z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.94-.55z"/></svg>',
    "user":  '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    "layers":'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>',
}


def clean_text(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'#{1,6}\s*', '', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    text = text.replace('- **', '').replace('**', '')
    return text.strip()


def _inject_theme():
    st.markdown("""
    <style>
      :root {
        --primary:#4f46e5; --primary-600:#4338ca; --primary-soft:rgba(79,70,229,.10);
        --bg:#0f1117; --surface:#171a23; --surface-2:#1e222e; --border:#2a2f3a;
        --text:#e6e8ee; --text-muted:#9aa1b1;
        --success:#16a34a; --warning:#d97706; --danger:#dc2626;
        --radius:12px; --gap:16px;
      }
      @keyframes fadeIn { from {opacity:0; transform:translateY(6px);} to {opacity:1; transform:none;} }
      .fade { animation: fadeIn .22s ease both; }
      .pi-header { background:var(--surface); border:1px solid var(--border);
        border-radius:var(--radius); padding:28px 30px; margin-bottom:24px;
        display:flex; align-items:center; gap:16px; }
      .pi-header .icon { width:48px; height:48px; border-radius:10px; flex:none;
        display:flex; align-items:center; justify-content:center;
        background:var(--primary-soft); color:var(--primary); }
      .pi-header h1 { color:var(--text); margin:0; font-size:1.5rem; font-weight:650; letter-spacing:-.01em; }
      .pi-header p  { color:var(--text-muted); margin:4px 0 0; font-size:.92rem; }
      .pi-row { display:flex; gap:var(--gap); margin:8px 0 4px; }
      .pi-stat { background:var(--surface); border:1px solid var(--border);
        border-radius:var(--radius); padding:16px 18px; flex:1;
        transition:border-color .18s ease, transform .18s ease; }
      .pi-stat:hover { border-color:var(--primary); transform:translateY(-2px); }
      .pi-stat .k { display:flex; align-items:center; gap:6px; color:var(--text-muted);
        font-size:.72rem; text-transform:uppercase; letter-spacing:.06em; }
      .pi-stat .v { color:var(--text); font-size:1.25rem; font-weight:650; margin-top:6px; }
      .pi-info { background:var(--surface); border:1px solid var(--border);
        border-left:3px solid var(--primary); border-radius:var(--radius);
        padding:16px 18px; margin:8px 0; }
      .pi-info .t { display:flex; align-items:center; gap:8px; color:var(--text); font-weight:600; }
      .pi-info .d { color:var(--text-muted); font-size:.88rem; margin-top:4px; }
      div.stButton > button[kind="primary"] { background:var(--primary); color:#fff;
        border:1px solid var(--primary-600); border-radius:10px; font-weight:600;
        padding:12px 22px; width:100%; transition:background .15s ease, transform .12s ease; }
      div.stButton > button[kind="primary"]:hover { background:var(--primary-600); }
      div.stButton > button[kind="primary"]:active { transform:translateY(1px); }
      .pi-band { border-radius:10px; padding:12px 16px; margin:20px 0 8px; font-weight:700; font-size:1rem; }
      .band-easy   { background:rgba(22,163,74,.12);  color:#22c55e; border-left:4px solid #22c55e; }
      .band-medium { background:rgba(217,119,6,.12);  color:#f59e0b; border-left:4px solid #f59e0b; }
      .band-hard   { background:rgba(220,38,38,.12);  color:#f87171; border-left:4px solid #f87171; }
      .q-card { background:var(--surface-2); border:1px solid var(--border);
        border-left:4px solid var(--primary); border-radius:10px; padding:16px 18px; margin:10px 0 4px; }
      .q-number { color:var(--primary); font-size:.8rem; font-weight:700;
        text-transform:uppercase; letter-spacing:.05em; margin-bottom:4px; }
      .q-text { color:var(--text); font-size:1rem; font-weight:600; line-height:1.5; }
      .badge-row { display:flex; gap:8px; margin:8px 0 0; flex-wrap:wrap; }
      .badge { padding:3px 10px; border-radius:20px; font-size:.72rem; font-weight:600; border:1px solid currentColor; }
      .badge-easy   { color:#22c55e; background:rgba(22,163,74,.12); }
      .badge-medium { color:#f59e0b; background:rgba(217,119,6,.12); }
      .badge-hard   { color:#f87171; background:rgba(220,38,38,.12); }
      .badge-tech   { color:#818cf8; background:rgba(129,140,248,.12); }
      .badge-hr     { color:#34d399; background:rgba(52,211,153,.12); }
      .badge-concept{ color:#fb923c; background:rgba(251,146,60,.12); }
      .answer-box { background:rgba(22,163,74,.06); border:1px solid rgba(22,163,74,.2);
        border-radius:8px; padding:12px 16px; margin:10px 0 6px; }
      .answer-label { color:#22c55e; font-size:.75rem; font-weight:700; letter-spacing:.04em; margin-bottom:6px; }
      .answer-text  { color:#d1fae5; font-size:.92rem; line-height:1.7; }
      .tip-box { background:rgba(251,191,36,.06); border:1px solid rgba(251,191,36,.2);
        border-radius:8px; padding:10px 14px; margin:4px 0 8px; display:flex; gap:8px; align-items:flex-start; }
      .tip-icon { color:#fbbf24; font-size:14px; flex:none; margin-top:1px; }
      .tip-text { color:#fde68a; font-size:.88rem; line-height:1.6; }
      .fb-box { background:var(--surface-2); border:1px solid var(--border);
        border-left:4px solid var(--primary); border-radius:10px; padding:14px 16px; margin:10px 0; }
      .fb-text { color:var(--text); font-size:.92rem; line-height:1.6; }
    </style>
    """, unsafe_allow_html=True)


# =========================================================================== #
# QUESTION BANK MODE
# =========================================================================== #
def render_question_cards(questions_text):
    lines = questions_text.split('\n')
    q_num = q_text = q_type = q_diff = tip_text = ""
    answer_lines = []
    in_answer = in_tip = False

    def flush():
        nonlocal q_num, q_text, q_type, q_diff, answer_lines, tip_text, in_answer, in_tip
        if not q_text:
            return
        dl = q_diff.lower()
        if 'hard' in dl:
            diff_class, card_border = 'badge-hard', '#f87171'
        elif 'medium' in dl:
            diff_class, card_border = 'badge-medium', '#f59e0b'
        else:
            diff_class, card_border = 'badge-easy', '#22c55e'
        tl = q_type.lower()
        if 'technical' in tl:
            type_class = 'badge-tech'
        elif 'hr' in tl or 'behavioral' in tl:
            type_class = 'badge-hr'
        else:
            type_class = 'badge-concept'
        answer_html = ""
        if answer_lines:
            ans = clean_text(' '.join(answer_lines))
            answer_html = f"<div class='answer-box'><div class='answer-label'>✅ ANSWER</div><div class='answer-text'>{ans}</div></div>"
        tip_html = ""
        if tip_text:
            tip_html = f"<div class='tip-box'><div class='tip-icon'>💡</div><div class='tip-text'>{clean_text(tip_text)}</div></div>"
        badge_diff = f"<span class='badge {diff_class}'>{clean_text(q_diff)}</span>" if q_diff else ""
        badge_type = f"<span class='badge {type_class}'>{clean_text(q_type)}</span>" if q_type else ""
        st.markdown(f"""
            <div class='q-card fade' style='border-left-color:{card_border};'>
                <div class='q-number'>{clean_text(q_num)}</div>
                <div class='q-text'>{clean_text(q_text)}</div>
                <div class='badge-row'>{badge_diff}{badge_type}</div>
                {answer_html}{tip_html}
            </div>""", unsafe_allow_html=True)
        q_num = q_text = q_type = q_diff = tip_text = ""
        answer_lines = []
        in_answer = in_tip = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        up = stripped.upper()
        if '🟢' in stripped or ('EASY' in up and 'QUESTION' in up):
            flush(); st.markdown(f"<div class='pi-band band-easy fade'>🟢 {clean_text(stripped)}</div>", unsafe_allow_html=True); in_answer=in_tip=False; continue
        if '🟡' in stripped or ('MEDIUM' in up and 'QUESTION' in up):
            flush(); st.markdown(f"<div class='pi-band band-medium fade'>🟡 {clean_text(stripped)}</div>", unsafe_allow_html=True); in_answer=in_tip=False; continue
        if '🔴' in stripped or ('HARD' in up and 'QUESTION' in up):
            flush(); st.markdown(f"<div class='pi-band band-hard fade'>🔴 {clean_text(stripped)}</div>", unsafe_allow_html=True); in_answer=in_tip=False; continue
        q_match = re.match(r'^(\*\*)?(?:###\s*)?(Q\d+)[:\.\)]\s*(.*)', stripped)
        if q_match:
            flush(); q_num = q_match.group(2); q_text = q_match.group(3) or ""; in_answer=in_tip=False; continue
        if re.search(r'\btype\b\s*:', stripped, re.I):
            q_type = clean_text(re.split(r'type\s*:', stripped, flags=re.I, maxsplit=1)[-1]); in_answer=in_tip=False; continue
        if re.search(r'\bdifficulty\b\s*:', stripped, re.I):
            q_diff = clean_text(re.split(r'difficulty\s*:', stripped, flags=re.I, maxsplit=1)[-1]); in_answer=in_tip=False; continue
        if re.search(r'✅|answer\s*:', stripped, re.I):
            in_answer=True; in_tip=False
            val = re.split(r'answer\s*:', stripped, flags=re.I, maxsplit=1)[-1].replace('✅','').strip()
            if val: answer_lines.append(val)
            continue
        if re.search(r'💡|tip\s*:', stripped, re.I):
            in_answer=False; in_tip=True
            tip_text = re.split(r'tip\s*:', stripped, flags=re.I, maxsplit=1)[-1].replace('💡','').strip()
            continue
        if in_answer and q_text: answer_lines.append(stripped)
        elif in_tip and q_text: tip_text += ' ' + stripped
    flush()


def render_question_bank(target_role, auto_skills, experience_level):

    # ✅ Session state initialize
    if "interview_type_selected" not in st.session_state:
        st.session_state.interview_type_selected = "Full interview"

    st.markdown("##### Interview type")

    # ✅ 3 styled toggle buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        is_full = st.session_state.interview_type_selected == "Full interview"
        if st.button(
            "🎯 Full Interview",
            key="btn_full",
            use_container_width=True,
            type="primary" if is_full else "secondary"
        ):
            st.session_state.interview_type_selected = "Full interview"
            st.rerun()

    with col2:
        is_tech = st.session_state.interview_type_selected == "Technical only"
        if st.button(
            "🧠 Technical Only",
            key="btn_tech",
            use_container_width=True,
            type="primary" if is_tech else "secondary"
        ):
            st.session_state.interview_type_selected = "Technical only"
            st.rerun()

    with col3:
        is_hr = st.session_state.interview_type_selected == "HR only"
        if st.button(
            "💼 HR Only",
            key="btn_hr",
            use_container_width=True,
            type="primary" if is_hr else "secondary"
        ):
            st.session_state.interview_type_selected = "HR only"
            st.rerun()

    interview_type = st.session_state.interview_type_selected

    # ✅ Info card
    type_info = {
        "Full interview": (ICONS["target"], "Full interview", "Technical, HR and conceptual rounds combined."),
        "Technical only": (ICONS["brain"],  "Technical only", "Role-specific technical questions only."),
        "HR only":        (ICONS["user"],   "HR only",        "Behavioral and situational questions with STAR answers."),
    }
    icon, title, desc = type_info[interview_type]
    st.markdown(f"""
        <div class='pi-info fade'>
            <div class='t'>{icon} {title}</div>
            <div class='d'>{desc} &nbsp;·&nbsp; 15 Easy · 15 Medium · 10 Hard = 40 questions</div>
        </div>""", unsafe_allow_html=True)

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
        st.markdown(f"""
            <div class='pi-info fade' style='margin-top:8px;'>
                <div class='t'>{ICONS['layers']} {target_role} · {experience_level} · {interview_type}</div>
            </div>""", unsafe_allow_html=True)
        st.divider()
        render_question_cards(questions)
        st.divider()
        st.download_button(
            "📥 Download all questions and answers",
            data=questions,
            file_name=f"interview_{target_role}_{experience_level}.txt",
            mime="text/plain"
        )

# =========================================================================== #
# MOCK INTERVIEW COACH MODE
# =========================================================================== #
def _badge(label):
    cls = {"Technical": "badge-tech", "HR": "badge-hr", "Behavioral": "badge-hr",
           "Conceptual": "badge-concept", "Easy": "badge-easy",
           "Medium": "badge-medium", "Hard": "badge-hard"}.get(label, "badge-concept")
    return f"<span class='badge {cls}'>{label}</span>"


def _start_coach(target_role, experience_level, interview_type, auto_skills, num_q):
    projects, missing = [], []
    if "latest_analysis" in st.session_state:
        data = st.session_state.latest_analysis
        projects = data.get("projects", []) or []
        missing = data.get("missing_skills", []) or []
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

    st.markdown(f"""
        <div class='pi-header fade'>
            <div class='icon'>{ICONS['layers']}</div>
            <div><h1>Interview Report</h1>
            <p>Your performance summary and improvement plan.</p></div>
        </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Overall score", f"{report['overall_score']}/10")
    c2.metric("Readiness", f"{report['readiness_percent']}%")
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
        cs.clear_pending()
        cs.reset_session()
        st.rerun()


def render_coach(target_role, experience_level, auto_skills):
    if not cs.has_session():
        st.markdown(f"""
            <div class='pi-info fade'>
                <div class='t'>{ICONS['brain']} Mock Interview Coach</div>
                <div class='d'>A live, resume-aware interview. Answer each question,
                get instant feedback, and receive a final report.</div>
            </div>""", unsafe_allow_html=True)
        itype = st.selectbox("Interview type",
                             ["Full interview", "Technical only", "HR only"], key="coach_type")
        num_q = st.slider("Number of questions", 5, 12, 8, key="coach_numq")
        if st.button("🚀 Start mock interview", type="primary", key="coach_start"):
            _start_coach(target_role, experience_level, itype, auto_skills, num_q)
        return

    if cs.is_finished():
        _render_final_report(target_role, experience_level)
        return

    total = cs.total_questions()
    answered = cs.answered_count()
    pending = cs.get_pending()

    st.progress(cs.progress_fraction())
    pc1, pc2 = st.columns([3, 1])
    pc1.caption(f"Question {answered + 1} of {total}")
    pc2.metric("Avg score", f"{cs.average_score()}/10")

    q = cs.current_question()
    if q is None:
        s = cs.get_session()
        if s:
            s["finished"] = True
        st.rerun()
        return

    st.markdown(f"""
        <div class='q-card fade'>
            <div class='q-number'>Question {answered + 1}</div>
            <div class='q-text'>{q['question']}</div>
            <div class='badge-row'>{_badge(q['type'])}{_badge(q['difficulty'])}</div>
        </div>""", unsafe_allow_html=True)

    if pending and pending.get("q_id") == q["id"]:
        evaluation = pending["evaluation"]
        sc = evaluation["scores"]
        st.text_area("Your answer", value=pending["answer"], height=160,
                     key=f"ans_view_{q['id']}", disabled=True)
        st.markdown(
            f"<div class='fb-box fade'><div class='answer-label' style='color:#818cf8'>FEEDBACK</div>"
            f"<div class='fb-text'>{evaluation['feedback']}</div></div>", unsafe_allow_html=True)
        m = st.columns(6)
        m[0].metric("Technical", sc["technical_accuracy"])
        m[1].metric("Comm.", sc["communication"])
        m[2].metric("Clarity", sc["clarity"])
        m[3].metric("Confidence", sc["confidence"])
        m[4].metric("Problem", sc["problem_solving"])
        m[5].metric("Depth", sc["depth"])
        nb1, nb2 = st.columns([3, 1])
        with nb1:
            if st.button("Next question →", type="primary", key=f"next_{q['id']}"):
                cs.clear_pending(); cs.advance(); st.rerun()
        with nb2:
            if st.button("End interview", key=f"end_eval_{q['id']}"):
                cs.clear_pending()
                s = cs.get_session()
                if s:
                    s["finished"] = True
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
        end = st.button("End interview", key=f"end_{q['id']}")

    if submit:
        if not (answer or "").strip():
            st.warning("Please type an answer, or use Skip.")
            st.stop()
        existing = cs.get_pending()
        if existing and existing.get("q_id") == q["id"]:
            st.rerun()
            return
        with st.spinner("Evaluating your answer…"):
            raw = evaluate_answer(q["question"], answer, target_role)
        evaluation = cp.parse_evaluation(raw)
        cs.record_turn(q, answer, evaluation)
        cs.set_pending(q["id"], answer, evaluation)
        st.rerun()

    if skip:
        cs.clear_pending(); cs.advance(); st.rerun()

    if end:
        s = cs.get_session()
        if s:
            s["finished"] = True
        st.rerun()


# =========================================================================== #
# PAGE ENTRY
# =========================================================================== #
def render_interview():
    _inject_theme()

    # ✅ Title updated
    st.markdown(f"""
        <div class='pi-header fade'>
            <div class='icon'>{ICONS['mic']}</div>
            <div>
                <h1>AI Interview Preparation</h1>
                <p>Practice with a 40-question bank or a live, resume-aware AI coach.</p>
            </div>
        </div>""", unsafe_allow_html=True)

    auto_role, auto_skills, auto_level = "", [], "Fresher"
    if "latest_analysis" in st.session_state:
        data = st.session_state.latest_analysis
        auto_role = data.get("role", "")
        auto_skills = data.get("skills", [])
        auto_level = data.get("experience_level", "Fresher")
        st.markdown(f"""
            <div class='pi-row fade'>
                <div class='pi-stat'><div class='k'>{ICONS['target']} Target role</div>
                    <div class='v'>{auto_role or '—'}</div></div>
                <div class='pi-stat'><div class='k'>{ICONS['chart']} Level</div>
                    <div class='v'>{auto_level}</div></div>
                <div class='pi-stat'><div class='k'>{ICONS['tools']} Skills detected</div>
                    <div class='v'>{len(auto_skills)}</div></div>
            </div>""", unsafe_allow_html=True)
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

    mode = st.radio(
        "Mode",
        ["📚 Question Bank", "🎤 Mock Interview Coach"],
        horizontal=True,
        key="interview_mode"
    )
    st.divider()

    if mode == "📚 Question Bank":
        render_question_bank(target_role, auto_skills, experience_level)
    else:
        render_coach(target_role, experience_level, auto_skills)

    if "latest_analysis" not in st.session_state:
        st.divider()
        st.warning("Your resume has not been analyzed yet.")
        st.info("Upload and analyze your resume in the Resume Analyzer, then return here for personalized questions.")