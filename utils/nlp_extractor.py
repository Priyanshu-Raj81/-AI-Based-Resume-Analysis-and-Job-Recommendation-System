import re
import spacy
import streamlit as st
from spacy.matcher import PhraseMatcher


@st.cache_resource(show_spinner=False)
def _load_spacy_model():
    """
    Load the spaCy model once per app session instead of on every import/rerun.

    Falls back to a blank tokenizer-only pipeline if the full model can't be
    loaded or downloaded (e.g. no internet access, restricted network on first
    deploy). extract_skills() only needs tokenization + PhraseMatcher, so the
    blank pipeline keeps skill extraction working instead of crashing the app.
    """
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        try:
            from spacy.cli import download as spacy_download
            spacy_download("en_core_web_sm")
            return spacy.load("en_core_web_sm")
        except (Exception, SystemExit):
            return spacy.blank("en")


nlp = _load_spacy_model()

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


@st.cache_resource(show_spinner=False)
def _build_skill_matcher():
    """
    Build a spaCy PhraseMatcher once and cache it — matching COMMON_SKILLS
    as tokenized phrases instead of raw regex. This is genuine NLP:
    matches happen over spaCy's tokens (so 'C++', 'Node.js', multi-word
    phrases like 'machine learning' are matched on token boundaries,
    not on a hand-rolled \\b regex that trips up on punctuation).
    """
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(skill) for skill in COMMON_SKILLS]
    matcher.add("SKILLS", patterns)
    return matcher


_skill_matcher = _build_skill_matcher()


def extract_skills(text):
    """
    NLP-based skill extraction using spaCy's PhraseMatcher over a
    tokenized Doc, instead of raw regex over a lowercased string.
    Same return type as before (list[str]) so callers don't need to change.
    """
    doc = nlp(text)
    matches = _skill_matcher(doc)
    extracted = set()
    for match_id, start, end in matches:
        span = doc[start:end]
        extracted.add(span.text.title())
    return list(extracted)


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


