"""
Rate Limiter Module - KPIs Social Extractor (Optimized)

This module implements a token bucket rate limiter to prevent detection
by social media platforms and respect API rate limits.
"""

import time
import asyncio
import logging
from typing import Dict, Any, Optional, Tuple

# Configure logging
logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Token bucket rate limiter for API and scraping requests
    """
    
    def __init__(self, rate: float = 1.0, per: float = 1.0, burst: int = 1):
        """
        Initialize the rate limiter
        
        Args:
            rate: Number of requests allowed per time period
            per: Time period in seconds
            burst: Maximum burst size (token bucket capacity)
        """
        self.rate = rate
        self.per = per
        self.tokens = burst
        self.max_tokens = burst
        self.updated_at = time.monotonic()
        self.lock = asyncio.Lock()
    
    async def acquire(self) -> Tuple[bool, float]:
        """
        Acquire a token from the bucket
        
        Returns:
            tuple: (success, wait_time)
                - success: True if token was acquired, False otherwise
                - wait_time: Time to wait before retrying if not successful
        """
        async with self.lock:
            now = time.monotonic()
            elapsed = now - self.updated_at
            self.updated_at = now
            
            # Add new tokens based on elapsed time
            self.tokens = min(self.max_tokens, self.tokens + elapsed * (self.rate / self.per))
            
            if self.tokens >= 1:
                self.tokens -= 1
                return True, 0.0
            else:
                # Calculate wait time until next token is available
                wait_time = (1 - self.tokens) * (self.per / self.rate)
                return False, wait_time
    
    async def wait(self) -> None:
        """
        Wait until a token is available and then acquire it
        """
        while True:
            can_proceed, wait_time = await self.acquire()
            if can_proceed:
                return
            
            logger.debug(f"Rate limit reached, waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)


class PlatformRateLimiter:
    """
    Manages rate limiters for multiple platforms
    """
    
    def __init__(self):
        """Initialize platform-specific rate limiters"""
        self.limiters = {
            "facebook": RateLimiter(rate=10, per=60, burst=3),  # 10 requests per minute, burst of 3
            "instagram": RateLimiter(rate=6, per=60, burst=2),  # 6 requests per minute, burst of 2
            "twitter": RateLimiter(rate=15, per=900, burst=5),  # 15 requests per 15 minutes, burst of 5
            "youtube": RateLimiter(rate=60, per=3600, burst=10),  # 60 requests per hour, burst of 10
            "linkedin": RateLimiter(rate=20, per=60, burst=5),  # 20 requests per minute, burst of 5
            "tiktok": RateLimiter(rate=10, per=60, burst=3),  # 10 requests per minute, burst of 3
            "default": RateLimiter(rate=30, per=60, burst=10)  # Default limiter
        }
    
    async def acquire(self, platform: str) -> Tuple[bool, float]:
        """
        Acquire a token for the specified platform
        
        Args:
            platform: Platform name
            
        Returns:
            tuple: (success, wait_time)
        """
        limiter = self.limiters.get(platform.lower(), self.limiters["default"])
        return await limiter.acquire()
    
    async def wait(self, platform: str) -> None:
        """
        Wait until a token is available for the specified platform
        
        Args:
            platform: Platform name
        """
        limiter = self.limiters.get(platform.lower(), self.limiters["default"])
        await limiter.wait()
