"""
Redis Cache Service
Handles caching for weather and astronomy API responses
"""

import redis
import json
import os
from typing import Optional, Any
from datetime import timedelta


class RedisCache:
    """
    Redis cache wrapper for weather/astronomy data
    """
    
    def __init__(self) -> None:
        """Initialize Redis connection"""
        self.redis_client: Optional[redis.Redis] = None
        redis_host = os.getenv("REDIS_HOST", "redis")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        redis_db = int(os.getenv("REDIS_DB", 0))
        
        try:
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            if self.redis_client is not None:
                self.redis_client.ping()
            self.enabled = True
            print("✅ Redis cache connected successfully")
        except (redis.ConnectionError, redis.TimeoutError) as e:
            print(f"⚠️  Redis connection failed: {e}")
            print("⚠️  Continuing without cache...")
            self.enabled = False
            self.redis_client = None
    
    def _generate_key(self, prefix: str, **kwargs) -> str:
        """
        Generate a cache key from parameters
        Example: weather:lat=-1.2944:lon=36.8362:date=2025-12-14
        """
        params = ":".join([f"{k}={v}" for k, v in sorted(kwargs.items())])
        return f"{prefix}:{params}"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        Returns None if key doesn't exist or cache is disabled
        """
        if not self.enabled or self.redis_client is None:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        """
        Set value in cache with TTL (time to live)
        Default TTL: 1 hour (3600 seconds)
        """
        if not self.enabled or self.redis_client is None:
            return False
        
        try:
            serialized = json.dumps(value)
            self.redis_client.setex(key, ttl_seconds, serialized)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete a key from cache"""
        if not self.enabled or self.redis_client is None:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching a pattern
        Example: clear_pattern("weather:*") clears all weather cache
        """
        if not self.enabled or self.redis_client is None:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache clear error: {e}")
            return 0
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.enabled or self.redis_client is None:
            return {"enabled": False, "message": "Cache disabled"}
        
        try:
            info = self.redis_client.info()
            return {
                "enabled": True,
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "total_keys": self.redis_client.dbsize(),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0)
            }
        except Exception as e:
            return {"enabled": True, "error": str(e)}


# Global cache instance
cache = RedisCache()