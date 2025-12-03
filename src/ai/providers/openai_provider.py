"""
OpenAI provider implementations for LLM and Embeddings.
"""
from typing import List, Optional
from openai import AsyncOpenAI

from src.config import get_settings
from src.ai.providers.base import (
    BaseLLMProvider,
    BaseEmbeddingProvider,
    Message,
    LLMResponse,
)


class OpenAILLMProvider(BaseLLMProvider):
    """OpenAI LLM provider using GPT models."""
    
    def __init__(self, model: Optional[str] = None):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = model or settings.llm_model
    
    @property
    def provider_name(self) -> str:
        return "openai"
    
    async def generate(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate response using OpenAI API."""
        # Convert to OpenAI format
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        kwargs = {
            "model": self.model,
            "messages": openai_messages,
            "temperature": temperature,
        }
        if max_tokens:
            kwargs["max_tokens"] = max_tokens
        
        response = await self.client.chat.completions.create(**kwargs)
        
        return LLMResponse(
            content=response.choices[0].message.content,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            } if response.usage else None,
            model=response.model,
        )
    
    async def generate_simple(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        """Simple generation with just a prompt."""
        messages = []
        if system_prompt:
            messages.append(Message(role="system", content=system_prompt))
        messages.append(Message(role="user", content=prompt))
        
        response = await self.generate(messages, temperature=temperature)
        return response.content


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """OpenAI Embedding provider."""
    
    def __init__(self, model: Optional[str] = None):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = model or settings.embedding_model
        self._dimensions = 1536  # Default for text-embedding-3-small
    
    @property
    def provider_name(self) -> str:
        return "openai"
    
    @property
    def dimensions(self) -> int:
        return self._dimensions
    
    async def generate(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        response = await self.client.embeddings.create(
            model=self.model,
            input=text,
        )
        return response.data[0].embedding
    
    async def generate_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        if not texts:
            return []
        
        response = await self.client.embeddings.create(
            model=self.model,
            input=texts,
        )
        return [item.embedding for item in response.data]

