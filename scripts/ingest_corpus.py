#!/usr/bin/env python3
"""CLI script to ingest the policy corpus into ChromaDB.

Usage:
    python scripts/ingest_corpus.py [--data-dir data/raw]
"""
import sys
import os
import argparse
import logging

# Ensure backend is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.rag.ingest import ingest_corpus


def main():
    parser = argparse.ArgumentParser(description="Ingest policy documents into ChromaDB")
    parser.add_argument("--data-dir", default="data/raw", help="Directory containing .txt policy documents")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    print(f"Ingesting corpus from: {args.data_dir}")
    count = ingest_corpus(raw_dir=args.data_dir)
    print(f"Done. {count} chunks stored in ChromaDB.")


if __name__ == "__main__":
    main()
