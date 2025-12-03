"""
Google Gemini provider implementations for LLM and Embeddings.
"""
from typing import List, Optional
import google.generativeai as genai

from src.config import get_settings
from src.ai.providers.base import (
    BaseLLMProvider,
    BaseEmbeddingProvider,
    Message,
    LLMResponse,
)


class GeminiLLMProvider(BaseLLMProvider):
    """Google Gemini LLM provider."""
    
    def __init__(self, model: Optional[str] = None):
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        # Use the correct model name format for Gemini API
        self.model_name = model or settings.llm_model or "gemini-2.0-flash"
        self.model = genai.GenerativeModel(self.model_name)
    
    @property
    def provider_name(self) -> str:
        return "gemini"
    
    async def generate(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate response using Gemini API."""
        # Convert messages to Gemini format
        # Gemini uses a different format - we need to build a conversation
        
        # Extract system prompt if present
        system_prompt = None
        chat_messages = []
        
        for msg in messages:
            if msg.role == "system":
                system_prompt = msg.content
            elif msg.role == "user":
                chat_messages.append({"role": "user", "parts": [msg.content]})
            elif msg.role == "assistant":
                chat_messages.append({"role": "model", "parts": [msg.content]})
        
        # Configure generation
        generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens if max_tokens else 2048,
        )
        
        # If we have a system prompt, include it in the model config
        if system_prompt:
            model = genai.GenerativeModel(
                self.model_name,
                system_instruction=system_prompt,
                generation_config=generation_config,
            )
        else:
            model = genai.GenerativeModel(
                self.model_name,
                generation_config=generation_config,
            )
        
        # Start chat if we have history, otherwise just generate
        if len(chat_messages) > 1:
            chat = model.start_chat(history=chat_messages[:-1])
            response = await chat.send_message_async(chat_messages[-1]["parts"][0])
        else:
            # Single message
            prompt = chat_messages[0]["parts"][0] if chat_messages else ""
            response = await model.generate_content_async(prompt)
        
        return LLMResponse(
            content=response.text,
            usage=None,  # Gemini doesn't expose token usage the same way
            model=self.model_name,
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


class GeminiEmbeddingProvider(BaseEmbeddingProvider):
    """Google Gemini Embedding provider."""
    
    def __init__(self, model: Optional[str] = None):
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        self.model = model or "models/text-embedding-004"
        self._dimensions = 768  # Gemini embedding dimensions
    
    @property
    def provider_name(self) -> str:
        return "gemini"
    
    @property
    def dimensions(self) -> int:
        return self._dimensions
    
    async def generate(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        # Gemini embeddings are synchronous, we wrap it
        result = genai.embed_content(
            model=self.model,
            content=text,
            task_type="retrieval_document",
        )
        return result['embedding']
    
    async def generate_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        if not texts:
            return []
        
        embeddings = []
        for text in texts:
            embedding = await self.generate(text)
            embeddings.append(embedding)
        
        return embeddings

