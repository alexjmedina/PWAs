"""
Main Application Module - KPIs Social Extractor

This module initializes and configures the Flask application.
"""

import os
import sys
import logging
from flask import Flask, render_template
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
                static_folder='../static',
                template_folder='../templates')
    
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
    
    # Register blueprints
    from app.api.routes import api_bp
    app.register_blueprint(api_bp)
    
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
    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    # This allows the app to be run with 'python app/main.py'
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
