# kpis-social-extractor-v1.1/app/api_clients/twitter_client.py

"""
Twitter API Client Module - KPIs Social Extractor (API-First)

This module implements the Twitter-specific API client using the Twitter API v2.
"""

import logging
from typing import Dict, Any, Optional

from app.api_clients.base_api_client import BaseAPIClient

# Configure logging
logger = logging.getLogger(__name__)

class TwitterAPIClient(BaseAPIClient):
    """
    Twitter-specific implementation of the BaseAPIClient that relies on direct API calls.
    """
    
    def __init__(self):
        """Initialize the Twitter API client"""
        super().__init__("twitter")
    
    async def get_user_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile information from the Twitter API
        
        Args:
            username: Twitter username (without @)
            
        Returns:
            dict: User profile data or None if extraction fails
        """
        if self.has_valid_credentials():
            return await self._get_profile_via_direct_api(username)
        
        logger.error("No valid method available for Twitter profile extraction. Please provide a Bearer Token in your .env file.")
        return None
    
    async def get_followers_count(self, username: str) -> Optional[int]:
        """
        Get followers count from the Twitter API
        
        Args:
            username: Twitter username (without @)
            
        Returns:
            int: Number of followers or None if extraction fails
        """
        profile = await self.get_user_profile(username)
        if profile and "followers_count" in profile:
            return profile["followers_count"]
        return None
    
    async def get_engagement_metrics(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get engagement metrics from the Twitter API
        
        Args:
            username: Twitter username (without @)
            
        Returns:
            dict: Engagement metrics or None if extraction fails
        """
        profile = await self.get_user_profile(username)
        if not profile:
            return None
        
        # This is a simplified engagement calculation based on public profile metrics.
        # A more detailed analysis would require fetching recent tweets.
        metrics = {
            "followers": profile.get("followers_count"),
            "following": profile.get("friends_count"),
            "tweets": profile.get("statuses_count"),
            "likes": profile.get("favourites_count"),
            "lists": profile.get("listed_count"),
            "engagement_rate": 0
        }
        
        if profile.get("followers_count", 0) > 0 and profile.get("favourites_count") is not None:
             metrics["engagement_rate"] = round((profile["favourites_count"] / profile["followers_count"]) * 100, 2)
        
        return metrics
    
    async def _get_profile_via_direct_api(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get Twitter profile using direct API call (Twitter API v2)
        
        Args:
            username: Twitter username (without @)
            
        Returns:
            dict: Normalized profile data or None if extraction fails
        """
        credentials = self.get_api_credentials()
        
        if "bearer_token" not in credentials:
            logger.error("Twitter API v2 requires a BEARER_TOKEN in your .env file.")
            return None
        
        headers = {
            "Authorization": f"Bearer {credentials['bearer_token']}",
        }
        
        endpoint = f"https://api.twitter.com/2/users/by/username/{username}"
        params = {
            "user.fields": "public_metrics,description,created_at,profile_image_url,verified"
        }
        
        response = await self.make_api_request(
            endpoint=endpoint,
            params=params,
            headers=headers
        )
        
        if not response or "data" not in response:
            logger.error(f"Failed to get Twitter profile for {username} via API v2.")
            return None
            
        return self._normalize_direct_api_response(response)

    def _normalize_direct_api_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize the direct API response to a standard format
        
        Args:
            response: Raw direct API response
            
        Returns:
            dict: Normalized profile data
        """
        try:
            user_data = response["data"]
            public_metrics = user_data.get("public_metrics", {})
            
            normalized = {
                "id": user_data.get("id"),
                "username": user_data.get("username"),
                "name": user_data.get("name"),
                "description": user_data.get("description"),
                "followers_count": public_metrics.get("followers_count"),
                "friends_count": public_metrics.get("following_count"),
                "statuses_count": public_metrics.get("tweet_count"),
                "listed_count": public_metrics.get("listed_count"),
                "created_at": user_data.get("created_at"),
                "verified": user_data.get("verified"),
                "profile_image_url": user_data.get("profile_image_url"),
            }
            # Note: The v2 API does not provide 'favourites_count' (total likes given by the user) directly in the user object.
            # This would require additional API calls to the user's liked tweets timeline.
            # We will omit it here for simplicity.
            normalized["favourites_count"] = None
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing Twitter direct API response: {str(e)}")
            return None