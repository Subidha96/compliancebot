"""Tests for the gap assessment engine."""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestQuestionBank:
    """Tests for the question bank."""

    def test_25_questions_total(self):
        from app.gap_assessment.question_bank import ALL_QUESTIONS
        assert len(ALL_QUESTIONS) == 25

    def test_5_questions_per_domain(self):
        from app.gap_assessment.question_bank import DOMAIN_QUESTIONS
        for domain_code, questions in DOMAIN_QUESTIONS.items():
            assert len(questions) == 5, f"Domain {domain_code} has {len(questions)} questions, expected 5"

    def test_all_questions_have_required_fields(self):
        from app.gap_assessment.question_bank import ALL_QUESTIONS
        for q in ALL_QUESTIONS:
            assert q.id, f"Question missing id"
            assert q.domain, f"Question {q.id} missing domain"
            assert q.text, f"Question {q.id} missing text"
            assert len(q.options) == 3, f"Question {q.id} should have 3 options"
            assert q.options == ["Yes", "Partially", "No"]
            assert q.regulatory_ref, f"Question {q.id} missing regulatory_ref"

    def test_domains_dict(self):
        from app.gap_assessment.question_bank import DOMAINS
        assert len(DOMAINS) == 5
        assert set(DOMAINS.keys()) == {"IR", "DP", "AC", "SA", "TPR"}


class TestWizardEngine:
    """Tests for the wizard state machine."""

    def test_start_assessment(self):
        from app.gap_assessment.wizard_engine import start_assessment
        state, step = start_assessment("test-session")
        assert state.session_id == "test-session"
        assert step is not None
        assert step.question.id == "IR-01"
        assert step.domain == "Incident Response"

    def test_submit_answer_advances(self):
        from app.gap_assessment.wizard_engine import start_assessment, submit_answer
        state, step = start_assessment("test-session")
        result = submit_answer(state, "IR-01", "Yes")
        assert result["total_answered"] == 1
        assert result["next_step"] is not None
        assert result["next_step"].question.id == "IR-02"

    def test_submit_all_answers_completes(self):
        from app.gap_assessment.wizard_engine import start_assessment, submit_answer, get_wizard_step
        from app.gap_assessment.question_bank import ALL_QUESTIONS

        state, _ = start_assessment("test-session")
        for q in ALL_QUESTIONS:
            result = submit_answer(state, q.id, "Yes")

        assert result["is_complete"] is True
        assert result["overall_score"] == 100.0

    def test_domain_scores_all_yes(self):
        from app.gap_assessment.wizard_engine import start_assessment, submit_answer
        from app.gap_assessment.question_bank import ALL_QUESTIONS

        state, _ = start_assessment("test-session")
        for q in ALL_QUESTIONS:
            submit_answer(state, q.id, "Yes")

        from app.gap_assessment.wizard_engine import compute_domain_scores
        scores = compute_domain_scores(state)
        assert all(s == 100.0 for s in scores.values())

    def test_domain_scores_all_no(self):
        from app.gap_assessment.wizard_engine import start_assessment, submit_answer
        from app.gap_assessment.question_bank import ALL_QUESTIONS

        state, _ = start_assessment("test-session")
        for q in ALL_QUESTIONS:
            submit_answer(state, q.id, "No")

        from app.gap_assessment.wizard_engine import compute_domain_scores
        scores = compute_domain_scores(state)
        assert all(s == 0.0 for s in scores.values())

    def test_invalid_answer_raises(self):
        from app.gap_assessment.wizard_engine import start_assessment, submit_answer
        state, _ = start_assessment("test-session")
        with pytest.raises(ValueError):
            submit_answer(state, "IR-01", "Maybe")


class TestReportGenerator:
    """Tests for the report generator."""

    def test_generate_report_all_yes(self):
        from app.gap_assessment.wizard_engine import start_assessment, submit_answer
        from app.gap_assessment.report_generator import generate_report
        from app.gap_assessment.question_bank import ALL_QUESTIONS

        state, _ = start_assessment("test-session")
        for q in ALL_QUESTIONS:
            submit_answer(state, q.id, "Yes")

        report = generate_report(state)
        assert report.overall_score == 100.0
        assert report.overall_maturity == "Optimised"
        assert len(report.strengths) == 5
        assert len(report.priorities) == 0

    def test_generate_report_all_no(self):
        from app.gap_assessment.wizard_engine import start_assessment, submit_answer
        from app.gap_assessment.report_generator import generate_report
        from app.gap_assessment.question_bank import ALL_QUESTIONS

        state, _ = start_assessment("test-session")
        for q in ALL_QUESTIONS:
            submit_answer(state, q.id, "No")

        report = generate_report(state)
        assert report.overall_score == 0.0
        assert report.overall_maturity == "Initial"
        assert len(report.priorities) == 5

    def test_format_report_text(self):
        from app.gap_assessment.wizard_engine import start_assessment, submit_answer
        from app.gap_assessment.report_generator import generate_report, format_report_text
        from app.gap_assessment.question_bank import ALL_QUESTIONS

        state, _ = start_assessment("test-session")
        for q in ALL_QUESTIONS:
            submit_answer(state, q.id, "Partially")

        report = generate_report(state)
        text = format_report_text(report)
        assert "COMPLIANCE GAP-ASSESSMENT REPORT" in text
        assert "Overall Score:" in text
        assert "Domain" in text or "INCIDENT RESPONSE" in text.upper()

    def test_mixed_answers(self):
        from app.gap_assessment.wizard_engine import start_assessment, submit_answer
        from app.gap_assessment.report_generator import generate_report
        from app.gap_assessment.question_bank import ALL_QUESTIONS

        state, _ = start_assessment("test-session")
        for i, q in enumerate(ALL_QUESTIONS):
            if i % 3 == 0:
                submit_answer(state, q.id, "Yes")
            elif i % 3 == 1:
                submit_answer(state, q.id, "Partially")
            else:
                submit_answer(state, q.id, "No")

        report = generate_report(state)
        assert 0 < report.overall_score < 100
        assert len(report.domain_reports) == 5
