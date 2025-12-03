"""
Search cache for caching property search results.
"""
import json
import hashlib
from typing import Optional, List, Any
from dataclasses import dataclass, asdict

from src.cache.redis_client import RedisClient
from src.config import get_settings


@dataclass
class CachedSearchResult:
    """Cached search result structure."""
    query: str
    filters: Optional[dict]
    results: List[dict]
    timestamp: str


class SearchCache:
    """
    Cache for property search results.
    Avoids repeated embedding + DB calls for similar queries.
    """
    
    KEY_PREFIX = "search"
    
    def __init__(self, redis_client: RedisClient):
        self.redis = redis_client
        self.settings = get_settings()
        self.ttl_seconds = self.settings.search_cache_ttl_seconds
    
    def _normalize_query(self, query: str) -> str:
        """
        Normalize query for cache key.
        Lowercase, strip whitespace, remove extra spaces.
        """
        return " ".join(query.lower().strip().split())
    
    def _generate_cache_key(self, query: str, filters: Optional[dict] = None) -> str:
        """
        Generate a deterministic cache key from query and filters.
        Uses hash to keep keys short.
        """
        normalized_query = self._normalize_query(query)
        
        # Sort filters for consistent hashing
        filters_str = ""
        if filters:
            sorted_filters = sorted(filters.items())
            filters_str = json.dumps(sorted_filters, sort_keys=True)
        
        # Create hash
        content = f"{normalized_query}:{filters_str}"
        hash_value = hashlib.md5(content.encode()).hexdigest()[:12]
        
        return f"{self.KEY_PREFIX}:{hash_value}"
    
    async def get(
        self,
        query: str,
        filters: Optional[dict] = None,
    ) -> Optional[List[dict]]:
        """
        Get cached search results.
        Returns None if not cached or expired.
        """
        key = self._generate_cache_key(query, filters)
        cached = await self.redis.get(key)
        
        if cached:
            try:
                data = json.loads(cached)
                return data.get("results")
            except json.JSONDecodeError:
                return None
        
        return None
    
    async def set(
        self,
        query: str,
        results: List[dict],
        filters: Optional[dict] = None,
    ) -> None:
        """Cache search results."""
        from datetime import datetime
        
        key = self._generate_cache_key(query, filters)
        
        cache_data = {
            "query": self._normalize_query(query),
            "filters": filters,
            "results": results,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        await self.redis.set(
            key,
            json.dumps(cache_data),
            ttl_seconds=self.ttl_seconds,
        )
    
    async def invalidate(self, query: str, filters: Optional[dict] = None) -> None:
        """Invalidate specific cache entry."""
        key = self._generate_cache_key(query, filters)
        await self.redis.delete(key)
    
    async def invalidate_all(self) -> None:
        """
        Invalidate all search cache entries.
        Note: This requires SCAN which may be slow on large datasets.
        For production, consider using a separate Redis DB or key patterns.
        """
        # This is a simplified version - in production you'd want to use SCAN
        # For now, individual entries will expire via TTL
        pass

