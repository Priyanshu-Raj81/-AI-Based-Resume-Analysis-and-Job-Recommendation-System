import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def load_jobs(filepath="dataset/jobs.csv"):
    try:
        df = pd.read_csv(filepath)
        return df
    except:
        return pd.DataFrame({
            'Job Title': ['Data Scientist', 'ML Engineer', 'Python Developer',
                         'Web Developer', 'DevOps Engineer', 'Data Analyst'],
            'Skills Required': [
                'python machine learning deep learning pandas numpy tensorflow',
                'python tensorflow pytorch scikit-learn mlops docker',
                'python flask django fastapi sql git',
                'html css javascript react nodejs mongodb',
                'docker kubernetes aws azure ci/cd linux',
                'python sql excel power bi tableau data visualization'
            ],
            'Experience Required': [2, 3, 1, 1, 2, 1],
            'Location': ['Bangalore', 'Hyderabad', 'Pune', 'Mumbai', 'Delhi', 'Chennai']
        })

def add_manual_job(df, title, skills, experience=0, location="Not specified"):
    skills_clean = skills.replace(",", " ").lower().strip()
    new_row = pd.DataFrame([{
        'Job Title':           title.strip(),
        'Skills Required':     skills_clean,
        'Experience Required': experience,
        'Location':            location.strip()
    }])
    return pd.concat([df, new_row], ignore_index=True)

def recommend_jobs(resume_text, df, top_n=5):
    skill_col = None
    for col in ['Skills Required', 'skills', 'description', 'Job Description', 'key_skills']:
        if col in df.columns:
            skill_col = col
            break

    if skill_col is None:
        return pd.DataFrame()

    job_texts = df[skill_col].fillna("").tolist()
    all_texts = [resume_text] + job_texts

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
    df = df.copy()
    df['Match Score'] = [round(s * 100, 2) for s in scores]
    df = df.sort_values('Match Score', ascending=False).head(top_n)
    return df