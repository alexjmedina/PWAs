"""
Twitter API Client Module - KPIs Social Extractor (API-First)

This module implements the Twitter-specific API client using the Twitter API v2
and the datasource module integration.
"""

import logging
import json
import sys
from typing import Dict, Any, Optional, List, Union

from app.api_clients.base_api_client import BaseAPIClient

# Configure logging
logger = logging.getLogger(__name__)

class TwitterAPIClient(BaseAPIClient):
    """
    Twitter-specific implementation of the BaseAPIClient
    """
    
    def __init__(self):
        """Initialize the Twitter API client"""
        super().__init__("twitter")
        self.use_datasource = True
    
    async def get_user_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile information from the Twitter API
        
        Args:
            username: Twitter username (without @)
            
        Returns:
            dict: User profile data or None if extraction fails
        """
        # Try using datasource module first
        if self.use_datasource:
            try:
                profile_data = await self._get_profile_via_datasource(username)
                if profile_data:
                    return profile_data
            except Exception as e:
                logger.error(f"Error using datasource for Twitter profile: {str(e)}")
                # Fall back to direct API
        
        # Fall back to direct API if datasource fails or is disabled
        if self.has_valid_credentials():
            return await self._get_profile_via_direct_api(username)
        
        logger.error("No valid method available for Twitter profile extraction")
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
        
        # Extract available engagement metrics from profile
        metrics = {}
        
        # Basic metrics
        if "followers_count" in profile:
            metrics["followers"] = profile["followers_count"]
        
        if "friends_count" in profile:
            metrics["following"] = profile["friends_count"]
        
        if "statuses_count" in profile:
            metrics["tweets"] = profile["statuses_count"]
        
        if "favourites_count" in profile:
            metrics["likes"] = profile["favourites_count"]
        
        if "listed_count" in profile:
            metrics["lists"] = profile["listed_count"]
        
        # Calculate engagement rate if possible
        if "followers_count" in profile and profile["followers_count"] > 0:
            # Simple engagement rate calculation
            engagement_sum = 0
            if "favourites_count" in profile:
                engagement_sum += profile["favourites_count"]
            
            if engagement_sum > 0:
                metrics["engagement_rate"] = round((engagement_sum / profile["followers_count"]) * 100, 2)
        
        return metrics
    
    async def _get_profile_via_datasource(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get Twitter profile using the datasource module
        
        Args:
            username: Twitter username (without @)
            
        Returns:
            dict: Normalized profile data or None if extraction fails
        """
        try:
            # Add path to datasource runtime
            sys.path.append('/opt/.manus/.sandbox-runtime')
            from data_api import ApiClient
            
            # Initialize API client
            client = ApiClient()
            
            # Call Twitter API endpoint
            response = client.call_api('Twitter/get_user_profile_by_username', query={'username': username})
            
            if not response or not isinstance(response, dict):
                logger.error(f"Invalid response from Twitter datasource API for {username}")
                return None
            
            # Extract and normalize the data
            return self._normalize_datasource_response(response)
            
        except ImportError:
            logger.error("Could not import datasource API client")
            return None
        except Exception as e:
            logger.error(f"Error calling Twitter datasource API: {str(e)}")
            return None
    
    async def _get_profile_via_direct_api(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get Twitter profile using direct API call
        
        Args:
            username: Twitter username (without @)
            
        Returns:
            dict: Normalized profile data or None if extraction fails
        """
        credentials = self.get_api_credentials()
        
        # Check for bearer token (preferred for v2 API)
        if "bearer_token" not in credentials:
            logger.error("Twitter API requires a bearer token")
            return None
        
        # Set up headers with bearer token
        headers = {
            "Authorization": f"Bearer {credentials['bearer_token']}",
            "Content-Type": "application/json"
        }
        
        # Twitter API v2 endpoint for user lookup by username
        endpoint = f"https://api.twitter.com/2/users/by/username/{username}"
        
        # Parameters to include additional user fields
        params = {
            "user.fields": "public_metrics,description,created_at,profile_image_url,verified"
        }
        
        # Make API request
        response = await self.make_api_request(
            endpoint=endpoint,
            params=params,
            headers=headers
        )
        
        if not response or "data" not in response:
            logger.error(f"Failed to get Twitter profile for {username}")
            return None
        
        # Extract and normalize the data
        return self._normalize_direct_api_response(response)
    
    def _normalize_datasource_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize the datasource API response to a standard format
        
        Args:
            response: Raw datasource API response
            
        Returns:
            dict: Normalized profile data
        """
        try:
            # Navigate through the response structure
            if "result" in response and "data" in response["result"] and "user" in response["result"]["data"]:
                user_data = response["result"]["data"]["user"]["result"]
                
                if "legacy" not in user_data:
                    logger.error("Missing legacy data in Twitter response")
                    return None
                
                legacy = user_data["legacy"]
                
                # Extract relevant fields
                normalized = {
                    "id": user_data.get("rest_id"),
                    "username": legacy.get("screen_name"),
                    "name": legacy.get("name"),
                    "description": legacy.get("description"),
                    "followers_count": legacy.get("followers_count"),
                    "friends_count": legacy.get("friends_count"),
                    "statuses_count": legacy.get("statuses_count"),
                    "favourites_count": legacy.get("favourites_count"),
                    "listed_count": legacy.get("listed_count"),
                    "created_at": legacy.get("created_at"),
                    "verified": legacy.get("verified") or user_data.get("is_blue_verified", False),
                    "profile_image_url": legacy.get("profile_image_url_https"),
                    "location": legacy.get("location")
                }
                
                return normalized
            
            logger.error("Unexpected Twitter datasource response structure")
            return None
            
        except Exception as e:
            logger.error(f"Error normalizing Twitter datasource response: {str(e)}")
            return None
    
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
            
            # Extract relevant fields
            normalized = {
                "id": user_data.get("id"),
                "username": user_data.get("username"),
                "name": user_data.get("name"),
                "description": user_data.get("description"),
                "followers_count": public_metrics.get("followers_count"),
                "friends_count": public_metrics.get("following_count"),
                "statuses_count": public_metrics.get("tweet_count"),
                "created_at": user_data.get("created_at"),
                "verified": user_data.get("verified"),
                "profile_image_url": user_data.get("profile_image_url"),
                "location": user_data.get("location")
            }
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing Twitter direct API response: {str(e)}")
            return None
