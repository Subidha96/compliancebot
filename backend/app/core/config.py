"""Application configuration and settings."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "ComplianceBot+"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # LLM Configuration
    MODEL_NAME: str = "mistralai/Mistral-7B-Instruct-v0.3"
    FALLBACK_MODEL: str = "Qwen/Qwen2-0.5B-Instruct"
    USE_GPU: bool = True
    MAX_NEW_TOKENS: int = 1024
    TEMPERATURE: float = 0.7

    # RAG Configuration — multilingual models
    EMBEDDING_MODEL: str = "intfloat/multilingual-e5-base"
    RERANKER_MODEL: str = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    COLLECTION_NAME: str = "nepal_grc_corpus"

    # Translation
    TRANSLATION_MODEL: str = "facebook/nllb-200-distilled-600M"
    TRANSLATE_OUTPUT: bool = True  # auto-translate NE queries to NE response

    # Session Configuration
    SESSION_TIMEOUT_MINUTES: int = 30
    SESSION_STORE_TYPE: str = "memory"  # "memory" or "sqlite"

    # Rate Limiting
    CHAT_RATE_LIMIT: int = 30  # requests per minute
    GAP_ASSESSMENT_RATE_LIMIT: int = 10  # assessments per hour

    # Bias Audit
    BIAS_THRESHOLD: float = 0.3

    # Explainability
    SHAP_ENABLED: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
