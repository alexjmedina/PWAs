# Correct file path for this code: kpis-social-extractor-v1.1/app/main.py

import asyncio
import logging
import os
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

# Relative imports because this file is inside the 'app' package
from .extractors.base_extractor import HybridExtractor
from .extractors.facebook_extractor import FacebookExtractor
from .extractors.instagram_extractor import InstagramExtractor
from .extractors.youtube_extractor import YouTubeExtractor
from .extractors.linkedin_extractor import LinkedInExtractor
from .extractors.twitter_extractor import TwitterExtractor
from .extractors.tiktok_extractor import TikTokExtractor
from .config.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
    Create and configure the Flask application.
    """
    app = Flask(__name__, instance_relative_config=True)
    
    CORS(app)
    
    app.config.from_object(Config)

    if test_config:
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
                    tasks[platform] = extractor.extract_complete_kpi_data(platform, url)

            if not tasks:
                 return jsonify({"success": False, "message": "No URLs provided for extraction."}), 400

            # Await the concurrent tasks
            results = await asyncio.gather(*tasks.values())
            
            # Map the results back to their platform names
            result_data = {}
            for platform, result in zip(tasks.keys(), results):
                result_data[platform] = result

            response = {
                "success": True,
                "message": "KPIs extracted successfully",
                "data": result_data
            }
            
            logger.info("Extraction completed successfully")
            # This is the crucial return statement that was missing
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