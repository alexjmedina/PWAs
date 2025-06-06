"""
KPI Validation Module - KPIs Social Extractor (API-First)

This module implements validation tests for KPI extraction accuracy and reliability.
"""

import logging
import json
import asyncio
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

from app.api_clients.twitter_client import TwitterAPIClient
from app.api_clients.linkedin_client import LinkedInAPIClient
from app.api_clients.facebook_client import FacebookAPIClient
from app.api_clients.instagram_client import InstagramAPIClient
from app.api_clients.youtube_client import YouTubeAPIClient
from app.api_clients.tiktok_client import TikTokAPIClient
from app.models.kpi_data_model import ProfileKPI, EngagementKPI, KPIValidationResult

# Configure logging
logger = logging.getLogger(__name__)

class KPIValidator:
    """
    Validates the accuracy and reliability of KPI extraction from social media APIs
    """
    
    def __init__(self):
        """Initialize the KPI validator"""
        self.clients = {
            "twitter": TwitterAPIClient(),
            "linkedin": LinkedInAPIClient(),
            "facebook": FacebookAPIClient(),
            "instagram": InstagramAPIClient(),
            "youtube": YouTubeAPIClient(),
            "tiktok": TikTokAPIClient()
        }
        
        # Define test cases for each platform
        self.test_cases = {
            "twitter": ["elonmusk", "BillGates", "BarackObama"],
            "linkedin": ["satyanadella", "jeffweiner", "billgates"],
            "facebook": ["meta", "microsoft", "cocacola"],
            "instagram": ["instagram", "natgeo", "nike"],
            "youtube": ["@MrBeast", "@PewDiePie", "@TEDx"],
            "tiktok": ["charlidamelio", "khaby.lame", "addisonre"]
        }
        
        # Expected KPI fields for validation
        self.expected_profile_fields = {
            "twitter": ["username", "name", "followers_count", "following_count"],
            "linkedin": ["username", "name", "profile_url"],
            "facebook": ["username", "name", "followers_count"],
            "instagram": ["username", "followers_count", "following_count", "media_count"],
            "youtube": ["title", "subscriber_count", "video_count", "view_count"],
            "tiktok": ["username", "follower_count", "following_count", "video_count"]
        }
        
        self.expected_engagement_fields = {
            "twitter": ["followers", "avg_likes", "avg_engagement"],
            "linkedin": ["total_reactions", "comments", "avg_engagement"],
            "facebook": ["avg_likes", "avg_comments", "avg_shares"],
            "instagram": ["avg_likes", "avg_comments", "avg_engagement"],
            "youtube": ["avg_views", "avg_likes", "avg_comments"],
            "tiktok": ["avg_views", "avg_likes", "avg_comments", "avg_shares"]
        }
    
    async def validate_platform(self, platform: str) -> List[KPIValidationResult]:
        """
        Validate KPI extraction for a specific platform
        
        Args:
            platform: Platform name (e.g., 'twitter', 'facebook')
            
        Returns:
            list: List of validation results
        """
        if platform not in self.clients:
            logger.error(f"Unsupported platform: {platform}")
            return []
        
        client = self.clients[platform]
        test_cases = self.test_cases.get(platform, [])
        results = []
        
        for username in test_cases:
            # Validate profile extraction
            profile_result = await self._validate_profile_extraction(platform, username, client)
            
            # Validate engagement extraction
            engagement_result = await self._validate_engagement_extraction(platform, username, client)
            
            # Combine results
            validation_result = KPIValidationResult(
                platform=platform,
                profile_id=username,
                username=username,
                is_valid=profile_result["is_valid"] and engagement_result["is_valid"],
                profile_validation=profile_result["validation"],
                engagement_validation=engagement_result["validation"],
                errors=profile_result["errors"] + engagement_result["errors"]
            )
            
            results.append(validation_result)
            
            # Log validation result
            if validation_result.is_valid:
                logger.info(f"Validation successful for {platform}/{username}")
            else:
                logger.warning(f"Validation failed for {platform}/{username}: {validation_result.errors}")
        
        return results
    
    async def validate_all_platforms(self) -> Dict[str, List[KPIValidationResult]]:
        """
        Validate KPI extraction for all supported platforms
        
        Returns:
            dict: Dictionary of validation results by platform
        """
        results = {}
        
        for platform in self.clients.keys():
            platform_results = await self.validate_platform(platform)
            results[platform] = platform_results
        
        return results
    
    async def _validate_profile_extraction(self, platform: str, username: str, client: Any) -> Dict[str, Any]:
        """
        Validate profile extraction for a specific platform and username
        
        Args:
            platform: Platform name
            username: Username to validate
            client: API client instance
            
        Returns:
            dict: Validation result
        """
        try:
            # Extract profile data
            profile_data = await client.get_user_profile(username)
            
            if not profile_data:
                return {
                    "is_valid": False,
                    "validation": {},
                    "errors": [f"Failed to extract profile data for {platform}/{username}"]
                }
            
            # Check expected fields
            expected_fields = self.expected_profile_fields.get(platform, [])
            validation = {}
            errors = []
            
            for field in expected_fields:
                field_valid = field in profile_data and profile_data[field] is not None
                validation[field] = field_valid
                
                if not field_valid:
                    errors.append(f"Missing or invalid field '{field}' in {platform}/{username} profile")
            
            # Check if all required fields are valid
            is_valid = all(validation.values())
            
            return {
                "is_valid": is_valid,
                "validation": validation,
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"Error validating profile extraction for {platform}/{username}: {str(e)}")
            return {
                "is_valid": False,
                "validation": {},
                "errors": [f"Exception during profile validation: {str(e)}"]
            }
    
    async def _validate_engagement_extraction(self, platform: str, username: str, client: Any) -> Dict[str, Any]:
        """
        Validate engagement extraction for a specific platform and username
        
        Args:
            platform: Platform name
            username: Username to validate
            client: API client instance
            
        Returns:
            dict: Validation result
        """
        try:
            # Extract engagement data
            engagement_data = await client.get_engagement_metrics(username)
            
            if not engagement_data:
                return {
                    "is_valid": False,
                    "validation": {},
                    "errors": [f"Failed to extract engagement data for {platform}/{username}"]
                }
            
            # Check expected fields
            expected_fields = self.expected_engagement_fields.get(platform, [])
            validation = {}
            errors = []
            
            for field in expected_fields:
                field_valid = field in engagement_data
                validation[field] = field_valid
                
                if not field_valid:
                    errors.append(f"Missing field '{field}' in {platform}/{username} engagement metrics")
            
            # Check if all required fields are valid
            is_valid = all(validation.values())
            
            # Additional validation for engagement rate
            if "engagement_rate" in engagement_data and "followers" in engagement_data:
                if engagement_data["followers"] > 0:
                    # Check if engagement rate calculation is reasonable
                    if engagement_data["engagement_rate"] < 0 or engagement_data["engagement_rate"] > 100:
                        errors.append(f"Unreasonable engagement rate ({engagement_data['engagement_rate']}%) for {platform}/{username}")
                        is_valid = False
            
            return {
                "is_valid": is_valid,
                "validation": validation,
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"Error validating engagement extraction for {platform}/{username}: {str(e)}")
            return {
                "is_valid": False,
                "validation": {},
                "errors": [f"Exception during engagement validation: {str(e)}"]
            }

async def run_validation_tests():
    """
    Run validation tests for all platforms and generate a report
    
    Returns:
        dict: Validation report
    """
    validator = KPIValidator()
    results = await validator.validate_all_platforms()
    
    # Generate summary report
    report = {
        "timestamp": datetime.now().isoformat(),
        "platforms": {},
        "overall_success_rate": 0,
        "total_tests": 0,
        "successful_tests": 0
    }
    
    total_tests = 0
    successful_tests = 0
    
    for platform, platform_results in results.items():
        platform_success = 0
        platform_total = len(platform_results)
        
        for result in platform_results:
            if result.is_valid:
                platform_success += 1
                successful_tests += 1
            
            total_tests += 1
        
        success_rate = (platform_success / platform_total * 100) if platform_total > 0 else 0
        
        report["platforms"][platform] = {
            "success_rate": round(success_rate, 2),
            "tests": platform_total,
            "successful": platform_success,
            "results": [r.to_dict() for r in platform_results]
        }
    
    # Calculate overall success rate
    report["overall_success_rate"] = round((successful_tests / total_tests * 100) if total_tests > 0 else 0, 2)
    report["total_tests"] = total_tests
    report["successful_tests"] = successful_tests
    
    return report

if __name__ == "__main__":
    import asyncio
    
    # Run validation tests
    report = asyncio.run(run_validation_tests())
    
    # Print summary
    print(f"Overall success rate: {report['overall_success_rate']}%")
    print(f"Total tests: {report['total_tests']}")
    print(f"Successful tests: {report['successful_tests']}")
    
    for platform, platform_data in report["platforms"].items():
        print(f"{platform}: {platform_data['success_rate']}% success rate ({platform_data['successful']}/{platform_data['tests']})")
