"""
Conversation cache for storing recent messages.
"""
import json
from typing import List, Optional
from dataclasses import dataclass, asdict

from src.cache.redis_client import RedisClient
from src.config import get_settings


@dataclass
class CachedMessage:
    """Cached message structure."""
    role: str  # "human" or "assistant"
    content: str
    timestamp: Optional[str] = None


class ConversationCache:
    """
    Cache for conversation history.
    Stores the last N messages for each conversation to provide context to LLM.
    """
    
    KEY_PREFIX = "conv"
    
    def __init__(self, redis_client: RedisClient):
        self.redis = redis_client
        self.settings = get_settings()
        self.max_messages = self.settings.conversation_history_limit
    
    def _get_key(self, conversation_id: str) -> str:
        """Generate Redis key for conversation."""
        return f"{self.KEY_PREFIX}:{conversation_id}"
    
    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        timestamp: Optional[str] = None,
    ) -> None:
        """
        Add a message to the conversation history.
        Maintains only the last N messages.
        """
        key = self._get_key(conversation_id)
        message = CachedMessage(role=role, content=content, timestamp=timestamp)
        
        # Push to the right (newest at the end)
        await self.redis.rpush(key, json.dumps(asdict(message)))
        
        # Trim to keep only last N messages
        await self.redis.ltrim(key, -self.max_messages, -1)
        
        # Set TTL (24 hours)
        await self.redis.expire(key, 86400)
    
    async def get_history(self, conversation_id: str) -> List[CachedMessage]:
        """Get conversation history."""
        key = self._get_key(conversation_id)
        messages_json = await self.redis.lrange(key, 0, -1)
        
        messages = []
        for msg_json in messages_json:
            try:
                data = json.loads(msg_json)
                messages.append(CachedMessage(**data))
            except (json.JSONDecodeError, TypeError):
                continue
        
        return messages
    
    async def get_history_for_llm(self, conversation_id: str) -> List[dict]:
        """
        Get conversation history formatted for LLM context.
        Returns list of {"role": "user"|"assistant", "content": "..."}
        """
        messages = await self.get_history(conversation_id)
        return [
            {
                "role": "user" if msg.role == "human" else "assistant",
                "content": msg.content,
            }
            for msg in messages
        ]
    
    async def clear(self, conversation_id: str) -> None:
        """Clear conversation history."""
        key = self._get_key(conversation_id)
        await self.redis.delete(key)
    
    async def exists(self, conversation_id: str) -> bool:
        """Check if conversation has cached history."""
        key = self._get_key(conversation_id)
        return await self.redis.exists(key)

