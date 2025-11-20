"""
Configuration settings for the Professor Brusseau Digital Twin
"""
import os
from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # API Keys
    openai_api_key: str = ""

    # Model Configuration
    primary_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"
    temperature: float = 0.7
    max_tokens: int = 4096

    # Vector Store Configuration
    vector_store_type: Literal["chromadb", "faiss"] = "chromadb"
    vector_store_path: str = "./data/embeddings/chroma_db"
    collection_name_ai_ethics: str = "brusseau_ai_ethics"
    collection_name_business_ethics: str = "brusseau_business_ethics"

    # Retrieval Configuration
    top_k_results: int = 5
    similarity_threshold: float = 0.7

    # Application Settings
    debug: bool = False
    log_level: str = "INFO"

    # Paths
    @property
    def project_root(self) -> Path:
        return Path(__file__).parent.parent

    @property
    def data_dir(self) -> Path:
        return self.project_root / "data"

    @property
    def raw_data_dir(self) -> Path:
        return self.data_dir / "raw"

    @property
    def processed_data_dir(self) -> Path:
        return self.data_dir / "processed"


# Global settings instance
settings = Settings()
