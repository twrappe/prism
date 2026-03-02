#!/usr/bin/env python3
"""
Example script for ingesting documentation into RAG system.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag import RAGPipeline, ChromaDBManager
from src.utils.logger import get_logger

logger = get_logger(__name__)


def ingest_documentation():
    """Ingest documentation from files"""
    logger.info("Starting documentation ingestion...")
    
    # Initialize manager
    manager = ChromaDBManager()
    
    # Get documentation files
    docs_dir = Path(__file__).parent.parent / "data" / "documentation"
    doc_files = list(docs_dir.glob("*.md"))
    
    if not doc_files:
        logger.warning(f"No documentation files found in {docs_dir}")
        return
    
    logger.info(f"Found {len(doc_files)} documentation files")
    
    # Process and ingest each file
    for doc_file in doc_files:
        logger.info(f"Ingesting {doc_file.name}...")
        
        with open(doc_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into chunks and add to database
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_text(content)
        
        manager.add_documents(
            documents=chunks,
            metadatas=[{"source": doc_file.name} for _ in chunks]
        )
        
        logger.info(f"  → Added {len(chunks)} chunks from {doc_file.name}")
    
    # Display collection stats
    stats = manager.get_collection_stats()
    logger.info(f"\nCollection Stats:")
    logger.info(f"  Total documents: {stats['document_count']}")
    
    logger.info("Documentation ingestion completed!")


if __name__ == "__main__":
    ingest_documentation()
