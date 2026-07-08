"""
Tests for utils/recommender.py.

Run with:  pytest tests/test_recommender.py -v
"""
import pandas as pd
import pytest
from utils.recommender import get_role_ats_score, get_job_missing_skills


class TestGetRoleAtsScore:
    def test_works_with_empty_dataframe(self):
        # Regression guard: ATS scoring must NOT depend on the jobs-listings
        # CSV. A previous version silently returned (0, []) whenever the
        # jobs CSV was empty/missing — even though the real scoring logic
        # (role_skills_dataset.csv) never used that CSV at all. If this
        # test starts failing, that bug has come back.
        resume_skills = ["Python", "SQL", "Machine Learning", "Pandas", "NumPy"]
        score, missing = get_role_ats_score(resume_skills, "Data Scientist", pd.DataFrame())
        assert score > 0, "ATS score should not be forced to 0 just because the jobs CSV is empty"

    def test_works_with_none_dataframe(self):
        resume_skills = ["Python", "SQL"]
        score, missing = get_role_ats_score(resume_skills, "Data Analyst", None)
        assert isinstance(score, int)

    def test_no_resume_skills_returns_zero(self):
        score, missing = get_role_ats_score([], "Data Scientist", pd.DataFrame())
        assert score == 0


class TestGetJobMissingSkills:
    def test_partial_match(self):
        resume_skills = ["Python", "SQL"]
        job_skills = "Python, SQL, AWS, Docker"
        score, matched, missing = get_job_missing_skills(resume_skills, job_skills)
        assert score == 50  # 2 of 4 required skills matched
        assert "Python" in matched
        assert "Aws" in missing or "AWS" in missing

    def test_empty_job_skills_returns_zero(self):
        score, matched, missing = get_job_missing_skills(["Python"], "")
        assert score == 0
        assert matched == []
        assert missing == []

    def test_full_match(self):
        score, matched, missing = get_job_missing_skills(
            ["Python", "SQL"], "Python, SQL"
        )
        assert score == 100
        assert missing == []


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))