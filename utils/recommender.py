import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from utils.scorer import calculate_similarity_score

DATASET_PATH = "dataset/marketing_sample_for_naukri_com-jobs__20190701_20190830__30k_data.csv"

@st.cache_data
def load_job_data():
    if not os.path.exists(DATASET_PATH):
        return pd.DataFrame()
    
    df = pd.read_csv(DATASET_PATH, nrows=5000) # Loading top 5K to keep it fast
    df = df.dropna(subset=['Job Title', 'Key Skills'])
    df['Clean_Skills'] = df['Key Skills'].apply(lambda x: str(x).replace('|', ' ').lower())
    return df

def get_role_ats_score(resume_skills_list, target_job_title, df):
    target_jobs = df[df['Job Title'].str.contains(target_job_title, case=False, na=False)]
    if target_jobs.empty:
        target_jobs = df
        
    all_required_skills = " ".join(target_jobs['Clean_Skills'].tolist())
    return calculate_similarity_score(resume_skills_list, all_required_skills)

def recommend_jobs(resume_skills_list, df, top_n=3):
    if df.empty or not resume_skills_list:
        return pd.DataFrame()
        
    resume_skills_str = " ".join(resume_skills_list).lower()
    vectorizer = TfidfVectorizer()
    job_skills_matrix = vectorizer.fit_transform(df['Clean_Skills'])
    resume_vector = vectorizer.transform([resume_skills_str])
    
    similarity_scores = cosine_similarity(resume_vector, job_skills_matrix).flatten()
    top_indices = similarity_scores.argsort()[-top_n:][::-1]
    
    recommended_jobs = df.iloc[top_indices].copy()
    recommended_jobs['Match_Score'] = (similarity_scores[top_indices] * 100).round()
    
    return recommended_jobs[['Job Title', 'Job Salary', 'Location', 'Key Skills', 'Match_Score']]