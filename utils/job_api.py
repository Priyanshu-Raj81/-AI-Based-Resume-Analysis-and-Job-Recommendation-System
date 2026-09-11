import os
import re
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def _get_secret(key: str):
    """
    Read a credential from (in order): environment variables (.env locally),
    then st.secrets (Streamlit Cloud's Settings > Secrets panel).
    """
    value = os.getenv(key)
    if value:
        return value
    try:
        return st.secrets.get(key)
    except Exception:
        return None


ADZUNA_APP_ID = _get_secret("ADZUNA_APP_ID")
ADZUNA_APP_KEY = _get_secret("ADZUNA_APP_KEY")
BASE_URL = "https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"


def is_configured() -> bool:
    """True if Adzuna credentials are present in the environment."""
    return bool(ADZUNA_APP_ID and ADZUNA_APP_KEY)


def _normalize(text: str) -> str:
    """Lowercase, strip punctuation/extra whitespace for fuzzy-safe comparison."""
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _dedupe_jobs(jobs: list) -> list:
    """
    Adzuna aggregates the same underlying job posting from many job boards
    and recruiters, so identical (title, company) pairs — and sometimes
    exact duplicate descriptions — commonly appear multiple times in one
    response. Collapse those down to a single listing, keeping the first
    (Adzuna's own relevance-ranked) occurrence.
    """
    seen_keys = set()
    seen_descriptions = set()
    unique_jobs = []

    for job in jobs:
        key = (_normalize(job["title"]), _normalize(job["company"]), _normalize(job["location"]))
        desc_key = _normalize(job.get("description", ""))[:300]  # fingerprint, not full text

        if key in seen_keys:
            continue
        if desc_key and desc_key in seen_descriptions:
            continue

        seen_keys.add(key)
        if desc_key:
            seen_descriptions.add(desc_key)
        unique_jobs.append(job)

    return unique_jobs


@st.cache_data(ttl=21600, show_spinner=False)  # 6h — this is a homepage stat, not a search result
def get_live_it_job_count(country: str = "in"):
    """
    Total number of currently-live IT-category job ads in Adzuna's index for
    this country. Used for an honest "live openings" homepage stat instead
    of summing a static, hand-curated dataset.

    Returns an int on success, or None if Adzuna isn't configured / the
    call fails — callers should fall back to a clearly-labeled static
    estimate in that case rather than showing a broken stat.
    """
    if not is_configured():
        return None

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "category": "it-jobs",
        "results_per_page": 1,  # we only need the "count" field, not the results
        "content-type": "application/json",
    }
    url = BASE_URL.format(country=country, page=1)

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return None
        data = response.json()
        count = data.get("count")
        return int(count) if count is not None else None
    except (requests.RequestException, ValueError, TypeError):
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def search_live_jobs(role: str, location: str = "", country: str = "in", results_per_page: int = 15):
    """
    Fetch real, live job listings from Adzuna.

    Cached for 1 hour per (role, location, country) combination — avoids
    re-hitting the API on every Streamlit rerun and helps stay within the
    free-tier rate limit.

    Returns:
        {
            "ok": bool,
            "error": str | None,   # human-readable reason when ok is False
            "jobs": [
                {
                    "title": str,
                    "company": str,
                    "location": str,
                    "salary_min": float | None,
                    "salary_max": float | None,
                    "apply_link": str,
                    "description": str,   # used for real NLP skill extraction
                    "posted": str,
                },
                ...
            ],
        }
    """
    if not is_configured():
        return {
            "ok": False,
            "error": "Adzuna API keys not configured. Add ADZUNA_APP_ID and "
                     "ADZUNA_APP_KEY to your .env file.",
            "jobs": [],
        }

    # Fetch extra results beyond what's requested — deduplication (see below)
    # removes a meaningful chunk of Adzuna's raw results, so over-fetching
    # keeps us from returning fewer jobs than the caller asked for.
    fetch_count = min(max(results_per_page * 2, 30), 50)  # Adzuna caps at 50/page

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "what": role,
        "results_per_page": fetch_count,
        "content-type": "application/json",
    }
    if location:
        params["where"] = location

    url = BASE_URL.format(country=country, page=1)

    try:
        response = requests.get(url, params=params, timeout=10)
    except requests.RequestException as e:
        return {"ok": False, "error": f"Network error reaching Adzuna: {e}", "jobs": []}

    if response.status_code == 429:
        return {"ok": False, "error": "Adzuna rate limit reached. Try again shortly.", "jobs": []}
    if response.status_code != 200:
        return {"ok": False, "error": f"Adzuna API returned status {response.status_code}.", "jobs": []}

    try:
        data = response.json()
    except ValueError:
        return {"ok": False, "error": "Adzuna returned an unreadable response.", "jobs": []}

    jobs = []
    for item in data.get("results", []):
        company_name = (item.get("company") or {}).get("display_name") or "Unknown"
        location_name = (item.get("location") or {}).get("display_name") or (location or "India")
        jobs.append({
            "title": (item.get("title") or "").strip(),
            "company": company_name,
            "location": location_name,
            "salary_min": item.get("salary_min"),
            "salary_max": item.get("salary_max"),
            "apply_link": item.get("redirect_url", ""),
            "description": item.get("description", ""),
            "posted": item.get("created", ""),
        })

    jobs = _dedupe_jobs(jobs)[:results_per_page]

    return {"ok": True, "error": None, "jobs": jobs}