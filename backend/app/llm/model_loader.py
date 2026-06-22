"""LLM Model Loader — Load and quantize HuggingFace models for inference.

Supports Mistral-7B-Instruct-v0.3 (default) with 4-bit quantisation on GPU,
or falls back to a small CPU-friendly model (Qwen2-0.5B-Instruct) when GPU
is unavailable.
"""
import logging
from typing import Optional

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
)

from app.core.config import settings

logger = logging.getLogger(__name__)

_model = None
_tokenizer = None
_model_name_used: Optional[str] = None


def _get_quantization_config() -> BitsAndBytesConfig:
    """4-bit NF4 quantisation config (QLoRA-compatible)."""
    return BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )


def _try_load_model(name: str, gpu: bool):
    """Attempt to load a model. Returns (model, tokenizer) or raises."""
    tokenizer = AutoTokenizer.from_pretrained(name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    if gpu and torch.cuda.is_available():
        bnb_config = _get_quantization_config()
        model = AutoModelForCausalLM.from_pretrained(
            name,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
            torch_dtype=torch.bfloat16,
        )
        logger.info("Model %s loaded on GPU with 4-bit quantisation", name)
    else:
        model = AutoModelForCausalLM.from_pretrained(
            name,
            device_map="cpu",
            trust_remote_code=True,
            torch_dtype=torch.float32,
        )
        logger.info("Model %s loaded on CPU (fp32)", name)

    return model, tokenizer


def load_model(model_name: Optional[str] = None, use_gpu: Optional[bool] = None):
    """Load the LLM and tokenizer.

    Tries the primary model first (Mistral-7B with quantisation on GPU).
    If that fails, falls back to a small CPU-friendly model (Qwen2-0.5B).

    Parameters
    ----------
    model_name : str, optional
        HuggingFace model ID. Defaults to ``settings.MODEL_NAME``.
    use_gpu : bool, optional
        Whether to place the model on GPU. Defaults to ``settings.USE_GPU``.

    Returns
    -------
    tuple[model, tokenizer]
        The loaded model and its tokenizer.
    """
    global _model, _tokenizer, _model_name_used

    if _model is not None and _tokenizer is not None:
        logger.info("Using cached model: %s", _model_name_used)
        return _model, _tokenizer

    primary = model_name or settings.MODEL_NAME
    gpu = use_gpu if use_gpu is not None else settings.USE_GPU

    # Try primary model first
    logger.info("Attempting to load primary model: %s (GPU=%s)", primary, gpu)
    try:
        _model, _tokenizer = _try_load_model(primary, gpu)
        _model_name_used = primary
        return _model, _tokenizer
    except Exception as e:
        logger.warning("Primary model %s failed: %s", primary, e)

    # Fall back to small CPU-friendly model
    fallback = settings.FALLBACK_MODEL
    logger.info("Falling back to CPU model: %s", fallback)
    try:
        _model, _tokenizer = _try_load_model(fallback, gpu=False)
        _model_name_used = fallback
        return _model, _tokenizer
    except Exception as e:
        logger.error("Fallback model %s also failed: %s", fallback, e)
        raise RuntimeError(
            f"Could not load any LLM. Primary ({primary}) and fallback ({fallback}) both failed."
        ) from e


def _check_ollama_available() -> bool:
    """Ping the Ollama server to confirm the configured model is present."""
    import httpx

    try:
        resp = httpx.get(f"{settings.OLLAMA_HOST}/api/tags", timeout=5.0)
        resp.raise_for_status()
        names = {m["name"] for m in resp.json().get("models", [])}
        return settings.OLLAMA_MODEL in names
    except Exception as e:
        logger.warning("Ollama health check failed: %s", e)
        return False


def get_model():
    """Return the loaded model, loading it if necessary.

    When ``settings.USE_OLLAMA`` is set, no HuggingFace model is loaded —
    generation is delegated to the Ollama server in inference.py. This
    returns a sentinel string so callers checking ``model is not None``
    (e.g. the health endpoint) still report correctly.
    """
    global _model, _model_name_used
    if settings.USE_OLLAMA:
        if _check_ollama_available():
            _model_name_used = f"ollama:{settings.OLLAMA_MODEL}"
            return _model_name_used
        return None
    if _model is None:
        load_model()
    return _model


def get_tokenizer():
    """Return the loaded tokenizer, loading it if necessary."""
    global _tokenizer
    if settings.USE_OLLAMA:
        return None
    if _tokenizer is None:
        load_model()
    return _tokenizer


def get_model_name() -> Optional[str]:
    """Return the name of the currently loaded model."""
    return _model_name_used


def unload_model():
    """Free model from memory."""
    global _model, _tokenizer, _model_name_used
    if _model is not None:
        del _model
        _model = None
    if _tokenizer is not None:
        del _tokenizer
        _tokenizer = None
    _model_name_used = None
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    logger.info("Model unloaded from memory")
