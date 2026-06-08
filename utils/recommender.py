from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def compare_resume_to_jd(resume_text, job_description):
    """
    Resume aur manually entered Job Description ke beech
    similarity score return karta hai (0 to 100).
    scorer.py ka calculate_score() bhi yahi karta hai —
    yeh function future multi-JD comparison ke liye hai.
    """
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
        score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(score * 100, 2)
    except:
        return 0.0