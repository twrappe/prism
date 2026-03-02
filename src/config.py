"""Configuration module for the LLM RAG QA Agent"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    model_config = ConfigDict(env_file=".env", case_sensitive=False)
    
    # OpenAI Configuration
    openai_api_key: str = Field(default="", validation_alias="OPENAI_API_KEY")
    llm_model: str = Field(default="gpt-4-turbo", validation_alias="LLM_MODEL")
    temperature: float = Field(default=0.7, validation_alias="TEMPERATURE")
    max_tokens: int = Field(default=2000, validation_alias="MAX_TOKENS")
    
    # ChromaDB Configuration
    chroma_db_path: str = Field(default="./chroma_db", validation_alias="CHROMA_DB_PATH")
    chroma_collection_name: str = Field(default="ci_cd_docs", validation_alias="CHROMA_COLLECTION_NAME")
    
    # RAG Configuration
    chunk_size: int = Field(default=1000, validation_alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, validation_alias="CHUNK_OVERLAP")
    top_k_retrieval: int = Field(default=3, validation_alias="TOP_K_RETRIEVAL")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", validation_alias="API_HOST")
    api_port: int = Field(default=8000, validation_alias="API_PORT")
    
    # Logging
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    
    # Paths
    logs_dir: str = Field(default="./data/logs")
    docs_dir: str = Field(default="./data/documentation")


def get_settings() -> Settings:
    """Get application settings"""
    return Settings()


# Global settings instance
settings = get_settings()
