"""
Application configuration loaded from environment variables.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Telegram
    telegram_bot_token: str
    
    # OpenAI
    openai_api_key: str
    
    # Database
    database_url: str
    database_url_sync: str
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # App Config
    debug: bool = False
    conversation_history_limit: int = 5
    search_cache_ttl_seconds: int = 3600
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4o-mini"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

