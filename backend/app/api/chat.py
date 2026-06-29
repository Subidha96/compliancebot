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
    ReadabilityLevel,
    SourceCitation,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])

# In-memory session store (ephemeral by design)
_sessions: dict[str, dict] = {}

# Verified official source URLs, keyed by document stem (the `source` field
# in chunk metadata). Confirmed via direct lookup against the issuing body's
# own site — do not add an entry here without verifying it first.
_SOURCE_URLS: dict[str, str] = {
    "iso_27001_2022_controls_summary": "https://www.iso.org/standard/27001",
    "nist_csf_2_0_summary": "https://www.nist.gov/cyberframework",
    "electronic_transactions_act_2063_key_clauses": "https://lawcommission.gov.np/content/13397/electronic--electronic--traded-international-act--2063/",
    "nepal_cyber_security_policy_2023_summary": "https://mocit.gov.np/content/7119/7119-national-cyber-security-policy/",
    "privacy_act_2075_summary": "https://lawcommission.gov.np/content/12261/12261-the-privacy-act-2075/",
    "cyber_security_bylaw_2077_checklist": "https://nta.gov.np/uploads/contents/Cyber-Security-Bylaw-2077-2020.pdf",
    "nrb_corporate_governance_directive": "https://www.nrb.org.np",
    "oecd_principles_corporate_governance": "https://www.oecd.org/en/publications/g20-oecd-principles-of-corporate-governance-2023_ed750b30-en.html",
    "nepal_companies_act_2063_summary": "https://lawcommission.gov.np/content/12157/12157-company-act-2063/",
    "iso_37000_governance_summary": "https://www.iso.org/standard/65036.html",
    "nepal_labour_act_2074_summary": "https://lawcommission.gov.np",
}

# Lazy-loaded singletons (avoid import-time failures)
_llm_available: Optional[bool] = None

_GREETING_WORDS = {
    "hi", "hello", "hey", "hiya", "yo", "namaste",
    "thanks", "thank", "thankyou", "ty",
    "bye", "goodbye", "ok", "okay", "k",
}

_GREETING_PHRASES = {
    "how are you", "how r you", "how are u", "hru",
    "whats up", "what's up", "wassup", "sup",
    "who are you", "what are you", "tell me about yourself",
    "what can you do", "what do you do", "help me",
    "good morning", "good afternoon", "good evening",
    "how's it going", "how is it going",
}

_GREETING_RESPONSE = (
    "Hello! I'm ComplianceBot+, here to help you understand cybersecurity "
    "governance, risk, and compliance (GRC) concepts, including Nepal cyber "
    "law, ISO 27001, and NIST CSF, in plain language. Ask me about a "
    "specific topic, like \"What is ISO 27001?\" or \"What does the "
    "Electronic Transactions Act say about data privacy?\", or start the "
    "gap assessment wizard to check your organisation's compliance posture."
)


def _strip_em_dash(text: Optional[str]) -> Optional[str]:
    """Replace em dashes with a comma/hyphen so they never reach the user.

    Project style rule: no '—' in any chatbot-facing response text.
    """
    if not text:
        return text
    return text.replace(" — ", ", ").replace("—", "-")


def _is_greeting(query: str) -> bool:
    """Detect trivial greetings/chitchat that don't need RAG + LLM generation."""
    normalised = query.lower().strip(" !.?").strip()
    # Check common phrases first (e.g. "how are you?")
    if normalised in _GREETING_PHRASES:
        return True
    # Also check partial phrase matches (strip trailing punctuation)
    for phrase in _GREETING_PHRASES:
        if normalised.startswith(phrase):
            return True
    # Fall back to single-word check
    words = normalised.split()
    return len(words) <= 3 and all(w.strip(",!.?") in _GREETING_WORDS for w in words)


def _max_tokens_for_query(query: str) -> int:
    """Scale generation length to the query's apparent complexity.

    Short greetings/simple questions don't need a 1024-token essay —
    this keeps latency proportional to what was actually asked.
    """
    word_count = len(query.split())
    if word_count <= 6:
        return 320
    if word_count <= 15:
        return 384
    return settings.MAX_NEW_TOKENS


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
    from app.core.config import settings
    if not settings.LOAD_LLM and not settings.USE_OLLAMA:
        _llm_available = False
        logger.info("LLM disabled (LOAD_LLM=false, USE_OLLAMA=false) — retrieval-only mode")
        return False
    try:
        from app.llm.model_loader import get_model
        get_model()
        _llm_available = True
        logger.info("LLM model loaded successfully")
    except Exception as e:
        _llm_available = False
        logger.warning("LLM not available (%s) — using retrieval-only mode", e)
    return _llm_available


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

    if _is_greeting(query):
        return ChatResponse(
            response=_GREETING_RESPONSE,
            mode=request.mode,
            confidence="high",
            confidence_score=1.0,
            sources=[],
            source_citations=[],
            session_id=session_id,
            bias_audit_passed=True,
        )

    try:
        # 1. Retrieve relevant chunks
        from app.rag.retriever import retrieve
        chunks = retrieve(query, top_k=5)

        # Auto-ingest if corpus is empty (first request after startup)
        if not chunks:
            try:
                from app.rag.ingest import get_collection, ingest_corpus
                collection = get_collection()
                if collection.count() == 0:
                    import os
                    data_dir = settings.DATA_DIR
                    if not os.path.isdir(data_dir):
                        data_dir = "data_raw"
                    if os.path.isdir(data_dir):
                        logger.info("Corpus empty — auto-ingesting from %s", data_dir)
                        ingest_corpus(raw_dir=data_dir)
                        chunks = retrieve(query, top_k=5)
            except Exception as ingest_err:
                logger.warning("Auto-ingest failed: %s", ingest_err)

        if not chunks:
            return ChatResponse(
                response=(
                    "I don't have enough information in my knowledge base to answer that "
                    "question accurately. I can help with governance, risk, and compliance "
                    "topics including: corporate governance (board structure, shareholder "
                    "rights, OECD Principles), Nepal banking regulation (NRB directives), "
                    "Nepal company law (Companies Act 2063), information security (ISO 27001, "
                    "NIST CSF), privacy law (Privacy Act 2075), and labour law (Labour Act "
                    "2074). Could you rephrase your question or ask about one of these areas?"
                ),
                mode=request.mode,
                confidence="low",
                confidence_score=0.0,
                sources=[],
                source_citations=[],
                session_id=session_id,
                bias_audit_passed=True,
            )

        # 2. Build source citations (with verified official links where known)
        source_citations = [
            SourceCitation(
                source=c["metadata"]["source"],
                section=c["metadata"]["section"],
                confidence=c.get("confidence", 0.5),
                url=_SOURCE_URLS.get(c["metadata"]["source"]),
            )
            for c in chunks
        ]
        source_names = list({c["metadata"]["source"] for c in chunks})
        source_urls = list({_SOURCE_URLS[s] for s in source_names if s in _SOURCE_URLS})

        # 3. Check if LLM is available
        llm_ready = _check_llm_available()

        if llm_ready:
            # Generate a single answer, directly in the session's locked mode
            # (default/simple/professional/legal) — no other mode is ever
            # generated for this turn. Switching modes requires a new chat.
            response_text, confidence, shap_summary, bias_passed = (
                await _generate_main_answer(query, chunks, request.mode)
            )
        else:
            # Fallback: format directly from retrieved chunks (mode-agnostic,
            # since there's no LLM available to rewrite for a given mode).
            response_text = _format_response_from_chunks(query, chunks)
            confidence = "medium"
            shap_summary = None
            bias_passed = True

        return ChatResponse(
            response=_strip_em_dash(response_text),
            mode=request.mode,
            confidence=confidence,
            confidence_score=chunks[0].get("confidence", 0.5) if chunks else 0.5,
            sources=source_names,
            source_urls=source_urls,
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


async def _generate_main_answer(
    query: str, chunks: list[dict], mode: ReadabilityLevel
) -> tuple:
    """Generate the single answer for this turn, directly in `mode`.

    Returns (response, confidence, shap_summary, bias_passed)
    """
    import asyncio

    from app.rag.prompt_builder import build_rag_prompt
    from app.llm.inference import generate_response, parse_response
    from app.bias_audit.tone_checker import audit_response, rewrite_biased_response
    from app.llm.prompt_templates import (
        plain_language_prompt,
        professional_prompt,
        legal_prompt,
    )

    # Scale generation length to query complexity — short questions don't
    # need a 1024-token essay, and this keeps latency proportional to the ask.
    max_tok = _max_tokens_for_query(query)
    base_prompt = build_rag_prompt(query, chunks)

    mode_prompt_fn = {
        ReadabilityLevel.SIMPLE: plain_language_prompt,
        ReadabilityLevel.PROFESSIONAL: professional_prompt,
        ReadabilityLevel.LEGAL: legal_prompt,
    }.get(mode)
    prompt = mode_prompt_fn(base_prompt) if mode_prompt_fn else base_prompt

    # Run off the event loop — generate_response() makes a synchronous
    # HTTP/torch call and would otherwise block all other requests.
    raw_response = await asyncio.to_thread(generate_response, prompt, max_new_tokens=max_tok)
    parsed = parse_response(raw_response)

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
        parsed["confidence"],
        shap_summary,
        audit.passed,
    )
