"""
Cache Manager Module - KPIs Social Extractor (Optimized)

This module implements a multi-level caching system for storing extraction results,
significantly improving performance and reducing load on target websites.
"""

import os
import json
import time
import hashlib
import logging
import asyncio
from typing import Dict, Any, Optional, Union

from app.config.config import Config

# Configure logging
logger = logging.getLogger(__name__)

class CacheManager:
    """
    Multi-level caching system for extraction results
    """
    
    def __init__(self):
        """Initialize the cache manager with configuration settings"""
        self.config = Config()
        self.enabled = self.config.CACHE_ENABLED
        self.ttl = self.config.CACHE_TTL
        self.backend = self.config.CACHE_BACKEND
        
        # Memory cache
        self._memory_cache = {}
        
        # Redis client (initialized lazily)
        self._redis_client = None
        
        # Create cache directory if using file backend
        if self.backend == "file":
            self.cache_dir = self.config.CACHE_DIR
            os.makedirs(self.cache_dir, exist_ok=True)
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache
        
        Args:
            key: Cache key
            
        Returns:
            Any: Cached value or None if not found or expired
        """
        if not self.enabled:
            return None
        
        # Try memory cache first (fastest)
        memory_result = self._get_from_memory(key)
        if memory_result is not None:
            logger.debug(f"Cache hit (memory): {key}")
            return memory_result
        
        # Try backend cache
        if self.backend == "redis":
            result = await self._get_from_redis(key)
        elif self.backend == "file":
            result = self._get_from_file(key)
        else:
            # Memory-only cache, already checked
            return None
        
        # Update memory cache if backend had a hit
        if result is not None:
            logger.debug(f"Cache hit ({self.backend}): {key}")
            self._memory_cache[key] = {
                "value": result,
                "timestamp": time.time()
            }
        else:
            logger.debug(f"Cache miss: {key}")
        
        return result
    
    async def set(self, key: str, value: Any) -> None:
        """
        Set a value in the cache
        
        Args:
            key: Cache key
            value: Value to cache
        """
        if not self.enabled:
            return
        
        # Update memory cache
        self._memory_cache[key] = {
            "value": value,
            "timestamp": time.time()
        }
        
        # Update backend cache
        if self.backend == "redis":
            await self._set_in_redis(key, value)
        elif self.backend == "file":
            self._set_in_file(key, value)
        
        logger.debug(f"Cached value for key: {key}")
    
    async def delete(self, key: str) -> None:
        """
        Delete a value from the cache
        
        Args:
            key: Cache key
        """
        if not self.enabled:
            return
        
        # Remove from memory cache
        if key in self._memory_cache:
            del self._memory_cache[key]
        
        # Remove from backend cache
        if self.backend == "redis":
            await self._delete_from_redis(key)
        elif self.backend == "file":
            self._delete_from_file(key)
        
        logger.debug(f"Deleted cache entry: {key}")
    
    async def clear(self) -> None:
        """Clear all cached values"""
        if not self.enabled:
            return
        
        # Clear memory cache
        self._memory_cache = {}
        
        # Clear backend cache
        if self.backend == "redis":
            await self._clear_redis()
        elif self.backend == "file":
            self._clear_files()
        
        logger.info("Cache cleared")
    
    async def close(self) -> None:
        """Close any open connections"""
        if self.backend == "redis" and self._redis_client is not None:
            await self._redis_client.close()
            self._redis_client = None
    
    def _get_from_memory(self, key: str) -> Optional[Any]:
        """Get a value from the memory cache"""
        if key not in self._memory_cache:
            return None
        
        entry = self._memory_cache[key]
        
        # Check if entry is expired
        if time.time() - entry["timestamp"] > self.ttl:
            del self._memory_cache[key]
            return None
        
        return entry["value"]
    
    async def _get_from_redis(self, key: str) -> Optional[Any]:
        """Get a value from Redis"""
        try:
            redis_client = await self._get_redis_client()
            value = await redis_client.get(key)
            
            if value is None:
                return None
            
            return json.loads(value)
        except Exception as e:
            logger.error(f"Error getting value from Redis: {str(e)}")
            return None
    
    def _get_from_file(self, key: str) -> Optional[Any]:
        """Get a value from file cache"""
        file_path = self._get_cache_file_path(key)
        
        if not os.path.exists(file_path):
            return None
        
        # Check if file is expired
        if time.time() - os.path.getmtime(file_path) > self.ttl:
            os.remove(file_path)
            return None
        
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading cache file: {str(e)}")
            return None
    
    async def _set_in_redis(self, key: str, value: Any) -> None:
        """Set a value in Redis"""
        try:
            redis_client = await self._get_redis_client()
            await redis_client.setex(
                key,
                self.ttl,
                json.dumps(value)
            )
        except Exception as e:
            logger.error(f"Error setting value in Redis: {str(e)}")
    
    def _set_in_file(self, key: str, value: Any) -> None:
        """Set a value in file cache"""
        file_path = self._get_cache_file_path(key)
        
        try:
            with open(file_path, 'w') as f:
                json.dump(value, f)
        except Exception as e:
            logger.error(f"Error writing cache file: {str(e)}")
    
    async def _delete_from_redis(self, key: str) -> None:
        """Delete a value from Redis"""
        try:
            redis_client = await self._get_redis_client()
            await redis_client.delete(key)
        except Exception as e:
            logger.error(f"Error deleting value from Redis: {str(e)}")
    
    def _delete_from_file(self, key: str) -> None:
        """Delete a value from file cache"""
        file_path = self._get_cache_file_path(key)
        
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.error(f"Error deleting cache file: {str(e)}")
    
    async def _clear_redis(self) -> None:
        """Clear all values from Redis"""
        try:
            redis_client = await self._get_redis_client()
            await redis_client.flushdb()
        except Exception as e:
            logger.error(f"Error clearing Redis cache: {str(e)}")
    
    def _clear_files(self) -> None:
        """Clear all cache files"""
        try:
            for filename in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        except Exception as e:
            logger.error(f"Error clearing file cache: {str(e)}")
    
    def _get_cache_file_path(self, key: str) -> str:
        """Get the file path for a cache key"""
        # Create a safe filename from the key
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{safe_key}.json")
    
    async def _get_redis_client(self):
        """Get or create Redis client"""
        if self._redis_client is None:
            try:
                import redis.asyncio as redis
                self._redis_client = redis.from_url(self.config.CACHE_REDIS_URL)
            except ImportError:
                logger.error("Redis package not installed. Please install with: pip install redis")
                raise
        
        return self._redis_client
