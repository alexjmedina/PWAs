import logging
import tweepy
from typing import Dict, Any, Optional

from .base_extractor import BaseExtractor

logger = logging.getLogger(__name__)

class TwitterExtractor(BaseExtractor):
    def __init__(self):
        super().__init__()
        self.api_client = None
        # Assumes TWITTER_API_KEY in .env is the Bearer Token
        bearer_token = self.config.TWITTER_API_KEY
        if bearer_token:
            try:
                self.api_client = tweepy.Client(bearer_token, wait_on_rate_limit=True)
                logger.info("Twitter API client initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize Twitter client: {e}")

    def _extract_username_from_url(self, url: str) -> Optional[str]:
        try:
            return url.strip().split('?')[0].split('/')[-1]
        except IndexError:
            return None

    def extract_followers(self, url: str) -> Optional[int]:
        if not self.api_client:
            logger.warning("Twitter API client not available.")
            return None
        
        username = self._extract_username_from_url(url)
        if not username:
            return None
            
        try:
            response = self.api_client.get_user(username=username, user_fields=["public_metrics"])
            if response.data:
                return response.data.public_metrics.get('followers_count')
        except tweepy.errors.TweepyException as e:
            logger.error(f"Twitter API error for followers: {e}")
        return None

    def extract_engagement(self, url: str) -> Optional[Dict[str, Any]]:
        logger.warning("Twitter engagement extraction not fully implemented in this version.")
        return None