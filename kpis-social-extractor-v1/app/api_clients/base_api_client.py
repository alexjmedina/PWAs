"""
Base API Client Module - KPIs Social Extractor (API-First)

This module implements the abstract base class for all API clients,
defining the common interface and shared functionality.
"""

import logging
import asyncio
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union

from app.utils.rate_limiter import PlatformRateLimiter
from app.utils.cache_manager import CacheManager
from app.config.config import Config

# Configure logging
logger = logging.getLogger(__name__)

class BaseAPIClient(ABC):
    """
    Abstract base class for all social media API clients.
    Defines the common interface and shared functionality.
    """
    
    def __init__(self, platform_name: str):
        """
        Initialize the API client with configuration settings
        
        Args:
            platform_name: Name of the social media platform (e.g., 'twitter', 'facebook')
        """
        self.config = Config()
        self.platform_name = platform_name.lower()
        self.cache = CacheManager()
        self.rate_limiter = PlatformRateLimiter()
        
        # Performance monitoring
        self.performance_monitoring = self.config.PERFORMANCE_MONITORING
    
    @abstractmethod
    async def get_user_profile(self, username_or_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile information from the API
        
        Args:
            username_or_id: Username or ID of the user
            
        Returns:
            dict: User profile data or None if extraction fails
        """
        pass
    
    @abstractmethod
    async def get_followers_count(self, username_or_id: str) -> Optional[int]:
        """
        Get followers count from the API
        
        Args:
            username_or_id: Username or ID of the user
            
        Returns:
            int: Number of followers or None if extraction fails
        """
        pass
    
    @abstractmethod
    async def get_engagement_metrics(self, username_or_id: str) -> Optional[Dict[str, Any]]:
        """
        Get engagement metrics from the API
        
        Args:
            username_or_id: Username or ID of the user
            
        Returns:
            dict: Engagement metrics or None if extraction fails
        """
        pass
    
    async def make_api_request(self, endpoint: str, params: Dict[str, Any] = None, 
                              method: str = "GET", data: Dict[str, Any] = None,
                              headers: Dict[str, str] = None) -> Optional[Dict[str, Any]]:
        """
        Make an API request with rate limiting, caching, and error handling
        
        Args:
            endpoint: API endpoint to call
            params: Query parameters
            method: HTTP method (GET, POST, etc.)
            data: Request body for POST/PUT requests
            headers: HTTP headers
            
        Returns:
            dict: API response or None if request fails
        """
        import aiohttp
        
        # Check cache first if it's a GET request
        cache_key = None
        if method == "GET" and self.config.CACHE_ENABLED:
            cache_key = f"{self.platform_name}:{endpoint}:{json.dumps(params or {})}"
            cached_result = await self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Using cached result for {endpoint}")
                return cached_result
        
        # Apply rate limiting
        if self.config.RATE_LIMIT_ENABLED:
            await self.rate_limiter.wait(self.platform_name)
        
        # Start performance monitoring
        import time
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                # Prepare request
                request_kwargs = {
                    "params": params,
                    "headers": headers or {},
                }
                
                if data and method in ["POST", "PUT", "PATCH"]:
                    request_kwargs["json"] = data
                
                # Make request
                async with session.request(method, endpoint, **request_kwargs) as response:
                    # Check for rate limiting
                    if response.status == 429:
                        retry_after = int(response.headers.get("Retry-After", 60))
                        logger.warning(f"Rate limit hit for {self.platform_name}. Retry after {retry_after}s")
                        return None
                    
                    # Check for success
                    if response.status >= 200 and response.status < 300:
                        result = await response.json()
                        
                        # Cache successful GET responses
                        if method == "GET" and self.config.CACHE_ENABLED and cache_key:
                            await self.cache.set(cache_key, result)
                        
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"API request failed: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error making API request to {endpoint}: {str(e)}")
            return None
        finally:
            # End performance monitoring
            if self.performance_monitoring:
                elapsed = time.time() - start_time
                logger.info(f"API request to {endpoint} completed in {elapsed:.2f}s")
    
    async def extract_with_retry(self, extraction_func, *args, max_retries: int = None, **kwargs) -> Any:
        """
        Execute an extraction function with automatic retry and exponential backoff
        
        Args:
            extraction_func: Async function to execute
            *args: Positional arguments for the function
            max_retries: Maximum number of retry attempts
            **kwargs: Keyword arguments for the function
            
        Returns:
            Any: Result of the extraction function or None if all attempts fail
        """
        max_retries = max_retries or self.config.MAX_RETRIES
        retries = 0
        last_exception = None
        
        while retries < max_retries:
            try:
                # Execute the extraction function
                result = await extraction_func(*args, **kwargs)
                
                if result is not None:
                    return result
                
            except Exception as e:
                last_exception = e
                
            # Increment retry counter
            retries += 1
            
            if retries < max_retries:
                # Calculate backoff time with jitter
                import random
                wait_time = min(2 ** retries + random.uniform(0, 1), 60)
                
                logger.warning(
                    f"Extraction attempt {retries}/{max_retries} failed. "
                    f"Retrying in {wait_time:.2f}s"
                )
                
                await asyncio.sleep(wait_time)
        
        logger.error(f"All extraction attempts failed: {last_exception}")
        return None
    
    def get_api_credentials(self) -> Dict[str, str]:
        """
        Get API credentials for the platform from configuration
        
        Returns:
            dict: API credentials
        """
        # Get platform-specific credentials
        credentials = {}
        
        # Common credential keys with platform prefix
        credential_keys = [
            f"{self.platform_name.upper()}_API_KEY",
            f"{self.platform_name.upper()}_API_SECRET",
            f"{self.platform_name.upper()}_ACCESS_TOKEN",
            f"{self.platform_name.upper()}_ACCESS_TOKEN_SECRET",
            f"{self.platform_name.upper()}_BEARER_TOKEN",
            f"{self.platform_name.upper()}_CLIENT_ID",
            f"{self.platform_name.upper()}_CLIENT_SECRET"
        ]
        
        # Extract available credentials
        for key in credential_keys:
            value = self.config.get(key)
            if value:
                # Store without platform prefix
                clean_key = key.replace(f"{self.platform_name.upper()}_", "").lower()
                credentials[clean_key] = value
        
        return credentials
    
    def has_valid_credentials(self) -> bool:
        """
        Check if valid API credentials are available for the platform
        
        Returns:
            bool: True if valid credentials are available, False otherwise
        """
        credentials = self.get_api_credentials()
        
        # Platform-specific credential requirements
        if self.platform_name == "twitter":
            return "bearer_token" in credentials or ("api_key" in credentials and "api_secret" in credentials)
        elif self.platform_name == "facebook":
            return "access_token" in credentials
        elif self.platform_name == "instagram":
            return "access_token" in credentials
        elif self.platform_name == "linkedin":
            return "client_id" in credentials and "client_secret" in credentials
        elif self.platform_name == "youtube":
            return "api_key" in credentials
        elif self.platform_name == "tiktok":
            return "client_key" in credentials and "client_secret" in credentials
        
        # Default case
        return bool(credentials)
