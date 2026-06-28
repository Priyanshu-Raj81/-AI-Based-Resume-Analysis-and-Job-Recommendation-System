"""
utils/scorer.py
---------------
ATS scoring and skill gap analysis for Resumatch AI.

Primary source: role_skills_dataset.csv (curated 2026 role-to-skills mapping)
Fallback:       TF-IDF cosine similarity on job description text
"""

import os
import re
import pandas as pd
from functools import lru_cache
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.nlp_extractor import COMMON_SKILLS

# ── Dataset path ──────────────────────────────────────────────────────────────
BASE_DIR          = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROLE_SKILLS_PATH  = os.path.join(BASE_DIR, "dataset", "role_skills_dataset.csv")


# ── Load role-skills dataset once ─────────────────────────────────────────────
@lru_cache(maxsize=1)
def _load_role_skills_df():
    """Load and cache the role-skills mapping dataset."""
    if not os.path.exists(ROLE_SKILLS_PATH):
        return pd.DataFrame()
    try:
        df = pd.read_csv(ROLE_SKILLS_PATH)
        # Normalize role names for matching
        df["Role_Lower"] = df["Role"].str.lower().str.strip()
        return df
    except Exception:
        return pd.DataFrame()


def _get_role_skills_from_csv(target_role: str) -> dict:
    """
    Fetch must-have and good-to-have skills for a role from CSV.

    Returns:
        {
            "must_have": ["python", "sql", ...],
            "good_to_have": ["docker", "aws", ...],
            "all": ["python", "sql", "docker", ...]
        }
        or empty dict if role not found.
    """
    df = _load_role_skills_df()
    if df.empty:
        return {}

    role_lower = target_role.lower().strip()

    # Level 1 — Exact match
    match = df[df["Role_Lower"] == role_lower]

    # Level 2 — Partial match (role string contains CSV role)
    if match.empty:
        match = df[df["Role_Lower"].apply(lambda r: r in role_lower or role_lower in r)]

    # Level 3 — Word-level match
    if match.empty:
        role_words = set(role_lower.split())
        scores = df["Role_Lower"].apply(
            lambda r: len(role_words & set(r.split()))
        )
        best_idx = scores.idxmax()
        if scores[best_idx] > 0:
            match = df.iloc[[best_idx]]

    if match.empty:
        return {}

    row = match.iloc[0]
    must_have     = [s.strip().lower() for s in str(row["Must_Have_Skills"]).split(",")  if s.strip()]
    good_to_have  = [s.strip().lower() for s in str(row["Good_To_Have_Skills"]).split(",") if s.strip()]

    return {
        "must_have":    must_have,
        "good_to_have": good_to_have,
        "all":          must_have + good_to_have,
        "role_name":    row["Role"],
    }


def get_ats_score(matched_count: int, total_count: int) -> int:
    """Clean ATS score — actual percentage, no artificial penalties."""
    if total_count == 0:
        return 0
    return min(round((matched_count / total_count) * 100), 100)


def calculate_similarity_score(resume_skills_list: list,
                                job_skills_str: str = "",
                                target_role: str = "") -> tuple:
    """
    Main scoring function — returns (ats_score, missing_skills).

    Priority:
        1. role_skills_dataset.csv — curated 2026 market mapping
        2. TF-IDF on job description text (fallback)

    Args:
        resume_skills_list: Skills extracted from resume
        job_skills_str:     Raw job skills string (for TF-IDF fallback)
        target_role:        Target job role (for CSV lookup)

    Returns:
        (ats_score: int, missing_skills: list[str])
    """
    if not resume_skills_list:
        return 0, []

    resume_lower = [s.lower().strip() for s in resume_skills_list]

    # ── Primary: CSV-based role matching ─────────────────────────
    role_data = _get_role_skills_from_csv(target_role) if target_role else {}

    if role_data:
        must_have    = role_data["must_have"]
        good_to_have = role_data["good_to_have"]

        # Match against must-have skills for ATS score
        must_matched  = [s for s in must_have    if s in resume_lower]
        must_missing  = [s for s in must_have    if s not in resume_lower]
        good_matched  = [s for s in good_to_have if s in resume_lower]
        good_missing  = [s for s in good_to_have if s not in resume_lower]

        # ATS score weighted: must-have = 70%, good-to-have = 30%
        must_score = get_ats_score(len(must_matched), len(must_have))   if must_have    else 0
        good_score = get_ats_score(len(good_matched), len(good_to_have)) if good_to_have else 0
        ats_score  = round(must_score * 0.70 + good_score * 0.30)

        # Missing skills: must-have first (more important), then good-to-have
        missing_skills = [s.title() for s in must_missing[:5]] + \
                         [s.title() for s in good_missing[:2]]

        return ats_score, missing_skills[:7]

    # ── Fallback: TF-IDF on job skills string ────────────────────
    if not job_skills_str:
        return 0, []

    resume_str = " ".join(resume_lower)
    job_str    = job_skills_str.lower()

    try:
        vectorizer   = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([resume_str, job_str])
        match_score  = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        ats_score    = min(round(match_score * 100), 100)
    except Exception:
        ats_score = 0

    job_has_skills = [
        skill for skill in COMMON_SKILLS
        if re.search(r'\b' + re.escape(skill) + r'\b', job_str)
    ]
    missing_skills = [
        s.title() for s in job_has_skills
        if s.lower() not in resume_lower
    ][:7]

    return ats_score, missing_skills


def get_skill_gap_analysis(resume_skills_list: list, target_role: str) -> dict:
    """
    Full skill gap breakdown for Resume Analyzer page.

    Returns detailed analysis including must-have vs good-to-have breakdown.

    Args:
        resume_skills_list: Skills from resume
        target_role:        Target job role

    Returns:
        {
            "ats_score":       int,
            "must_matched":    list,
            "must_missing":    list,
            "good_matched":    list,
            "good_missing":    list,
            "missing_skills":  list,   # combined for display
            "role_found":      bool,
        }
    """
    resume_lower = [s.lower().strip() for s in resume_skills_list]
    role_data    = _get_role_skills_from_csv(target_role)

    if not role_data:
        ats_score, missing = calculate_similarity_score(
            resume_skills_list, "", target_role
        )
        return {
            "ats_score":    ats_score,
            "must_matched": [],
            "must_missing": missing,
            "good_matched": [],
            "good_missing": [],
            "missing_skills": missing,
            "role_found":   False,
        }

    must_have    = role_data["must_have"]
    good_to_have = role_data["good_to_have"]

    must_matched  = [s for s in must_have    if s in resume_lower]
    must_missing  = [s for s in must_have    if s not in resume_lower]
    good_matched  = [s for s in good_to_have if s in resume_lower]
    good_missing  = [s for s in good_to_have if s not in resume_lower]

    must_score = get_ats_score(len(must_matched), len(must_have))    if must_have    else 0
    good_score = get_ats_score(len(good_matched), len(good_to_have)) if good_to_have else 0
    ats_score  = round(must_score * 0.70 + good_score * 0.30)

    missing_skills = [s.title() for s in must_missing[:5]] + \
                     [s.title() for s in good_missing[:2]]

    return {
        "ats_score":    ats_score,
        "must_matched": [s.title() for s in must_matched],
        "must_missing": [s.title() for s in must_missing],
        "good_matched": [s.title() for s in good_matched],
        "good_missing": [s.title() for s in good_missing],
        "missing_skills": missing_skills[:7],
        "role_found":   True,
    }


# ── Backwards compatibility ───────────────────────────────────────────────────
def calculate_score_from_dataset(resume_skills_list: list,
                                  target_role: str, df=None) -> tuple:
    """Backwards-compatible wrapper — now uses CSV instead of jobs dataset."""
    return calculate_similarity_score(resume_skills_list, "", target_role)