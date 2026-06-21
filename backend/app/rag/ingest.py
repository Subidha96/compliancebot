"""RAG Ingestion Pipeline — Clause-boundary chunking, multilingual embeddings, ChromaDB storage.

Loads policy documents from data/raw/, chunks them by legal clause/section
boundaries, embeds using multilingual-e5-base, and persists to ChromaDB.
"""
import re
import os
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import chromadb
from sentence_transformers import SentenceTransformer

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """A single chunked piece of a policy document."""
    text: str
    source: str
    section: str
    language: str
    chunk_id: str = ""


# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------

def _detect_language(text: str) -> str:
    """Detect whether text is primarily Nepali (Devanagari) or English."""
    devanagari_chars = sum(1 for c in text if "\u0900" <= c <= "\u097F")
    return "ne" if devanagari_chars > len(text) * 0.2 else "en"


# ---------------------------------------------------------------------------
# Document loading
# ---------------------------------------------------------------------------

def load_text_files(raw_dir: str) -> list[tuple[str, str]]:
    """Load all .txt files from *raw_dir* and return (stem, text) pairs."""
    docs: list[tuple[str, str]] = []
    for path in Path(raw_dir).glob("*.txt"):
        text = path.read_text(encoding="utf-8")
        docs.append((path.stem, text))
        logger.info("Loaded document: %s (%d chars)", path.name, len(text))
    return docs


# ---------------------------------------------------------------------------
# Clause-boundary chunking
# ---------------------------------------------------------------------------

_SECTION_PATTERN = re.compile(
    r"(?=(?:Section|Clause|Article|Bylaw|Article)\s+\d+[\.\d]*|धारा\s*[\d०-९]+)",
    re.IGNORECASE,
)

_LABEL_PATTERN = re.compile(
    r"((?:Section|Clause|Article|Bylaw)\s+[\d\.]+|धारा\s*[\d०-९]+)",
    re.IGNORECASE,
)

# For splitting long chunks that exceed max_chunk_chars
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?।])\s+")


def _split_long_text(text: str, max_chars: int, overlap: int) -> list[str]:
    """Sliding-window split with overlap, breaking on sentence boundaries."""
    sentences = _SENTENCE_SPLIT.split(text)
    chunks: list[str] = []
    current = ""
    for sent in sentences:
        if len(current) + len(sent) > max_chars and current:
            chunks.append(current.strip())
            current = current[-overlap:] + " " + sent
        else:
            current += " " + sent
    if current.strip():
        chunks.append(current.strip())
    return chunks


def chunk_by_clause(
    text: str,
    source_name: str,
    max_chunk_chars: int = 1200,
    overlap: int = 150,
) -> list[Chunk]:
    """Split legal/policy text on clause/section markers.

    Falls back to paragraph splitting if no markers found, then
    hard-splits anything still too long.
    """
    raw_sections = _SECTION_PATTERN.split(text)
    raw_sections = [s.strip() for s in raw_sections if s.strip()]

    if len(raw_sections) <= 1:
        # No clause markers — fall back to paragraph splitting
        raw_sections = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks: list[Chunk] = []
    for i, section_text in enumerate(raw_sections):
        label_match = _LABEL_PATTERN.match(section_text)
        section_label = label_match.group(1) if label_match else f"part-{i + 1}"

        if len(section_text) > max_chunk_chars:
            sub_chunks = _split_long_text(section_text, max_chunk_chars, overlap)
            for j, sub in enumerate(sub_chunks):
                chunk_id = f"{source_name}_{section_label}_p{j}".replace(" ", "_")
                chunks.append(
                    Chunk(
                        text=sub,
                        source=source_name,
                        section=f"{section_label} (part {j + 1})",
                        language=_detect_language(sub),
                        chunk_id=chunk_id,
                    )
                )
        else:
            chunk_id = f"{source_name}_{section_label}".replace(" ", "_")
            chunks.append(
                Chunk(
                    text=section_text,
                    source=source_name,
                    section=section_label,
                    language=_detect_language(section_text),
                    chunk_id=chunk_id,
                )
            )
    return chunks


# ---------------------------------------------------------------------------
# Embedding
# ---------------------------------------------------------------------------

_embedder: Optional[SentenceTransformer] = None


def get_embedder() -> SentenceTransformer:
    """Lazy-load the multilingual embedding model (singleton)."""
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.info("Loaded embedding model: %s", settings.EMBEDDING_MODEL)
    return _embedder


def embed_chunks(chunks: list[Chunk]) -> list[list[float]]:
    """Embed a list of Chunks using multilingual-e5-base.

    E5 models require a ``passage:`` prefix for documents being indexed.
    """
    model = get_embedder()
    texts = [f"passage: {c.text}" for c in chunks]
    embeddings = model.encode(
        texts, normalize_embeddings=True, show_progress_bar=True
    )
    return embeddings.tolist()


# ---------------------------------------------------------------------------
# ChromaDB storage
# ---------------------------------------------------------------------------

_client: Optional[chromadb.PersistentClient] = None
_collection: Optional[chromadb.Collection] = None


def get_chroma_client() -> chromadb.PersistentClient:
    """Return a persistent ChromaDB client (singleton)."""
    global _client
    if _client is None:
        persist_dir = settings.CHROMA_PERSIST_DIR
        os.makedirs(persist_dir, exist_ok=True)
        _client = chromadb.PersistentClient(path=persist_dir)
    return _client


def get_collection() -> chromadb.Collection:
    """Return (or create) the main corpus collection (singleton)."""
    global _collection
    if _collection is None:
        client = get_chroma_client()
        _collection = client.get_or_create_collection(
            name=settings.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def build_vector_store(chunks: list[Chunk]) -> chromadb.Collection:
    """Embed chunks and persist them in ChromaDB.

    If the collection already has data, it is cleared first (idempotent re-ingest).
    """
    collection = get_collection()

    # Idempotent: clear existing data before re-ingesting
    existing = collection.get()
    if existing["ids"]:
        collection.delete(ids=existing["ids"])
        logger.info("Cleared %d existing chunks from collection", len(existing["ids"]))

    embeddings = embed_chunks(chunks)

    collection.add(
        ids=[c.chunk_id for c in chunks],
        embeddings=embeddings,
        documents=[c.text for c in chunks],
        metadatas=[
            {"source": c.source, "section": c.section, "language": c.language}
            for c in chunks
        ],
    )
    logger.info("Stored %d chunks in ChromaDB at %s", len(chunks), settings.CHROMA_PERSIST_DIR)
    return collection


# ---------------------------------------------------------------------------
# Full pipeline entry point
# ---------------------------------------------------------------------------

def ingest_corpus(raw_dir: str = "data/raw") -> int:
    """Run the full ingestion pipeline. Returns the number of chunks stored."""
    docs = load_text_files(raw_dir)
    all_chunks: list[Chunk] = []
    for source_name, text in docs:
        all_chunks.extend(chunk_by_clause(text, source_name))
    logger.info("Total chunks created: %d from %d documents", len(all_chunks), len(docs))
    build_vector_store(all_chunks)
    return len(all_chunks)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    count = ingest_corpus()
    print(f"Ingestion complete: {count} chunks stored.")
