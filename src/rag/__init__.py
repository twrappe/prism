"""RAG (Retrieval-Augmented Generation) module for CI/CD documentation"""
import os
import chromadb
from typing import List, Dict, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ChromaDBManager:
    """Manager for ChromaDB operations"""
    
    def __init__(self, persist_directory: str = None, collection_name: str = None):
        """
        Initialize ChromaDB manager.
        
        Args:
            persist_directory: Path to persist ChromaDB data
            collection_name: Name of the collection to work with
        """
        self.persist_directory = persist_directory or settings.chroma_db_path
        self.collection_name = collection_name or settings.chroma_collection_name
        
        # Ensure directory exists
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"ChromaDB initialized with collection: {self.collection_name}")
    
    def add_documents(self, documents: List[str], metadatas: List[Dict] = None, 
                     ids: List[str] = None) -> None:
        """
        Add documents to ChromaDB collection.
        
        Args:
            documents: List of document texts
            metadatas: Optional list of metadata dictionaries
            ids: Optional list of document IDs
        """
        if not documents:
            logger.warning("No documents provided to add")
            return
        
        # Generate IDs if not provided
        if ids is None:
            ids = [f"doc_{i}_{hash(doc)}" for i, doc in enumerate(documents)]
        
        # Set default metadata
        if metadatas is None:
            metadatas = [{"source": "ci_cd_docs"} for _ in documents]
        
        try:
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            logger.info(f"Added {len(documents)} documents to ChromaDB")
        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {e}")
            raise
    
    def query(self, query_text: str, n_results: int = None) -> Dict:
        """
        Query documents from ChromaDB.
        
        Args:
            query_text: Query text
            n_results: Number of results to return
            
        Returns:
            Dictionary with query results
        """
        n_results = n_results or settings.top_k_retrieval
        
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}")
            return {"documents": [[]], "distances": [[]], "metadatas": [[]]}
    
    def get_collection_stats(self) -> Dict:
        """Get collection statistics"""
        count = self.collection.count()
        return {"collection_name": self.collection_name, "document_count": count}
    
    def clear_collection(self) -> None:
        """Clear all documents from collection"""
        try:
            self.collection.delete(where={})
            logger.info(f"Cleared collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")


class DocumentProcessor:
    """Process and chunk documents for RAG"""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        Initialize document processor.
        
        Args:
            chunk_size: Size of each chunk
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def process_files(self, file_paths: List[str]) -> List[str]:
        """
        Process multiple files and return chunked documents.
        
        Args:
            file_paths: List of file paths
            
        Returns:
            List of chunked documents
        """
        all_chunks = []
        
        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                chunks = self.splitter.split_text(content)
                all_chunks.extend(chunks)
                logger.info(f"Processed {file_path}: {len(chunks)} chunks")
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
        
        return all_chunks
    
    def process_text(self, text: str) -> List[str]:
        """
        Process text and return chunks.
        
        Args:
            text: Text to process
            
        Returns:
            List of chunked text
        """
        return self.splitter.split_text(text)


class RAGPipeline:
    """Complete RAG pipeline for CI/CD documentation"""
    
    def __init__(self):
        """Initialize RAG pipeline"""
        self.db_manager = ChromaDBManager()
        self.doc_processor = DocumentProcessor()
        self.logger = get_logger(__name__)
    
    def ingest_documentation(self, doc_paths: List[str]) -> None:
        """
        Ingest documentation files into RAG system.
        
        Args:
            doc_paths: List of documentation file paths
        """
        self.logger.info(f"Ingesting {len(doc_paths)} documentation files")
        
        chunks = self.doc_processor.process_files(doc_paths)
        self.db_manager.add_documents(chunks)
        
        self.logger.info(f"Successfully ingested {len(chunks)} document chunks")
    
    def retrieve_relevant_docs(self, query: str, top_k: int = None) -> List[str]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Query text
            top_k: Number of top results to return
            
        Returns:
            List of relevant documents
        """
        results = self.db_manager.query(query, n_results=top_k)
        
        # Extract documents from results
        documents = results.get("documents", [[]])[0]
        
        return documents
    
    def get_stats(self) -> Dict:
        """Get RAG pipeline statistics"""
        return self.db_manager.get_collection_stats()
