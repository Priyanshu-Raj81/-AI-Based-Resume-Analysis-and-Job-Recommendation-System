"""
coach_state.py
--------------
Session-state manager for the AI Interview Coach.
Pure logic over st.session_state["coach"]. No AI calls here.
"""

import streamlit as st

COACH_KEY = "coach"


# ---------- Lifecycle ----------
def init_session(questions, meta=None):
    st.session_state[COACH_KEY] = {
        "active": True,
        "questions": questions or [],
        "index": 0,
        "turns": [],
        "weakness_tally": {},
        "finished": False,
        "report": None,
        "pending": None,
        "meta": meta or {},
    }


def reset_session():
    st.session_state.pop(COACH_KEY, None)


def has_session() -> bool:
    return COACH_KEY in st.session_state and bool(st.session_state[COACH_KEY].get("active"))


def get_session() -> dict:
    return st.session_state.get(COACH_KEY, {})


# ---------- Navigation / progress ----------
def total_questions() -> int:
    return len(get_session().get("questions", []))


def current_index() -> int:
    return get_session().get("index", 0)


def current_question():
    s = get_session()
    qs = s.get("questions", [])
    i = s.get("index", 0)
    if 0 <= i < len(qs):
        return qs[i]
    return None


def answered_count() -> int:
    return len(get_session().get("turns", []))


def progress_fraction() -> float:
    total = total_questions()
    return (answered_count() / total) if total else 0.0


def advance():
    s = get_session()
    if not s:
        return
    s["index"] = s.get("index", 0) + 1
    if s["index"] >= total_questions():
        s["finished"] = True


def is_finished() -> bool:
    return get_session().get("finished", False)


# ---------- Recording + weakness tally ----------
def record_turn(question, user_answer, evaluation):
    s = get_session()
    if not s:
        return
    s["turns"].append({
        "q_id": question.get("id"),
        "question": question.get("question", ""),
        "type": question.get("type", ""),
        "difficulty": question.get("difficulty", ""),
        "focus_skill": question.get("focus_skill", ""),
        "answer": (user_answer or "").strip(),
        "scores": evaluation.get("scores", {}),
        "overall": evaluation.get("overall", 0),
        "weakness": evaluation.get("weakness_category", "General"),
        "feedback": evaluation.get("feedback", ""),
    })
    cat = evaluation.get("weakness_category", "General")
    if (user_answer or "").strip():
        s["weakness_tally"][cat] = s["weakness_tally"].get(cat, 0) + 1


def average_score() -> float:
    turns = get_session().get("turns", [])
    if not turns:
        return 0.0
    return round(sum(t.get("overall", 0) for t in turns) / len(turns), 1)


def top_weaknesses(n=3):
    tally = get_session().get("weakness_tally", {})
    return sorted(tally.items(), key=lambda kv: kv[1], reverse=True)[:n]


# ---------- Pending feedback (between Submit and Next) ----------
def set_pending(question_id, answer, evaluation):
    s = get_session()
    if s:
        s["pending"] = {"q_id": question_id, "answer": answer, "evaluation": evaluation}


def get_pending():
    return get_session().get("pending")


def clear_pending():
    s = get_session()
    if s:
        s.pop("pending", None)


# ---------- Final report support ----------
def build_summary() -> str:
    s = get_session()
    turns = s.get("turns", [])
    meta = s.get("meta", {})
    lines = [
        f"Role: {meta.get('role', 'N/A')}",
        f"Level: {meta.get('level', 'N/A')}",
        f"Interview type: {meta.get('type', 'N/A')}",
        f"Questions answered: {len(turns)} / {total_questions()}",
        f"Average score: {average_score()}/10",
        "",
        "Per-question results:",
    ]
    for i, t in enumerate(turns, 1):
        scores = t.get("scores", {})
        score_str = ", ".join(f"{k}:{v}" for k, v in scores.items())
        lines.append(
            f"{i}. [{t.get('difficulty','?')}/{t.get('type','?')}] "
            f"{t.get('question','')[:90]} | overall {t.get('overall',0)}/10 "
            f"| weak: {t.get('weakness','General')} | {score_str}"
        )
    tally = s.get("weakness_tally", {})
    if tally:
        weak_str = ", ".join(f"{k} ({v})" for k, v in
                             sorted(tally.items(), key=lambda kv: kv[1], reverse=True))
        lines += ["", f"Weakness frequency: {weak_str}"]
    return "\n".join(lines)


def set_report(report: dict):
    s = get_session()
    if s:
        s["report"] = report
        s["finished"] = True


def get_report():
    return get_session().get("report")
