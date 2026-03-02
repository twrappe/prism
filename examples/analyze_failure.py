#!/usr/bin/env python3
"""
Main example script demonstrating the CI/CD Failure Analysis Agent.
"""

import os
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents import CIDDQAAgent
from src.rag import RAGPipeline
from src.utils.formatter import format_rca_analysis, format_remediation_suggestions, format_as_json
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Main example function"""
    logger.info("=" * 70)
    logger.info("CI/CD Failure Analysis Agent - Example Run")
    logger.info("=" * 70)
    
    # Initialize RAG pipeline
    logger.info("\n1. Initializing RAG Pipeline...")
    rag_pipeline = RAGPipeline()
    
    # Ingest documentation
    docs_dir = Path(__file__).parent.parent / "data" / "documentation"
    doc_files = list(docs_dir.glob("*.md"))
    
    if doc_files:
        logger.info(f"\n2. Ingesting documentation from {docs_dir}")
        rag_pipeline.ingest_documentation([str(f) for f in doc_files])
        
        stats = rag_pipeline.get_stats()
        logger.info(f"   Documents in RAG: {stats['document_count']}")
    else:
        logger.warning(f"   No documentation files found in {docs_dir}")
    
    # Load example failure log
    log_file = Path(__file__).parent.parent / "data" / "logs" / "example_failure.log"
    if log_file.exists():
        logger.info(f"\n3. Loading failure log from {log_file}")
        with open(log_file, 'r') as f:
            log_content = f.read()
        logger.info(f"   Log size: {len(log_content)} bytes")
    else:
        logger.warning(f"   Example log file not found at {log_file}")
        log_content = """
[2024-01-15 10:23:45] [ERROR] [pytest] Test suite execution failed
[2024-01-15 10:23:45] [ERROR] [database] Connection pool exhausted after 30 seconds
TimeoutError: Connection pool exhausted - too many concurrent requests
"""
    
    # Initialize agent
    logger.info("\n4. Initializing CI/CD QA Agent...")
    agent = CIDDQAAgent(rag_pipeline)
    
    # Analyze failure
    logger.info("\n5. Analyzing CI/CD failure...")
    result = agent.analyze_and_remediate(log_content)
    
    # Display results
    logger.info("\n" + "=" * 70)
    logger.info("ANALYSIS RESULTS")
    logger.info("=" * 70)
    
    # RCA Analysis
    logger.info("\n--- ROOT CAUSE ANALYSIS ---")
    rca = result.get("rca", {})
    logger.info(format_rca_analysis(rca))
    
    # Remediation Suggestions
    logger.info("\n--- REMEDIATION SUGGESTIONS ---")
    suggestions = result.get("remediation_suggestions", [])
    logger.info(format_remediation_suggestions(suggestions))
    
    # Full JSON output
    logger.info("\n--- FULL JSON OUTPUT ---")
    logger.info(format_as_json(result))
    
    # Save results
    output_file = Path(__file__).parent.parent / "example_output.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    logger.info(f"\nResults saved to: {output_file}")
    
    logger.info("\n" + "=" * 70)
    logger.info("Analysis Complete!")
    logger.info("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Error during analysis: {e}", exc_info=True)
        sys.exit(1)
