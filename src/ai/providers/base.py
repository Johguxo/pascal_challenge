"""
Base abstract classes for AI providers.
Defines the interface that all LLM and Embedding providers must implement.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class Message:
    """Standard message format for all providers."""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass  
class LLMResponse:
    """Standard response format from LLM providers."""
    content: str
    usage: Optional[Dict[str, int]] = None  # tokens used
    model: Optional[str] = None


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    All LLM providers (OpenAI, Gemini, Anthropic, etc.) must implement this interface.
    """
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name."""
        pass
    
    @abstractmethod
    async def generate(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """
        Generate a response from the LLM.
        
        Args:
            messages: List of messages (system, user, assistant)
            temperature: Creativity level (0.0 to 1.0)
            max_tokens: Maximum tokens in response
        
        Returns:
            LLMResponse with the generated content
        """
        pass
    
    @abstractmethod
    async def generate_simple(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        """
        Simple generation with just a prompt.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system instructions
            temperature: Creativity level
        
        Returns:
            Generated text string
        """
        pass


class BaseEmbeddingProvider(ABC):
    """
    Abstract base class for Embedding providers.
    All embedding providers must implement this interface.
    """
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name."""
        pass
    
    @property
    @abstractmethod
    def dimensions(self) -> int:
        """Return the embedding dimensions."""
        pass
    
    @abstractmethod
    async def generate(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
        
        Returns:
            List of floats (embedding vector)
        """
        pass
    
    @abstractmethod
    async def generate_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
        
        Returns:
            List of embedding vectors
        """
        pass

