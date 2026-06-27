import re
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

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


def extract_projects(text):
    """Extract clean project titles from resume"""
    lines = text.split("\n")
    projects = []
    capturing = False

    project_start_re = re.compile(r'^projects?\s*:?\s*$', re.I)
    stop_section_re = re.compile(
        r'^(experience|education|skills?|technical skills?|certifications?|'
        r'achievements?|contact|summary|objective|interests?|languages?|'
        r'work experience|internship|profile|awards?|publications?|'
        r'extra.curricular|activities|hobbies|references?)\s*:?\s*$', re.I
    )
    bullet_re = re.compile(r'^\s*[-•*▪◦‣·]')
    techstack_re = re.compile(
        r'^(tech stack|technologies|tools used|built with|stack)\s*:', re.I)
    date_re = re.compile(
        r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*\d{4}'
        r'|\b\d{4}\s*[-–]\s*(\d{4}|present)\b'
        r'|\b(present|current|ongoing)\b', re.I
    )
    description_re = re.compile(
        r'^(developed|built|created|implemented|designed|used|utilized|'
        r'extracted|identified|uploaded|retrieved|interacted|structured|'
        r'integrated|deployed|configured|managed|led|handled|worked|'
        r'responsible|achieved|improved|reduced|increased|enabled|'
        r'collaborated|analyzed|processed|generated|performed|applied|'
        r'established|maintained|supported|provided|ensured|automated|'
        r'stored|scanned|digitized|answered)\b', re.I
    )
    noise_re = re.compile(
        r'(certificate|awarded|score|cgpa|gpa|github\.com|linkedin|http|www\.|@)', re.I
    )
    project_indicators = re.compile(
        r'(chatbot|app|application|system|platform|project|tool|website|'
        r'dashboard|api|bot|model|engine|portal|manager|tracker|analyzer|'
        r'generator|assistant|service|solution|framework|rental|locker|'
        r'medlock|ridelo|genai)', re.I
    )

    # Step 1: Join lines that were split across multiple lines in the PDF
    # Long titles in PDFs often wrap — merge them back into one line
    joined_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            joined_lines.append(line)
            i += 1
            continue

        # If a line ends with an open bracket, join the next line to close it
        # e.g. "GenAI Chatbot (LangChain Project" — missing closing parenthesis
        open_brackets = line.count('(') - line.count(')')
        while open_brackets > 0 and i + 1 < len(lines):
            i += 1
            next_line = lines[i].strip()
            if next_line:
                line = line + ' ' + next_line
                open_brackets = line.count('(') - line.count(')')

        # Handle multi-line continuation (already covered by bracket check above)
#


        joined_lines.append(line)
        i += 1

    # Step 2: Extract project titles from the joined lines
    for raw in joined_lines:
        line = raw.strip()
        if not line:
            continue

        if project_start_re.match(line):
            capturing = True
            continue

        if not capturing:
            continue

        if stop_section_re.match(line):
            break

        if line.isupper():
            continue

        if bullet_re.match(line):
            continue

        if techstack_re.match(line):
            continue

        if date_re.search(line) and len(line.strip()) < 40:
            continue

        if description_re.match(line):
            continue

        if noise_re.search(line):
            continue

        # Clean title
        title = date_re.sub('', line).strip()
        title = re.sub(r'\s{2,}', ' ', title)
        title = title.strip(" \t-–|•:·(),.")

        word_count = len(title.split())
        comma_count = title.count(',')
        has_project_keyword = bool(project_indicators.search(title))

        if (5 < len(title) < 100  # Allow up to 100 chars to support joined multi-line titles
                and not title.isdigit()
                and word_count >= 2
                and comma_count <= 1
                and (has_project_keyword or word_count <= 10)):
            projects.append(title)

    # Deduplicate
    seen, out = set(), []
    for p in projects:
        key = p.lower()
        if key not in seen:
            seen.add(key)
            out.append(p)

    return out[:6]