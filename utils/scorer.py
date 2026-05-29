from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_score(resume_text, job_description):
    """Calculate match score between resume and job description"""
    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
        score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(score * 100, 2)
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

def get_missing_skills(resume_skills, required_skills):
    resume_lower = [s.lower() for s in resume_skills]
    missing = []
    for skill in required_skills:
        if skill.lower() not in resume_lower:
            missing.append(skill)
    return missing