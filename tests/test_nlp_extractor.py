"""
Tests for utils/nlp_extractor.py.

Note: importing this module loads the spaCy `en_core_web_sm` model, so these
tests require it to be installed locally:
    python -m spacy download en_core_web_sm

Run with:  pytest tests/test_nlp_extractor.py -v
"""
import pytest
from utils.nlp_extractor import extract_projects, extract_skills


class TestExtractProjects:
    def test_basic_project_section(self):
        text = """
        PROJECTS
        AI Resume Analyzer
        Built a resume parsing tool using Python and spaCy.

        EDUCATION
        B.Tech Computer Science, 2021-2025
        """
        projects = extract_projects(text)
        assert any("Resume Analyzer" in p for p in projects)

    def test_no_projects_section_returns_empty(self):
        text = """
        EDUCATION
        B.Tech Computer Science, 2021-2025

        SKILLS
        Python, SQL, Machine Learning
        """
        assert extract_projects(text) == []

    def test_stops_at_next_section_header(self):
        # Regression guard: project extraction must not bleed into the
        # next resume section (e.g. Education) once it's reached.
        text = """
        PROJECTS
        Chatbot Assistant using LangChain

        EXPERIENCE
        Software Engineer, Some Company
        """
        projects = extract_projects(text)
        assert not any("Software Engineer" in p for p in projects)

    def test_wrapped_project_title_with_open_bracket_is_joined(self):
        # PDF text extraction sometimes wraps a long title across two lines,
        # leaving an unclosed parenthesis on the first line.
        text = """
        PROJECTS
        GenAI Chatbot (LangChain
        Project) for customer support
        """
        projects = extract_projects(text)
        assert any("GenAI Chatbot" in p for p in projects)


class TestExtractSkills:
    def test_extracts_known_skill(self):
        text = "I have 3 years of experience in Python and Machine Learning."
        skills = extract_skills(text)
        assert "Python" in skills
        assert "Machine Learning" in skills

    def test_no_skills_present_returns_empty_list(self):
        text = "I enjoy hiking, reading, and playing the guitar on weekends."
        skills = extract_skills(text)
        assert skills == []

    def test_returns_list_type_not_set(self):
        # analyzer.py / career.py expect list[str] (e.g. for sorting, slicing)
        skills = extract_skills("Python and SQL developer.")
        assert isinstance(skills, list)


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))