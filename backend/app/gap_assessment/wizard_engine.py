"""Gap Assessment Wizard Engine — Stateful question flow and scoring.

Manages the assessment session: tracks which questions have been answered,
computes domain scores, and advances through the 5 domains sequentially.
"""
import logging
from dataclasses import dataclass, field
from typing import Optional

from app.gap_assessment.question_bank import (
    ALL_QUESTIONS,
    DOMAINS,
    DOMAIN_QUESTIONS,
    Question,
)

logger = logging.getLogger(__name__)

# Scoring: "Yes"=1.0, "Partially"=0.5, "No"=0.0
_ANSWER_SCORES = {"Yes": 1.0, "Partially": 0.5, "No": 0.0}


@dataclass
class AssessmentState:
    """Mutable state for a single assessment session."""
    session_id: str
    answers: dict[str, str] = field(default_factory=dict)  # question_id → answer
    current_domain_index: int = 0
    current_question_index: int = 0
    is_complete: bool = False


@dataclass
class WizardStep:
    """A single step in the wizard — the next question to present."""
    question: Question
    domain: str
    domain_code: str
    progress: str  # e.g. "Domain 1/5, Question 2/5"
    total_questions: int
    answered: int


def get_wizard_step(state: AssessmentState) -> Optional[WizardStep]:
    """Return the next unanswered question, or None if assessment is complete."""
    domain_codes = list(DOMAINS.keys())

    if state.current_domain_index >= len(domain_codes):
        state.is_complete = True
        return None

    domain_code = domain_codes[state.current_domain_index]
    questions = DOMAIN_QUESTIONS[domain_code]

    # Find next unanswered question in this domain
    while state.current_question_index < len(questions):
        q = questions[state.current_question_index]
        if q.id not in state.answers:
            answered = len(state.answers)
            return WizardStep(
                question=q,
                domain=DOMAINS[domain_code],
                domain_code=domain_code,
                progress=f"Domain {state.current_domain_index + 1}/5, "
                         f"Question {state.current_question_index + 1}/{len(questions)}",
                total_questions=len(ALL_QUESTIONS),
                answered=answered,
            )
        state.current_question_index += 1

    # All questions in this domain answered — move to next domain
    state.current_domain_index += 1
    state.current_question_index = 0

    # Recurse to get first question of next domain
    return get_wizard_step(state)


def submit_answer(state: AssessmentState, question_id: str, answer: str) -> dict:
    """Record an answer and return the next step.

    Returns
    -------
    dict
        Keys: ``next_step`` (WizardStep or None), ``is_complete`` (bool),
        ``domain_scores`` (current running scores).
    """
    if answer not in _ANSWER_SCORES:
        raise ValueError(f"Invalid answer '{answer}'. Must be one of: Yes, Partially, No")

    state.answers[question_id] = answer
    logger.info("Answer recorded: %s → %s (total: %d)", question_id, answer, len(state.answers))

    # Move past the answered question
    state.current_question_index += 1

    next_step = get_wizard_step(state)

    if next_step is None:
        state.is_complete = True

    return {
        "next_step": next_step,
        "is_complete": state.is_complete,
        "domain_scores": compute_domain_scores(state),
        "overall_score": compute_overall_score(state),
        "total_answered": len(state.answers),
    }


def compute_domain_scores(state: AssessmentState) -> dict[str, float]:
    """Compute normalised 0–100 scores for each domain."""
    scores: dict[str, float] = {}
    for domain_code, questions in DOMAIN_QUESTIONS.items():
        domain_answers = [state.answers.get(q.id) for q in questions]
        scored = [_ANSWER_SCORES.get(a, 0.0) for a in domain_answers if a is not None]
        if scored:
            scores[domain_code] = round((sum(scored) / len(questions)) * 100, 1)
        else:
            scores[domain_code] = 0.0
    return scores


def compute_overall_score(state: AssessmentState) -> float:
    """Compute the overall compliance score (0–100)."""
    domain_scores = compute_domain_scores(state)
    if not domain_scores:
        return 0.0
    return round(sum(domain_scores.values()) / len(domain_scores), 1)


def start_assessment(session_id: str) -> WizardStep:
    """Create a fresh assessment state and return the first question."""
    state = AssessmentState(session_id=session_id)
    step = get_wizard_step(state)
    return state, step
