# import re
# import spacy

# try:
#     nlp = spacy.load("en_core_web_sm")
# except:
#     import spacy.cli
#     spacy.cli.download("en_core_web_sm")
#     nlp = spacy.load("en_core_web_sm")

# # Expanded list including standard tech and specific frameworks
# COMMON_SKILLS = [
#     'python', 'java', 'c++', 'c#', 'sql', 'machine learning', 'data analysis', 'aws', 'cloud', 
#     'react', 'node.js', 'angular', 'docker', 'kubernetes', 'html', 'css', 'javascript',
#     'django', 'flask', 'pandas', 'numpy', 'scikit-learn', 'deep learning', 'nlp', 'git',
#     'flutter', 'dart', 'android studio', 'mobile app development', 'firebase',
#     'information security', 'cryptography', 'rsa', 'aes', 'des', 'cybersecurity',
#     'communication', 'project management', 'agile', 'marketing', 'sales', 'tableau'
# ]

# def extract_skills(text):
#     text_lower = text.lower()
#     extracted_skills = []
    
#     for skill in COMMON_SKILLS:
#         if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
#             extracted_skills.append(skill.title())
            
#     return list(set(extracted_skills))

import re
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# ✅ Expanded & better organized skill list
COMMON_SKILLS = [
    # Programming Languages
    'python', 'java', 'c++', 'c#', 'javascript', 'typescript', 'sql', 'r', 'go', 'rust',
    # Web
    'html', 'css', 'react', 'angular', 'node.js', 'django', 'flask', 'fastapi',
    # Data & ML
    'machine learning', 'deep learning', 'nlp', 'data analysis', 'pandas', 'numpy',
    'scikit-learn', 'tensorflow', 'pytorch', 'tableau', 'power bi',
    # Cloud & DevOps
    'aws', 'gcp', 'azure', 'docker', 'kubernetes', 'git', 'linux', 'cloud',
    # Mobile
    'flutter', 'dart', 'android studio', 'firebase', 'mobile app development',
    # Security
    'information security', 'cybersecurity', 'cryptography', 'rsa', 'aes', 'des',
    # Databases
    'mongodb', 'postgresql', 'mysql', 'redis',
    # Soft Skills
    'communication', 'project management', 'agile', 'leadership', 'teamwork',
    # Other
    'marketing', 'sales', 'excel', 'streamlit'
]

def extract_skills(text):
    text_lower = text.lower()
    extracted_skills = []
    
    for skill in COMMON_SKILLS:
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            extracted_skills.append(skill.title())
            
    return list(set(extracted_skills))