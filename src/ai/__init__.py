"""
AI module for embeddings, RAG, and conversational agents.
"""
from src.ai.embeddings import EmbeddingService, get_embedding_service
from src.ai.chat_service import ChatService
from src.ai.providers import (
    BaseLLMProvider,
    BaseEmbeddingProvider,
    get_llm_provider,
    get_embedding_provider,
)

__all__ = [
    # Services
    "EmbeddingService",
    "get_embedding_service",
    "ChatService",
    # Providers
    "BaseLLMProvider",
    "BaseEmbeddingProvider",
    "get_llm_provider",
    "get_embedding_provider",
]
