# JobFit AI — AI-Powered Resume Analysis & Job Recommendation System

> **Analyze your resume. Discover skill gaps. Get matched to jobs. Prepare for interviews — all in one place.**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?logo=streamlit)](https://streamlit.io/)
[![LLM](https://img.shields.io/badge/LLM-Groq%20%7C%20GPT--OSS%20120B-green)](https://groq.com/)
[![License](https://img.shields.io/badge/License-Unlicensed-lightgrey)](#-license)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Project Structure](#-project-structure)
- [Tech Stack](#-tech-stack)
- [Datasets](#-datasets)
- [Getting Started](#-getting-started)
- [Configuration](#-configuration)
- [Module Walkthrough](#-module-walkthrough)
- [How It Works](#-how-it-works)
- [Screenshots](#-screenshots)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

**JobFit AI** is an end-to-end, AI-powered career intelligence platform built with **Streamlit**. It helps job seekers — from freshers to senior professionals — understand how well their resume matches a target role, discover which skills they are missing, find relevant job listings (from a curated dataset and, optionally, live from Adzuna), and prepare for technical interviews — all backed by a large language model via Groq.

### Why JobFit AI?

| Problem | JobFit AI Solution |
|---|---|
| "Why did my resume get rejected?" | ATS Score with weighted must-have / nice-to-have skill breakdown |
| "Which skills should I learn next?" | Personalized 4-week learning roadmap from AI |
| "Which jobs match my profile?" | TF-IDF cosine similarity against a curated dataset, plus optional live Adzuna search |
| "How do I prepare for interviews?" | AI-generated mock questions + answer evaluation |
| "What are career growth trends?" | Visual dashboard with salary, growth & demand data |

---

## ✨ Key Features

### 1. 📄 Resume Analyzer
- Upload a **PDF or DOCX** resume
- Automatically extract skills, projects, and experience level
- Get an **ATS Match Score** (0–100%) broken down by must-have (70%) and good-to-have (30%) skills
- See exactly which skills are **matched** vs **missing**
- Receive **AI-generated resume improvement suggestions** tailored to your role and experience level

### 2. 📊 Career Dashboard
- Visual overview of your resume analysis results
- Skill match progress bars
- Plotly-powered charts for ATS scores and skill coverage
- Persistent session state — no re-uploads needed across pages

### 3. 💼 Job Recommendation
- Matches your resume against a curated jobs dataset using **TF-IDF cosine similarity**
- Optionally pulls **real, live job listings from the Adzuna API** (requires `ADZUNA_APP_ID` / `ADZUNA_APP_KEY`)
- Displays match score, matched skills, and missing skills per job listing
- Apply links point to the original job dataset entry or, for live results, directly to the Adzuna listing

### 4. 🗺️ Learning Path
- AI-generated **4-week roadmap** specific to your target role and experience level
- Adapts content for Fresher / Mid-Level / Senior candidates
- Focuses only on your **missing skills** — no generic advice
- Pulls real YouTube playlists per skill (needs `YOUTUBE_API_KEY`; falls back to a plain search link if not configured)
- Export roadmap as a **PDF**

### 5. 🎤 Interview Preparation
- Two modes:
  - **Question Bank** — role-based, difficulty-tiered question bank (Easy/Medium/Hard, Technical/HR/Conceptual)
  - **AI Mock Interview Coach** — interactive Q&A with project-based questions, AI evaluation of your answers, and a final performance report
- Exportable **PDF interview report**

### 6. 📈 Career Trends (Home Page)
- Industry growth rates, average salaries, and job openings by role, from the curated dataset
- A **live "IT Job Openings" count from Adzuna** when configured (falls back to a clearly-labeled dataset estimate otherwise)
- Top emerging skills across the market
- Role-specific skill demand scores

### 7. 🍔 Navigation
- Persistent top masthead with a hamburger toggle for the sidebar — works well on both desktop and mobile

---

## 🏗️ System Architecture

```
User Uploads Resume (PDF/DOCX)
          │
          ▼
   ┌─────────────┐
   │ PDF Parser  │  ──► Extract raw text (PyPDF2 / python-docx)
   └─────────────┘
          │
          ▼
   ┌──────────────────┐
   │  NLP Extractor   │  ──► Skills, Projects, Experience Level
   └──────────────────┘
          │
    ┌─────┴─────┐
    ▼           ▼
┌─────────┐  ┌───────────────────────────────┐
│  Scorer │  │        Recommender             │
│(ATS     │  │  TF-IDF (dataset) + optional   │
│ Score)  │  │  live Adzuna search             │
└────┬────┘  └───────────────────────────────┘
     │               │
     │               ▼
     │       ┌──────────────┐
     │       │  Job Listings │
     │       └──────────────┘
     │
     ▼
┌────────────────┐
│  Groq LLM API  │  (openai/gpt-oss-120b, configurable via GROQ_MODEL)
│  ai_suggestions│
└────────────────┘
     │
     ├──► Resume Improvement Suggestions
     ├──► 4-Week Learning Roadmap
     ├──► Interview Questions
     └──► Answer Evaluation & Final Report
```

---

## 📁 Project Structure

```
JobFit-AI/
│
├── app.py                        # 🚀 Main entry point — Streamlit app, top masthead & sidebar navigation
│
├── views/                        # 📄 UI Pages (one file per page)
│   ├── home.py                   #    Home page — career trends & market insights
│   ├── analyzer.py               #    Resume Analyzer — upload, score, skill gap
│   ├── dashboard.py              #    Dashboard — visual summary of resume analysis
│   ├── career.py                 #    Job Recommendation — dataset + live Adzuna listings
│   ├── learning.py               #    Learning Path — AI-generated 4-week roadmap
│   └── interview.py              #    Interview Preparation — question bank & mock AI coach
│
├── utils/                        # 🔧 Backend Logic & Helpers
│   ├── pdf_parser.py             #    Extracts raw text from PDF / DOCX files
│   ├── nlp_extractor.py          #    Extracts skills & projects using spaCy + regex
│   ├── scorer.py                 #    ATS scoring — CSV-primary, TF-IDF fallback
│   ├── recommender.py            #    Dataset-based job matching (TF-IDF cosine similarity)
│   ├── job_api.py                #    Live job search & live job-count via the Adzuna API
│   ├── resource_search.py        #    Live YouTube playlists + course search links per skill
│   ├── ai_suggestions.py         #    All Groq LLM prompts & API calls
│   ├── coach_parsing.py          #    Safely parses AI responses into structured data
│   ├── coach_state.py            #    Manages mock interview session state
│   ├── pdf_export.py             #    Generates downloadable PDF reports
│   └── theme.py                  #    Custom CSS, UI components & design system
│
├── dataset/                      # 📊 Data Files
│   ├── role_skills_dataset.csv   #    Must-have & good-to-have skills per role
│   └── career_trends.csv         #    Growth rate, salary & job openings by role
│
├── assets/                       # 🖼️ Static assets (app logo, etc.)
├── screenshots/                  # 📸 README screenshots
├── tests/                        # ✅ Pytest suite (NLP extraction, recommender, scorer)
│
├── .env.example                  # 🔑 Environment variable template
├── .gitignore
└── requirements.txt               # 📦 Python dependencies
```

> **Note:** `utils/recommender.py` expects a `dataset/jobs_2026_market_data.csv` file for the offline/dataset-based job matching path. That file is not currently present in this repository — add it under `dataset/` (or point `DATASET_PATH` in `recommender.py` at your own jobs CSV) before relying on that feature. Live Adzuna search doesn't need it.

---

## 🛠️ Tech Stack

| Category | Technology | Purpose |
|---|---|---|
| **Frontend / UI** | Streamlit | Web application framework |
| **Language** | Python 3.9+ | Core programming language |
| **LLM / AI** | Groq API (default model: `openai/gpt-oss-120b`) | Resume suggestions, roadmap, interview coaching |
| **Live Jobs** | Adzuna API | Live job search & live job-openings count |
| **Learning Resources** | YouTube Data API v3 | Real playlist links per skill |
| **NLP** | spaCy (`en_core_web_sm`) | Named entity recognition, text processing |
| **ML** | scikit-learn (TF-IDF, Cosine Similarity) | Job matching & scoring fallback |
| **Data** | Pandas, NumPy | Dataset loading, manipulation |
| **Charts** | Plotly | Interactive career trend visualizations |
| **PDF Parsing** | PyPDF2, python-docx | Resume text extraction |
| **PDF Export** | ReportLab | Downloadable report generation |
| **Styling** | Custom CSS (via `theme.py`) | Glassmorphism dark UI design |
| **Config** | python-dotenv | Environment variable management |

---

## 📊 Datasets

| File | Rows | Description |
|---|---|---|
| `role_skills_dataset.csv` | 30 roles | Curated must-have and good-to-have skills per job role (used for weighted ATS scoring) |
| `career_trends.csv` | ~150 | Growth rate, average salary (LPA), job openings, and skill demand scores by role |
| `jobs_2026_market_data.csv` *(not included — see note above)* | — | Expected by `recommender.py` for offline/dataset-based job matching |

---

## 🚀 Getting Started

### Prerequisites

- Python **3.9 or higher**
- A **Groq API Key** (free tier available at [groq.com](https://groq.com)) — required for all AI features
- An **Adzuna API Key** (free at [developer.adzuna.com](https://developer.adzuna.com)) — optional, enables live job search & live homepage stats
- A **YouTube Data API v3 Key** (free at [Google Cloud Console](https://console.cloud.google.com/)) — optional, enables real playlist links in the Learning Path
- `pip` package manager

### Step 1 — Clone the Repository

```bash
git clone https://github.com/your-username/JobFit-AI.git
cd JobFit-AI
```

### Step 2 — Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Download spaCy Language Model

```bash
python -m spacy download en_core_web_sm
```

### Step 5 — Configure Environment Variables

```bash
cp .env.example .env
```

Open `.env` and fill in your keys:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b

# Optional — enables live job search + live homepage stats
ADZUNA_APP_ID=your_adzuna_app_id_here
ADZUNA_APP_KEY=your_adzuna_api_key_here

# Optional — enables real YouTube playlist links in Learning Path
YOUTUBE_API_KEY=your_youtube_api_key_here
```

Only `GROQ_API_KEY` is required to run the app. The Adzuna and YouTube keys are optional — each feature fails gracefully to a clearly-labeled fallback if its key is missing.

> **Get a free Groq API key** → [https://console.groq.com](https://console.groq.com)

### Step 6 — Run the Application

```bash
streamlit run app.py
```

The app will open at **`http://localhost:8501`** in your browser.

---

## ⚙️ Configuration

| Variable | File | Required? | Description |
|---|---|---|---|
| `GROQ_API_KEY` | `.env` | **Yes** | Your Groq API key — powers all AI features |
| `GROQ_MODEL` | `.env` | No | Groq model name. Defaults to `openai/gpt-oss-120b` in code if unset |
| `ADZUNA_APP_ID` / `ADZUNA_APP_KEY` | `.env` | No | Enables live job search and the live "Job Openings" homepage stat |
| `YOUTUBE_API_KEY` | `.env` | No | Enables real YouTube playlist links in the Learning Path |

The following are hardcoded path *constants* in code (not environment variables) — edit the source directly if you need to point them elsewhere:

| Constant | File | Description |
|---|---|---|
| `DATASET_PATH` | `utils/recommender.py` | Path to the offline jobs dataset CSV |
| `ROLE_SKILLS_PATH` (`CSV_PATH`) | `utils/scorer.py` | Path to the role-skills CSV |

---

## 🔍 Module Walkthrough

### `utils/pdf_parser.py`
Accepts a Streamlit `UploadedFile` object. Uses **PyPDF2** for PDFs and **python-docx** for Word files to extract raw text. Returns a plain string.

### `utils/nlp_extractor.py`
- **`extract_skills(text)`** — Matches against a curated skill vocabulary using spaCy's `PhraseMatcher`. Covers programming languages, frameworks, cloud, DevOps, databases, ML tools, and soft skills.
- **`extract_projects(text)`** — Multi-pass parser that detects the "Projects" section, joins split lines, and filters out noise (dates, bullets, descriptions) to return clean project titles.

### `utils/scorer.py`
- **Primary path** — Looks up the target role in `role_skills_dataset.csv` with 3-level matching (exact → partial → word-overlap). Computes a **weighted ATS score**: must-have skills (70%) + good-to-have skills (30%).
- **Fallback path** — TF-IDF cosine similarity between resume skills and job description string.
- Results cached with `lru_cache` for performance.

### `utils/recommender.py`
- Loads the offline jobs dataset once with `@st.cache_data` (see the dataset note above).
- Vectorizes all job skill columns using **TF-IDF**.
- Transforms the resume skills string and computes **cosine similarity** scores against every job.
- Returns top N jobs with per-job match scores, matched skills, and missing skills.

### `utils/job_api.py`
- **`search_live_jobs()`** — Fetches real, live job listings from the Adzuna API, deduplicated (Adzuna often returns the same posting multiple times from different source boards) and cached for 1 hour.
- **`get_live_it_job_count()`** — A single lightweight Adzuna call used for the homepage's live "Job Openings" stat, cached for 6 hours. Returns `None` (triggering a dataset fallback) if Adzuna isn't configured.

### `utils/resource_search.py`
- **`search_youtube_playlists()`** — Real, current YouTube playlists per skill via the YouTube Data API v3. Fails silently to an empty list if `YOUTUBE_API_KEY` is missing or the request fails.
- Course links are built directly as stable platform search-query URLs (Coursera, Udemy, freeCodeCamp, edX) — no API key needed for those.

### `utils/ai_suggestions.py`
All LLM interactions, via the `groq` SDK.

| Function | What it does |
|---|---|
| `generate_resume_suggestions()` | 5-section resume improvement (skills, projects, summary, keywords, actions) |
| `generate_learning_path()` | 4-week structured roadmap with daily/weekly tasks |
| `generate_interview_questions()` | 40-question role-specific bank across difficulty tiers |
| `generate_coach_questions()` | Project-aware mock interview questions for the AI coach |
| `evaluate_answer()` | Scores the candidate's answer and gives structured feedback |
| `generate_final_report()` | Comprehensive interview performance summary |

### `utils/coach_parsing.py`
Safe parsing layer between raw Groq responses and the UI — never raises to the caller. Also normalizes interview-question responses that come back as a markdown table (some models ignore the requested block format) into the canonical format both the on-screen cards and the PDF export expect.

### `utils/pdf_export.py`
Generates downloadable PDF reports (learning roadmaps, interview reports) using **ReportLab**. Escapes raw text before layering markdown-derived formatting on top, so content like `if x<y:` or `List<Integer>` in an AI-generated answer can't be mistaken for markup and crash generation.

---

## ⚙️ How It Works

```
1. User selects target role & experience level on the Resume Analyzer page
2. User uploads PDF or DOCX resume
3. pdf_parser extracts raw text
4. nlp_extractor identifies skills and projects from the text
5. scorer computes ATS score from role_skills_dataset.csv
6. Result is saved to st.session_state["latest_analysis"]
7. All other pages (Dashboard, Job Recommendation, Learning Path, Interview Prep)
   read from this shared session state — no re-upload needed
8. AI features (suggestions, roadmap, interview coaching) call the Groq API on demand
9. Live features (job search, live job count, YouTube resources) call their
   respective APIs on demand and fall back gracefully if unconfigured
```

**Session State Keys Used:**

| Key | Type | Set By | Used By |
|---|---|---|---|
| `latest_analysis` | `dict` | Resume Analyzer | Dashboard, Learning, Interview |
| `qbank_result` | `str` | Interview Prep (Question Bank) | Interview Prep (Question Bank) |
| `coach_state` | `dict` | AI Coach | AI Coach (mock interview session) |

---

## 📸 Screenshots

### 🏠 Home — Career Market Overview
> Tracked skills, career paths, an openings-weighted average salary, and job openings — live from Adzuna when configured, or a clearly-labeled dataset estimate otherwise

![Home Page](screenshots/home.jpeg)

---
### 📊 Resume Analyzer
![Resume Analyzer](screenshots/Resume_analyzer.jpeg)

---

### 📊 Dashboard — Resume Strength Meter
> ATS gauge chart with score breakdown across Skills Match, ATS Keywords, Experience Level, and Education

![Dashboard](screenshots/dashboard.jpeg)

---
### 💼 Job Recommendation — Skill-Based Job Search
> Skills auto-loaded from resume analysis. Editable skill list, role filter, and "Skills You Should Learn" gap suggestions

![Job Recommendation](screenshots/job_recommendation.jpeg)

---

### 🗺️ Learning Path — AI Roadmap Generator
> Three modes: From Resume Analysis / By Job Role / Custom Input. Shows target role, experience level, missing skills, and generates a 4-week roadmap

![Learning Path](screenshots/Learning_Path.jpeg)

---

### 🎤 Interview Preparation — AI Coach
> Auto-filled from resume. Choose between a 40-question bank or the live Mock Interview Coach with AI-evaluated answers

![Interview Preparation](screenshots/Interview_prep.jpeg)

---

## ✅ Testing

A pytest suite covers NLP extraction, the recommender, and the scorer:

```bash
pip install pytest
pytest tests/ -v
```

---

## 🤝 Contributing

Contributions are welcome! To get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a Pull Request

### Areas Open for Contribution
- Add the missing `jobs_2026_market_data.csv` dataset (see note in [Project Structure](#-project-structure))
- Add more roles to `role_skills_dataset.csv`
- Expand the jobs dataset with additional cities / domains
- Implement user authentication for saving history
- Add resume section completeness checker
- Multi-language resume support

---

## 📄 License

No `LICENSE` file is currently included in this repository, so the project is **all rights reserved by default** — others cannot legally reuse, modify, or redistribute the code until a license is added. If you intend this to be open source, add a `LICENSE` file (e.g. [choosealicense.com](https://choosealicense.com/) to pick one) and update the badge at the top of this README to match.

---

## 🙏 Acknowledgements

- [Groq](https://groq.com/) — Ultra-fast LLM inference API
- [Adzuna](https://www.adzuna.com/) — Live job listings API
- [Streamlit](https://streamlit.io/) — Python web app framework
- [spaCy](https://spacy.io/) — Industrial-strength NLP library
- [scikit-learn](https://scikit-learn.org/) — ML utilities for TF-IDF & cosine similarity

---

<div align="center">
  <b>JobFit AI v1.0</b> — AI-Powered Career Intelligence<br>
  Built with ❤️ using Python & Streamlit
</div>
