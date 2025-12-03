"""
Application configuration loaded from environment variables.
"""
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Telegram
    telegram_bot_token: str = ""
    
    # AI Providers
    # OpenAI
    openai_api_key: Optional[str] = None
    # Gemini
    gemini_api_key: Optional[str] = None
    
    # Provider Selection (openai or gemini)
    llm_provider: str = "gemini"  # Default to Gemini
    embedding_provider: str = "gemini"  # Default to Gemini
    
    # Model names (provider-specific)
    llm_model: str = "gemini-1.5-flash"  # or "gpt-4o-mini" for OpenAI
    embedding_model: str = "models/text-embedding-004"  # or "text-embedding-3-small" for OpenAI
    
    # Database
    database_url: str
    database_url_sync: str
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # App Config
    debug: bool = False
    conversation_history_limit: int = 5
    search_cache_ttl_seconds: int = 3600
    
    # Embedding dimensions (768 for Gemini, 1536 for OpenAI)
    embedding_dimensions: int = 768
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

