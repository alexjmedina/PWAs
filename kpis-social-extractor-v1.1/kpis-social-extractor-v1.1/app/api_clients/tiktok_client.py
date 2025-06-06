"""
TikTok API Client Module - KPIs Social Extractor (API-First)

This module implements the TikTok-specific API client using the TikTok API.
"""

import logging
import json
import sys
from typing import Dict, Any, Optional, List, Union

from app.api_clients.base_api_client import BaseAPIClient

# Configure logging
logger = logging.getLogger(__name__)

class TikTokAPIClient(BaseAPIClient):
    """
    TikTok-specific implementation of the BaseAPIClient
    """
    
    def __init__(self):
        """Initialize the TikTok API client"""
        super().__init__("tiktok")
        self.base_url = "https://open-api.tiktok.com/api"
    
    async def get_user_profile(self, username_or_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile information from the TikTok API
        
        Args:
            username_or_id: TikTok username or user ID
            
        Returns:
            dict: User profile data or None if extraction fails
        """
        if not self.has_valid_credentials():
            logger.error("No valid TikTok API credentials available")
            return None
        
        # TikTok API requires a user ID
        # First, we need to resolve the username to an ID if necessary
        user_id = await self._resolve_user_id(username_or_id)
        if not user_id:
            logger.error(f"Could not resolve user ID for {username_or_id}")
            return None
        
        # Make API request
        endpoint = f"{self.base_url}/user/info/"
        
        credentials = self.get_api_credentials()
        params = {
            "open_id": user_id,
            "access_token": credentials.get("access_token")
        }
        
        response = await self.make_api_request(
            endpoint=endpoint,
            params=params
        )
        
        if not response or "data" not in response:
            logger.error(f"Failed to get TikTok profile for {username_or_id}")
            return None
        
        # Normalize the response
        return self._normalize_profile_response(response["data"])
    
    async def get_followers_count(self, username_or_id: str) -> Optional[int]:
        """
        Get followers count from the TikTok API
        
        Args:
            username_or_id: TikTok username or user ID
            
        Returns:
            int: Number of followers or None if extraction fails
        """
        profile = await self.get_user_profile(username_or_id)
        if profile and "follower_count" in profile:
            return profile["follower_count"]
        return None
    
    async def get_engagement_metrics(self, username_or_id: str) -> Optional[Dict[str, Any]]:
        """
        Get engagement metrics from the TikTok API
        
        Args:
            username_or_id: TikTok username or user ID
            
        Returns:
            dict: Engagement metrics or None if extraction fails
        """
        if not self.has_valid_credentials():
            logger.error("No valid TikTok API credentials available")
            return None
        
        # TikTok API requires a user ID
        user_id = await self._resolve_user_id(username_or_id)
        if not user_id:
            logger.error(f"Could not resolve user ID for {username_or_id}")
            return None
        
        # Get videos to analyze engagement
        videos = await self._get_recent_videos(user_id)
        if not videos:
            logger.error(f"Failed to get videos for TikTok user {username_or_id}")
            return None
        
        # Calculate engagement metrics
        metrics = self._calculate_engagement_metrics(videos)
        
        # Add follower count if available
        profile = await self.get_user_profile(user_id)
        if profile and "follower_count" in profile:
            metrics["followers"] = profile["follower_count"]
            
            # Calculate engagement rate if we have followers
            if metrics["followers"] > 0 and "avg_engagement" in metrics:
                metrics["engagement_rate"] = round((metrics["avg_engagement"] / metrics["followers"]) * 100, 2)
        
        return metrics
    
    async def _resolve_user_id(self, username_or_id: str) -> Optional[str]:
        """
        Resolve a TikTok username to a user ID if necessary
        
        Args:
            username_or_id: TikTok username or user ID
            
        Returns:
            str: User ID or None if resolution fails
        """
        # If it looks like an ID (numeric), use it directly
        if username_or_id.isdigit():
            return username_or_id
        
        # TikTok API doesn't provide a direct way to look up a username
        # In a real implementation, you would need to use the search API
        # or other methods to find the user ID
        
        # This is a simplified implementation - in a real application, you would need
        # to implement a more robust solution
        
        logger.warning(f"TikTok username resolution requires additional API calls")
        logger.warning(f"Using username as ID for demonstration purposes: {username_or_id}")
        
        # For demonstration purposes, we'll return the username
        # In a real implementation, this would be replaced with actual ID resolution
        return username_or_id
    
    async def _get_recent_videos(self, user_id: str, max_count: int = 10) -> Optional[List[Dict[str, Any]]]:
        """
        Get recent videos from a TikTok user
        
        Args:
            user_id: TikTok user ID
            max_count: Maximum number of videos to retrieve
            
        Returns:
            list: List of videos or None if extraction fails
        """
        credentials = self.get_api_credentials()
        if not credentials.get("access_token"):
            logger.error("TikTok API requires an access token")
            return None
        
        # Make API request
        endpoint = f"{self.base_url}/video/list/"
        params = {
            "open_id": user_id,
            "access_token": credentials.get("access_token"),
            "cursor": 0,
            "max_count": max_count
        }
        
        response = await self.make_api_request(
            endpoint=endpoint,
            params=params
        )
        
        if not response or "data" not in response or "videos" not in response["data"]:
            logger.error(f"Failed to get videos for TikTok user {user_id}")
            return None
        
        return response["data"]["videos"]
    
    def _normalize_profile_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize the TikTok API profile response
        
        Args:
            response: Raw API response
            
        Returns:
            dict: Normalized profile data
        """
        normalized = {
            "id": response.get("open_id"),
            "username": response.get("display_name"),
            "nickname": response.get("nickname"),
            "avatar_url": response.get("avatar_url"),
            "bio": response.get("bio_description"),
            "follower_count": response.get("follower_count"),
            "following_count": response.get("following_count"),
            "video_count": response.get("video_count"),
            "like_count": response.get("like_count"),
            "profile_deep_link": response.get("profile_deep_link")
        }
        
        return normalized
    
    def _calculate_engagement_metrics(self, videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate engagement metrics from a list of videos
        
        Args:
            videos: List of video data from the API
            
        Returns:
            dict: Calculated engagement metrics
        """
        if not videos:
            return {
                "videos": 0,
                "avg_views": 0,
                "avg_likes": 0,
                "avg_comments": 0,
                "avg_shares": 0,
                "avg_engagement": 0
            }
        
        total_views = 0
        total_likes = 0
        total_comments = 0
        total_shares = 0
        video_count = len(videos)
        
        for video in videos:
            # Extract statistics
            statistics = video.get("statistics", {})
            
            # Extract views
            total_views += int(statistics.get("view_count", 0))
            
            # Extract likes
            total_likes += int(statistics.get("like_count", 0))
            
            # Extract comments
            total_comments += int(statistics.get("comment_count", 0))
            
            # Extract shares
            total_shares += int(statistics.get("share_count", 0))
        
        # Calculate averages
        avg_views = round(total_views / video_count) if video_count > 0 else 0
        avg_likes = round(total_likes / video_count) if video_count > 0 else 0
        avg_comments = round(total_comments / video_count) if video_count > 0 else 0
        avg_shares = round(total_shares / video_count) if video_count > 0 else 0
        avg_engagement = avg_likes + avg_comments + avg_shares
        
        return {
            "videos": video_count,
            "avg_views": avg_views,
            "avg_likes": avg_likes,
            "avg_comments": avg_comments,
            "avg_shares": avg_shares,
            "avg_engagement": avg_engagement,
            "total_views": total_views,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_shares": total_shares
        }
