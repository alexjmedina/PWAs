"""
Configuration settings for KPIs Social Extractor
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

class Config:
    """Base configuration class"""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    DEBUG = False
    TESTING = False
    
    # API keys and tokens
    META_ACCESS_TOKEN = os.environ.get('META_ACCESS_TOKEN')
    TWITTER_API_KEY = os.environ.get('TWITTER_API_KEY')      
    TWITTER_API_SECRET = os.environ.get('TWITTER_API_SECRET')
    YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
    LINKEDIN_API_KEY = os.environ.get('LINKEDIN_API_KEY')
    TIKTOK_API_KEY = os.environ.get('TIKTOK_API_KEY')
    
    # Proxy settings
    USE_PROXIES = os.environ.get('USE_PROXIES', 'False').lower() == 'true'
    PROXY_LIST = os.environ.get('PROXY_LIST', '').split(',') if os.environ.get('PROXY_LIST') else []
    PROXY_USERNAME = os.environ.get('PROXY_USERNAME')
    PROXY_PASSWORD = os.environ.get('PROXY_PASSWORD')
    
    # Browser automation settings
    HEADLESS = os.environ.get('HEADLESS', 'True').lower() == 'true'
    BROWSER_TIMEOUT = int(os.environ.get('BROWSER_TIMEOUT', 30))
    MAX_RETRIES = int(os.environ.get('MAX_RETRIES', 3))
    
    # Cache settings
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300))
    
    # Rate limiting
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '200 per day, 50 per hour')
    
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    
class ProductionConfig(Config):
    """Production configuration"""
    # Production-specific settings
    pass

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
