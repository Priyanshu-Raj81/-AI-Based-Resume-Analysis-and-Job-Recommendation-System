from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def query_groq(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {e}"

def generate_resume_suggestions(target_role, extracted_skills, missing_skills, job_desc="", experience_level="Fresher"):
    if job_desc:
        context = f"Job Description:\n{job_desc}"
    else:
        context = f"Target Job Role: {target_role}"

    prompt = f"""You are an expert HR consultant and resume coach with 10+ years of experience hiring for top tech companies.

Candidate Profile:
- Target: {context}
- Experience Level: {experience_level}
- Current skills in resume: {', '.join(extracted_skills) if extracted_skills else 'None'}
- Missing skills for this role: {', '.join(missing_skills) if missing_skills else 'None'}

IMPORTANT INSTRUCTIONS:
- Give suggestions SPECIFICALLY for "{target_role}" role only — do NOT give generic advice
- Tailor advice based on experience level "{experience_level}":
  * If Fresher: focus on projects, internships, certifications, and foundational skills
  * If Mid-Level (1-3 years): focus on real work experience, system design, leadership
  * If Senior (3+ years): focus on architecture, team leadership, and strategic impact
- Every suggestion must be directly relevant to "{target_role}" — no irrelevant skills

Give improvement suggestions in these 5 sections:

1. **Skills to Add** — Only skills directly required for {target_role}, not generic ones
2. **Projects to Build** — Specific project ideas that impress {target_role} interviewers
3. **Resume Summary** — Write an example summary specifically for {target_role} at {experience_level} level
4. **ATS Keywords** — Keywords that {target_role} job postings specifically use
5. **Top 3 Priority Actions** — Most impactful things for a {experience_level} targeting {target_role}

Be role-specific, practical, and direct. Format in clean Markdown."""

    return query_groq(prompt)


def generate_learning_path(target_role, experience_level="Fresher", missing_skills=None):
    # ✅ Missing skills optional hai ab
    if missing_skills:
        skills_context = f"Candidate's missing skills identified from resume: {', '.join(missing_skills)}"
    else:
        skills_context = f"Identify the most important skills needed for {target_role} and create roadmap for those."

    prompt = f"""You are an expert technical mentor and career coach.

Candidate Profile:
- Target Role: {target_role}
- Experience Level: {experience_level}
- {skills_context}

Create a detailed, practical 4-week learning roadmap specifically for a {experience_level} targeting {target_role}.

IMPORTANT:
- If Fresher: start from basics, include foundational concepts
- If Mid-Level: skip basics, focus on advanced topics and system design  
- If Senior: focus on architecture, leadership, and cutting-edge tech

Format the roadmap EXACTLY like this for each week:

## 🗓️ Week 1: [Week Title]
**Goal:** [What candidate will achieve this week]

### Topics to Cover:
- [Topic 1]
- [Topic 2]

### 📚 Free Resources:
- **YouTube:** [Specific channel/video name] - [URL or search query]
- **Course:** [Platform name] - [Course name] - [URL if known]
- **Docs:** [Official documentation link]

### ✅ Weekly Project:
[Specific mini-project to build this week to practice]

---

Do this for all 4 weeks. Be specific with resource names. No vague suggestions."""

    return query_groq(prompt)