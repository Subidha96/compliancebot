"""Bias & Tone Checker — Inclusive language scoring, gender bias detection.

Every response is checked before delivery. Responses scoring above the bias
threshold are intercepted and rewritten.
"""
import re
import logging
from dataclasses import dataclass, field
from typing import Optional

import textstat

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class BiasAuditResult:
    """Result of a bias/tone audit."""
    bias_score: float  # 0.0 (clean) → 1.0 (highly biased)
    tone_score: float  # 0.0 (hostile) → 1.0 (inclusive/warm)
    readability_score: float  # Flesch-Kincaid grade level
    readability_label: str  # "simple", "professional", "legal"
    issues: list[str] = field(default_factory=list)
    passed: bool = True  # True if bias_score <= threshold


# ---------------------------------------------------------------------------
# Gendered language patterns
# ---------------------------------------------------------------------------

_GENDERED_PATTERNS = [
    (re.compile(r"\bhe\b", re.IGNORECASE), "he/she"),
    (re.compile(r"\bshe\b", re.IGNORECASE), "he/she"),
    (re.compile(r"\bhis\b", re.IGNORECASE), "his/her"),
    (re.compile(r"\bher\b", re.IGNORECASE), "his/her"),
    (re.compile(r"\bhim\b", re.IGNORECASE), "him/her"),
    (re.compile(r"\bmanpower\b", re.IGNORECASE), "workforce/personnel"),
    (re.compile(r"\bchairman\b", re.IGNORECASE), "chairperson"),
    (re.compile(r"\bfireman\b", re.IGNORECASE), "firefighter"),
    (re.compile(r"\bpoliceman\b", re.IGNORECASE), "police officer"),
    (re.compile(r"\bmankind\b", re.IGNORECASE), "humanity"),
    (re.compile(r"\bguys\b", re.IGNORECASE), "everyone/team"),
]

# Patronising or condescending patterns
_PATRONISING_PATTERNS = [
    (re.compile(r"\bjust\b.*\byou\b", re.IGNORECASE), "minimising language"),
    (re.compile(r"\bsimple\b", re.IGNORECASE), "potentially patronising if used about compliance tasks"),
    (re.compile(r"\bobviously\b", re.IGNORECASE), "presumes knowledge"),
    (re.compile(r"\bof course\b", re.IGNORECASE), "presumes knowledge"),
    (re.compile(r"\bbasic\b", re.IGNORECASE), "potentially patronising"),
    (re.compile(r"\byou should know\b", re.IGNORECASE), "presumes knowledge"),
    (re.compile(r"\bit's easy\b", re.IGNORECASE), "minimises complexity"),
    (re.compile(r"\banyone can\b", re.IGNORECASE), "minimises difficulty"),
]

# Exclusionary or biased terms
_EXCLUSIONARY_PATTERNS = [
    (re.compile(r"\bdisables?\b", re.IGNORECASE), "person with a disability"),
    (re.compile(r"\bretarded?\b", re.IGNORECASE), "person with a cognitive disability"),
    (re.compile(r"\bcrippled?\b", re.IGNORECASE), "person with a disability"),
    (re.compile(r"\bblind\b", re.IGNORECASE), "person with visual impairment (if metaphorical)"),
    (re.compile(r"\blame\b", re.IGNORECASE), "person with mobility impairment (if metaphorical)"),
    (re.compile(r"\bminority\b", re.IGNORECASE), "underrepresented group"),
    (re.compile(r"\bforeign\b", re.IGNORECASE), "international (context-dependent)"),
]


def _check_gendered_language(text: str) -> list[str]:
    """Detect gendered language and suggest neutral alternatives."""
    issues = []
    for pattern, suggestion in _GENDERED_PATTERNS:
        matches = pattern.findall(text)
        if matches:
            issues.append(
                f"Gendered language detected: '{matches[0]}' → consider '{suggestion}'"
            )
    return issues


def _check_patronising_tone(text: str) -> list[str]:
    """Detect patronising or condescending language."""
    issues = []
    for pattern, description in _PATRONISING_PATTERNS:
        matches = pattern.findall(text)
        if matches:
            issues.append(f"Potentially patronising: {description}")
    return issues


def _check_exclusionary_language(text: str) -> list[str]:
    """Detect exclusionary or ableist language."""
    issues = []
    for pattern, suggestion in _EXCLUSIONARY_PATTERNS:
        matches = pattern.findall(text)
        if matches:
            issues.append(
                f"Exclusionary term detected: '{matches[0]}' → consider '{suggestion}'"
            )
    return issues


def _compute_bias_score(issues: list[str]) -> float:
    """Convert issue count to a 0–1 bias score."""
    if not issues:
        return 0.0
    # Each issue adds ~0.15 bias, capped at 1.0
    return min(1.0, len(issues) * 0.15)


def _compute_tone_score(text: str) -> float:
    """Score tone warmth/inclusiveness (0 = hostile, 1 = warm)."""
    score = 0.5  # baseline

    # Positive indicators
    warm_patterns = [
        r"\bwelcome\b", r"\bencourage\b", r"\bsupport\b",
        r"\btogether\b", r"\byour team\b", r"\byour organisation\b",
        r"\bgreat question\b", r"\bwell done\b", r"\bnice work\b",
        r"\byou can\b", r"\bempower\b", r"\binclusive\b",
    ]
    for p in warm_patterns:
        if re.search(p, text, re.IGNORECASE):
            score += 0.05

    # Negative indicators
    cold_patterns = [
        r"\bshould have\b", r"\bfail\b", r"\bfailure\b",
        r"\bstupid\b", r"\bobvious\b", r"\buseless\b",
        r"\bwrong\b", r"\berror\b", r"\bmistake\b",
    ]
    for p in cold_patterns:
        if re.search(p, text, re.IGNORECASE):
            score -= 0.05

    return max(0.0, min(1.0, score))


def _classify_readability(grade_level: float) -> str:
    """Map Flesch-Kincaid grade level to a label."""
    if grade_level <= 8:
        return "simple"
    elif grade_level <= 12:
        return "professional"
    else:
        return "legal"


def audit_response(text: str) -> BiasAuditResult:
    """Run the full bias/tone audit on a response.

    Parameters
    ----------
    text : str
        The LLM-generated response to audit.

    Returns
    -------
    BiasAuditResult
        Audit results including scores, issues, and pass/fail status.
    """
    issues: list[str] = []

    # Collect all issues
    issues.extend(_check_gendered_language(text))
    issues.extend(_check_patronising_tone(text))
    issues.extend(_check_exclusionary_language(text))

    # Compute scores
    bias_score = _compute_bias_score(issues)
    tone_score = _compute_tone_score(text)

    # Readability
    try:
        readability = textstat.flesch_kincaid_grade(text)
    except Exception:
        readability = 10.0
    readability_label = _classify_readability(readability)

    passed = bias_score <= settings.BIAS_THRESHOLD

    result = BiasAuditResult(
        bias_score=bias_score,
        tone_score=tone_score,
        readability_score=readability,
        readability_label=readability_label,
        issues=issues,
        passed=passed,
    )

    if not passed:
        logger.warning(
            "Response FAILED bias audit (score=%.2f, threshold=%.2f). Issues: %s",
            bias_score,
            settings.BIAS_THRESHOLD,
            issues,
        )

    return result


def rewrite_biased_response(text: str, issues: list[str]) -> str:
    """Attempt to automatically fix bias issues in a response.

    This is a rule-based rewriter. For production quality, a fine-tuned
    model would be better, but this handles the most common patterns.
    """
    rewritten = text

    # Fix gendered language
    for pattern, suggestion in _GENDERED_PATTERNS:
        rewritten = pattern.sub(suggestion, rewritten)

    # Fix exclusionary terms
    for pattern, suggestion in _EXCLUSIONARY_PATTERNS:
        rewritten = pattern.sub(suggestion, rewritten)

    return rewritten
