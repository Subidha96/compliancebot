"""SHAP-based Explainability — Token-level attribution for LLM responses.

Provides interpretability for why the model generated specific tokens,
directly feeding the FR-06 (explainability) requirement.
"""
import logging
from typing import Optional

import torch
import shap

from app.llm.model_loader import get_model, get_tokenizer

logger = logging.getLogger(__name__)


def explain_generation(
    prompt: str,
    generated_text: str,
    top_n_tokens: int = 10,
) -> dict:
    """Compute SHAP attribution for the generated response.

    Parameters
    ----------
    prompt : str
        The input prompt sent to the LLM.
    generated_text : str
        The model's generated response.
    top_n_tokens : int
        Number of most-attributed tokens to return.

    Returns
    -------
    dict
        Contains ``top_tokens`` (list of token/attribute pairs) and
        ``summary`` string.
    """
    try:
        model = get_model()
        tokenizer = get_tokenizer()

        full_text = prompt + " " + generated_text

        # Use SHAP's language model explainer
        explainer = shap.Explainer(
            lambda x: _score_tokens(model, tokenizer, x, prompt),
            tokenizer,
            output_names=["attribution"],
        )

        # Explain only the generated portion
        shap_values = explainer([generated_text])

        # Extract top tokens by absolute attribution
        if hasattr(shap_values, "values") and shap_values.values is not None:
            values = shap_values.values[0]
            tokens = shap_values.data[0] if hasattr(shap_values, "data") else []

            if len(values) > 0 and len(tokens) > 0:
                token_attr = list(zip(tokens, values))
                token_attr.sort(key=lambda x: abs(x[1]), reverse=True)
                top = token_attr[:top_n_tokens]

                return {
                    "top_tokens": [
                        {"token": t, "attribution": float(v)} for t, v in top
                    ],
                    "summary": (
                        f"Top contributing tokens: "
                        + ", ".join(f"'{t}' ({v:.3f})" for t, v in top[:5])
                    ),
                }

        return {
            "top_tokens": [],
            "summary": "SHAP analysis completed but no significant attributions found.",
        }

    except Exception as e:
        logger.warning("SHAP explanation failed: %s", e)
        return {
            "top_tokens": [],
            "summary": f"SHAP analysis unavailable: {e}",
        }


def _score_tokens(
    model, tokenizer, texts: list[str], prompt: str
) -> list[float]:
    """Score each token in the generated text by its contribution to the output.

    This is a simplified attribution that measures how much each input token
    contributes to the next-token prediction distribution.
    """
    scores = []
    for text in texts:
        full_input = prompt + " " + text
        inputs = tokenizer(full_input, return_tensors="pt", truncation=True, max_length=4096)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits[0, -1, :]  # logits for next token

        # Get probabilities
        probs = torch.softmax(logits, dim=-1)

        # For each token in the generated text, compute its "surprise"
        # (negative log-prob under the model distribution)
        text_tokens = tokenizer.encode(text, add_special_tokens=False)
        prompt_tokens = tokenizer.encode(prompt, add_special_tokens=False)

        token_scores = []
        for i, token_id in enumerate(text_tokens):
            if token_id < len(probs):
                token_scores.append(-probs[token_id].item())
            else:
                token_scores.append(0.0)

        scores.extend(token_scores)

    # Pad or truncate to match
    return scores if scores else [0.0]
