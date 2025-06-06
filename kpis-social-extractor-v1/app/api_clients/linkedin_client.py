"""
LinkedIn API Client Module - KPIs Social Extractor (API-First)

This module implements the LinkedIn-specific API client using the LinkedIn API
and the datasource module integration.
"""

import logging
import json
import sys
from typing import Dict, Any, Optional, List, Union

from app.api_clients.base_api_client import BaseAPIClient

# Configure logging
logger = logging.getLogger(__name__)

class LinkedInAPIClient(BaseAPIClient):
    """
    LinkedIn-specific implementation of the BaseAPIClient
    """
    
    def __init__(self):
        """Initialize the LinkedIn API client"""
        super().__init__("linkedin")
        self.use_datasource = True
    
    async def get_user_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile information from the LinkedIn API
        
        Args:
            username: LinkedIn username
            
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
                logger.error(f"Error using datasource for LinkedIn profile: {str(e)}")
                # Fall back to direct API
        
        # Fall back to direct API if datasource fails or is disabled
        if self.has_valid_credentials():
            return await self._get_profile_via_direct_api(username)
        
        logger.error("No valid method available for LinkedIn profile extraction")
        return None
    
    async def get_followers_count(self, username: str) -> Optional[int]:
        """
        Get followers count from the LinkedIn API
        
        Args:
            username: LinkedIn username
            
        Returns:
            int: Number of followers or None if extraction fails
        """
        profile = await self.get_user_profile(username)
        if profile and "followers_count" in profile:
            return profile["followers_count"]
        return None
    
    async def get_engagement_metrics(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get engagement metrics from the LinkedIn API
        
        Args:
            username: LinkedIn username
            
        Returns:
            dict: Engagement metrics or None if extraction fails
        """
        # Try using datasource module first
        if self.use_datasource:
            try:
                metrics = await self._get_engagement_via_datasource(username)
                if metrics:
                    return metrics
            except Exception as e:
                logger.error(f"Error using datasource for LinkedIn engagement: {str(e)}")
                # Fall back to direct API
        
        # Fall back to direct API if datasource fails or is disabled
        if self.has_valid_credentials():
            return await self._get_engagement_via_direct_api(username)
        
        logger.error("No valid method available for LinkedIn engagement extraction")
        return None
    
    async def _get_profile_via_datasource(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get LinkedIn profile using the datasource module
        
        Args:
            username: LinkedIn username
            
        Returns:
            dict: Normalized profile data or None if extraction fails
        """
        try:
            # Add path to datasource runtime
            sys.path.append('/opt/.manus/.sandbox-runtime')
            from data_api import ApiClient
            
            # Initialize API client
            client = ApiClient()
            
            # Call LinkedIn API endpoint
            response = client.call_api('LinkedIn/get_user_profile_by_username', query={'username': username})
            
            if not response or not isinstance(response, dict):
                logger.error(f"Invalid response from LinkedIn datasource API for {username}")
                return None
            
            # Extract and normalize the data
            return self._normalize_datasource_profile_response(response)
            
        except ImportError:
            logger.error("Could not import datasource API client")
            return None
        except Exception as e:
            logger.error(f"Error calling LinkedIn datasource API: {str(e)}")
            return None
    
    async def _get_engagement_via_datasource(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get LinkedIn engagement metrics using the datasource module
        
        Args:
            username: LinkedIn username
            
        Returns:
            dict: Normalized engagement metrics or None if extraction fails
        """
        try:
            # Add path to datasource runtime
            sys.path.append('/opt/.manus/.sandbox-runtime')
            from data_api import ApiClient
            
            # Initialize API client
            client = ApiClient()
            
            # Call LinkedIn API endpoint
            response = client.call_api('LinkedIn/get_user_profile_by_username', query={'username': username})
            
            if not response or not isinstance(response, dict):
                logger.error(f"Invalid response from LinkedIn datasource API for {username}")
                return None
            
            # Extract and normalize the engagement data
            return self._normalize_datasource_engagement_response(response)
            
        except ImportError:
            logger.error("Could not import datasource API client")
            return None
        except Exception as e:
            logger.error(f"Error calling LinkedIn datasource API: {str(e)}")
            return None
    
    async def _get_profile_via_direct_api(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get LinkedIn profile using direct API call
        
        Args:
            username: LinkedIn username
            
        Returns:
            dict: Normalized profile data or None if extraction fails
        """
        credentials = self.get_api_credentials()
        
        if not credentials.get("client_id") or not credentials.get("client_secret"):
            logger.error("LinkedIn API requires client_id and client_secret")
            return None
        
        # LinkedIn API requires OAuth 2.0 authentication
        # This is a simplified implementation - in a real application, you would need to
        # implement the full OAuth flow to get an access token
        
        logger.warning("LinkedIn direct API implementation requires OAuth flow")
        return None
    
    async def _get_engagement_via_direct_api(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get LinkedIn engagement metrics using direct API call
        
        Args:
            username: LinkedIn username
            
        Returns:
            dict: Normalized engagement metrics or None if extraction fails
        """
        # Similar to profile extraction, this would require OAuth authentication
        logger.warning("LinkedIn direct API implementation requires OAuth flow")
        return None
    
    def _normalize_datasource_profile_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize the datasource API profile response to a standard format
        
        Args:
            response: Raw datasource API response
            
        Returns:
            dict: Normalized profile data
        """
        try:
            # Check if response has the expected structure
            if not response.get("success") or "data" not in response:
                logger.error("Invalid LinkedIn datasource response structure")
                return None
            
            data = response["data"]
            
            # Extract post author information if available
            author = None
            if "post" in data and "author" in data["post"]:
                author = data["post"]["author"]
            
            # Build normalized profile
            normalized = {
                "username": author.get("username") if author else None,
                "name": f"{author.get('firstName', '')} {author.get('lastName', '')}" if author else None,
                "headline": author.get("headline") if author else None,
                "followers_count": None,  # Not directly available in the response
                "profile_url": author.get("url") if author else None,
                "id": author.get("id") if author else None
            }
            
            # Extract profile picture if available
            if author and "profilePictures" in author and author["profilePictures"]:
                normalized["profile_picture_url"] = author["profilePictures"][0].get("url")
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing LinkedIn datasource profile response: {str(e)}")
            return None
    
    def _normalize_datasource_engagement_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize the datasource API engagement response to a standard format
        
        Args:
            response: Raw datasource API response
            
        Returns:
            dict: Normalized engagement metrics
        """
        try:
            # Check if response has the expected structure
            if not response.get("success") or "data" not in response:
                logger.error("Invalid LinkedIn datasource response structure")
                return None
            
            data = response["data"]
            
            # Extract engagement metrics from post data if available
            metrics = {}
            
            if "post" in data:
                post = data["post"]
                
                metrics["total_reactions"] = post.get("totalReactionCount", 0)
                metrics["likes"] = post.get("likeCount", 0)
                metrics["comments"] = post.get("commentsCount", 0)
                metrics["reposts"] = post.get("repostsCount", 0)
                
                # Additional reaction types
                metrics["appreciation"] = post.get("appreciationCount", 0)
                metrics["empathy"] = post.get("empathyCount", 0)
                metrics["interest"] = post.get("InterestCount", 0)
                metrics["praise"] = post.get("praiseCount", 0)
                
                # Calculate engagement rate if we have author followers (not available in this response)
                # This would need to be enhanced with additional API calls in a real implementation
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error normalizing LinkedIn datasource engagement response: {str(e)}")
            return None
