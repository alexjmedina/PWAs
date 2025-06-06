"""
YouTube API Client Module - KPIs Social Extractor (API-First)

This module implements the YouTube-specific API client using the YouTube Data API.
"""

import logging
import json
import sys
from typing import Dict, Any, Optional, List, Union

from app.api_clients.base_api_client import BaseAPIClient

# Configure logging
logger = logging.getLogger(__name__)

class YouTubeAPIClient(BaseAPIClient):
    """
    YouTube-specific implementation of the BaseAPIClient
    """
    
    def __init__(self):
        """Initialize the YouTube API client"""
        super().__init__("youtube")
        self.base_url = "https://www.googleapis.com/youtube/v3"
    
    async def get_user_profile(self, channel_id_or_username: str) -> Optional[Dict[str, Any]]:
        """
        Get channel information from the YouTube Data API
        
        Args:
            channel_id_or_username: YouTube channel ID or username
            
        Returns:
            dict: Channel profile data or None if extraction fails
        """
        if not self.has_valid_credentials():
            logger.error("No valid YouTube API credentials available")
            return None
        
        # Resolve channel ID if username is provided
        channel_id = await self._resolve_channel_id(channel_id_or_username)
        if not channel_id:
            logger.error(f"Could not resolve channel ID for {channel_id_or_username}")
            return None
        
        # Make API request to get channel details
        endpoint = f"{self.base_url}/channels"
        params = {
            "part": "snippet,statistics,brandingSettings",
            "id": channel_id,
            "key": self.get_api_credentials().get("api_key")
        }
        
        response = await self.make_api_request(
            endpoint=endpoint,
            params=params
        )
        
        if not response or "items" not in response or not response["items"]:
            logger.error(f"Failed to get YouTube channel profile for {channel_id_or_username}")
            return None
        
        # Normalize the response
        return self._normalize_profile_response(response["items"][0])
    
    async def get_followers_count(self, channel_id_or_username: str) -> Optional[int]:
        """
        Get subscribers count from the YouTube Data API
        
        Args:
            channel_id_or_username: YouTube channel ID or username
            
        Returns:
            int: Number of subscribers or None if extraction fails
        """
        profile = await self.get_user_profile(channel_id_or_username)
        if profile and "subscriber_count" in profile:
            return profile["subscriber_count"]
        return None
    
    async def get_engagement_metrics(self, channel_id_or_username: str) -> Optional[Dict[str, Any]]:
        """
        Get engagement metrics from the YouTube Data API
        
        Args:
            channel_id_or_username: YouTube channel ID or username
            
        Returns:
            dict: Engagement metrics or None if extraction fails
        """
        if not self.has_valid_credentials():
            logger.error("No valid YouTube API credentials available")
            return None
        
        # Resolve channel ID if username is provided
        channel_id = await self._resolve_channel_id(channel_id_or_username)
        if not channel_id:
            logger.error(f"Could not resolve channel ID for {channel_id_or_username}")
            return None
        
        # Get videos to analyze engagement
        videos = await self._get_recent_videos(channel_id)
        if not videos:
            logger.error(f"Failed to get videos for YouTube channel {channel_id_or_username}")
            return None
        
        # Calculate engagement metrics
        metrics = self._calculate_engagement_metrics(videos)
        
        # Add subscriber count if available
        profile = await self.get_user_profile(channel_id)
        if profile and "subscriber_count" in profile:
            metrics["subscribers"] = profile["subscriber_count"]
            
            # Calculate engagement rate if we have subscribers
            if metrics["subscribers"] > 0 and "avg_engagement" in metrics:
                metrics["engagement_rate"] = round((metrics["avg_engagement"] / metrics["subscribers"]) * 100, 2)
        
        return metrics
    
    async def _resolve_channel_id(self, channel_id_or_username: str) -> Optional[str]:
        """
        Resolve a YouTube username or custom URL to a channel ID
        
        Args:
            channel_id_or_username: YouTube channel ID or username
            
        Returns:
            str: Channel ID or None if resolution fails
        """
        # If it looks like a channel ID (starts with UC), use it directly
        if channel_id_or_username.startswith("UC"):
            return channel_id_or_username
        
        # Otherwise, try to resolve the username or custom URL
        credentials = self.get_api_credentials()
        if not credentials.get("api_key"):
            logger.error("YouTube API requires an API key")
            return None
        
        # Try to look up the channel by username
        endpoint = f"{self.base_url}/channels"
        params = {
            "part": "id",
            "forUsername": channel_id_or_username,
            "key": credentials["api_key"]
        }
        
        response = await self.make_api_request(
            endpoint=endpoint,
            params=params
        )
        
        if response and "items" in response and response["items"]:
            return response["items"][0]["id"]
        
        # If username lookup fails, try search as a fallback
        endpoint = f"{self.base_url}/search"
        params = {
            "part": "snippet",
            "q": channel_id_or_username,
            "type": "channel",
            "maxResults": 1,
            "key": credentials["api_key"]
        }
        
        response = await self.make_api_request(
            endpoint=endpoint,
            params=params
        )
        
        if response and "items" in response and response["items"]:
            return response["items"][0]["snippet"]["channelId"]
        
        logger.error(f"Could not resolve YouTube channel ID for {channel_id_or_username}")
        return None
    
    async def _get_recent_videos(self, channel_id: str, max_results: int = 10) -> Optional[List[Dict[str, Any]]]:
        """
        Get recent videos from a YouTube channel
        
        Args:
            channel_id: YouTube channel ID
            max_results: Maximum number of videos to retrieve
            
        Returns:
            list: List of videos or None if extraction fails
        """
        credentials = self.get_api_credentials()
        if not credentials.get("api_key"):
            logger.error("YouTube API requires an API key")
            return None
        
        # First, get the uploads playlist ID
        endpoint = f"{self.base_url}/channels"
        params = {
            "part": "contentDetails",
            "id": channel_id,
            "key": credentials["api_key"]
        }
        
        response = await self.make_api_request(
            endpoint=endpoint,
            params=params
        )
        
        if not response or "items" not in response or not response["items"]:
            logger.error(f"Failed to get uploads playlist for YouTube channel {channel_id}")
            return None
        
        uploads_playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        
        # Now get the videos from the uploads playlist
        endpoint = f"{self.base_url}/playlistItems"
        params = {
            "part": "snippet,contentDetails",
            "playlistId": uploads_playlist_id,
            "maxResults": max_results,
            "key": credentials["api_key"]
        }
        
        response = await self.make_api_request(
            endpoint=endpoint,
            params=params
        )
        
        if not response or "items" not in response:
            logger.error(f"Failed to get videos for YouTube channel {channel_id}")
            return None
        
        # Extract video IDs
        video_ids = [item["contentDetails"]["videoId"] for item in response["items"]]
        
        # Get video statistics
        endpoint = f"{self.base_url}/videos"
        params = {
            "part": "statistics",
            "id": ",".join(video_ids),
            "key": credentials["api_key"]
        }
        
        response = await self.make_api_request(
            endpoint=endpoint,
            params=params
        )
        
        if not response or "items" not in response:
            logger.error(f"Failed to get video statistics for YouTube channel {channel_id}")
            return None
        
        return response["items"]
    
    def _normalize_profile_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize the YouTube Data API channel response
        
        Args:
            response: Raw API response
            
        Returns:
            dict: Normalized profile data
        """
        snippet = response.get("snippet", {})
        statistics = response.get("statistics", {})
        branding = response.get("brandingSettings", {}).get("channel", {})
        
        normalized = {
            "id": response.get("id"),
            "title": snippet.get("title"),
            "description": snippet.get("description"),
            "custom_url": snippet.get("customUrl"),
            "published_at": snippet.get("publishedAt"),
            "country": snippet.get("country"),
            "subscriber_count": int(statistics.get("subscriberCount", 0)) if statistics.get("hiddenSubscriberCount") != True else None,
            "video_count": int(statistics.get("videoCount", 0)),
            "view_count": int(statistics.get("viewCount", 0)),
            "hidden_subscriber_count": statistics.get("hiddenSubscriberCount", False),
            "keywords": branding.get("keywords"),
            "banner_image_url": branding.get("image", {}).get("bannerImageUrl")
        }
        
        # Extract thumbnail URLs
        if "thumbnails" in snippet:
            thumbnails = snippet["thumbnails"]
            if "high" in thumbnails:
                normalized["profile_picture_url"] = thumbnails["high"].get("url")
            elif "medium" in thumbnails:
                normalized["profile_picture_url"] = thumbnails["medium"].get("url")
            elif "default" in thumbnails:
                normalized["profile_picture_url"] = thumbnails["default"].get("url")
        
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
                "avg_engagement": 0
            }
        
        total_views = 0
        total_likes = 0
        total_comments = 0
        video_count = len(videos)
        
        for video in videos:
            statistics = video.get("statistics", {})
            
            # Extract views
            total_views += int(statistics.get("viewCount", 0))
            
            # Extract likes
            total_likes += int(statistics.get("likeCount", 0))
            
            # Extract comments
            total_comments += int(statistics.get("commentCount", 0))
        
        # Calculate averages
        avg_views = round(total_views / video_count) if video_count > 0 else 0
        avg_likes = round(total_likes / video_count) if video_count > 0 else 0
        avg_comments = round(total_comments / video_count) if video_count > 0 else 0
        avg_engagement = avg_likes + avg_comments
        
        return {
            "videos": video_count,
            "avg_views": avg_views,
            "avg_likes": avg_likes,
            "avg_comments": avg_comments,
            "avg_engagement": avg_engagement,
            "total_views": total_views,
            "total_likes": total_likes,
            "total_comments": total_comments
        }
