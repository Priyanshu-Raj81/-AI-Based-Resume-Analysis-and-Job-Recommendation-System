from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ── Known tech skills database ──────────────────────────────────────────────
KNOWN_SKILLS = {
    # Languages
    "python", "java", "javascript", "c++", "c#", "r", "matlab", "kotlin",
    "swift", "go", "rust", "scala", "typescript", "php", "ruby",
    # Web
    "html", "css", "react", "react.js", "angular", "vue", "node.js",
    "express.js", "django", "flask", "fastapi", "spring boot", "spring",
    "bootstrap", "tailwind",
    # Databases
    "mysql", "postgresql", "mongodb", "sqlite", "redis", "oracle",
    "sql", "nosql", "firebase",
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "git", "github",
    "ci/cd", "jenkins", "linux", "terraform", "ansible",
    # ML / Data
    "machine learning", "deep learning", "nlp", "tensorflow", "pytorch",
    "scikit-learn", "pandas", "numpy", "opencv", "keras",
    "data analysis", "data science", "power bi", "tableau", "excel",
    # CS Fundamentals
    "data structures", "algorithms", "oop", "object-oriented programming",
    "operating systems", "computer networks", "dbms",
    # Other
    "restful api", "rest api", "api", "microservices", "agile", "scrum",
}


def extract_skills_from_jd(job_description):
    """
    Extracts only actual technical skills from JD —
    ignores normal English words like responsibilities, design, write.
    """
    jd_lower = job_description.lower()
    found = []
    # Check multi-word skills first (e.g. "machine learning", "spring boot")
    for skill in sorted(KNOWN_SKILLS, key=len, reverse=True):
        if skill in jd_lower:
            found.append(skill)
    return list(set(found))


def calculate_score(resume_text, job_description):
    """
    Calculates match score between resume and JD.
    Combines TF-IDF similarity (30%) + skill keyword overlap (70%).
    """
    try:
        # Part 1: TF-IDF cosine similarity
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
        tfidf_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

        # Part 2: Skill keyword overlap
        jd_skills = set(extract_skills_from_jd(job_description))
        resume_lower = resume_text.lower()
        resume_skills_found = {s for s in jd_skills if s in resume_lower}

        skill_overlap = len(resume_skills_found) / len(jd_skills) if jd_skills else 0

        # 30% TF-IDF + 70% skill overlap
        combined = (tfidf_score * 0.3) + (skill_overlap * 0.7)
        return round(combined * 100, 2)

    except:
        return 0.0


def get_grade(score):
    if score >= 75:
        return "A", "🟢 Excellent Match"
    elif score >= 55:
        return "B", "🔵 Good Match"
    elif score >= 40:
        return "C", "🟡 Average Match"
    elif score >= 25:
        return "D", "🟠 Below Average"
    else:
        return "F", "🔴 Poor Match"


def get_missing_skills(resume_skills, jd_text_or_list, resume_raw_text=""):
    """
    Returns skills required by the JD but NOT found in the resume.

    Two-layer check:
    1. Against resume_skills list (from nlp_extractor) — catches title-cased skills
    2. Against resume_raw_text (full resume text) — catches skills nlp_extractor
       missed but are actually present in the resume

    Parameters:
        resume_skills    : list of skills extracted by nlp_extractor (title case)
        jd_text_or_list  : full JD string or list of words
        resume_raw_text  : full raw resume text (optional, for deeper matching)
    """
    # Step 1: Extract actual tech skills from JD
    if isinstance(jd_text_or_list, str):
        jd_skills = extract_skills_from_jd(jd_text_or_list)
    else:
        jd_skills = [w for w in jd_text_or_list if w.lower() in KNOWN_SKILLS]

    # Step 2: Build normalized set of skills resume has
    resume_skills_lower = {s.lower() for s in resume_skills}
    resume_raw_lower    = resume_raw_text.lower() if resume_raw_text else ""

    missing = []
    for skill in jd_skills:
        skill_lower  = skill.lower()
        in_extracted = skill_lower in resume_skills_lower
        in_raw_text  = (skill_lower in resume_raw_lower) if resume_raw_lower else False

        if not in_extracted and not in_raw_text:
            missing.append(skill.title())

    return missing