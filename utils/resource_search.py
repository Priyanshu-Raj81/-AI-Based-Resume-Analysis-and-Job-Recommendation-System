"""
utils/resource_search.py
-------------------------
Fetches REAL, currently-existing learning resources (YouTube videos + courses)
for a given skill.

YouTube playlists  -> fetched live via the YouTube Data API v3 (real, current
                       results, cached 24h).
Course links       -> constructed directly as platform SEARCH-QUERY URLs
                       (Coursera, Udemy, freeCodeCamp, edX, etc.). No search
                       API is used for this anymore — a platform's own
                       search-query URL pattern is stable and public, so it
                       is guaranteed to load a real results page and never
                       needs an API key, quota, or CSE setup. This replaces
                       the old search_courses() which relied on Google
                       Custom Search (GOOGLE_CSE_API_KEY / GOOGLE_CSE_CX) and
                       could return zero results on quota exhaustion.

Requires (in .env):
    YOUTUBE_API_KEY      — YouTube Data API v3 key (Google Cloud Console)

If YOUTUBE_API_KEY is missing or a request fails (quota exceeded, network
issue, etc.), search_youtube_playlists() fails SILENTLY and returns an empty
list — callers fall back to a plain "search on YouTube" link so the UI never
shows a broken/fake URL. Course links never fail since they're constructed
locally, not fetched from an API.
"""

import os
import requests
import streamlit as st
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"


@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)  # cache 24h — same query won't burn quota twice
def search_youtube_playlists(query: str, max_results: int = 2) -> list:
    """
    Search YouTube for the most-watched PLAYLISTS matching `query`.
    Playlists are preferred over single videos for learning paths because
    they give structured, multi-part coverage of a skill.

    Returns:
        [{"title": str, "channel": str, "url": str}, ...]  (empty list on failure)
    """
    if not YOUTUBE_API_KEY:
        return []

    params = {
        "part":              "snippet",
        "q":                 f"{query} tutorial for beginners",
        "type":              "playlist",
        "maxResults":        max_results,
        "order":             "relevance",          # relevance > viewCount for playlists — viewCount returns popular-but-unrelated results
        "relevanceLanguage": "en",
        "safeSearch":        "strict",
        "key":               YOUTUBE_API_KEY,
    }

    try:
        resp = requests.get(YOUTUBE_SEARCH_URL, params=params, timeout=8)
        resp.raise_for_status()
        items = resp.json().get("items", [])
    except Exception:
        return []

    results = []
    for item in items:
        playlist_id = item.get("id", {}).get("playlistId")
        snippet     = item.get("snippet", {})
        if not playlist_id:
            continue
        results.append({
            "title":   snippet.get("title", "Untitled playlist").strip(),
            "channel": snippet.get("channelTitle", "").strip(),
            "url":     f"https://www.youtube.com/playlist?list={playlist_id}",
        })
    return results


def get_course_search_links(skill: str, max_results: int = 2) -> list:
    """
    Build always-valid course SEARCH links for `skill` on trusted learning
    platforms. Replaces the old search_courses() — no API key, no quota,
    no CSE setup, and it can never return zero results due to quota
    exhaustion since nothing is actually fetched over the network.

    These are search-RESULTS pages (not a single specific course), but the
    URL itself is guaranteed to load and show real, current course listings
    for the query — unlike an LLM-guessed direct course URL, which is prone
    to hallucination (404s).

    Args:
        skill:       the skill/topic to search for (e.g. "Python", "Data Visualization")
        max_results: how many platforms to return (in priority order below)

    Returns:
        [{"title": str, "source": str, "url": str}, ...]
        (kept in the same shape as the old search_courses() output so
        callers/templates don't need to change)
    """
    if not skill or not skill.strip():
        return []

    query = quote_plus(skill.strip())

    platforms = [
        ("Coursera",           f"https://www.coursera.org/search?query={query}"),
        ("Udemy",               f"https://www.udemy.com/courses/search/?q={query}"),
        ("edX",                 f"https://www.edx.org/search?q={query}"),
        ("freeCodeCamp",        f"https://www.freecodecamp.org/news/search/?query={query}"),
        ("Khan Academy",        f"https://www.khanacademy.org/search?page_search_query={query}"),
        ("LinkedIn Learning",   f"https://www.linkedin.com/learning/search?keywords={query}"),
        ("Pluralsight",         f"https://www.pluralsight.com/search?q={query}"),
        ("Codecademy",          f"https://www.codecademy.com/search?query={query}"),
        ("GeeksforGeeks",       f"https://www.geeksforgeeks.org/?s={query}"),
    ]

    results = []
    for source, url in platforms[:max_results]:
        results.append({
            "title":  f"{skill.strip()} courses on {source}",
            "source": source,
            "url":    url,
        })
    return results


def fallback_search_links(query: str) -> dict:
    """
    Zero-API-cost fallback — always-valid search-result links (not specific
    playlists/courses, but guaranteed to never 404). Used when API keys are
    missing or a live search returns nothing.
    """
    q = quote_plus(query)
    return {
        "youtube": f"https://www.youtube.com/results?search_query={q}+playlist",
        "courses": f"https://www.google.com/search?q={q}+course+beginner+site:coursera.org+OR+site:udemy.com+OR+site:freecodecamp.org",
    }


def get_week_resources(skill: str, topic_context: str = "") -> dict:
    """
    Fetch real learning resources for a given skill (from missing_skills list).

    `skill`         — the actual missing skill (e.g. "Data Visualization")
                      used as primary search query for max relevance.
    `topic_context` — optional LLM-generated topic context to enrich the query
                      when skill alone is too short (e.g. "Tableau fundamentals").

    Returns:
        {
            "skill":    str,    # the skill this resource block is for
            "youtube":  [...],  # real playlists (most-watched), possibly empty
            "courses":  [...],  # always-valid platform search links
            "fallback": {...}   # always-valid search links
        }
    """
    # Primary query: skill name is the anchor, topic_context adds flavour
    query = f"{skill} {topic_context}".strip() if topic_context else skill

    return {
        "skill":    skill,
        "youtube":  search_youtube_playlists(f"{skill} complete course", max_results=2),
        "courses":  get_course_search_links(skill, max_results=2),
        "fallback": fallback_search_links(query),
    }