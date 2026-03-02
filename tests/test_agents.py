"""
Test suite for CLI/CD QA Agent
"""

import pytest
from pathlib import Path
from src.agents import CIDDQAAgent, RCAgent, RemediationAgent
from src.rag import RAGPipeline, ChromaDBManager
from src.utils.parser import parse_ci_cd_logs, LogLevel


class TestLogParser:
    """Test log parsing functionality"""
    
    def test_parse_structured_logs(self):
        """Test parsing structured logs"""
        log_content = """
[2024-01-15 10:23:45] [ERROR] [database] Connection failed
[2024-01-15 10:23:46] [WARNING] [api] Retry attempt 1
"""
        entries = parse_ci_cd_logs(log_content)
        assert len(entries) > 0
        assert entries[0].level == LogLevel.ERROR
    
    def test_parse_empty_logs(self):
        """Test parsing empty logs"""
        entries = parse_ci_cd_logs("")
        assert isinstance(entries, list)


class TestRAGPipeline:
    """Test RAG pipeline"""
    
    @pytest.fixture
    def rag(self):
        """Create RAG pipeline instance"""
        return RAGPipeline()
    
    def test_initialization(self, rag):
        """Test RAG pipeline initialization"""
        assert rag.db_manager is not None
        assert rag.doc_processor is not None
    
    def test_document_ingestion(self, rag, tmp_path):
        """Test document ingestion"""
        # Create test document
        doc_file = tmp_path / "test.md"
        doc_file.write_text("This is a test document about connection pools")
        
        # Ingest
        rag.ingest_documentation([str(doc_file)])
        
        # Verify
        stats = rag.get_stats()
        assert stats['document_count'] > 0
    
    def test_retrieval(self, rag, tmp_path):
        """Test document retrieval"""
        # Create and ingest test document
        doc_file = tmp_path / "connections.md"
        doc_file.write_text("Connection pool management best practices")
        rag.ingest_documentation([str(doc_file)])
        
        # Retrieve
        results = rag.retrieve_relevant_docs("how to manage connections")
        assert isinstance(results, list)


class TestRCAAgent:
    """Test RCA Agent"""
    
    @pytest.fixture
    def agent(self):
        """Create RCA agent"""
        return RCAgent()
    
    def test_initialization(self, agent):
        """Test agent initialization"""
        # Agent can be initialized with or without API key
        assert agent is not None
        assert agent.rag_pipeline is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
