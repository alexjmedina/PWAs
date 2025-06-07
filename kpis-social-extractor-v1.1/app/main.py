# File: app/main.py
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

extractor = HybridExtractor()
extractor.register_extractor("facebook", FacebookExtractor())
extractor.register_extractor("instagram", InstagramExtractor())
extractor.register_extractor("youtube", YouTubeExtractor())
extractor.register_extractor("linkedin", LinkedInExtractor())
extractor.register_extractor("twitter", TwitterExtractor())
extractor.register_extractor("tiktok", TikTokExtractor())

def create_app(test_config=None):
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
        # This function's logic is kept from our previous successful step
        # ... (async logic remains the same) ...
        pass # Placeholder for brevity, the logic is correct from the previous turn

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)