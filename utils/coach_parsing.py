"""
coach_parsing.py
----------------
Safe parsing layer between Groq AI responses and the AI Interview Coach UI.
Never raises to the caller; always returns a predictable structure.
"""

import json
import re

VALID_TYPES = {"Technical", "HR", "Behavioral", "Conceptual"}
VALID_DIFFICULTY = {"Easy", "Medium", "Hard"}
SCORE_DIMENSIONS = (
    "technical_accuracy", "communication", "clarity",
    "confidence", "problem_solving", "depth",
)


def is_error_response(raw) -> bool:
    return isinstance(raw, str) and raw.strip().startswith("⚠️ Error")


def strip_md(text) -> str:
    if not text:
        return ""
    text = str(text)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"[*_`]", "", text)
    text = re.sub(r"^#{1,6}\s*", "", text.strip(), flags=re.M)
    text = re.sub(r"^\s*[-•]\s*", "", text, flags=re.M)
    return text.strip()


def _extract_json_blob(raw: str):
    if not raw:
        return None
    text = raw.strip()
    text = re.sub(r"```(?:json)?", "", text, flags=re.I).strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    for open_ch, close_ch in (("[", "]"), ("{", "}")):
        start = text.find(open_ch)
        end = text.rfind(close_ch)
        if start != -1 and end != -1 and end > start:
            candidate = text[start:end + 1]
            try:
                return json.loads(candidate)
            except Exception:
                continue
    return None


def _clamp_score(value, lo=0, hi=10, default=5) -> int:
    try:
        n = int(round(float(value)))
    except (TypeError, ValueError):
        return default
    return max(lo, min(hi, n))


def parse_questions(raw) -> list:
    if is_error_response(raw):
        return []
    data = raw if isinstance(raw, list) else _extract_json_blob(raw)
    if isinstance(data, dict):
        data = data.get("questions", [])
    if not isinstance(data, list):
        return []
    out = []
    for i, q in enumerate(data, 1):
        if not isinstance(q, dict):
            continue
        q_type = str(q.get("type", "Technical")).strip().title()
        if q_type not in VALID_TYPES:
            q_type = "Technical"
        diff = str(q.get("difficulty", "Medium")).strip().title()
        if diff not in VALID_DIFFICULTY:
            diff = "Medium"
        question_text = strip_md(q.get("question", ""))
        if not question_text:
            continue
        out.append({
            "id": q.get("id", i),
            "type": q_type,
            "difficulty": diff,
            "question": question_text,
            "focus_skill": strip_md(q.get("focus_skill", "")),
            "based_on": strip_md(q.get("based_on", "general")),
        })
    return out


def parse_evaluation(raw) -> dict:
    fallback = {
        "scores": {dim: 5 for dim in SCORE_DIMENSIONS},
        "overall": 5,
        "weakness_category": "General",
        "feedback": "Evaluation unavailable for this answer. "
                    "Try rephrasing with concrete examples.",
        "ok": False,
    }
    if is_error_response(raw):
        return fallback
    data = raw if isinstance(raw, dict) else _extract_json_blob(raw)
    if not isinstance(data, dict):
        return fallback
    raw_scores = data.get("scores", {}) if isinstance(data.get("scores"), dict) else {}
    scores = {dim: _clamp_score(raw_scores.get(dim, 5)) for dim in SCORE_DIMENSIONS}
    overall = data.get("overall")
    if overall is None:
        overall = round(sum(scores.values()) / len(scores))
    overall = _clamp_score(overall)
    return {
        "scores": scores,
        "overall": overall,
        "weakness_category": strip_md(data.get("weakness_category", "General")) or "General",
        "feedback": strip_md(data.get("feedback", "")) or "No specific feedback returned.",
        "ok": True,
    }


def parse_report(raw) -> dict:
    fallback = {
        "overall_score": 0.0,
        "readiness_percent": 0,
        "strengths": [],
        "weaknesses": [],
        "improvement_plan": [],
        "recommended_topics": [],
        "hiring_recommendation": "Not enough data",
        "ok": False,
    }
    if is_error_response(raw):
        return fallback
    data = raw if isinstance(raw, dict) else _extract_json_blob(raw)
    if not isinstance(data, dict):
        return fallback

    def _list(key):
        v = data.get(key, [])
        if isinstance(v, str):
            v = [v]
        return [strip_md(x) for x in v if str(x).strip()] if isinstance(v, list) else []

    try:
        overall_score = round(float(data.get("overall_score", 0)), 1)
    except (TypeError, ValueError):
        overall_score = 0.0
    readiness = _clamp_score(data.get("readiness_percent", 0), lo=0, hi=100, default=0)
    return {
        "overall_score": max(0.0, min(10.0, overall_score)),
        "readiness_percent": readiness,
        "strengths": _list("strengths"),
        "weaknesses": _list("weaknesses"),
        "improvement_plan": _list("improvement_plan"),
        "recommended_topics": _list("recommended_topics"),
        "hiring_recommendation": strip_md(data.get("hiring_recommendation", "Not enough data"))
                                 or "Not enough data",
        "ok": True,
    }
