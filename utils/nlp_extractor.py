import re
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# ✅ Complete COMMON_SKILLS — sare roles cover karte hain
COMMON_SKILLS = [
    # Programming Languages
    'python', 'java', 'c++', 'c#', 'javascript', 'typescript', 'sql', 'r',
    'go', 'rust', 'kotlin', 'swift', 'scala', 'php', 'ruby',

    # Web Development
    'html', 'css', 'react', 'angular', 'node.js', 'django', 'flask',
    'fastapi', 'bootstrap', 'tailwind', 'vue.js', 'next.js',

    # Data & ML
    'machine learning', 'deep learning', 'nlp', 'data analysis', 'data analytics',
    'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch',
    'tableau', 'power bi', 'excel', 'matplotlib', 'seaborn',
    'statistics', 'data visualization', 'spark', 'hadoop',
    'airflow', 'kafka', 'dbt', 'looker',

    # Cloud & DevOps
    'aws', 'gcp', 'azure', 'docker', 'kubernetes', 'git', 'linux', 'cloud',
    'jenkins', 'terraform', 'ansible', 'ci/cd', 'prometheus', 'grafana',

    # Mobile
    'flutter', 'dart', 'android studio', 'firebase', 'mobile app development',
    'react native', 'xcode', 'swift', 'kotlin',

    # Security
    'information security', 'cybersecurity', 'cryptography',
    'ethical hacking', 'penetration testing', 'linux', 'networking', 'firewall',

    # Databases
    'mongodb', 'postgresql', 'mysql', 'redis', 'sqlite',
    'sql server', 'cassandra', 'dynamodb',

    # Soft Skills
    'communication', 'project management', 'agile', 'leadership',
    'teamwork', 'scrum', 'risk management',

    # Design
    'figma', 'photoshop', 'illustrator', 'canva', 'adobe xd',
    'wireframing', 'prototyping', 'user research',

    # AI/LLM Tools
    'langchain', 'transformers', 'openai', 'llm',

    # Other
    'streamlit', 'git', 'jira', 'confluence',
    'marketing', 'sales', 'excel', 'powerpoint',
]

def extract_skills(text):
    text_lower = text.lower()
    extracted_skills = []

    for skill in COMMON_SKILLS:
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            extracted_skills.append(skill.title())

    return list(set(extracted_skills))