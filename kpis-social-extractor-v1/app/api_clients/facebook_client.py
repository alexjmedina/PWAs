"""
Facebook API Client Module - KPIs Social Extractor (API-First)

This module implements the Facebook-specific API client using the Facebook Graph API.
"""

import logging
import json
import sys
from typing import Dict, Any, Optional, List, Union

from app.api_clients.base_api_client import BaseAPIClient

# Configure logging
logger = logging.getLogger(__name__)

class FacebookAPIClient(BaseAPIClient):
    """
    Facebook-specific implementation of the BaseAPIClient
    """
    
    def __init__(self):
        """Initialize the Facebook API client"""
        super().__init__("facebook")
        self.api_version = "v18.0"  # Facebook Graph API version
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
    
    async def get_user_profile(self, page_id_or_username: str) -> Optional[Dict[str, Any]]:
        """
        Get page profile information from the Facebook Graph API
        
        Args:
            page_id_or_username: Facebook page ID or username
            
        Returns:
            dict: Page profile data or None if extraction fails
        """
        if not self.has_valid_credentials():
            logger.error("No valid Facebook API credentials available")
            return None
        
        # Extract page ID if username is provided
        page_id = await self._resolve_page_id(page_id_or_username)
        if not page_id:
            logger.error(f"Could not resolve page ID for {page_id_or_username}")
            return None
        
        # Define fields to retrieve
        fields = [
            "id", 
            "name", 
            "username", 
            "about", 
            "category", 
            "fan_count", 
            "followers_count", 
            "verification_status", 
            "website", 
            "picture", 
            "cover"
        ]
        
        # Make API request
        endpoint = f"{self.base_url}/{page_id}"
        params = {
            "fields": ",".join(fields),
            "access_token": self.get_api_credentials().get("access_token")
        }
        
        response = await self.make_api_request(
            endpoint=endpoint,
            params=params
        )
        
        if not response:
            logger.error(f"Failed to get Facebook page profile for {page_id_or_username}")
            return None
        
        # Normalize the response
        return self._normalize_profile_response(response)
    
    async def get_followers_count(self, page_id_or_username: str) -> Optional[int]:
        """
        Get followers count from the Facebook Graph API
        
        Args:
            page_id_or_username: Facebook page ID or username
            
        Returns:
            int: Number of followers or None if extraction fails
        """
        profile = await self.get_user_profile(page_id_or_username)
        if profile and "followers_count" in profile:
            return profile["followers_count"]
        return None
    
    async def get_engagement_metrics(self, page_id_or_username: str) -> Optional[Dict[str, Any]]:
        """
        Get engagement metrics from the Facebook Graph API
        
        Args:
            page_id_or_username: Facebook page ID or username
            
        Returns:
            dict: Engagement metrics or None if extraction fails
        """
        if not self.has_valid_credentials():
            logger.error("No valid Facebook API credentials available")
            return None
        
        # Extract page ID if username is provided
        page_id = await self._resolve_page_id(page_id_or_username)
        if not page_id:
            logger.error(f"Could not resolve page ID for {page_id_or_username}")
            return None
        
        # Get posts to analyze engagement
        posts = await self._get_recent_posts(page_id)
        if not posts:
            logger.error(f"Failed to get posts for Facebook page {page_id_or_username}")
            return None
        
        # Calculate engagement metrics
        metrics = self._calculate_engagement_metrics(posts)
        
        # Add follower count if available
        profile = await self.get_user_profile(page_id)
        if profile and "followers_count" in profile:
            metrics["followers"] = profile["followers_count"]
            
            # Calculate engagement rate if we have followers
            if metrics["followers"] > 0 and "avg_engagement" in metrics:
                metrics["engagement_rate"] = round((metrics["avg_engagement"] / metrics["followers"]) * 100, 2)
        
        return metrics
    
    async def _resolve_page_id(self, page_id_or_username: str) -> Optional[str]:
        """
        Resolve a page username to its ID if necessary
        
        Args:
            page_id_or_username: Facebook page ID or username
            
        Returns:
            str: Page ID or None if resolution fails
        """
        # If it looks like an ID (numeric), use it directly
        if page_id_or_username.isdigit():
            return page_id_or_username
        
        # Otherwise, try to resolve the username
        credentials = self.get_api_credentials()
        if not credentials.get("access_token"):
            logger.error("Facebook API requires an access token")
            return None
        
        # Try to look up the page by username
        endpoint = f"{self.base_url}/{page_id_or_username}"
        params = {
            "fields": "id",
            "access_token": credentials["access_token"]
        }
        
        response = await self.make_api_request(
            endpoint=endpoint,
            params=params
        )
        
        if response and "id" in response:
            return response["id"]
        
        logger.error(f"Could not resolve Facebook page ID for {page_id_or_username}")
        return None
    
    async def _get_recent_posts(self, page_id: str, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """
        Get recent posts from a Facebook page
        
        Args:
            page_id: Facebook page ID
            limit: Maximum number of posts to retrieve
            
        Returns:
            list: List of posts or None if extraction fails
        """
        credentials = self.get_api_credentials()
        if not credentials.get("access_token"):
            logger.error("Facebook API requires an access token")
            return None
        
        # Define fields to retrieve for posts
        fields = [
            "id", 
            "message", 
            "created_time", 
            "likes.summary(true)", 
            "comments.summary(true)", 
            "shares"
        ]
        
        # Make API request
        endpoint = f"{self.base_url}/{page_id}/posts"
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
            logger.error(f"Failed to get posts for Facebook page {page_id}")
            return None
        
        return response["data"]
    
    def _normalize_profile_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize the Facebook Graph API profile response
        
        Args:
            response: Raw API response
            
        Returns:
            dict: Normalized profile data
        """
        normalized = {
            "id": response.get("id"),
            "name": response.get("name"),
            "username": response.get("username"),
            "about": response.get("about"),
            "category": response.get("category"),
            "followers_count": response.get("followers_count") or response.get("fan_count"),
            "fan_count": response.get("fan_count"),
            "verified": response.get("verification_status") == "verified",
            "website": response.get("website")
        }
        
        # Extract profile picture URL if available
        if "picture" in response and "data" in response["picture"]:
            normalized["profile_picture_url"] = response["picture"]["data"].get("url")
        
        # Extract cover photo URL if available
        if "cover" in response:
            normalized["cover_photo_url"] = response["cover"].get("source")
        
        return normalized
    
    def _calculate_engagement_metrics(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate engagement metrics from a list of posts
        
        Args:
            posts: List of post data from the API
            
        Returns:
            dict: Calculated engagement metrics
        """
        if not posts:
            return {
                "posts": 0,
                "avg_likes": 0,
                "avg_comments": 0,
                "avg_shares": 0,
                "avg_engagement": 0
            }
        
        total_likes = 0
        total_comments = 0
        total_shares = 0
        post_count = len(posts)
        
        for post in posts:
            # Extract likes
            if "likes" in post and "summary" in post["likes"]:
                total_likes += post["likes"]["summary"].get("total_count", 0)
            
            # Extract comments
            if "comments" in post and "summary" in post["comments"]:
                total_comments += post["comments"]["summary"].get("total_count", 0)
            
            # Extract shares
            if "shares" in post:
                total_shares += post["shares"].get("count", 0)
        
        # Calculate averages
        avg_likes = round(total_likes / post_count) if post_count > 0 else 0
        avg_comments = round(total_comments / post_count) if post_count > 0 else 0
        avg_shares = round(total_shares / post_count) if post_count > 0 else 0
        avg_engagement = avg_likes + avg_comments + avg_shares
        
        return {
            "posts": post_count,
            "avg_likes": avg_likes,
            "avg_comments": avg_comments,
            "avg_shares": avg_shares,
            "avg_engagement": avg_engagement,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_shares": total_shares
        }
