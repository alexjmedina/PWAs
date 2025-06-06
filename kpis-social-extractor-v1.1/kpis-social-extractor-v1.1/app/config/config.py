"""
Configuration Module - KPIs Social Extractor (Optimized)

This module provides centralized configuration management with support for
environment variables, configuration files, and runtime overrides.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Config:
    """
    Configuration class for KPIs Social Extractor
    Provides centralized access to all configuration settings
    """
    
    # Default configuration values
    DEFAULT_CONFIG = {
        # API Keys and Authentication
        "FACEBOOK_API_KEY": None,
        "INSTAGRAM_API_KEY": None,
        "TWITTER_API_KEY": None,
        "YOUTUBE_API_KEY": None,
        "LINKEDIN_API_KEY": None,
        "TIKTOK_API_KEY": None,
        
        # Browser and Scraping Settings
        "HEADLESS": True,
        "BROWSER_TIMEOUT": 30000,  # milliseconds
        "MAX_RETRIES": 3,
        "BROWSER_POOL_SIZE": 3,
        "PAGE_LOAD_TIMEOUT": 60000,  # milliseconds
        
        # Proxy Settings
        "USE_PROXIES": False,
        "PROXY_LIST": [],
        "PROXY_ROTATION_STRATEGY": "round_robin",  # round_robin, random
        
        # Rate Limiting
        "RATE_LIMIT_ENABLED": True,
        "REQUESTS_PER_MINUTE": 10,
        "RATE_LIMIT_STRATEGY": "token_bucket",  # token_bucket, leaky_bucket
        
        # Caching
        "CACHE_ENABLED": True,
        "CACHE_TTL": 3600,  # seconds
        "CACHE_BACKEND": "memory",  # memory, redis, file
        "CACHE_REDIS_URL": "redis://localhost:6379/0",
        "CACHE_DIR": ".cache",
        
        # Extraction Settings
        "PARALLEL_EXTRACTION": True,
        "MAX_CONCURRENT_EXTRACTIONS": 3,
        "EXTRACTION_TIMEOUT": 300,  # seconds
        
        # Human Simulation
        "HUMAN_SIMULATION_LEVEL": "medium",  # low, medium, high
        "SCROLL_COUNT": 3,
        "MIN_DELAY": 1.0,  # seconds
        "MAX_DELAY": 3.0,  # seconds
        
        # Logging and Monitoring
        "LOG_LEVEL": "INFO",
        "PERFORMANCE_MONITORING": True,
        "ERROR_REPORTING": True,
        
        # API and Web Interface
        "API_RATE_LIMIT": 100,  # requests per hour
        "ENABLE_CORS": True,
        "ALLOWED_ORIGINS": ["*"],
        "API_VERSION": "v1",
        
        # Development Settings
        "DEBUG": False,
        "TESTING": False
    }
    
    def __init__(self):
        """Initialize configuration with values from environment and files"""
        self._config = self.DEFAULT_CONFIG.copy()
        self._load_from_env()
        self._load_from_file()
        self._validate()
        
        # Set up logging based on configuration
        logging.getLogger().setLevel(getattr(logging, self._config["LOG_LEVEL"]))
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        for key in self._config:
            env_value = os.getenv(key)
            if env_value is not None:
                # Convert string values to appropriate types
                if isinstance(self._config[key], bool):
                    self._config[key] = env_value.lower() in ('true', 'yes', '1')
                elif isinstance(self._config[key], int):
                    try:
                        self._config[key] = int(env_value)
                    except ValueError:
                        logger.warning(f"Invalid integer value for {key}: {env_value}")
                elif isinstance(self._config[key], float):
                    try:
                        self._config[key] = float(env_value)
                    except ValueError:
                        logger.warning(f"Invalid float value for {key}: {env_value}")
                elif isinstance(self._config[key], list):
                    try:
                        self._config[key] = json.loads(env_value)
                    except json.JSONDecodeError:
                        # Fallback to comma-separated list
                        self._config[key] = [item.strip() for item in env_value.split(',')]
                else:
                    self._config[key] = env_value
    
    def _load_from_file(self):
        """Load configuration from JSON file if it exists"""
        config_file = os.getenv("CONFIG_FILE", "config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    file_config = json.load(f)
                    for key, value in file_config.items():
                        if key in self._config:
                            self._config[key] = value
                logger.info(f"Loaded configuration from {config_file}")
            except Exception as e:
                logger.error(f"Error loading configuration from {config_file}: {str(e)}")
    
    def _validate(self):
        """Validate configuration values and log warnings for missing credentials"""
        # Check API keys and log warnings
        for platform in ["FACEBOOK", "INSTAGRAM", "TWITTER", "YOUTUBE", "LINKEDIN", "TIKTOK"]:
            key_name = f"{platform}_API_KEY"
            if not self._config.get(key_name):
                logger.warning(f"{platform} API key not provided. Scraping will be used instead.")
        
        # Validate numeric values
        for key in ["BROWSER_TIMEOUT", "MAX_RETRIES", "CACHE_TTL", "EXTRACTION_TIMEOUT"]:
            if self._config[key] <= 0:
                logger.warning(f"Invalid value for {key}: {self._config[key]}. Using default.")
                self._config[key] = self.DEFAULT_CONFIG[key]
    
    def __getattr__(self, name):
        """Allow attribute-style access to configuration values"""
        if name in self._config:
            return self._config[name]
        raise AttributeError(f"Configuration has no attribute '{name}'")
    
    def get(self, key, default=None):
        """Get configuration value with optional default"""
        return self._config.get(key, default)
    
    def update(self, updates: Dict[str, Any]):
        """Update configuration at runtime"""
        for key, value in updates.items():
            if key in self._config:
                self._config[key] = value
                logger.debug(f"Updated configuration: {key}={value}")
            else:
                logger.warning(f"Ignored unknown configuration key: {key}")
    
    def get_available_methods(self, platform: str) -> List[str]:
        """
        Get available extraction methods for a platform
        
        Args:
            platform: Platform name (e.g., 'facebook', 'instagram')
            
        Returns:
            list: Available extraction methods in priority order
        """
        methods = []
        
        # Check if API is available
        key_name = f"{platform.upper()}_API_KEY"
        if self._config.get(key_name):
            methods.append("api")
        
        # Always include scraping and simulation
        methods.append("scraping")
        methods.append("simulation")
        
        return methods
    
    def get_proxy(self, strategy=None):
        """
        Get a proxy based on the configured rotation strategy
        
        Args:
            strategy: Override the default proxy rotation strategy
            
        Returns:
            str: Proxy URL or None if proxies are disabled
        """
        if not self._config["USE_PROXIES"] or not self._config["PROXY_LIST"]:
            return None
        
        strategy = strategy or self._config["PROXY_ROTATION_STRATEGY"]
        proxies = self._config["PROXY_LIST"]
        
        if strategy == "random":
            import random
            return random.choice(proxies)
        else:  # round_robin
            # Simple round-robin implementation
            proxy = proxies[0]
            self._config["PROXY_LIST"] = proxies[1:] + [proxies[0]]
            return proxy
    
    def to_dict(self):
        """Return configuration as dictionary"""
        return self._config.copy()
    
    def get_safe_dict(self):
        """Return configuration as dictionary with sensitive values redacted"""
        safe_config = self._config.copy()
        
        # Redact sensitive values
        for key in safe_config:
            if "API_KEY" in key and safe_config[key]:
                safe_config[key] = "********"
        
        return safe_config
