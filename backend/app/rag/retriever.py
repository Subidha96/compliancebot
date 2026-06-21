"""Hybrid Retrieval Pipeline — Semantic + Keyword search, RRF fusion, Cross-Encoder reranking.

Provides the full retrieval chain for ComplianceBot+:
  query → semantic_search + keyword_search → reciprocal_rank_fusion → rerank → top_k results
"""
import re
import logging
from typing import Optional

import chromadb
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder, SentenceTransformer

from app.core.config import settings
from app.rag.ingest import get_collection, get_embedder

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy-loaded singletons
# ---------------------------------------------------------------------------

_reranker: Optional[CrossEncoder] = None
_bm25: Optional[BM25Okapi] = None
_corpus_ids: list[str] = []
_corpus_texts: list[str] = []
_corpus_metadatas: list[dict] = []


def get_reranker() -> CrossEncoder:
    """Lazy-load the multilingual cross-encoder reranker."""
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder(settings.RERANKER_MODEL)
        logger.info("Loaded reranker: %s", settings.RERANKER_MODEL)
    return _reranker


def _ensure_bm25_index() -> None:
    """Build BM25 keyword index from ChromaDB corpus (once per process)."""
    global _bm25, _corpus_ids, _corpus_texts, _corpus_metadatas
    if _bm25 is not None:
        return

    collection = get_collection()
    data = collection.get(include=["documents", "metadatas"])
    _corpus_ids = data["ids"]
    _corpus_texts = data["documents"]
    _corpus_metadatas = data["metadatas"]

    tokenized = [re.findall(r"\w+", doc.lower()) for doc in _corpus_texts]
    _bm25 = BM25Okapi(tokenized)
    logger.info("Built BM25 index over %d documents", len(_corpus_texts))


# ---------------------------------------------------------------------------
# Semantic search
# ---------------------------------------------------------------------------

def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """Dense vector search using multilingual embeddings + cosine similarity."""
    embedder = get_embedder()
    query_embedding = embedder.encode(
        [f"query: {query}"], normalize_embeddings=True
    )[0].tolist()

    collection = get_collection()
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)

    items: list[dict] = []
    for i in range(len(results["ids"][0])):
        # ChromaDB cosine distance → similarity score
        distance = results["distances"][0][i]
        score = 1 - distance
        items.append({
            "id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "score": score,
        })
    return items


# ---------------------------------------------------------------------------
# Keyword search (BM25)
# ---------------------------------------------------------------------------

def keyword_search(query: str, top_k: int = 10) -> list[dict]:
    """Sparse keyword search using BM25Okapi."""
    _ensure_bm25_index()

    tokenized_query = re.findall(r"\w+", query.lower())
    scores = _bm25.get_scores(tokenized_query)

    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

    items: list[dict] = []
    for idx in top_indices:
        if scores[idx] > 0:
            items.append({
                "id": _corpus_ids[idx],
                "text": _corpus_texts[idx],
                "metadata": _corpus_metadatas[idx],
                "score": float(scores[idx]),
            })
    return items


# ---------------------------------------------------------------------------
# Reciprocal Rank Fusion
# ---------------------------------------------------------------------------

def reciprocal_rank_fusion(
    semantic_results: list[dict],
    keyword_results: list[dict],
    k: int = 60,
) -> list[dict]:
    """Merge two ranked lists using Reciprocal Rank Fusion.

    RRF score = sum of 1/(k + rank) across both lists.
    This normalises wildly different score scales (cosine vs BM25 counts).
    """
    scores: dict[str, float] = {}
    items: dict[str, dict] = {}

    for rank, item in enumerate(semantic_results):
        doc_id = item["id"]
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
        items[doc_id] = item

    for rank, item in enumerate(keyword_results):
        doc_id = item["id"]
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
        items[doc_id] = item

    fused = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [items[doc_id] for doc_id, _ in fused]


# ---------------------------------------------------------------------------
# Cross-encoder reranking
# ---------------------------------------------------------------------------

def rerank(query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
    """Re-rank candidate chunks using a multilingual cross-encoder.

    Cross-encoders are slow but far more precise than bi-encoder similarity.
    We only rerank the top candidates (not the whole corpus).
    """
    if not candidates:
        return []

    cross_encoder = get_reranker()
    pairs = [[query, c["text"]] for c in candidates]
    rerank_scores = cross_encoder.predict(pairs)

    for candidate, score in zip(candidates, rerank_scores):
        candidate["rerank_score"] = float(score)

    reranked = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)
    return reranked[:top_k]


# ---------------------------------------------------------------------------
# Full retrieval pipeline
# ---------------------------------------------------------------------------

def retrieve(query: str, top_k: int = 5) -> list[dict]:
    """End-to-end hybrid retrieval: semantic + keyword → fuse → rerank → top_k.

    Returns a list of dicts with keys:
        id, text, metadata, score, rerank_score, confidence
    """
    semantic_results = semantic_search(query, top_k=10)
    keyword_results = keyword_search(query, top_k=10)

    fused = reciprocal_rank_fusion(semantic_results, keyword_results)

    # Rerank only top-15 candidates (rerankers are slow)
    final = rerank(query, fused[:15], top_k=top_k)

    # Normalise rerank_score to a 0–1 confidence for the UI
    for r in final:
        # Cross-encoder scores vary by model; typical range is roughly -10 to +10
        r["confidence"] = max(0.0, min(1.0, (r["rerank_score"] + 10) / 20))

    return final
