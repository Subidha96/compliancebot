"""Translation Layer — NLLB-200 distilled model for EN↔NE translation.

Handles translation at the output layer rather than generation, since open LLMs
have poor native Nepali generation quality. This is a deliberate architectural
choice: reasoning in English, translation via a specialised model.
"""
import logging
from typing import Optional

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from app.core.config import settings

logger = logging.getLogger(__name__)

_model = None
_tokenizer = None

NLLB_MODEL = "facebook/nllb-200-distilled-600M"

# NLLB language codes
_LANG_CODES = {
    "en": "eng_Latn",
    "ne": "npi_Deva",
}


def load_translation_model():
    """Load NLLB-200 distilled model and tokenizer."""
    global _model, _tokenizer

    if _model is not None:
        return _model, _tokenizer

    logger.info("Loading NLLB-200 translation model: %s", NLLB_MODEL)
    _tokenizer = AutoTokenizer.from_pretrained(NLLB_MODEL)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    _model = AutoModelForSeq2SeqLM.from_pretrained(NLLB_MODEL).to(device)

    logger.info("NLLB model loaded on %s", device)
    return _model, _tokenizer


def translate(
    text: str,
    source_lang: str = "en",
    target_lang: str = "ne",
    max_length: int = 1024,
) -> str:
    """Translate text from source_lang to target_lang using NLLB.

    Parameters
    ----------
    text : str
        The text to translate.
    source_lang : str
        ISO 639-1 language code (default "en").
    target_lang : str
        ISO 639-1 language code (default "ne").
    max_length : int
        Maximum output length in tokens.

    Returns
    -------
    str
        Translated text.
    """
    if not text.strip():
        return text

    # If already in target language, return as-is
    if source_lang == target_lang:
        return text

    model, tokenizer = load_translation_model()

    src_code = _LANG_CODES.get(source_lang, f"{source_lang}_Latn")
    tgt_code = _LANG_CODES.get(target_lang, f"{target_lang}_Deva")

    # NLLB requires a language prefix
    tokenizer.src_lang = src_code
    tokenizer.tgt_lang = tgt_code

    device = next(model.parameters()).device
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=max_length,
        padding=True,
    ).to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=max_length,
            forced_bos_token_id=tokenizer.convert_tokens_to_ids(tgt_code),
        )

    translation = tokenizer.decode(outputs[0], skip_special_tokens=True)
    logger.info("Translated %s→%s (%d chars → %d chars)", source_lang, target_lang, len(text), len(translation))
    return translation


def detect_and_translate_if_needed(
    text: str,
    target_lang: str = "ne",
) -> tuple[str, str]:
    """Detect language and translate to target if needed.

    Returns (detected_lang, translated_text).
    """
    from app.rag.ingest import _detect_language
    detected = _detect_language(text)

    if detected == target_lang:
        return detected, text

    return detected, translate(text, source_lang=detected, target_lang=target_lang)
