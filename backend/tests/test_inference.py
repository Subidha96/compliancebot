"""Tests for the LLM inference pipeline."""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestPromptTemplates:
    """Tests for prompt template generation."""

    def test_plain_language_suffix(self):
        from app.llm.prompt_templates import plain_language_prompt
        base = "Answer: ISO 27001 requires access controls."
        result = plain_language_prompt(base)
        assert result.startswith(base)
        assert "plain" in result.lower() or "everyday" in result.lower()

    def test_professional_suffix(self):
        from app.llm.prompt_templates import professional_prompt
        base = "Answer: ISO 27001 requires access controls."
        result = professional_prompt(base)
        assert result.startswith(base)
        assert "professional" in result.lower() or "compliance officer" in result.lower()

    def test_legal_suffix(self):
        from app.llm.prompt_templates import legal_prompt
        base = "Answer: ISO 27001 requires access controls."
        result = legal_prompt(base)
        assert result.startswith(base)
        assert "legal" in result.lower() or "clause" in result.lower()


class TestBiasAudit:
    """Tests for the bias/tone checker."""

    def test_clean_response_passes(self):
        from app.bias_audit.tone_checker import audit_response
        result = audit_response(
            "Your organisation should implement access controls "
            "as required by ISO 27001 Annex A.9. This ensures "
            "only authorised personnel can access sensitive data."
        )
        assert result.passed is True
        assert result.bias_score <= 0.3

    def test_gendered_language_detected(self):
        from app.bias_audit.tone_checker import audit_response
        result = audit_response(
            "Every employee should do his part to protect the company. "
            "He must follow the security policy."
        )
        assert result.bias_score > 0.0
        assert any("Gendered" in i or "gendered" in i.lower() for i in result.issues)

    def test_patronising_tone_detected(self):
        from app.bias_audit.tone_checker import audit_response
        result = audit_response(
            "It's easy to implement ISO 27001. Anyone can do it. "
            "You should obviously follow the basic steps."
        )
        assert result.bias_score > 0.0

    def test_readability_score(self):
        from app.bias_audit.tone_checker import audit_response
        result = audit_response(
            "ISO 27001 provides a framework for managing information "
            "security risks through systematic assessment and control "
            "implementation across organisational processes."
        )
        assert result.readability_score > 0
        assert result.readability_label in ("simple", "professional", "legal")

    def test_tone_score_range(self):
        from app.bias_audit.tone_checker import audit_response
        result = audit_response("We welcome your questions about compliance.")
        assert 0.0 <= result.tone_score <= 1.0


class TestResponseParsing:
    """Tests for LLM response parsing."""

    def test_parse_citations(self):
        from app.llm.inference import parse_response
        text = "According to [Source: ETA 2063, Section 47], penalties apply."
        parsed = parse_response(text)
        assert len(parsed["citations"]) == 1
        assert "ETA 2063" in parsed["citations"][0]

    def test_parse_high_confidence(self):
        from app.llm.inference import parse_response
        text = "The regulation states in Section 47 that penalties apply. The clause mandates compliance."
        parsed = parse_response(text)
        assert parsed["confidence"] == "high"

    def test_parse_low_confidence(self):
        from app.llm.inference import parse_response
        text = "I'm not sure, the context may not contain this. Please verify with official sources."
        parsed = parse_response(text)
        assert parsed["confidence"] == "low"
