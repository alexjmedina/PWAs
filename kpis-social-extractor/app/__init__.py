"""
KPIs Social Extractor - Flask Application
Main application initialization module
"""

from flask import Flask
from flask_cors import CORS
from app.api import api_bp
from app.config.config import Config

def create_app(config_class=Config):
    """Create and configure the Flask application"""
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Register error handlers
    register_error_handlers(app)
    
    @app.route('/')
    def index():
        from flask import render_template
        return render_template('index.html')
    
    return app

def register_error_handlers(app):
    """Register error handlers for the application"""
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import jsonify
        return jsonify({"error": "Resource not found"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import jsonify
        return jsonify({"error": "Internal server error"}), 500
