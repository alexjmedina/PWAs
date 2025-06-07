"""
Base Extractor Module - Hybrid KPI Extraction System (Optimized)

This module implements the core hybrid extraction logic with three levels:
1. Official APIs (when available)
2. Advanced web scraping
3. Human-like simulation

The system includes fallback mechanisms, robust error handling, and asynchronous processing.
"""

import logging
import time
import random
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple, Union
import traceback

from app.config.config import Config
from app.utils.cache_manager import CacheManager
from app.utils.rate_limiter import RateLimiter
from app.utils.browser_pool import BrowserPool
from ..config.config import Config
from ..utils.human_simulation import HumanSimulation

# Configure logging
logger = logging.getLogger(__name__)

class BaseExtractor(ABC):
    """
    Abstract base class for all extractors.
    Defines the common interface and shared functionality.
    """
    
    def __init__(self):
        """Initialize the extractor with configuration settings"""
        self.config = Config()
        self.max_retries = self.config.MAX_RETRIES
        self.use_proxies = self.config.USE_PROXIES
        self.headless = self.config.HEADLESS
        self.browser_timeout = self.config.BROWSER_TIMEOUT
        self.cache = CacheManager()
        self.rate_limiter = RateLimiter(
            rate=self.config.REQUESTS_PER_MINUTE,
            per=60.0,
            burst=self.config.REQUESTS_PER_MINUTE
        )
        
        # Performance monitoring
        self.performance_monitoring = self.config.PERFORMANCE_MONITORING
    
    @abstractmethod
    async def extract_followers(self, url: str) -> Optional[int]:
        """
        Extract followers count from a social media profile
        
        Args:
            url: URL of the social media profile
            
        Returns:
            int: Number of followers or None if extraction fails
        """
        pass
    
    @abstractmethod
    async def extract_engagement(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract engagement metrics from a social media profile
        
        Args:
            url: URL of the social media profile
            
        Returns:
            dict: Engagement metrics or None if extraction fails
        """
        pass
    
    def get_proxy(self) -> Optional[str]:
        """Get a proxy from the configured proxy list"""
        return self.config.get_proxy()
    
    async def random_delay(self, min_seconds: float = None, max_seconds: float = None) -> None:
        """
        Implement a random delay to simulate human behavior and avoid detection
        
        Args:
            min_seconds: Minimum delay in seconds
            max_seconds: Maximum delay in seconds
        """
        min_seconds = min_seconds or self.config.MIN_DELAY
        max_seconds = max_seconds or self.config.MAX_DELAY
        
        delay = random.uniform(min_seconds, max_seconds)
        logger.debug(f"Waiting for {delay:.2f} seconds")
        await asyncio.sleep(delay)
    
    async def extract_with_retry(self, extraction_func, *args, **kwargs) -> Any:
        """
        Execute an extraction function with automatic retry and exponential backoff
        
        Args:
            extraction_func: Async function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Any: Result of the extraction function or None if all attempts fail
        """
        retries = 0
        last_exception = None
        
        while retries < self.max_retries:
            try:
                # Apply rate limiting
                if self.config.RATE_LIMIT_ENABLED:
                    can_proceed, wait_time = await self.rate_limiter.acquire()
                    if not can_proceed:
                        logger.info(f"Rate limit reached, waiting {wait_time:.2f}s")
                        await asyncio.sleep(wait_time)
                
                # Start performance monitoring
                start_time = time.time()
                
                # Execute the extraction function
                result = await extraction_func(*args, **kwargs)
                
                # End performance monitoring
                if self.performance_monitoring:
                    elapsed = time.time() - start_time
                    logger.info(f"Extraction completed in {elapsed:.2f}s")
                
                return result
                
            except Exception as e:
                last_exception = e
                retries += 1
                
                # Calculate backoff time
                wait_time = min(2 ** retries, 60)  # Cap at 60 seconds
                
                logger.warning(
                    f"Extraction attempt {retries}/{self.max_retries} failed: {str(e)}. "
                    f"Retrying in {wait_time}s"
                )
                
                if self.config.ERROR_REPORTING:
                    logger.debug(f"Exception details: {traceback.format_exc()}")
                
                await asyncio.sleep(wait_time)
        
        logger.error(f"All extraction attempts failed: {last_exception}")
        return None


class HybridExtractor:
    """
    Main hybrid extractor that orchestrates the extraction process
    using the three-level approach: API, scraping, and simulation.
    """
    
    def __init__(self):
        """Initialize the hybrid extractor with platform-specific extractors"""
        self.config = Config()
        self.extractors = {}  # Will be populated with platform-specific extractors
        self.max_retries = self.config.MAX_RETRIES
        self.cache = CacheManager()
        self.browser_pool = BrowserPool(max_browsers=self.config.BROWSER_POOL_SIZE)
        
        # Performance monitoring
        self.performance_monitoring = self.config.PERFORMANCE_MONITORING
    
    def register_extractor(self, platform: str, extractor: BaseExtractor) -> None:
        """
        Register a platform-specific extractor
        
        Args:
            platform: Platform name (e.g., 'facebook', 'instagram')
            extractor: Extractor instance for the platform
        """
        self.extractors[platform] = extractor
        logger.info(f"Registered extractor for {platform}")
    
    async def extract_followers(self, platform: str, url: str) -> Optional[int]:
        """
        Extract followers count using the hybrid approach
        
        Args:
            platform: Platform name (e.g., 'facebook', 'instagram')
            url: URL of the social media profile
            
        Returns:
            int: Number of followers or None if all extraction methods fail
        """
        logger.info(f"Starting hybrid extraction for {platform} followers: {url}")
        
        # Check cache first
        if self.config.CACHE_ENABLED:
            cache_key = f"{platform}:followers:{url}"
            cached_result = await self.cache.get(cache_key)
            if cached_result is not None:
                logger.info(f"Using cached followers for {platform}: {cached_result}")
                return cached_result
        
        if platform not in self.extractors:
            logger.error(f"No extractor registered for platform: {platform}")
            return None
        
        # Level 1: Try API extraction
        logger.info(f"Level 1: Attempting to extract {platform} followers via API")
        try:
            # API extraction will be implemented in platform-specific extractors
            followers = await self.extractors[platform].extract_followers(url)
            if followers is not None:
                logger.info(f"Successfully extracted {platform} followers via API: {followers}")
                
                # Cache the result
                if self.config.CACHE_ENABLED:
                    await self.cache.set(cache_key, followers)
                
                return followers
        except Exception as e:
            logger.error(f"API extraction failed for {platform}: {str(e)}")
        
        logger.info(f"API extraction failed for {platform}, falling back to scraping")
        
        # Level 2 & 3: Try web scraping with fallback to human simulation
        # These levels are implemented within the platform-specific extractors
        followers = await self.extractors[platform].extract_with_retry(
            self.extractors[platform].extract_followers, url
        )
        
        if followers is not None:
            logger.info(f"Successfully extracted {platform} followers via scraping: {followers}")
            
            # Cache the result
            if self.config.CACHE_ENABLED:
                await self.cache.set(cache_key, followers)
            
            return followers
        
        logger.error(f"All extraction methods failed for {platform} followers")
        return None
    
    async def extract_engagement(self, platform: str, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract engagement metrics using the hybrid approach
        
        Args:
            platform: Platform name (e.g., 'facebook', 'instagram')
            url: URL of the social media profile
            
        Returns:
            dict: Engagement metrics or None if all extraction methods fail
        """
        logger.info(f"Starting hybrid extraction for {platform} engagement: {url}")
        
        # Check cache first
        if self.config.CACHE_ENABLED:
            cache_key = f"{platform}:engagement:{url}"
            cached_result = await self.cache.get(cache_key)
            if cached_result is not None:
                logger.info(f"Using cached engagement for {platform}")
                return cached_result
        
        if platform not in self.extractors:
            logger.error(f"No extractor registered for platform: {platform}")
            return None
        
        # Level 1: Try API extraction
        logger.info(f"Level 1: Attempting to extract {platform} engagement via API")
        try:
            # API extraction will be implemented in platform-specific extractors
            engagement = await self.extractors[platform].extract_engagement(url)
            if engagement is not None:
                logger.info(f"Successfully extracted {platform} engagement via API")
                
                # Cache the result
                if self.config.CACHE_ENABLED:
                    await self.cache.set(cache_key, engagement)
                
                return engagement
        except Exception as e:
            logger.error(f"API extraction failed for {platform}: {str(e)}")
        
        logger.info(f"API extraction failed for {platform}, falling back to scraping")
        
        # Level 2 & 3: Try web scraping with fallback to human simulation
        # These levels are implemented within the platform-specific extractors
        engagement = await self.extractors[platform].extract_with_retry(
            self.extractors[platform].extract_engagement, url
        )
        
        if engagement is not None:
            logger.info(f"Successfully extracted {platform} engagement via scraping")
            
            # Cache the result
            if self.config.CACHE_ENABLED:
                await self.cache.set(cache_key, engagement)
            
            return engagement
        
        logger.error(f"All extraction methods failed for {platform} engagement")
        return None
    
    async def extract_complete_kpi_data(self, platform: str, url: str) -> Dict[str, Any]:
        """
        Extract complete KPI data for a social media profile
        
        Args:
            platform: Platform name (e.g., 'facebook', 'instagram')
            url: URL of the social media profile
            
        Returns:
            dict: Complete KPI data including followers and engagement metrics
        """
        logger.info(f"Extracting complete KPI data for {platform}: {url}")
        
        result = {
            "platform": platform,
            "url": url,
            "timestamp": int(time.time()),
            "success": False,
            "error": None
        }
        
        try:
            # Start performance monitoring
            start_time = time.time()
            
            # Extract followers count
            followers = await self.extract_followers(platform, url)
            result["followers"] = followers
            
            # Extract engagement metrics
            engagement = await self.extract_engagement(platform, url)
            if engagement:
                result.update(engagement)
            
            # Calculate engagement rate if possible
            if followers and engagement and "avg_likes" in engagement and "avg_comments" in engagement:
                total_engagement = engagement["avg_likes"] + engagement["avg_comments"]
                result["engagement_rate"] = round((total_engagement / followers) * 100, 2)
            
            result["success"] = followers is not None or engagement is not None
            
            # End performance monitoring
            if self.performance_monitoring:
                elapsed = time.time() - start_time
                logger.info(f"Complete KPI extraction for {platform} completed in {elapsed:.2f}s")
            
        except Exception as e:
            logger.error(f"Error extracting complete KPI data for {platform}: {str(e)}")
            result["error"] = str(e)
        
        return result
    
    async def extract_multiple_platforms(self, urls: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """
        Extract KPI data for multiple platforms in parallel
        
        Args:
            urls: Dictionary with platform names as keys and URLs as values
            
        Returns:
            dict: Dictionary with platform names as keys and KPI data as values
        """
        logger.info(f"Starting extraction for multiple platforms: {', '.join(urls.keys())}")
        
        results = {}
        
        # Start performance monitoring
        start_time = time.time()
        
        if self.config.PARALLEL_EXTRACTION:
            # Process platforms in parallel
            tasks = []
            for platform, url in urls.items():
                if url:
                    tasks.append(self._create_extraction_task(platform, url))
            
            # Wait for all tasks to complete
            platform_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, (platform, _) in enumerate([(p, u) for p, u in urls.items() if u]):
                if isinstance(platform_results[i], Exception):
                    logger.error(f"Error extracting from {platform}: {platform_results[i]}")
                    results[platform] = {
                        "platform": platform,
                        "url": urls[platform],
                        "timestamp": int(time.time()),
                        "success": False,
                        "error": str(platform_results[i])
                    }
                else:
                    results[platform] = platform_results[i]
        else:
            # Process platforms in sequence to avoid detection
            for platform, url in urls.items():
                if url:
                    results[platform] = await self.extract_complete_kpi_data(platform, url)
                    
                    # Add random delay between platforms to avoid detection
                    if platform != list(urls.keys())[-1]:
                        delay = random.uniform(3, 8)
                        logger.info(f"Waiting {delay:.1f}s before processing next platform")
                        await asyncio.sleep(delay)
        
        # End performance monitoring
        if self.performance_monitoring:
            elapsed = time.time() - start_time
            logger.info(f"Multiple platform extraction completed in {elapsed:.2f}s")
        
        return results
    
    async def _create_extraction_task(self, platform: str, url: str):
        """Create a task for extracting KPI data from a platform"""
        return await self.extract_complete_kpi_data(platform, url)
    
    async def calculate_time_based_metrics(self, historical_data: List[Dict[str, Any]], days: int = 30) -> Dict[str, Any]:
        """
        Calculate time-based metrics from historical data
        
        Args:
            historical_data: List of data points with timestamps
            days: Number of days to analyze
            
        Returns:
            dict: Time-based metrics
        """
        if not historical_data or len(historical_data) < 2:
            return {
                "post_frequency": None,
                "growth_rate": None,
                "engagement_trend": None,
                "has_time_data": False
            }
        
        try:
            # Sort data by timestamp
            sorted_data = sorted(historical_data, key=lambda x: x["timestamp"])
            
            # Filter data for the specified time period
            now = time.time()
            cutoff = now - (days * 24 * 60 * 60)
            recent_data = [data for data in sorted_data if data["timestamp"] >= cutoff]
            
            if len(recent_data) < 2:
                logger.warning(f"Insufficient data points for time-based metrics in the last {days} days")
                recent_data = sorted_data  # Fall back to all data
            
            # Calculate post frequency (posts per week)
            time_span_seconds = recent_data[-1]["timestamp"] - recent_data[0]["timestamp"]
            time_span_weeks = time_span_seconds / (60 * 60 * 24 * 7)
            post_frequency = len(recent_data) / time_span_weeks if time_span_weeks > 0 else 0
            
            # Calculate follower growth rate
            oldest_followers = recent_data[0].get("followers", 0)
            newest_followers = recent_data[-1].get("followers", 0)
            growth_rate = ((newest_followers - oldest_followers) / oldest_followers * 100) if oldest_followers > 0 else 0
            
            # Calculate engagement trend
            engagement_rates = [data.get("engagement_rate", 0) for data in recent_data if "engagement_rate" in data]
            engagement_trend = await self._calculate_trend(engagement_rates)
            
            return {
                "post_frequency": round(post_frequency, 1),
                "growth_rate": round(growth_rate, 1),
                "engagement_trend": engagement_trend,
                "has_time_data": True,
                "data_points": len(recent_data),
                "time_span_days": round(time_span_seconds / (60 * 60 * 24), 1)
            }
            
        except Exception as e:
            logger.error(f"Error calculating time-based metrics: {str(e)}")
            return {
                "post_frequency": None,
                "growth_rate": None,
                "engagement_trend": None,
                "has_time_data": False,
                "error": str(e)
            }
    
    async def _calculate_trend(self, values: List[float]) -> str:
        """
        Calculate trend direction from a series of values using linear regression
        
        Args:
            values: List of numeric values
            
        Returns:
            str: Trend direction: 'increasing', 'decreasing', or 'stable'
        """
        if not values or len(values) < 2:
            return "stable"
        
        # Simple linear regression to determine trend
        n = len(values)
        indices = list(range(n))
        
        # Calculate means
        mean_x = sum(indices) / n
        mean_y = sum(values) / n
        
        # Calculate slope
        numerator = sum((indices[i] - mean_x) * (values[i] - mean_y) for i in range(n))
        denominator = sum((indices[i] - mean_x) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        
        # Determine trend based on slope and statistical significance
        if abs(slope) < 0.05:
            return "stable"
        elif slope > 0:
            return "increasing"
        else:
            return "decreasing"
    
    async def close(self):
        """Clean up resources"""
        await self.browser_pool.close_all()
        await self.cache.close()
