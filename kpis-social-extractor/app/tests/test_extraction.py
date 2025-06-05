"""
Test script for KPIs Social Extractor

This script tests the extraction capabilities of the system with real-world URLs.
"""

import os
import sys
import logging
import json
from pprint import pprint

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.extractors.facebook_extractor import FacebookExtractor
from app.extractors.instagram_extractor import InstagramExtractor
from app.extractors.youtube_extractor import YouTubeExtractor
from app.extractors.linkedin_extractor import LinkedInExtractor
from app.extractors.twitter_extractor import TwitterExtractor
from app.extractors.tiktok_extractor import TikTokExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_facebook_extraction():
    """Test Facebook extraction with real URLs"""
    logger.info("Testing Facebook extraction...")
    
    # Initialize extractor
    extractor = FacebookExtractor()
    
    # Test URLs
    urls = [
        "https://www.facebook.com/ADENBusinessSchool",
        "https://www.facebook.com/GrupoBuro/",
        "https://www.facebook.com/INCAE"
    ]
    
    results = {}
    
    for url in urls:
        logger.info(f"Testing URL: {url}")
        
        try:
            # Extract followers
            followers = extractor.extract_followers(url)
            logger.info(f"Followers: {followers}")
            
            # Extract engagement
            engagement = extractor.extract_engagement(url)
            logger.info(f"Engagement: {engagement}")
            
            results[url] = {
                "followers": followers,
                "engagement": engagement
            }
        except Exception as e:
            logger.error(f"Error extracting data from {url}: {str(e)}")
            results[url] = {"error": str(e)}
    
    return results

def test_instagram_extraction():
    """Test Instagram extraction with real URLs"""
    logger.info("Testing Instagram extraction...")
    
    # Initialize extractor
    extractor = InstagramExtractor()
    
    # Test URLs
    urls = [
        "https://www.instagram.com/adenbs",
        "https://www.instagram.com/somosburobs/",
        "https://www.instagram.com/incae/"
    ]
    
    results = {}
    
    for url in urls:
        logger.info(f"Testing URL: {url}")
        
        try:
            # Extract followers
            followers = extractor.extract_followers(url)
            logger.info(f"Followers: {followers}")
            
            # Extract engagement
            engagement = extractor.extract_engagement(url)
            logger.info(f"Engagement: {engagement}")
            
            results[url] = {
                "followers": followers,
                "engagement": engagement
            }
        except Exception as e:
            logger.error(f"Error extracting data from {url}: {str(e)}")
            results[url] = {"error": str(e)}
    
    return results

def test_youtube_extraction():
    """Test YouTube extraction with real URLs"""
    logger.info("Testing YouTube extraction...")
    
    # Initialize extractor
    extractor = YouTubeExtractor()
    
    # Test URLs
    urls = [
        "https://www.youtube.com/user/ADENBusinessSchool",
        "https://www.youtube.com/@somosburo",
        "https://www.youtube.com/user/incaebusiness"
    ]
    
    results = {}
    
    for url in urls:
        logger.info(f"Testing URL: {url}")
        
        try:
            # Extract followers
            followers = extractor.extract_followers(url)
            logger.info(f"Followers: {followers}")
            
            # Extract engagement
            engagement = extractor.extract_engagement(url)
            logger.info(f"Engagement: {engagement}")
            
            results[url] = {
                "followers": followers,
                "engagement": engagement
            }
        except Exception as e:
            logger.error(f"Error extracting data from {url}: {str(e)}")
            results[url] = {"error": str(e)}
    
    return results

def test_linkedin_extraction():
    """Test LinkedIn extraction with real URLs"""
    logger.info("Testing LinkedIn extraction...")
    
    # Initialize extractor
    extractor = LinkedInExtractor()
    
    # Test URLs
    urls = [
        "https://www.linkedin.com/school/adenbs/",
        "https://www.linkedin.com/school/somosburobs/",
        "https://www.linkedin.com/school/incae/"
    ]
    
    results = {}
    
    for url in urls:
        logger.info(f"Testing URL: {url}")
        
        try:
            # Extract followers
            followers = extractor.extract_followers(url)
            logger.info(f"Followers: {followers}")
            
            # Extract engagement
            engagement = extractor.extract_engagement(url)
            logger.info(f"Engagement: {engagement}")
            
            results[url] = {
                "followers": followers,
                "engagement": engagement
            }
        except Exception as e:
            logger.error(f"Error extracting data from {url}: {str(e)}")
            results[url] = {"error": str(e)}
    
    return results

def test_twitter_extraction():
    """Test Twitter extraction with real URLs"""
    logger.info("Testing Twitter extraction...")
    
    # Initialize extractor
    extractor = TwitterExtractor()
    
    # Test URLs
    urls = [
        "https://twitter.com/ADENBS",
        "https://twitter.com/somosburo",
        "https://twitter.com/incae"
    ]
    
    results = {}
    
    for url in urls:
        logger.info(f"Testing URL: {url}")
        
        try:
            # Extract followers
            followers = extractor.extract_followers(url)
            logger.info(f"Followers: {followers}")
            
            # Extract engagement
            engagement = extractor.extract_engagement(url)
            logger.info(f"Engagement: {engagement}")
            
            results[url] = {
                "followers": followers,
                "engagement": engagement
            }
        except Exception as e:
            logger.error(f"Error extracting data from {url}: {str(e)}")
            results[url] = {"error": str(e)}
    
    return results

def test_tiktok_extraction():
    """Test TikTok extraction with real URLs"""
    logger.info("Testing TikTok extraction...")
    
    # Initialize extractor
    extractor = TikTokExtractor()
    
    # Test URLs
    urls = [
        "https://www.tiktok.com/@adenbusinessschool",
        "https://www.tiktok.com/@somosburo",
        "https://www.tiktok.com/@incae"
    ]
    
    results = {}
    
    for url in urls:
        logger.info(f"Testing URL: {url}")
        
        try:
            # Extract followers
            followers = extractor.extract_followers(url)
            logger.info(f"Followers: {followers}")
            
            # Extract engagement
            engagement = extractor.extract_engagement(url)
            logger.info(f"Engagement: {engagement}")
            
            results[url] = {
                "followers": followers,
                "engagement": engagement
            }
        except Exception as e:
            logger.error(f"Error extracting data from {url}: {str(e)}")
            results[url] = {"error": str(e)}
    
    return results

def run_all_tests():
    """Run all extraction tests and save results"""
    logger.info("Running all extraction tests...")
    
    results = {
        "facebook": test_facebook_extraction(),
        "instagram": test_instagram_extraction(),
        "youtube": test_youtube_extraction(),
        "linkedin": test_linkedin_extraction(),
        "twitter": test_twitter_extraction(),
        "tiktok": test_tiktok_extraction()
    }
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info("All tests completed. Results saved to test_results.json")
    
    return results

if __name__ == "__main__":
    results = run_all_tests()
    
    # Print summary
    print("\n=== TEST RESULTS SUMMARY ===\n")
    
    for platform, platform_results in results.items():
        print(f"--- {platform.upper()} ---")
        for url, data in platform_results.items():
            if "error" in data:
                print(f"{url}: ERROR - {data['error']}")
            else:
                print(f"{url}: {data['followers']} followers, {data['engagement']['posts'] if data['engagement'] and 'posts' in data['engagement'] else 'N/A'} posts")
        print()
