import spacy
import re

nlp = spacy.load("en_core_web_sm")

# ── Expanded Skills Database ─────────────────────────────────────────────────
SKILLS_DB = [
    # Languages
    "python", "java", "javascript", "c++", "c#", "r", "matlab",
    "kotlin", "swift", "go", "rust", "scala", "typescript", "php", "ruby",
    # Web Frontend
    "html", "css", "react", "react.js", "angular", "vue", "bootstrap", "tailwind",
    # Backend
    "node.js", "express.js", "django", "flask", "fastapi", "spring boot", "spring",
    # Databases
    "sql", "mysql", "postgresql", "mongodb", "sqlite", "redis", "oracle",
    "nosql", "firebase",
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "git", "github",
    "ci/cd", "jenkins", "linux", "terraform", "ansible",
    # ML / Data Science
    "machine learning", "deep learning", "nlp", "tensorflow", "pytorch",
    "scikit-learn", "pandas", "numpy", "opencv", "keras",
    "data analysis", "data science", "power bi", "tableau", "excel",
    # CS Fundamentals
    "data structures", "algorithms", "oop", "operating systems",
    "computer networks", "dbms",
    # Other
    "restful api", "rest api", "microservices", "agile", "scrum",
]

def extract_skills(text):
    text_lower = text.lower()
    found_skills = []
    
    for skill in sorted(SKILLS_DB, key=len, reverse=True):
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