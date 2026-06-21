"""Tests for the RAG retrieval pipeline."""
import pytest
import sys
import os

# Ensure backend is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestChunking:
    """Tests for clause-boundary chunking."""

    def test_chunk_by_clause_basic(self):
        from app.rag.ingest import chunk_by_clause

        text = """Section 1. Introduction
This section covers the basics.

Section 2. Requirements
All organisations must comply.

Section 3. Penalties
Non-compliance carries fines."""
        chunks = chunk_by_clause(text, "test_doc")
        assert len(chunks) >= 3
        assert all(c.source == "test_doc" for c in chunks)

    def test_chunk_by_clause_with_nepali(self):
        from app.rag.ingest import chunk_by_clause

        text = """धारा १. परिचय
यो धाराले आधारभूत कुराहरू समेट्छ।

धारा २. आवश्यकताहरू
सबै संस्थाहरूले पालना गर्नुपर्छ।"""
        chunks = chunk_by_clause(text, "nepal_policy")
        assert len(chunks) >= 2

    def test_chunk_long_section_splits(self):
        from app.rag.ingest import chunk_by_clause

        # Create a section longer than 1200 chars
        long_text = "Section 4. " + "Word " * 500
        chunks = chunk_by_clause(long_text, "long_doc")
        assert len(chunks) > 1  # Should be split

    def test_language_detection_english(self):
        from app.rag.ingest import _detect_language
        assert _detect_language("This is English text about compliance.") == "en"

    def test_language_detection_nepali(self):
        from app.rag.ingest import _detect_language
        assert _detect_language("यो नेपाली पाठ हो।") == "ne"

    def test_load_text_files(self):
        import os
        from app.rag.ingest import load_text_files
        raw_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
        docs = load_text_files(raw_dir)
        assert len(docs) == 6
        assert all(isinstance(d, tuple) and len(d) == 2 for d in docs)


class TestRetrieval:
    """Tests for hybrid retrieval (requires ChromaDB with data)."""

    def test_semantic_search_returns_results(self):
        from app.rag.retriever import semantic_search
        results = semantic_search("data breach reporting", top_k=3)
        assert isinstance(results, list)
        assert all("id" in r and "text" in r and "metadata" in r for r in results)

    def test_keyword_search_returns_results(self):
        from app.rag.retriever import keyword_search
        results = keyword_search("ISO 27001 access control", top_k=3)
        assert isinstance(results, list)

    def test_reciprocal_rank_fusion_merges(self):
        from app.rag.retriever import reciprocal_rank_fusion
        semantic = [{"id": "a", "text": "x", "metadata": {}, "score": 0.9}]
        keyword = [{"id": "b", "text": "y", "metadata": {}, "score": 5.0}]
        fused = reciprocal_rank_fusion(semantic, keyword)
        assert len(fused) == 2
        assert fused[0]["id"] in ("a", "b")

    def test_retrieve_returns_top_k(self):
        from app.rag.retriever import retrieve
        results = retrieve("incident response plan", top_k=3)
        assert len(results) <= 3
        for r in results:
            assert "confidence" in r
            assert 0.0 <= r["confidence"] <= 1.0

    def test_nepali_query_returns_results(self):
        from app.rag.retriever import retrieve
        results = retrieve("साइबर सुरक्षा नीति", top_k=3)
        assert isinstance(results, list)

    def test_irrelevant_query_low_confidence(self):
        from app.rag.retriever import retrieve
        results = retrieve("how to bake a chocolate cake recipe", top_k=3)
        if results:
            assert all(r["confidence"] < 0.8 for r in results)


class TestPromptBuilder:
    """Tests for prompt assembly."""

    def test_build_rag_prompt_contains_context(self):
        from app.rag.prompt_builder import build_rag_prompt
        chunks = [
            {"text": "Section 47: Unauthorized access penalties.", "metadata": {"source": "ETA 2063", "section": "Section 47"}}
        ]
        prompt = build_rag_prompt("What are the penalties?", chunks)
        assert "ETA 2063" in prompt
        assert "Section 47" in prompt
        assert "What are the penalties?" in prompt
        assert "ANSWER (with citations):" in prompt

    def test_build_rag_prompt_rules_present(self):
        from app.rag.prompt_builder import build_rag_prompt
        prompt = build_rag_prompt("test", [])
        assert "RULES:" in prompt
        assert "cite" in prompt.lower()
