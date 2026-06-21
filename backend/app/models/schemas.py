"""Pydantic schemas for API request/response models."""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

class Language(str, Enum):
    EN = "en"
    NE = "ne"


class ReadabilityLevel(str, Enum):
    SIMPLE = "simple"
    PROFESSIONAL = "professional"
    LEGAL = "legal"


class ChatRequest(BaseModel):
    """Incoming chat message."""
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    language: Language = Language.EN
    private_mode: bool = True
    readability_level: ReadabilityLevel = ReadabilityLevel.SIMPLE


class SourceCitation(BaseModel):
    """A single source citation."""
    source: str
    section: str
    confidence: float = Field(ge=0.0, le=1.0)


class ChatResponse(BaseModel):
    """Response sent back to the frontend."""
    response: str
    plain_language: Optional[str] = None
    professional: Optional[str] = None
    legal: Optional[str] = None
    confidence: str = "medium"
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.5)
    sources: list[str] = []
    source_citations: list[SourceCitation] = []
    session_id: str
    shap_summary: Optional[str] = None
    bias_audit_passed: bool = True


# ---------------------------------------------------------------------------
# Gap Assessment
# ---------------------------------------------------------------------------

class GapStartRequest(BaseModel):
    """Request to start a gap assessment."""
    session_id: Optional[str] = None
    language: Language = Language.EN


class GapAnswerRequest(BaseModel):
    """Submit an answer to a gap-assessment question."""
    session_id: str
    question_id: str
    answer: str = Field(..., pattern="^(Yes|Partially|No)$")


class GapQuestionResponse(BaseModel):
    """A question to present to the user."""
    question_id: str
    domain: str
    domain_code: str
    text: str
    options: list[str]
    regulatory_ref: str
    progress: str
    total_questions: int
    answered: int


class GapStepResponse(BaseModel):
    """Response after submitting an answer or starting assessment."""
    question: Optional[GapQuestionResponse] = None
    is_complete: bool = False
    domain_scores: dict[str, float] = {}
    overall_score: float = 0.0
    total_answered: int = 0
    report_text: Optional[str] = None


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str
    model_loaded: bool = False
    chromadb_connected: bool = False
    corpus_size: int = 0
