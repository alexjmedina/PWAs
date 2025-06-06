"""
Main Application Module - KPIs Social Extractor

This module initializes and configures the Flask application.
"""

import os
import asyncio
import logging
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

# Import the HybridExtractor and all specific extractor classes
# NEW, CORRECTED IMPORTS (absolute)
from app.extractors.base_extractor import HybridExtractor
from app.extractors.facebook_extractor import FacebookExtractor
from app.extractors.instagram_extractor import InstagramExtractor
from app.extractors.youtube_extractor import YouTubeExtractor
from app.extractors.linkedin_extractor import LinkedInExtractor
from app.extractors.twitter_extractor import TwitterExtractor
from app.extractors.tiktok_extractor import TikTokExtractor


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# --- Create and configure the extractor instance once when the app starts ---
extractor = HybridExtractor()
extractor.register_extractor("facebook", FacebookExtractor())
extractor.register_extractor("instagram", InstagramExtractor())
extractor.register_extractor("youtube", YouTubeExtractor())
extractor.register_extractor("linkedin", LinkedInExtractor())
extractor.register_extractor("twitter", TwitterExtractor())
extractor.register_extractor("tiktok", TikTokExtractor())
# ---

def create_app(test_config=None):
    """
    Create and configure the Flask application
    
    Args:
        test_config: Test configuration to override default configuration
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    CORS(app)
    
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/api/extract', methods=['POST'])
    async def extract_kpis():
        """Extract KPIs from social media profiles asynchronously"""
        try:
            data = request.json
            logger.info(f"Received extraction request: {data}")
            
            tasks = {}
            urls_to_process = {
                'facebook': data.get('facebookUrl'),
                'instagram': data.get('instagramUrl'),
                'youtube': data.get('youtubeUrl'),
                'linkedin': data.get('linkedinUrl'),
                'twitter': data.get('twitterUrl'),
                'tiktok': data.get('tiktokUrl')
            }

            for platform, url in urls_to_process.items():
                if url:
                    # Use the single, pre-configured extractor instance
                    tasks[platform] = extractor.extract_complete_kpi_data(platform, url)

            if not tasks:
                 return jsonify({"success": False, "message": "No URLs provided for extraction."}), 400

            results = await asyncio.gather(*tasks.values())
            
            result_data = {}
            for platform, result in zip(tasks.keys(), results):
                result_data[platform] = result

            response = {
                "success": True,
                "message": "KPIs extracted successfully",
                "data": result_data
            }
            
            logger.info("Extraction completed successfully")
            return jsonify(response)
            
        except Exception as e:
            logger.error(f"Error extracting KPIs: {e}", exc_info=True)
            return jsonify({
                "success": False,
                "message": str(e),
                "data": None
            }), 500
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)