"""LLM Inference — Generate responses from the loaded model.

Handles tokenisation, generation, and basic response parsing.
Uses chat templates for proper instruction-following (Qwen2, Mistral, etc.).
"""
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def generate_response(
    prompt: str,
    max_new_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    top_p: float = 0.9,
    repetition_penalty: float = 1.1,
) -> str:
    """Generate a response from the LLM.

    Uses the model chat template when available for proper
    instruction-following and stop-token handling.

    Parameters
    ----------
    prompt : str
        The full RAG prompt (system + context + query).
    max_new_tokens : int, optional
        Maximum tokens to generate. Defaults to settings.MAX_NEW_TOKENS.
    temperature : float, optional
        Sampling temperature. Defaults to settings.TEMPERATURE.
    top_p : float
        Nucleus sampling threshold.
    repetition_penalty : float
        Penalty for repeating tokens.

    Returns
    -------
    str
        The generated response text.
    """
    import torch
    from app.core.config import settings
    from app.llm.model_loader import get_model, get_tokenizer

    model = get_model()
    tokenizer = get_tokenizer()

    max_tok = max_new_tokens or settings.MAX_NEW_TOKENS
    temp = temperature if temperature is not None else settings.TEMPERATURE

    messages = [{"role": "user", "content": prompt}]
    try:
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    except Exception:
        text = prompt

    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=4096)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    stop_ids = []
    if tokenizer.eos_token_id is not None:
        stop_ids.append(tokenizer.eos_token_id)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tok,
            temperature=temp,
            top_p=top_p,
            repetition_penalty=repetition_penalty,
            do_sample=temp > 0,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=stop_ids if stop_ids else None,
        )

    generated_ids = outputs[0][inputs["input_ids"].shape[1]:]
    response = tokenizer.decode(generated_ids, skip_special_tokens=True).strip()

    # Strip any leftover prompt/template fragments
    for marker in ["Assistant:", "assistant:", " ANSWER", "User question:"]:
        idx = response.find(marker)
        if idx > 0:
            response = response[:idx].strip()

    logger.info("Generated %d tokens", len(generated_ids))
    return response


def parse_response(response: str) -> dict:
    """Parse a raw LLM response into structured fields.

    Attempts to extract:
    - answer: the main response text
    - citations: any [Source: ...] references found in the text
    - confidence_indicator: inferred confidence level from textual cues
    """
    citation_pattern = re.compile(r"\[Source:\s*([^\]]+)\]")
    citations = citation_pattern.findall(response)

    low_confidence_markers = [
        "not sure",
        "unclear",
        "may not",
        "might not",
        "cannot confirm",
        "recommend checking",
        "please verify",
        "i don't have",
        "not available in the context",
    ]
    high_confidence_markers = [
        "according to",
        "the regulation states",
        "section",
        "clause",
        "mandates",
        "requires",
    ]

    text_lower = response.lower()
    low_hits = sum(1 for m in low_confidence_markers if m in text_lower)
    high_hits = sum(1 for m in high_confidence_markers if m in text_lower)

    if low_hits > high_hits:
        confidence = "low"
    elif high_hits > low_hits:
        confidence = "high"
    else:
        confidence = "medium"

    return {
        "answer": response,
        "citations": citations,
        "confidence": confidence,
    }
