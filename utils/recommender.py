import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from utils.scorer import calculate_score_from_dataset, calculate_similarity_score

# Dynamic path — works on local, Streamlit Cloud, and any deployment
BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "dataset", "jobs_2026_market_data.csv")


@st.cache_data
def load_job_data() -> pd.DataFrame:
    """Load the 2026 job market dataset."""
    if not os.path.exists(DATASET_PATH):
        st.warning("⚠️ Job dataset not found. Please ensure the dataset file is present in the `dataset/` folder.")
        return pd.DataFrame()
    try:
        df = pd.read_csv(DATASET_PATH)
        df = df.dropna(subset=["Job Title", "Key Skills"])
        # Normalize skills for TF-IDF vectorization
        df["Clean_Skills"] = df["Key Skills"].apply(
            lambda x: str(x).replace("|", " ").replace(",", " ").lower()
        )
        return df
    except Exception as e:
        st.error(f"❌ Failed to load job dataset: {e}")
        return pd.DataFrame()


def get_role_ats_score(resume_skills_list: list, target_role: str, df: pd.DataFrame) -> tuple:
    """
    Compute ATS score and missing skills for a given role using dataset.

    Uses calculate_score_from_dataset() which fetches required skills
    directly from the 2026 jobs CSV — accurate, market-driven results.

    Args:
        resume_skills_list: Skills extracted from resume
        target_role:        Target job role string
        df:                 Loaded jobs DataFrame

    Returns:
        (ats_score: int, missing_skills: list[str])
    """
    if df.empty:
        return 0, []
    return calculate_score_from_dataset(resume_skills_list, target_role, df)


def get_job_missing_skills(resume_skills_list: list, job_key_skills: str) -> tuple:
    """
    For a specific job listing, compute match score and missing skills
    by comparing resume skills against that job's actual required skills.

    Args:
        resume_skills_list: Skills from resume
        job_key_skills:     Raw "Key Skills" value from dataset row

    Returns:
        (match_score: int, matched: list[str], missing: list[str])
    """
    resume_lower = [s.lower().strip() for s in resume_skills_list]

    # Parse job's required skills from CSV column
    required = [
        s.strip().lower()
        for s in str(job_key_skills).split(",")
        if s.strip()
    ]

    if not required:
        return 0, [], []

    matched = [s for s in required if s in resume_lower]
    missing = [s for s in required if s not in resume_lower]

    score = round((len(matched) / len(required)) * 100)
    return score, [s.title() for s in matched], [s.title() for s in missing[:7]]


def recommend_jobs(resume_skills_list: list, df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """
    Recommend top N jobs from dataset based on resume skills.

    Scoring uses TF-IDF cosine similarity for ranking,
    then per-job actual skill matching for display.

    Args:
        resume_skills_list: Skills extracted from resume
        df:                 Loaded jobs DataFrame
        top_n:              Number of jobs to return

    Returns:
        DataFrame with top N jobs + Match_Score + Matched_Skills + Missing_Skills columns
    """
    if df.empty or not resume_skills_list:
        return pd.DataFrame()

    resume_skills_str = " ".join(resume_skills_list).lower()

    try:
        # TF-IDF for ranking
        vectorizer        = TfidfVectorizer()
        job_skills_matrix = vectorizer.fit_transform(df["Clean_Skills"])
        resume_vector     = vectorizer.transform([resume_skills_str])

        similarity_scores = cosine_similarity(resume_vector, job_skills_matrix).flatten()
        top_indices       = similarity_scores.argsort()[-top_n:][::-1]

        recommended = df.iloc[top_indices].copy()

        # Per-job accurate skill matching from dataset
        match_scores, matched_list, missing_list = [], [], []
        for _, row in recommended.iterrows():
            score, matched, missing = get_job_missing_skills(
                resume_skills_list, row["Key Skills"]
            )
            match_scores.append(score)
            matched_list.append(matched)
            missing_list.append(missing)

        recommended["Match_Score"]    = match_scores
        recommended["Matched_Skills"] = matched_list
        recommended["Missing_Skills"] = missing_list

        # Build output columns
        cols = ["Job Title", "Job Salary", "Location", "Key Skills",
                "Match_Score", "Matched_Skills", "Missing_Skills"]
        if "Apply Link"   in df.columns: cols.append("Apply Link")
        if "Description"  in df.columns: cols.append("Description")

        return recommended[cols]

    except Exception as e:
        st.error(f"❌ Job recommendation failed: {e}")
        return pd.DataFrame()