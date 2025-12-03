"""
Redis client for cache operations.
"""
import redis.asyncio as redis
from functools import lru_cache
from typing import Optional

from src.config import get_settings


class RedisClient:
    """Async Redis client wrapper."""
    
    def __init__(self, url: str):
        self.url = url
        self._client: Optional[redis.Redis] = None
    
    async def connect(self) -> redis.Redis:
        """Get or create Redis connection."""
        if self._client is None:
            self._client = redis.from_url(
                self.url,
                encoding="utf-8",
                decode_responses=True,
            )
        return self._client
    
    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None
    
    async def get(self, key: str) -> Optional[str]:
        """Get value by key."""
        client = await self.connect()
        return await client.get(key)
    
    async def set(
        self,
        key: str,
        value: str,
        ttl_seconds: Optional[int] = None,
    ) -> bool:
        """Set value with optional TTL."""
        client = await self.connect()
        if ttl_seconds:
            return await client.setex(key, ttl_seconds, value)
        return await client.set(key, value)
    
    async def delete(self, key: str) -> int:
        """Delete key."""
        client = await self.connect()
        return await client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        client = await self.connect()
        return await client.exists(key) > 0
    
    async def lpush(self, key: str, *values: str) -> int:
        """Push values to the left of a list."""
        client = await self.connect()
        return await client.lpush(key, *values)
    
    async def rpush(self, key: str, *values: str) -> int:
        """Push values to the right of a list."""
        client = await self.connect()
        return await client.rpush(key, *values)
    
    async def lrange(self, key: str, start: int, end: int) -> list:
        """Get range of list elements."""
        client = await self.connect()
        return await client.lrange(key, start, end)
    
    async def ltrim(self, key: str, start: int, end: int) -> bool:
        """Trim list to specified range."""
        client = await self.connect()
        return await client.ltrim(key, start, end)
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on key."""
        client = await self.connect()
        return await client.expire(key, seconds)
    
    async def ping(self) -> bool:
        """Check Redis connection."""
        try:
            client = await self.connect()
            return await client.ping()
        except Exception:
            return False


# Global Redis client instance
_redis_client: Optional[RedisClient] = None


def get_redis_client() -> RedisClient:
    """Get global Redis client instance."""
    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        _redis_client = RedisClient(settings.redis_url)
    return _redis_client

