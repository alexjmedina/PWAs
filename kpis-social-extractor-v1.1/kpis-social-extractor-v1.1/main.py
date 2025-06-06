"""
Main Application Module - KPIs Social Extractor

This module initializes and configures the Flask application.
"""

import os
import sys
import logging
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

# Import the HybridExtractor
from app.extractors.base_extractor import HybridExtractor
from app.utils.cache_manager import CacheManager
from app.utils.rate_limiter import RateLimiter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Initialize cache and rate limiter
cache_manager = CacheManager()
rate_limiter = RateLimiter()

def create_app(test_config=None):
    """
    Create and configure the Flask application
    
    Args:
        test_config: Test configuration to override default configuration
        
    Returns:
        Flask application instance
    """
    # Create Flask app
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    # Enable CORS
    CORS(app)
    
    # Load configuration
    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Root route
    @app.route('/')
    def index():
        """Render the index page"""
        return render_template('index.html')
    
    # Dashboard route
    @app.route('/dashboard')
    def dashboard():
        """Render the dashboard page"""
        return render_template('dashboard.html')
    
    # API route for extracting KPIs
    @app.route('/api/extract', methods=['POST'])
    def extract_kpis():
        """Extract KPIs from social media profiles"""
        try:
            data = request.json
            logger.info(f"Received extraction request: {data}")
            
            # Initialize the HybridExtractor with cache and rate limiter
            extractor = HybridExtractor(cache_manager=cache_manager, rate_limiter=rate_limiter)
            
            # Extract URLs from the request
            website_url = data.get('websiteUrl', '')
            facebook_url = data.get('facebookUrl', '')
            instagram_url = data.get('instagramUrl', '')
            youtube_url = data.get('youtubeUrl', '')
            linkedin_url = data.get('linkedinUrl', '')
            twitter_url = data.get('twitterUrl', '')
            tiktok_url = data.get('tiktokUrl', '')
            
            # Initialize result dictionary
            result_data = {
                "website": {},
                "facebook": None,
                "instagram": None,
                "youtube": None,
                "linkedin": None,
                "twitter": None,
                "tiktok": None
            }
            
            # Extract website information if URL is provided
            if website_url:
                try:
                    website_info = extractor.extract_website_info(website_url)
                    result_data["website"] = {
                        "title": website_info.get("title", "Unknown Website"),
                        "description": website_info.get("description", "No description available")
                    }
                except Exception as e:
                    logger.error(f"Error extracting website info: {str(e)}")
                    result_data["website"] = {
                        "title": "Error extracting website info",
                        "description": str(e)
                    }
            
            # Extract Facebook KPIs if URL is provided
            if facebook_url:
                try:
                    facebook_kpis = extractor.extract_facebook_kpis(facebook_url)
                    result_data["facebook"] = {
                        "followers": facebook_kpis.get("followers", 0),
                        "posts": facebook_kpis.get("posts", 0),
                        "avgLikes": facebook_kpis.get("avg_likes", 0),
                        "avgComments": facebook_kpis.get("avg_comments", 0),
                        "totalEngagement": facebook_kpis.get("total_engagement", 0)
                    }
                except Exception as e:
                    logger.error(f"Error extracting Facebook KPIs: {str(e)}")
            
            # Extract Instagram KPIs if URL is provided
            if instagram_url:
                try:
                    instagram_kpis = extractor.extract_instagram_kpis(instagram_url)
                    result_data["instagram"] = {
                        "followers": instagram_kpis.get("followers", 0),
                        "posts": instagram_kpis.get("posts", 0),
                        "avgLikes": instagram_kpis.get("avg_likes", 0),
                        "avgComments": instagram_kpis.get("avg_comments", 0),
                        "totalEngagement": instagram_kpis.get("total_engagement", 0)
                    }
                except Exception as e:
                    logger.error(f"Error extracting Instagram KPIs: {str(e)}")
            
            # Extract YouTube KPIs if URL is provided
            if youtube_url:
                try:
                    youtube_kpis = extractor.extract_youtube_kpis(youtube_url)
                    result_data["youtube"] = {
                        "subscribers": youtube_kpis.get("subscribers", 0),
                        "videos": youtube_kpis.get("videos", 0),
                        "avgViews": youtube_kpis.get("avg_views", 0),
                        "avgLikes": youtube_kpis.get("avg_likes", 0),
                        "avgComments": youtube_kpis.get("avg_comments", 0)
                    }
                except Exception as e:
                    logger.error(f"Error extracting YouTube KPIs: {str(e)}")
            
            # Extract LinkedIn KPIs if URL is provided
            if linkedin_url:
                try:
                    linkedin_kpis = extractor.extract_linkedin_kpis(linkedin_url)
                    result_data["linkedin"] = {
                        "followers": linkedin_kpis.get("followers", 0),
                        "posts": linkedin_kpis.get("posts", 0),
                        "avgLikes": linkedin_kpis.get("avg_likes", 0),
                        "avgComments": linkedin_kpis.get("avg_comments", 0),
                        "totalEngagement": linkedin_kpis.get("total_engagement", 0)
                    }
                except Exception as e:
                    logger.error(f"Error extracting LinkedIn KPIs: {str(e)}")
            
            # Extract Twitter KPIs if URL is provided
            if twitter_url:
                try:
                    twitter_kpis = extractor.extract_twitter_kpis(twitter_url)
                    result_data["twitter"] = {
                        "followers": twitter_kpis.get("followers", 0),
                        "tweets": twitter_kpis.get("tweets", 0),
                        "avgLikes": twitter_kpis.get("avg_likes", 0),
                        "avgRetweets": twitter_kpis.get("avg_retweets", 0),
                        "avgReplies": twitter_kpis.get("avg_replies", 0),
                        "totalEngagement": twitter_kpis.get("total_engagement", 0)
                    }
                except Exception as e:
                    logger.error(f"Error extracting Twitter KPIs: {str(e)}")
            
            # Extract TikTok KPIs if URL is provided
            if tiktok_url:
                try:
                    tiktok_kpis = extractor.extract_tiktok_kpis(tiktok_url)
                    result_data["tiktok"] = {
                        "followers": tiktok_kpis.get("followers", 0),
                        "videos": tiktok_kpis.get("videos", 0),
                        "avgViews": tiktok_kpis.get("avg_views", 0),
                        "avgLikes": tiktok_kpis.get("avg_likes", 0),
                        "avgComments": tiktok_kpis.get("avg_comments", 0),
                        "avgShares": tiktok_kpis.get("avg_shares", 0)
                    }
                except Exception as e:
                    logger.error(f"Error extracting TikTok KPIs: {str(e)}")
            
            # Prepare the response
            result = {
                "success": True,
                "message": "KPIs extracted successfully",
                "data": result_data
            }
            
            logger.info(f"Extraction completed successfully")
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Error extracting KPIs: {str(e)}")
            return jsonify({
                "success": False,
                "message": f"Error extracting KPIs: {str(e)}",
                "data": None
            }), 500
    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    # This allows the app to be run with 'python app/main.py'
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
