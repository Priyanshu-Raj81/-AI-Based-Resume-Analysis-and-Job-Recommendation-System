import os
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

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "what": role,
        "results_per_page": results_per_page,
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

    return {"ok": True, "error": None, "jobs": jobs}