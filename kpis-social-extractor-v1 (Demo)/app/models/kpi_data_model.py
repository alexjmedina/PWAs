"""
KPI Data Model Module - KPIs Social Extractor (API-First)

This module defines the standardized data models for KPI data across platforms.
"""

from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ProfileKPI:
    """Standardized profile KPI data model"""
    
    # Basic profile information
    platform: str
    profile_id: str
    username: str
    name: Optional[str] = None
    url: Optional[str] = None
    profile_picture_url: Optional[str] = None
    
    # Core metrics
    followers_count: Optional[int] = None
    following_count: Optional[int] = None
    posts_count: Optional[int] = None
    
    # Platform-specific metrics
    verified: Optional[bool] = None
    created_at: Optional[datetime] = None
    description: Optional[str] = None
    
    # Additional metrics
    engagement_rate: Optional[float] = None
    avg_likes: Optional[int] = None
    avg_comments: Optional[int] = None
    avg_shares: Optional[int] = None
    avg_views: Optional[int] = None
    
    # Metadata
    extraction_timestamp: datetime = datetime.now()
    extraction_method: str = "api"
    extraction_success: bool = True
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the data model to a dictionary"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            else:
                result[key] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProfileKPI':
        """Create a ProfileKPI instance from a dictionary"""
        # Convert datetime strings back to datetime objects
        for key in ['created_at', 'extraction_timestamp']:
            if key in data and isinstance(data[key], str):
                try:
                    data[key] = datetime.fromisoformat(data[key])
                except ValueError:
                    data[key] = None
        
        return cls(**data)

@dataclass
class EngagementKPI:
    """Standardized engagement KPI data model"""
    
    # Basic information
    platform: str
    profile_id: str
    username: str
    
    # Engagement metrics
    followers_count: Optional[int] = None
    engagement_rate: Optional[float] = None
    
    # Post metrics
    posts_count: Optional[int] = None
    avg_likes: Optional[int] = None
    avg_comments: Optional[int] = None
    avg_shares: Optional[int] = None
    avg_views: Optional[int] = None
    avg_engagement: Optional[int] = None
    
    # Total metrics
    total_likes: Optional[int] = None
    total_comments: Optional[int] = None
    total_shares: Optional[int] = None
    total_views: Optional[int] = None
    
    # Platform-specific metrics
    twitter_retweets: Optional[int] = None
    facebook_reactions: Optional[int] = None
    youtube_subscribers: Optional[int] = None
    
    # Time-based metrics
    posts_per_week: Optional[float] = None
    growth_rate: Optional[float] = None
    trend: Optional[str] = None
    
    # Metadata
    extraction_timestamp: datetime = datetime.now()
    extraction_method: str = "api"
    extraction_success: bool = True
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the data model to a dictionary"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            else:
                result[key] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EngagementKPI':
        """Create an EngagementKPI instance from a dictionary"""
        # Convert datetime strings back to datetime objects
        if 'extraction_timestamp' in data and isinstance(data['extraction_timestamp'], str):
            try:
                data['extraction_timestamp'] = datetime.fromisoformat(data['extraction_timestamp'])
            except ValueError:
                data['extraction_timestamp'] = datetime.now()
        
        return cls(**data)

@dataclass
class KPIValidationResult:
    """Model for KPI validation results"""
    
    platform: str
    profile_id: str
    username: str
    
    # Validation results
    is_valid: bool
    validation_timestamp: datetime = datetime.now()
    
    # Validation metrics
    profile_validation: Dict[str, bool] = None
    engagement_validation: Dict[str, bool] = None
    
    # Error details
    errors: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the validation result to a dictionary"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            else:
                result[key] = value
        return result
