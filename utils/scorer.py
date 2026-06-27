from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.nlp_extractor import COMMON_SKILLS
import re

ROLE_SKILLS = {
    # ── Software Development ──────────────────────────────────
    "software developer": [
        "python", "java", "javascript", "sql", "git",
        "html", "css", "react", "docker", "agile"
    ],
    "backend developer": [
        "python", "node.js", "java", "sql", "mongodb",
        "docker", "git", "django", "flask", "aws"
    ],
    "frontend developer": [
        "html", "css", "javascript", "react", "angular",
        "git", "typescript", "bootstrap", "tailwind"
    ],
    "full stack developer": [
        "html", "css", "javascript", "react", "node.js",
        "sql", "mongodb", "git", "python", "docker"
    ],
    "mobile app developer": [
        "flutter", "dart", "firebase", "android studio",
        "git", "react native"
    ],
    "flutter developer": [
        "flutter", "dart", "firebase", "android studio", "git"
    ],
    "android developer": [
        "kotlin", "java", "android studio", "firebase", "git"
    ],
    "ios developer": [
        "swift", "xcode", "firebase", "git"
    ],

    # ── Data & AI ─────────────────────────────────────────────
    "data scientist": [
        "python", "machine learning", "deep learning",
        "pandas", "numpy", "scikit-learn", "sql",
        "statistics", "nlp", "tensorflow", "matplotlib"
    ],
    "data analyst": [
        "sql", "python", "excel", "pandas", "numpy",
        "power bi", "data analysis", "tableau",
        "matplotlib", "r", "statistics"
    ],
    "data engineer": [
        "python", "sql", "aws", "docker", "mongodb",
        "postgresql", "spark", "airflow", "kafka"
    ],
    "ml engineer": [
        "python", "machine learning", "deep learning",
        "tensorflow", "pytorch", "docker", "scikit-learn", "aws"
    ],
    "ai engineer": [
        "python", "machine learning", "deep learning",
        "nlp", "tensorflow", "pytorch", "langchain",
        "transformers", "llm", "docker", "aws"
    ],
    "business analyst": [
        "sql", "excel", "tableau", "power bi",
        "communication", "agile", "data analysis", "scrum"
    ],
    "nlp engineer": [
        "python", "nlp", "machine learning",
        "tensorflow", "pytorch", "transformers", "langchain"
    ],
    "prompt engineer": [
        "python", "nlp", "machine learning",
        "langchain", "communication", "llm"
    ],

    # ── Cloud & DevOps ────────────────────────────────────────
    "devops engineer": [
        "docker", "kubernetes", "aws", "linux",
        "git", "python", "jenkins", "terraform", "ci/cd"
    ],
    "cloud engineer": [
        "aws", "azure", "gcp", "docker",
        "kubernetes", "terraform", "linux", "python"
    ],
    "site reliability engineer": [
        "linux", "python", "docker", "kubernetes",
        "aws", "git", "terraform", "prometheus"
    ],

    # ── Security ──────────────────────────────────────────────
    "information security analyst": [
        "cybersecurity", "information security",
        "cryptography", "linux", "python", "networking"
    ],
    "cybersecurity engineer": [
        "cybersecurity", "linux", "python",
        "cryptography", "aws", "firewall", "networking"
    ],
    "ethical hacker": [
        "cybersecurity", "linux", "python",
        "cryptography", "ethical hacking", "penetration testing"
    ],

    # ── Management ────────────────────────────────────────────
    "product manager": [
        "agile", "project management", "communication",
        "leadership", "sql", "tableau", "scrum"
    ],
    "project manager": [
        "agile", "project management", "communication",
        "leadership", "scrum", "risk management", "jira"
    ],

    # ── Design ────────────────────────────────────────────────
    "ui ux designer": [
        "figma", "html", "css", "communication",
        "wireframing", "prototyping", "user research", "adobe xd"
    ],
    "graphic designer": [
        "photoshop", "illustrator", "figma", "canva"
    ],

    # ── Emerging ──────────────────────────────────────────────
    "blockchain developer": [
        "python", "javascript", "git", "cryptography"
    ],
    "game developer": [
        "python", "git", "c++"
    ],
    "ar vr developer": [
        "python", "git", "javascript"
    ],
}


def get_ats_score(matched_count, total_count):
    """
    Clean ATS score — no artificial penalties.
    Returns actual percentage of matched skills (0–100).
    """
    if total_count == 0:
        return 0
    score = round((matched_count / total_count) * 100)
    return min(score, 100)


def find_role_match(role_key):
    if not role_key:
        return None
    role_key = role_key.lower().strip()

    # Level 1 — Exact match
    if role_key in ROLE_SKILLS:
        return ROLE_SKILLS[role_key]

    # Level 2 — Dictionary key contained in role string
    for key in ROLE_SKILLS:
        if key in role_key:
            return ROLE_SKILLS[key]

    # Level 3 — Word level match
    role_words = set(role_key.split())
    best_match = None
    best_score = 0
    for key in ROLE_SKILLS:
        key_words = set(key.split())
        common = role_words & key_words
        if len(common) > best_score:
            best_score = len(common)
            best_match = ROLE_SKILLS[key]

    return best_match if best_score > 0 else None


def calculate_similarity_score(resume_skills_list, job_skills_str, target_role=""):
    """
    Returns (ats_score, missing_skills).
    Priority: role-based matching → TF-IDF fallback → default 0.
    """
    if not resume_skills_list:
        return 0, []

    resume_skills_lower = [s.lower() for s in resume_skills_list]
    required_skills = find_role_match(target_role)

    if required_skills:
        # Role-based matching — clean percentage, no penalties
        matched = [s for s in required_skills if s.lower() in resume_skills_lower]
        missing = [s for s in required_skills if s.lower() not in resume_skills_lower]
        ats_score = get_ats_score(len(matched), len(required_skills))
        missing_skills = [s.title() for s in missing[:7]]

    else:
        # TF-IDF fallback — no artificial bonus
        if not job_skills_str:
            return 0, []

        resume_skills_str = " ".join(resume_skills_lower)
        job_skills_str_lower = job_skills_str.lower()

        try:
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([resume_skills_str, job_skills_str_lower])
            match_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            ats_score = min(round(match_score * 100), 100)
        except Exception:
            ats_score = 0

        job_has_skills = [
            skill for skill in COMMON_SKILLS
            if re.search(r'\b' + re.escape(skill) + r'\b', job_skills_str_lower)
        ]
        missing_skills = [
            s.title() for s in job_has_skills
            if s.lower() not in resume_skills_lower
        ][:7]

    return ats_score, missing_skills