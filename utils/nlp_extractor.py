import spacy
import re

nlp = spacy.load("en_core_web_sm")

# Common skills list
SKILLS_DB = [
    "python", "java", "javascript", "c++", "sql", "machine learning",
    "deep learning", "nlp", "data analysis", "pandas", "numpy",
    "tensorflow", "pytorch", "scikit-learn", "docker", "kubernetes",
    "aws", "azure", "git", "react", "node.js", "html", "css",
    "mongodb", "mysql", "postgresql", "flask", "django", "fastapi",
    "power bi", "tableau", "excel", "r", "matlab", "opencv"
]

def extract_skills(text):
    text_lower = text.lower()
    found_skills = []
    for skill in SKILLS_DB:
        if skill in text_lower:
            found_skills.append(skill.title())
    return list(set(found_skills))

def extract_education(text):
    education_keywords = [
        "b.tech", "btech", "b.e", "m.tech", "mtech", "mba",
        "bca", "mca", "b.sc", "m.sc", "phd", "bachelor",
        "master", "degree", "12th", "10th", "diploma"
    ]
    found = []
    text_lower = text.lower()
    for keyword in education_keywords:
        if keyword in text_lower:
            found.append(keyword.upper())
    return list(set(found))

def extract_experience(text):
    # Find years of experience
    patterns = [
        r'(\d+)\+?\s*years?\s*of\s*experience',
        r'experience\s*of\s*(\d+)\+?\s*years?',
        r'(\d+)\+?\s*years?\s*experience'
    ]
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return int(match.group(1))
    return 0

def extract_name(text):
    lines = text.strip().split('\n')
    for line in lines[:5]:
        line = line.strip()
        if len(line) > 2 and len(line) < 40:
            if not any(char.isdigit() for char in line):
                return line
    return "Candidate"