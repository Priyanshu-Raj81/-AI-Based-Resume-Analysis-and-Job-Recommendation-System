"""
Tests for utils/scorer.py — the core ATS scoring logic.

Run with:  pytest tests/test_scorer.py -v
(Run from the project root so the `utils` package resolves correctly.)
"""
import pytest
from utils.scorer import get_ats_score, calculate_similarity_score


class TestGetAtsScore:
    """get_ats_score() is a pure function — no dataset/model dependency."""

    def test_full_match(self):
        assert get_ats_score(5, 5) == 100

    def test_partial_match(self):
        assert get_ats_score(3, 4) == 75

    def test_no_match(self):
        assert get_ats_score(0, 5) == 0

    def test_zero_total_skills_does_not_crash(self):
        # Regression guard: division by zero must return 0, not raise.
        assert get_ats_score(0, 0) == 0

    def test_score_never_exceeds_100(self):
        # Guards against a matched_count > total_count edge case producing >100%.
        assert get_ats_score(10, 5) == 100


class TestCalculateSimilarityScore:
    """
    calculate_similarity_score() — CSV-based (must-have/good-to-have) scoring
    for a known role, and safe fallback behavior for edge cases.
    """

    def test_empty_resume_skills_returns_zero(self):
        score, missing = calculate_similarity_score([], target_role="Data Scientist")
        assert score == 0
        assert missing == []

    def test_known_role_full_skill_match_scores_high(self):
        # "Data Analyst" is a curated role in role_skills_dataset.csv.
        # Feeding in a broad, realistic skill set should score reasonably high,
        # not 0 — a regression here would mean the CSV lookup silently broke.
        resume_skills = [
            "Python", "SQL", "Excel", "Power BI", "Statistics",
            "Data Visualization", "Pandas", "NumPy",
        ]
        score, missing = calculate_similarity_score(resume_skills, target_role="Data Analyst")
        assert score > 40, f"Expected a reasonably high score for a strong skill match, got {score}"
        assert isinstance(missing, list)

    def test_unknown_role_does_not_crash(self):
        # A role that isn't in role_skills_dataset.csv and has no job_skills_str
        # to fall back on should degrade gracefully to (0, []), not raise.
        score, missing = calculate_similarity_score(["Python"], target_role="Underwater Basket Weaver")
        assert score == 0
        assert missing == []

    def test_missing_skills_are_title_cased(self):
        # Missing-skill chips are displayed in the UI — they should be
        # human-readable ("Sql" not "sql").
        score, missing = calculate_similarity_score(["Python"], target_role="Data Analyst")
        for skill in missing:
            assert skill[0].isupper(), f"Expected title-cased skill, got {skill!r}"


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))