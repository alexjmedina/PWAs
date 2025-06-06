"""
Instagram API Client Module - KPIs Social Extractor (API-First)

This module implements the Instagram-specific API client using the Instagram Graph API.
"""

import logging
import json
import sys
from typing import Dict, Any, Optional, List, Union

from app.api_clients.base_api_client import BaseAPIClient

# Configure logging
logger = logging.getLogger(__name__)

class InstagramAPIClient(BaseAPIClient):
    """
    Instagram-specific implementation of the BaseAPIClient
    """
    
    def __init__(self):
        """Initialize the Instagram API client"""
        super().__init__("instagram")
        self.api_version = "v18.0"  # Instagram Graph API uses Facebook's versioning
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
    
    async def get_user_profile(self, username_or_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile information from the Instagram Graph API
        
        Args:
            username_or_id: Instagram username or business account ID
            
        Returns:
            dict: User profile data or None if extraction fails
        """
        if not self.has_valid_credentials():
            logger.error("No valid Instagram API credentials available")
            return None
        
        # Instagram Graph API requires a business account ID
        # First, we need to resolve the username to an ID if necessary
        business_account_id = await self._resolve_business_account_id(username_or_id)
        if not business_account_id:
            logger.error(f"Could not resolve business account ID for {username_or_id}")
            return None
        
        # Define fields to retrieve
        fields = [
            "id", 
            "username", 
            "name", 
            "biography", 
            "followers_count", 
            "follows_count", 
            "media_count", 
            "profile_picture_url", 
            "website"
        ]
        
        # Make API request
        endpoint = f"{self.base_url}/{business_account_id}"
        params = {
            "fields": ",".join(fields),
            "access_token": self.get_api_credentials().get("access_token")
        }
        
        response = await self.make_api_request(
            endpoint=endpoint,
            params=params
        )
        
        if not response:
            logger.error(f"Failed to get Instagram profile for {username_or_id}")
            return None
        
        # Normalize the response
        return self._normalize_profile_response(response)
    
    async def get_followers_count(self, username_or_id: str) -> Optional[int]:
        """
        Get followers count from the Instagram Graph API
        
        Args:
            username_or_id: Instagram username or business account ID
            
        Returns:
            int: Number of followers or None if extraction fails
        """
        profile = await self.get_user_profile(username_or_id)
        if profile and "followers_count" in profile:
            return profile["followers_count"]
        return None
    
    async def get_engagement_metrics(self, username_or_id: str) -> Optional[Dict[str, Any]]:
        """
        Get engagement metrics from the Instagram Graph API
        
        Args:
            username_or_id: Instagram username or business account ID
            
        Returns:
            dict: Engagement metrics or None if extraction fails
        """
        if not self.has_valid_credentials():
            logger.error("No valid Instagram API credentials available")
            return None
        
        # Instagram Graph API requires a business account ID
        business_account_id = await self._resolve_business_account_id(username_or_id)
        if not business_account_id:
            logger.error(f"Could not resolve business account ID for {username_or_id}")
            return None
        
        # Get media to analyze engagement
        media = await self._get_recent_media(business_account_id)
        if not media:
            logger.error(f"Failed to get media for Instagram account {username_or_id}")
            return None
        
        # Calculate engagement metrics
        metrics = self._calculate_engagement_metrics(media)
        
        # Add follower count if available
        profile = await self.get_user_profile(business_account_id)
        if profile and "followers_count" in profile:
            metrics["followers"] = profile["followers_count"]
            
            # Calculate engagement rate if we have followers
            if metrics["followers"] > 0 and "avg_engagement" in metrics:
                metrics["engagement_rate"] = round((metrics["avg_engagement"] / metrics["followers"]) * 100, 2)
        
        return metrics
    
    async def _resolve_business_account_id(self, username_or_id: str) -> Optional[str]:
        """
        Resolve an Instagram username to a business account ID if necessary
        
        Args:
            username_or_id: Instagram username or business account ID
            
        Returns:
            str: Business account ID or None if resolution fails
        """
        # If it looks like an ID (numeric), use it directly
        if username_or_id.isdigit():
            return username_or_id
        
        # Instagram Graph API doesn't provide a direct way to look up a username
        # In a real implementation, you would need to use the Facebook Pages API
        # to find the Instagram Business Account ID associated with a Facebook Page
        
        # This is a simplified implementation - in a real application, you would need
        # to implement a more robust solution
        
        logger.warning(f"Instagram username resolution requires additional API calls")
        logger.warning(f"Using username as ID for demonstration purposes: {username_or_id}")
        
        # For demonstration purposes, we'll return the username
        # In a real implementation, this would be replaced with actual ID resolution
        return username_or_id
    
    async def _get_recent_media(self, business_account_id: str, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """
        Get recent media from an Instagram business account
        
        Args:
            business_account_id: Instagram business account ID
            limit: Maximum number of media items to retrieve
            
        Returns:
            list: List of media items or None if extraction fails
        """
        credentials = self.get_api_credentials()
        if not credentials.get("access_token"):
            logger.error("Instagram API requires an access token")
            return None
        
        # Define fields to retrieve for media
        fields = [
            "id", 
            "caption", 
            "media_type", 
            "media_url", 
            "permalink", 
            "thumbnail_url", 
            "timestamp", 
            "like_count", 
            "comments_count"
        ]
        
        # Make API request
        endpoint = f"{self.base_url}/{business_account_id}/media"
        params = {
            "fields": ",".join(fields),
            "limit": limit,
            "access_token": credentials["access_token"]
        }
        
        response = await self.make_api_request(
            endpoint=endpoint,
            params=params
        )
        
        if not response or "data" not in response:
            logger.error(f"Failed to get media for Instagram account {business_account_id}")
            return None
        
        return response["data"]
    
    def _normalize_profile_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize the Instagram Graph API profile response
        
        Args:
            response: Raw API response
            
        Returns:
            dict: Normalized profile data
        """
        normalized = {
            "id": response.get("id"),
            "username": response.get("username"),
            "name": response.get("name"),
            "biography": response.get("biography"),
            "followers_count": response.get("followers_count"),
            "following_count": response.get("follows_count"),
            "media_count": response.get("media_count"),
            "profile_picture_url": response.get("profile_picture_url"),
            "website": response.get("website")
        }
        
        return normalized
    
    def _calculate_engagement_metrics(self, media: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate engagement metrics from a list of media items
        
        Args:
            media: List of media data from the API
            
        Returns:
            dict: Calculated engagement metrics
        """
        if not media:
            return {
                "posts": 0,
                "avg_likes": 0,
                "avg_comments": 0,
                "avg_engagement": 0
            }
        
        total_likes = 0
        total_comments = 0
        media_count = len(media)
        
        for item in media:
            # Extract likes
            total_likes += item.get("like_count", 0)
            
            # Extract comments
            total_comments += item.get("comments_count", 0)
        
        # Calculate averages
        avg_likes = round(total_likes / media_count) if media_count > 0 else 0
        avg_comments = round(total_comments / media_count) if media_count > 0 else 0
        avg_engagement = avg_likes + avg_comments
        
        return {
            "posts": media_count,
            "avg_likes": avg_likes,
            "avg_comments": avg_comments,
            "avg_engagement": avg_engagement,
            "total_likes": total_likes,
            "total_comments": total_comments
        }
