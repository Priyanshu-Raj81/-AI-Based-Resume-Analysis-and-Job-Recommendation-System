from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "llama-3.3-70b-versatile"


def query_groq(prompt, max_tokens=2000, temperature=0.7):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
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

    return query_groq(prompt, max_tokens=2000)


def generate_learning_path(target_role, experience_level="Fresher", missing_skills=None):
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

    return query_groq(prompt, max_tokens=2000)


def generate_interview_questions(target_role, extracted_skills, experience_level="Fresher",
                                  interview_type="Full interview"):

    # ✅ Handle both formats
    type_lower = interview_type.lower()

    if "technical" in type_lower:
        structure = f"""Generate exactly 40 TECHNICAL interview questions for {target_role} at {experience_level} level.

STRICTLY follow this order:

## 🟢 EASY TECHNICAL QUESTIONS (15 questions) — Q1 to Q15
Basic fundamentals, core concepts, definitions specific to {target_role}

## 🟡 MEDIUM TECHNICAL QUESTIONS (15 questions) — Q16 to Q30
Implementation, problem solving, real work scenarios

## 🔴 HARD TECHNICAL QUESTIONS (10 questions) — Q31 to Q40
System design, optimization, architecture decisions

For EACH question provide:
**Q[N]: [Question text ending with ?]**
- **Difficulty:** Easy/Medium/Hard
- **✅ Answer:** [Minimum 4-5 lines detailed answer specific to {target_role}]
- **💡 Tip:** [One actionable interview tip]

---"""

    elif "hr" in type_lower:
        structure = f"""Generate exactly 40 HR and Behavioral questions for {target_role} at {experience_level} level.

STRICTLY follow this order:

## 🟢 EASY HR QUESTIONS (15 questions) — Q1 to Q15
Introduction, background, motivation, why this role, basic situational

## 🟡 MEDIUM HR QUESTIONS (15 questions) — Q16 to Q30
Teamwork, conflict resolution, project challenges, leadership situations

## 🔴 HARD HR QUESTIONS (10 questions) — Q31 to Q40
Salary negotiation, career goals, failures, tough decisions, pressure situations

For EACH question provide:
**Q[N]: [Question text ending with ?]**
- **Difficulty:** Easy/Medium/Hard
- **✅ Answer:** [STAR method — Situation, Task, Action, Result — minimum 4-5 lines]
- **💡 Tip:** [One line tip to impress interviewer]

---"""

    else:  # Full interview
        structure = f"""Generate exactly 40 interview questions covering ALL rounds for {target_role} at {experience_level} level.

STRICTLY follow this order:

## 🟢 EASY QUESTIONS (15 questions) — Q1 to Q15
Mix: 8 basic technical + 7 simple HR questions

## 🟡 MEDIUM QUESTIONS (15 questions) — Q16 to Q30
Mix: 9 intermediate technical + 6 situational HR questions

## 🔴 HARD QUESTIONS (10 questions) — Q31 to Q40
Mix: 6 advanced technical + 4 complex behavioral questions

For EACH question provide:
**Q[N]: [Question text ending with ?]**
- **Type:** Technical / HR / Conceptual
- **Difficulty:** Easy/Medium/Hard
- **✅ Answer:** [Detailed 4-5 line answer]
- **💡 Tip:** [One line interview tip]

---"""

    prompt = f"""You are an expert technical interviewer and HR consultant at a top tech company with 15+ years of hiring experience.

Candidate Profile:
- Target Role: {target_role}
- Experience Level: {experience_level}
- Interview Type: {interview_type}
- Candidate Skills: {', '.join(extracted_skills) if extracted_skills else 'General'}

{structure}

CRITICAL INSTRUCTIONS:
- Generate ALL 40 questions — do NOT stop early under any circumstances
- STRICTLY Easy (Q1-Q15) → Medium (Q16-Q30) → Hard (Q31-Q40) order
- Every question 100% specific to {target_role} — NO generic questions
- Every answer minimum 4-5 lines — NO short answers allowed
- Every question MUST end with a question mark (?)
- Number questions clearly: Q1, Q2... Q40
- Tailor difficulty to {experience_level}:
  * Fresher: basics, fundamentals, college projects, simple concepts
  * Mid-Level (1-3 years): real work scenarios, system design, team situations
  * Senior (3+ years): architecture decisions, leadership, complex problem solving
- Use candidate skills in questions: {', '.join(extracted_skills[:5]) if extracted_skills else 'general skills'}
- Answers must be practical and impressive — NOT textbook definitions

Format in clean Markdown. ALL 40 questions mandatory."""

    return query_groq(prompt, max_tokens=8000)


# =========================================================================== #
# AI INTERVIEW COACH
# =========================================================================== #
def generate_coach_questions(target_role, extracted_skills=None, experience_level="Fresher",
                             interview_type="Full interview", num_questions=8,
                             projects=None, missing_skills=None):
    skills = ", ".join(extracted_skills) if extracted_skills else "general"
    projects_str = ", ".join(projects[:6]) if projects else "none provided"
    missing_str = ", ".join(missing_skills) if missing_skills else "none"

    prompt = f"""You are a senior technical interviewer conducting a live mock interview
for a {experience_level} {target_role}. Interview type: {interview_type}.

Candidate context (use it to personalize questions):
- Skills: {skills}
- Projects: {projects_str}
- Skill gaps to probe: {missing_str}

Generate exactly {num_questions} interview questions, progressively harder
(start Easy, move to Medium, end Hard). Reference the candidate's ACTUAL skills
and projects whenever possible. Avoid generic textbook questions.

Return ONLY a valid JSON array. No markdown, no code fences, no commentary.
Each object MUST be exactly:
{{"id": 1, "type": "Technical", "difficulty": "Easy",
  "question": "...", "focus_skill": "...", "based_on": "skill|project|role"}}

Rules:
- "type": one of Technical, HR, Behavioral
- "difficulty": one of Easy, Medium, Hard
- "question": a single clear question ending with a question mark (?)
- "focus_skill": the main skill/topic the question targets
- "based_on": "project" if it references a candidate project, "skill" if a listed
  skill, otherwise "role"
"""
    return query_groq(prompt, max_tokens=2500, temperature=0.6)


def evaluate_answer(question, user_answer, target_role="the role"):
    safe_answer = (user_answer or "").strip() or "(no answer provided)"
    prompt = f"""You are a strict but fair senior interviewer for a {target_role}.
Evaluate the candidate's answer to the interview question below.

QUESTION:
{question}

CANDIDATE ANSWER:
{safe_answer}

Score each dimension from 0 to 10 (integers only). If the answer is empty,
irrelevant, or wrong, give low scores honestly.

Return ONLY a valid JSON object. No markdown, no code fences, no commentary:
{{"scores": {{"technical_accuracy": 0, "communication": 0, "clarity": 0,
  "confidence": 0, "problem_solving": 0, "depth": 0}},
  "overall": 0, "weakness_category": "...", "feedback": "..."}}

Rules:
- All scores are integers 0-10
- "overall": integer 0-10 reflecting the whole answer
- "weakness_category": the SINGLE biggest weak area. One of:
  Python, SQL, Machine Learning, Deep Learning, Projects, Communication,
  Confidence, Problem Solving, or General
- "feedback": 1-2 concise, constructive sentences. No markdown symbols.
"""
    return query_groq(prompt, max_tokens=600, temperature=0.2)


def generate_final_report(target_role, experience_level, session_summary):
    prompt = f"""You are a senior hiring manager summarizing a mock interview for a
{experience_level} {target_role}.

INTERVIEW SUMMARY:
{session_summary}

Based ONLY on this summary, produce a final assessment.

Return ONLY a valid JSON object. No markdown, no code fences, no commentary:
{{"overall_score": 0.0, "readiness_percent": 0,
  "strengths": ["..."], "weaknesses": ["..."],
  "improvement_plan": ["..."], "recommended_topics": ["..."],
  "hiring_recommendation": "..."}}

Rules:
- "overall_score": float 0-10 (one decimal)
- "readiness_percent": integer 0-100
- "strengths"/"weaknesses": 2-4 short bullet phrases each, no markdown symbols
- "improvement_plan": 3-5 concrete, actionable steps
- "recommended_topics": 3-6 specific topics to study
- "hiring_recommendation": one of "Strong Hire", "Hire", "Lean Hire",
  "Lean No Hire", "No Hire"
"""
    return query_groq(prompt, max_tokens=1500, temperature=0.4)


# New Update

