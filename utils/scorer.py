from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.nlp_extractor import COMMON_SKILLS
import re

def calculate_similarity_score(resume_skills_list, job_skills_str):
    if not resume_skills_list or not job_skills_str:
        return 0, []
    
    resume_skills_str = " ".join(resume_skills_list).lower()
    job_skills_lower = job_skills_str.lower()

    # --- ATS Score (same TF-IDF logic, this part is fine) ---
    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform([resume_skills_str, job_skills_lower])
        match_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        ats_score = min(round(match_score * 100) + 20, 100)
    except:
        ats_score = 20

    # --- Missing Skills Fix ---
    # TF-IDF words nahi, COMMON_SKILLS list se match karo
    job_has_skills = []
    for skill in COMMON_SKILLS:
        if re.search(r'\b' + re.escape(skill) + r'\b', job_skills_lower):
            job_has_skills.append(skill)

    resume_skills_lower = [s.lower() for s in resume_skills_list]
    
    # Jo skills job mein hain but resume mein nahi
    missing_skills = [
        s.title() for s in job_has_skills 
        if s.lower() not in resume_skills_lower
    ]

    return ats_score, missing_skills[:7]