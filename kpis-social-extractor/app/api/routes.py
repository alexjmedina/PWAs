"""
API Routes Module - KPIs Social Extractor

This module defines the Flask API routes for the KPI extraction and dashboard functionality.
"""

import logging
from typing import Dict, Any, Optional, List

from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin

from app.extractors.facebook_extractor import FacebookExtractor
from app.extractors.instagram_extractor import InstagramExtractor
from app.extractors.youtube_extractor import YouTubeExtractor
from app.extractors.linkedin_extractor import LinkedInExtractor
from app.extractors.twitter_extractor import TwitterExtractor
from app.extractors.tiktok_extractor import TikTokExtractor

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Initialize extractors
facebook_extractor = FacebookExtractor()
instagram_extractor = InstagramExtractor()
youtube_extractor = YouTubeExtractor()
linkedin_extractor = LinkedInExtractor()
twitter_extractor = TwitterExtractor()
tiktok_extractor = TikTokExtractor()

@api_bp.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'KPIs Social Extractor API is running'
    })

@api_bp.route('/extract', methods=['POST'])
@cross_origin()
def extract_kpis():
    """
    Extract KPIs from social media profiles
    
    Request body:
    {
        "website": "https://example.com",
        "facebook": "https://facebook.com/example",
        "instagram": "https://instagram.com/example",
        "youtube": "https://youtube.com/c/example",
        "linkedin": "https://linkedin.com/company/example",
        "twitter": "https://twitter.com/example",
        "tiktok": "https://tiktok.com/@example"
    }
    
    Response:
    {
        "website": {
            "title": "Example Website",
            "description": "Example description"
        },
        "facebook": {
            "followers": 12345,
            "engagement": {
                "posts": 100,
                "avg_likes": 50,
                "avg_comments": 10,
                "total_engagement": 60
            }
        },
        ...
    }
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Initialize response
        response = {}
        
        # Process each platform
        if 'website' in data and data['website']:
            response['website'] = extract_website_data(data['website'])
        
        if 'facebook' in data and data['facebook']:
            response['facebook'] = extract_facebook_data(data['facebook'])
        
        if 'instagram' in data and data['instagram']:
            response['instagram'] = extract_instagram_data(data['instagram'])
        
        if 'youtube' in data and data['youtube']:
            response['youtube'] = extract_youtube_data(data['youtube'])
        
        if 'linkedin' in data and data['linkedin']:
            response['linkedin'] = extract_linkedin_data(data['linkedin'])
        
        if 'twitter' in data and data['twitter']:
            response['twitter'] = extract_twitter_data(data['twitter'])
        
        if 'tiktok' in data and data['tiktok']:
            response['tiktok'] = extract_tiktok_data(data['tiktok'])
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error extracting KPIs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/extract/<platform>', methods=['POST'])
@cross_origin()
def extract_platform_kpis(platform):
    """
    Extract KPIs from a specific social media platform
    
    Request body:
    {
        "url": "https://platform.com/example"
    }
    
    Response:
    {
        "followers": 12345,
        "engagement": {
            "posts": 100,
            "avg_likes": 50,
            "avg_comments": 10,
            "total_engagement": 60
        }
    }
    """
    try:
        # Get request data
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'No URL provided'}), 400
        
        url = data['url']
        
        # Extract data based on platform
        if platform == 'website':
            result = extract_website_data(url)
        elif platform == 'facebook':
            result = extract_facebook_data(url)
        elif platform == 'instagram':
            result = extract_instagram_data(url)
        elif platform == 'youtube':
            result = extract_youtube_data(url)
        elif platform == 'linkedin':
            result = extract_linkedin_data(url)
        elif platform == 'twitter':
            result = extract_twitter_data(url)
        elif platform == 'tiktok':
            result = extract_tiktok_data(url)
        else:
            return jsonify({'error': f'Unsupported platform: {platform}'}), 400
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error extracting KPIs for {platform}: {str(e)}")
        return jsonify({'error': str(e)}), 500

def extract_website_data(url: str) -> Dict[str, Any]:
    """
    Extract metadata from a website
    
    Args:
        url: Website URL
        
    Returns:
        dict: Website metadata
    """
    try:
        # Use any extractor to get website metadata
        metadata = facebook_extractor.extract_website_metadata(url)
        return metadata or {'title': 'Unknown', 'description': 'No description available'}
    except Exception as e:
        logger.error(f"Error extracting website data: {str(e)}")
        return {'title': 'Unknown', 'description': 'Error extracting data'}

def extract_facebook_data(url: str) -> Dict[str, Any]:
    """
    Extract KPIs from Facebook
    
    Args:
        url: Facebook page URL
        
    Returns:
        dict: Facebook KPIs
    """
    try:
        followers = facebook_extractor.extract_followers(url)
        engagement = facebook_extractor.extract_engagement(url)
        
        return {
            'followers': followers,
            'engagement': engagement
        }
    except Exception as e:
        logger.error(f"Error extracting Facebook data: {str(e)}")
        return {'error': str(e)}

def extract_instagram_data(url: str) -> Dict[str, Any]:
    """
    Extract KPIs from Instagram
    
    Args:
        url: Instagram profile URL
        
    Returns:
        dict: Instagram KPIs
    """
    try:
        followers = instagram_extractor.extract_followers(url)
        engagement = instagram_extractor.extract_engagement(url)
        
        return {
            'followers': followers,
            'engagement': engagement
        }
    except Exception as e:
        logger.error(f"Error extracting Instagram data: {str(e)}")
        return {'error': str(e)}

def extract_youtube_data(url: str) -> Dict[str, Any]:
    """
    Extract KPIs from YouTube
    
    Args:
        url: YouTube channel URL
        
    Returns:
        dict: YouTube KPIs
    """
    try:
        followers = youtube_extractor.extract_followers(url)
        engagement = youtube_extractor.extract_engagement(url)
        
        return {
            'followers': followers,
            'engagement': engagement
        }
    except Exception as e:
        logger.error(f"Error extracting YouTube data: {str(e)}")
        return {'error': str(e)}

def extract_linkedin_data(url: str) -> Dict[str, Any]:
    """
    Extract KPIs from LinkedIn
    
    Args:
        url: LinkedIn page URL
        
    Returns:
        dict: LinkedIn KPIs
    """
    try:
        followers = linkedin_extractor.extract_followers(url)
        engagement = linkedin_extractor.extract_engagement(url)
        
        return {
            'followers': followers,
            'engagement': engagement
        }
    except Exception as e:
        logger.error(f"Error extracting LinkedIn data: {str(e)}")
        return {'error': str(e)}

def extract_twitter_data(url: str) -> Dict[str, Any]:
    """
    Extract KPIs from Twitter/X
    
    Args:
        url: Twitter profile URL
        
    Returns:
        dict: Twitter KPIs
    """
    try:
        followers = twitter_extractor.extract_followers(url)
        engagement = twitter_extractor.extract_engagement(url)
        
        return {
            'followers': followers,
            'engagement': engagement
        }
    except Exception as e:
        logger.error(f"Error extracting Twitter data: {str(e)}")
        return {'error': str(e)}

def extract_tiktok_data(url: str) -> Dict[str, Any]:
    """
    Extract KPIs from TikTok
    
    Args:
        url: TikTok profile URL
        
    Returns:
        dict: TikTok KPIs
    """
    try:
        followers = tiktok_extractor.extract_followers(url)
        engagement = tiktok_extractor.extract_engagement(url)
        
        return {
            'followers': followers,
            'engagement': engagement
        }
    except Exception as e:
        logger.error(f"Error extracting TikTok data: {str(e)}")
        return {'error': str(e)}
