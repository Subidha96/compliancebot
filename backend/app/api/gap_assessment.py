"""Gap Assessment API endpoint — 25-question compliance wizard.

Guides users through 5 domains, scores answers, and produces a
gap-assessment report with remediation suggestions.
"""
import uuid
import logging

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    GapStartRequest,
    GapAnswerRequest,
    GapStepResponse,
    GapQuestionResponse,
)
from app.gap_assessment.wizard_engine import (
    AssessmentState,
    get_wizard_step,
    submit_answer,
    start_assessment,
)
from app.gap_assessment.report_generator import generate_report, format_report_text

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/gap", tags=["gap-assessment"])

# In-memory assessment session store
_assessments: dict[str, AssessmentState] = {}


@router.post("/start", response_model=GapStepResponse)
async def start_gap_assessment(request: GapStartRequest) -> GapStepResponse:
    """Start a new gap-assessment and return the first question."""
    session_id = request.session_id or str(uuid.uuid4())

    state, step = start_assessment(session_id)
    _assessments[session_id] = state

    if step is None:
        return GapStepResponse(is_complete=True, total_answered=0)

    question = GapQuestionResponse(
        question_id=step.question.id,
        domain=step.domain,
        domain_code=step.domain_code,
        text=step.question.text,
        options=step.question.options,
        regulatory_ref=step.question.regulatory_ref,
        progress=step.progress,
        total_questions=step.total_questions,
        answered=step.answered,
    )

    return GapStepResponse(
        question=question,
        is_complete=False,
        total_answered=step.answered,
    )


@router.post("/answer", response_model=GapStepResponse)
async def submit_gap_answer(request: GapAnswerRequest) -> GapStepResponse:
    """Submit an answer and receive the next question (or final report)."""
    state = _assessments.get(request.session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Assessment session not found. Call /api/gap/start first.")

    try:
        result = submit_answer(state, request.question_id, request.answer)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if result["is_complete"]:
        # Generate final report
        report = generate_report(state)
        report_text = format_report_text(report)

        return GapStepResponse(
            question=None,
            is_complete=True,
            domain_scores=result["domain_scores"],
            overall_score=result["overall_score"],
            total_answered=result["total_answered"],
            report_text=report_text,
        )

    next_step = result["next_step"]
    if next_step is None:
        report = generate_report(state)
        report_text = format_report_text(report)
        return GapStepResponse(
            question=None,
            is_complete=True,
            domain_scores=result["domain_scores"],
            overall_score=result["overall_score"],
            total_answered=result["total_answered"],
            report_text=report_text,
        )

    question = GapQuestionResponse(
        question_id=next_step.question.id,
        domain=next_step.domain,
        domain_code=next_step.domain_code,
        text=next_step.question.text,
        options=next_step.question.options,
        regulatory_ref=next_step.question.regulatory_ref,
        progress=next_step.progress,
        total_questions=next_step.total_questions,
        answered=next_step.answered,
    )

    return GapStepResponse(
        question=question,
        is_complete=False,
        domain_scores=result["domain_scores"],
        overall_score=result["overall_score"],
        total_answered=result["total_answered"],
    )
