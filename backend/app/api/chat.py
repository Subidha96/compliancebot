"""Chat API endpoint — RAG-powered GRC chatbot with bilingual support.

Pipeline: query → retrieve → prompt → LLM → bias audit → translate → respond
Falls back to retrieval-only if LLM is not available.
"""
import uuid
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    SourceCitation,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])

# In-memory session store (ephemeral by design)
_sessions: dict[str, dict] = {}

# Lazy-loaded singletons (avoid import-time failures)
_llm_available: Optional[bool] = None


def _get_or_create_session(session_id: Optional[str]) -> str:
    if session_id and session_id in _sessions:
        return session_id
    new_id = session_id or str(uuid.uuid4())
    _sessions[new_id] = {"messages": []}
    return new_id


def _check_llm_available() -> bool:
    """Check if LLM model can be loaded (cached after first check)."""
    global _llm_available
    if _llm_available is not None:
        return _llm_available
    try:
        from app.llm.model_loader import get_model
        get_model()
        _llm_available = True
        logger.info("LLM model loaded successfully")
    except Exception as e:
        _llm_available = False
        logger.warning("LLM not available (%s) — using retrieval-only mode", e)
    return _llm_available


def _build_context_block(chunks: list[dict]) -> str:
    """Build the context string from retrieved chunks."""
    return "\n\n".join(
        f"[Source: {c['metadata']['source']}, {c['metadata']['section']}]\n{c['text']}"
        for c in chunks
    )


def _format_response_from_chunks(query: str, chunks: list[dict]) -> str:
    """Build a readable answer directly from retrieved chunks (no LLM needed).

    Extracts the most relevant passages from the top chunks and presents
    them as a structured answer with source citations.
    """
    if not chunks:
        return "I don't have enough information to answer that question."

    query_lower = query.lower()
    query_words = set(query_lower.split())

    scored_parts: list[tuple[float, str, str, str]] = []
    for chunk in chunks:
        text = chunk["text"].strip()
        src = chunk["metadata"]["source"]
        sec = chunk["metadata"]["section"]
        conf = chunk.get("confidence", 0.5)

        # Split into paragraphs (double newline) or sentences
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if len(paragraphs) <= 1:
            paragraphs = [s.strip() + "." for s in text.split(". ") if len(s.strip()) > 15]

        # Score each paragraph by keyword overlap with query
        best_para = ""
        best_score = -1
        for para in paragraphs:
            para_lower = para.lower()
            # Score: direct phrase match + word overlap
            score = 0
            if query_lower in para_lower:
                score += 10  # Exact phrase match
            for word in query_words:
                if len(word) > 3 and word in para_lower:
                    score += 1
            if score > best_score:
                best_score = score
                best_para = para

        if best_para and best_score >= 0:
            # Truncate very long passages
            if len(best_para) > 600:
                best_para = best_para[:600].rsplit(" ", 1)[0] + "..."
            scored_parts.append((conf + best_score * 0.1, best_para, src, sec))

    # Sort by combined score (relevance + confidence)
    scored_parts.sort(key=lambda x: x[0], reverse=True)

    # Deduplicate by source — keep best passage per source
    seen_sources: set[str] = set()
    unique_parts: list[tuple[float, str, str, str]] = []
    for part in scored_parts:
        src_key = part[2]
        if src_key not in seen_sources:
            seen_sources.add(src_key)
            unique_parts.append(part)

    top_parts = unique_parts[:3]

    if not top_parts:
        # Absolute fallback: use first chunk
        c = chunks[0]
        text = c["text"][:500].strip()
        return f"{text}\n\nSource: {c['metadata']['source']} ({c['metadata']['section']})"

    # Build the response with clear formatting
    answer_parts = []
    sources_seen: list[str] = []
    for conf, passage, src, sec in top_parts:
        answer_parts.append(passage)
        label = f"{src} ({sec})"
        if label not in sources_seen:
            sources_seen.append(label)

    answer = "\n\n".join(answer_parts)
    sources_str = "; ".join(sources_seen)

    return f"{answer}\n\nSources: {sources_str}"


def _build_plain_language(chunks: list[dict]) -> str:
    """Extract the most accessible chunk as plain-language version."""
    for c in chunks:
        text = c["text"].strip()
        # Prefer shorter, simpler chunks
        if len(text) < 600:
            return f"[{c['metadata']['source']}]\n{text}"
    # Fallback: truncate the first chunk
    if chunks:
        text = chunks[0]["text"].strip()
        return f"[{chunks[0]['metadata']['source']}]\n{text[:500]}..."
    return ""


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Process a chat message through the RAG pipeline.

    If LLM is available: retrieve → prompt → generate → audit → translate
    If LLM is unavailable: retrieve → format from chunks directly
    """
    session_id = _get_or_create_session(request.session_id)
    query = request.message.strip()

    if not query:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        # 1. Retrieve relevant chunks
        from app.rag.retriever import retrieve
        chunks = retrieve(query, top_k=5)

        if not chunks:
            return ChatResponse(
                response=(
                    "I don't have enough information in my knowledge base to answer that question accurately. "
                    "Could you rephrase, or ask about a specific Nepal cybersecurity regulation, "
                    "ISO 27001 control, or NIST CSF topic?"
                ),
                plain_language="Try asking about topics like: ISO 27001, Nepal cyber laws, data protection, access controls, or incident response.",
                professional="No relevant corpus entries found for this query. Consider rephrasing or consulting official sources.",
                legal="The knowledge base does not contain sufficient information to provide a legally grounded response.",
                confidence="low",
                confidence_score=0.0,
                sources=[],
                source_citations=[],
                session_id=session_id,
                bias_audit_passed=True,
            )

        # 2. Build source citations
        source_citations = [
            SourceCitation(
                source=c["metadata"]["source"],
                section=c["metadata"]["section"],
                confidence=c.get("confidence", 0.5),
            )
            for c in chunks
        ]
        source_names = list({c["metadata"]["source"] for c in chunks})

        # 3. Check if LLM is available
        llm_ready = _check_llm_available()

        if llm_ready:
            # Full pipeline: LLM generation
            response_text, plain, prof, legal, confidence, shap_summary, bias_passed = (
                _generate_with_llm(query, chunks)
            )
        else:
            # Fallback: format directly from retrieved chunks
            response_text = _format_response_from_chunks(query, chunks)
            plain = _build_plain_language(chunks)
            prof = response_text
            legal = _build_context_block(chunks)
            confidence = "medium"
            shap_summary = None
            bias_passed = True

        # 4. Detect language and translate if needed
        from app.rag.ingest import _detect_language
        query_lang = _detect_language(query)

        if query_lang == "ne" and settings.TRANSLATE_OUTPUT and llm_ready:
            from app.llm.translator import translate
            response_text = translate(response_text, source_lang="en", target_lang="ne")
            plain = translate(plain, source_lang="en", target_lang="ne") if plain else ""

        return ChatResponse(
            response=response_text,
            plain_language=plain,
            professional=prof,
            legal=legal,
            confidence=confidence,
            confidence_score=chunks[0].get("confidence", 0.5) if chunks else 0.5,
            sources=source_names,
            source_citations=source_citations,
            session_id=session_id,
            shap_summary=shap_summary,
            bias_audit_passed=bias_passed,
        )

    except Exception as e:
        logger.error("Chat pipeline error: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}",
        )


def _generate_with_llm(query: str, chunks: list[dict]) -> tuple:
    """Run the full LLM generation pipeline.

    Returns (response, plain, professional, legal, confidence, shap_summary, bias_passed)
    """
    from app.rag.prompt_builder import build_rag_prompt
    from app.llm.inference import generate_response, parse_response
    from app.llm.prompt_templates import (
        plain_language_prompt,
        professional_prompt,
        legal_prompt,
    )
    from app.bias_audit.tone_checker import audit_response, rewrite_biased_response

    # Build prompt and generate
    base_prompt = build_rag_prompt(query, chunks)
    raw_response = generate_response(base_prompt)
    parsed = parse_response(raw_response)

    # Generate readability variants
    plain = generate_response(plain_language_prompt(base_prompt), max_new_tokens=512)
    prof = generate_response(professional_prompt(base_prompt), max_new_tokens=512)
    legal = generate_response(legal_prompt(base_prompt), max_new_tokens=512)

    # Bias audit
    audit = audit_response(parsed["answer"])
    if not audit.passed:
        parsed["answer"] = rewrite_biased_response(parsed["answer"], audit.issues)

    # SHAP explainability
    shap_summary = None
    if settings.SHAP_ENABLED:
        try:
            from app.llm.shap_explainer import explain_generation
            shap_result = explain_generation(base_prompt, parsed["answer"])
            shap_summary = shap_result.get("summary")
        except Exception as e:
            logger.warning("SHAP explanation failed: %s", e)

    return (
        parsed["answer"],
        plain,
        prof,
        legal,
        parsed["confidence"],
        shap_summary,
        audit.passed,
    )
