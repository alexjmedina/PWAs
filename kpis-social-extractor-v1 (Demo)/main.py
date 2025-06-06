"""
Main Application Module - KPIs Social Extractor

This module initializes and configures the Flask application.
"""

import os
import sys
import logging
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

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
            
            # In a real application, this would call the extraction logic
            # For demo purposes, we'll return mock data
            
            result = {
                "success": True,
                "message": "KPIs extracted successfully",
                "data": {
                    "website": {
                        "title": "ADEN International Business School | Escuela de Negocios",
                        "description": "Escuela de Negocios abocada al desarrollo profesional de Directivos y Gerentes. ADEN tiene 20 sedes en América Latina. Business School."
                    },
                    "facebook": {
                        "followers": 12500,
                        "posts": 3,
                        "avgLikes": 0,
                        "avgComments": 0,
                        "totalEngagement": 0
                    },
                    "instagram": {
                        "followers": 8700,
                        "posts": 0,
                        "avgLikes": 0,
                        "avgComments": 0,
                        "totalEngagement": 0
                    },
                    "youtube": {
                        "subscribers": 30300,
                        "videos": 1,
                        "avgViews": 0,
                        "avgLikes": 0,
                        "avgComments": 0
                    },
                    "linkedin": {
                        "followers": 5200,
                        "posts": 0,
                        "avgLikes": 0,
                        "avgComments": 0,
                        "totalEngagement": 0
                    },
                    "twitter": {
                        "followers": 5700,
                        "tweets": 10,
                        "avgLikes": 1,
                        "avgRetweets": 0,
                        "avgReplies": 0,
                        "totalEngagement": 1
                    }
                }
            }
            
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
