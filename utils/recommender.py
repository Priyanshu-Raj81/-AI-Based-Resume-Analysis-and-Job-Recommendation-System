from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def compare_resume_to_jd(resume_text, job_description):
    """
    It returns a similarity score (from 0 to 100) between the
    resume and the manually entered job description.
    The `calculate_score()` function in `scorer.py` performs
    the same task; this function is intended for future multi-JD comparisons.
    """
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
        score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(score * 100, 2)
    except:
        return 0.0