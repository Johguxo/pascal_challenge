"""
Factory functions for creating AI providers based on configuration.
"""
from typing import Optional
from functools import lru_cache

from src.config import get_settings
from src.ai.providers.base import BaseLLMProvider, BaseEmbeddingProvider


@lru_cache()
def get_llm_provider(provider: Optional[str] = None) -> BaseLLMProvider:
    """
    Get LLM provider based on configuration.
    
    Args:
        provider: Optional provider name override ("openai" or "gemini")
                 If not provided, uses config setting
    
    Returns:
        LLM provider instance
    """
    settings = get_settings()
    provider_name = provider or settings.llm_provider
    
    if provider_name == "openai":
        from src.ai.providers.openai_provider import OpenAILLMProvider
        return OpenAILLMProvider()
    elif provider_name == "gemini":
        from src.ai.providers.gemini_provider import GeminiLLMProvider
        return GeminiLLMProvider()
    else:
        raise ValueError(f"Unknown LLM provider: {provider_name}")


@lru_cache()
def get_embedding_provider(provider: Optional[str] = None) -> BaseEmbeddingProvider:
    """
    Get Embedding provider based on configuration.
    
    Args:
        provider: Optional provider name override ("openai" or "gemini")
                 If not provided, uses config setting
    
    Returns:
        Embedding provider instance
    """
    settings = get_settings()
    provider_name = provider or settings.embedding_provider
    
    if provider_name == "openai":
        from src.ai.providers.openai_provider import OpenAIEmbeddingProvider
        return OpenAIEmbeddingProvider()
    elif provider_name == "gemini":
        from src.ai.providers.gemini_provider import GeminiEmbeddingProvider
        return GeminiEmbeddingProvider()
    else:
        raise ValueError(f"Unknown embedding provider: {provider_name}")


def clear_provider_cache():
    """Clear the provider cache (useful for testing or config changes)."""
    get_llm_provider.cache_clear()
    get_embedding_provider.cache_clear()

