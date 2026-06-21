"""Prompt Templates — Standardised prompts for different response modes."""

PLAIN_LANGUAGE_SUFFIX = """

Rewrite the above answer in plain, everyday language that a non-technical person \
with no background in cybersecurity or law could understand. Use short sentences, \
avoid jargon, and explain any technical terms in parentheses.\
"""

PROFESSIONAL_SUFFIX = """

Rewrite the above answer at a professional level suitable for a compliance officer \
or IT manager. Use precise terminology but keep it concise.\
"""

LEGAL_SUFFIX = """

Rewrite the above answer with full legal precision, citing exact section/clause \
numbers from the regulatory sources. Use formal legal language.\
"""


def plain_language_prompt(base_prompt: str) -> str:
    """Append instructions to simplify the response."""
    return base_prompt + PLAIN_LANGUAGE_SUFFIX


def professional_prompt(base_prompt: str) -> str:
    """Append instructions for professional-level response."""
    return base_prompt + PROFESSIONAL_SUFFIX


def legal_prompt(base_prompt: str) -> str:
    """Append instructions for legal-grade response."""
    return base_prompt + LEGAL_SUFFIX
