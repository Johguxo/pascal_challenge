"""
AI Providers module - Abstract interfaces and implementations for different AI services.
"""
from src.ai.providers.base import BaseLLMProvider, BaseEmbeddingProvider
from src.ai.providers.factory import get_llm_provider, get_embedding_provider
from src.ai.providers.openai_provider import OpenAILLMProvider, OpenAIEmbeddingProvider
from src.ai.providers.gemini_provider import GeminiLLMProvider, GeminiEmbeddingProvider

__all__ = [
    # Base classes
    "BaseLLMProvider",
    "BaseEmbeddingProvider",
    # Factory
    "get_llm_provider",
    "get_embedding_provider",
    # OpenAI
    "OpenAILLMProvider",
    "OpenAIEmbeddingProvider",
    # Gemini
    "GeminiLLMProvider",
    "GeminiEmbeddingProvider",
]

