from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_ai_suggestions(resume_text, missing_skills, job_title=""):
    prompt = f"""
You are an expert HR consultant and career coach.

Analyze this resume and provide specific improvement suggestions:

Resume Content:
{resume_text[:2000]}

Missing Skills for {job_title}: {', '.join(missing_skills) if missing_skills else 'None identified'}

Please provide:
1. Top 3 Resume Improvements
2. Skills to Learn (with free resources)
3. Career Path Suggestions
4. ATS Optimization Tips

Be specific, practical, and encouraging. Format with clear sections.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI suggestions unavailable: {str(e)}"

def get_resume_score_feedback(score, grade, name):
    prompt = f"""
The candidate {name} got a resume match score of {score}% (Grade: {grade}).

Give a short, motivating 2-3 line feedback message based on this score.
Be encouraging and suggest one key action they should take.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        return response.choices[0].message.content
    except:
        return "Keep improving your resume and skills!"