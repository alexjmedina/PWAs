"""
Base Extractor Module - Hybrid KPI Extraction System

This module implements the core hybrid extraction logic with three levels:
1. Official APIs (when available)
2. Advanced web scraping
3. Human-like simulation

The system includes fallback mechanisms and robust error handling.
"""

import logging
import time
import random
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple

from app.config.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
        self.proxy_list = self.config.PROXY_LIST
        self.headless = self.config.HEADLESS
        self.browser_timeout = self.config.BROWSER_TIMEOUT
    
    @abstractmethod
    def extract_followers(self, url: str) -> Optional[int]:
        """
        Extract followers count from a social media profile
        
        Args:
            url: URL of the social media profile
            
        Returns:
            int: Number of followers or None if extraction fails
        """
        pass
    
    @abstractmethod
    def extract_engagement(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract engagement metrics from a social media profile
        
        Args:
            url: URL of the social media profile
            
        Returns:
            dict: Engagement metrics or None if extraction fails
        """
        pass
    
    def get_random_proxy(self) -> Optional[str]:
        """Get a random proxy from the configured proxy list"""
        if not self.use_proxies or not self.proxy_list:
            return None
        
        return random.choice(self.proxy_list)
    
    def random_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0) -> None:
        """
        Implement a random delay to simulate human behavior and avoid detection
        
        Args:
            min_seconds: Minimum delay in seconds
            max_seconds: Maximum delay in seconds
        """
        delay = random.uniform(min_seconds, max_seconds)
        logger.debug(f"Waiting for {delay:.2f} seconds")
        time.sleep(delay)


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
    
    def register_extractor(self, platform: str, extractor: BaseExtractor) -> None:
        """
        Register a platform-specific extractor
        
        Args:
            platform: Platform name (e.g., 'facebook', 'instagram')
            extractor: Extractor instance for the platform
        """
        self.extractors[platform] = extractor
        logger.info(f"Registered extractor for {platform}")
    
    def extract_followers(self, platform: str, url: str) -> Optional[int]:
        """
        Extract followers count using the hybrid approach
        
        Args:
            platform: Platform name (e.g., 'facebook', 'instagram')
            url: URL of the social media profile
            
        Returns:
            int: Number of followers or None if all extraction methods fail
        """
        logger.info(f"Starting hybrid extraction for {platform} followers: {url}")
        
        if platform not in self.extractors:
            logger.error(f"No extractor registered for platform: {platform}")
            return None
        
        # Level 1: Try API extraction
        logger.info(f"Level 1: Attempting to extract {platform} followers via API")
        try:
            # API extraction will be implemented in platform-specific extractors
            followers = self.extractors[platform].extract_followers(url)
            if followers is not None:
                logger.info(f"Successfully extracted {platform} followers via API: {followers}")
                return followers
        except Exception as e:
            logger.error(f"API extraction failed for {platform}: {str(e)}")
        
        logger.info(f"API extraction failed for {platform}, falling back to scraping")
        
        # Level 2 & 3: Try web scraping with fallback to human simulation
        # These levels are implemented within the platform-specific extractors
        for attempt in range(1, self.max_retries + 1):
            try:
                followers = self.extractors[platform].extract_followers(url)
                if followers is not None:
                    logger.info(f"Successfully extracted {platform} followers via scraping: {followers}")
                    return followers
                
                logger.warning(f"Scraping attempt {attempt} failed for {platform}")
            except Exception as e:
                logger.error(f"Error in scraping attempt {attempt} for {platform}: {str(e)}")
            
            # Wait before retry with increasing delay
            if attempt < self.max_retries:
                delay = 2 * attempt
                logger.info(f"Waiting {delay}s before retry {attempt + 1}")
                time.sleep(delay)
        
        logger.error(f"All extraction methods failed for {platform} followers")
        return None
    
    def extract_engagement(self, platform: str, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract engagement metrics using the hybrid approach
        
        Args:
            platform: Platform name (e.g., 'facebook', 'instagram')
            url: URL of the social media profile
            
        Returns:
            dict: Engagement metrics or None if all extraction methods fail
        """
        logger.info(f"Starting hybrid extraction for {platform} engagement: {url}")
        
        if platform not in self.extractors:
            logger.error(f"No extractor registered for platform: {platform}")
            return None
        
        # Level 1: Try API extraction
        logger.info(f"Level 1: Attempting to extract {platform} engagement via API")
        try:
            # API extraction will be implemented in platform-specific extractors
            engagement = self.extractors[platform].extract_engagement(url)
            if engagement is not None:
                logger.info(f"Successfully extracted {platform} engagement via API")
                return engagement
        except Exception as e:
            logger.error(f"API extraction failed for {platform}: {str(e)}")
        
        logger.info(f"API extraction failed for {platform}, falling back to scraping")
        
        # Level 2 & 3: Try web scraping with fallback to human simulation
        # These levels are implemented within the platform-specific extractors
        for attempt in range(1, self.max_retries + 1):
            try:
                engagement = self.extractors[platform].extract_engagement(url)
                if engagement is not None:
                    logger.info(f"Successfully extracted {platform} engagement via scraping")
                    return engagement
                
                logger.warning(f"Scraping attempt {attempt} failed for {platform}")
            except Exception as e:
                logger.error(f"Error in scraping attempt {attempt} for {platform}: {str(e)}")
            
            # Wait before retry with increasing delay
            if attempt < self.max_retries:
                delay = 2 * attempt
                logger.info(f"Waiting {delay}s before retry {attempt + 1}")
                time.sleep(delay)
        
        logger.error(f"All extraction methods failed for {platform} engagement")
        return None
    
    def extract_complete_kpi_data(self, platform: str, url: str) -> Dict[str, Any]:
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
            # Extract followers count
            followers = self.extract_followers(platform, url)
            result["followers"] = followers
            
            # Extract engagement metrics
            engagement = self.extract_engagement(platform, url)
            if engagement:
                result.update(engagement)
            
            # Calculate engagement rate if possible
            if followers and engagement and "avg_likes" in engagement and "avg_comments" in engagement:
                total_engagement = engagement["avg_likes"] + engagement["avg_comments"]
                result["engagement_rate"] = round((total_engagement / followers) * 100, 2)
            
            result["success"] = followers is not None or engagement is not None
            
        except Exception as e:
            logger.error(f"Error extracting complete KPI data for {platform}: {str(e)}")
            result["error"] = str(e)
        
        return result
    
    def extract_multiple_platforms(self, urls: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """
        Extract KPI data for multiple platforms
        
        Args:
            urls: Dictionary with platform names as keys and URLs as values
            
        Returns:
            dict: Dictionary with platform names as keys and KPI data as values
        """
        logger.info(f"Starting extraction for multiple platforms: {', '.join(urls.keys())}")
        
        results = {}
        
        # Process platforms in sequence to avoid detection
        for platform, url in urls.items():
            if url:
                results[platform] = self.extract_complete_kpi_data(platform, url)
                
                # Add random delay between platforms to avoid detection
                if platform != list(urls.keys())[-1]:
                    delay = random.uniform(3, 8)
                    logger.info(f"Waiting {delay:.1f}s before processing next platform")
                    time.sleep(delay)
        
        return results
    
    def calculate_time_based_metrics(self, historical_data: List[Dict[str, Any]], days: int = 30) -> Dict[str, Any]:
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
            
            # Calculate post frequency (posts per week)
            time_span_seconds = sorted_data[-1]["timestamp"] - sorted_data[0]["timestamp"]
            time_span_weeks = time_span_seconds / (60 * 60 * 24 * 7)
            post_frequency = len(sorted_data) / time_span_weeks if time_span_weeks > 0 else 0
            
            # Calculate follower growth rate
            oldest_followers = sorted_data[0].get("followers", 0)
            newest_followers = sorted_data[-1].get("followers", 0)
            growth_rate = ((newest_followers - oldest_followers) / oldest_followers * 100) if oldest_followers > 0 else 0
            
            # Calculate engagement trend
            engagement_rates = [data.get("engagement_rate", 0) for data in sorted_data if "engagement_rate" in data]
            engagement_trend = self._calculate_trend(engagement_rates)
            
            return {
                "post_frequency": round(post_frequency, 1),
                "growth_rate": round(growth_rate, 1),
                "engagement_trend": engagement_trend,
                "has_time_data": True
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
    
    def _calculate_trend(self, values: List[float]) -> str:
        """
        Calculate trend direction from a series of values
        
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
        
        # Determine trend based on slope
        if slope > 0.05:
            return "increasing"
        elif slope < -0.05:
            return "decreasing"
        else:
            return "stable"
