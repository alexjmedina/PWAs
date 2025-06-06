"""
Browser Pool Module - KPIs Social Extractor (Optimized)

This module implements a browser pool for efficient browser instance management
and reuse, significantly reducing resource usage and improving performance.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from playwright.async_api import async_playwright, Browser, Page

from app.config.config import Config

# Configure logging
logger = logging.getLogger(__name__)

class BrowserPool:
    """
    Manages a pool of browser instances for efficient resource usage
    """
    
    def __init__(self, max_browsers: int = None):
        """
        Initialize the browser pool
        
        Args:
            max_browsers: Maximum number of browser instances to keep in the pool
        """
        self.config = Config()
        self.max_browsers = max_browsers or self.config.BROWSER_POOL_SIZE
        self.browsers = []
        self.semaphore = asyncio.Semaphore(self.max_browsers)
        self.playwright = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize the playwright instance"""
        if not self.initialized:
            self.playwright = await async_playwright().start()
            self.initialized = True
    
    async def get_browser(self) -> Browser:
        """
        Get a browser instance from the pool or create a new one
        
        Returns:
            Browser: Playwright browser instance
        """
        await self.initialize()
        await self.semaphore.acquire()
        
        if not self.browsers:
            # Create new browser instance with optimized settings
            browser = await self.playwright.chromium.launch(
                headless=self.config.HEADLESS,
                args=[
                    '--disable-gpu',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-accelerated-2d-canvas',
                    '--disable-infobars',
                    '--window-size=1280,800',
                    '--disable-extensions',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            logger.debug("Created new browser instance")
        else:
            browser = self.browsers.pop()
            logger.debug("Reusing browser instance from pool")
        
        return browser
    
    async def release_browser(self, browser: Browser):
        """
        Release a browser back to the pool
        
        Args:
            browser: Browser instance to release
        """
        # Check if browser is still connected
        try:
            # Simple check to see if browser is still usable
            contexts = browser.contexts
            
            # Add browser back to pool
            self.browsers.append(browser)
            logger.debug("Released browser back to pool")
        except Exception as e:
            logger.warning(f"Browser instance is no longer usable: {str(e)}")
            # Don't add back to pool, it will be garbage collected
        
        self.semaphore.release()
    
    async def create_page(self, user_agent: str = None, viewport: Dict[str, int] = None) -> Page:
        """
        Create a new page with anti-detection measures
        
        Args:
            user_agent: Custom user agent string
            viewport: Custom viewport dimensions
            
        Returns:
            Page: Playwright page object
        """
        browser = await self.get_browser()
        
        # Default viewport if not specified
        if viewport is None:
            viewport = {'width': 1280, 'height': 800}
        
        # Create context with anti-detection measures
        context = await browser.new_context(
            user_agent=user_agent,
            viewport=viewport,
            device_scale_factor=1,
        )
        
        # Add custom JavaScript to evade detection
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Overwrite the languages property to make it more realistic
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en', 'es'],
            });
            
            // Overwrite the plugins property
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
        """)
        
        # Create and return page
        page = await context.new_page()
        
        # Set page timeout
        page.set_default_timeout(self.config.PAGE_LOAD_TIMEOUT)
        
        return page
    
    async def close_page(self, page: Page):
        """
        Close a page and release its browser back to the pool
        
        Args:
            page: Page to close
        """
        browser = page.context.browser
        
        try:
            await page.context.close()
            await self.release_browser(browser)
        except Exception as e:
            logger.error(f"Error closing page: {str(e)}")
            # Try to release browser anyway
            try:
                await self.release_browser(browser)
            except:
                pass
    
    async def close_all(self):
        """Close all browser instances in the pool"""
        logger.info(f"Closing all browsers in pool ({len(self.browsers)})")
        
        for browser in self.browsers:
            try:
                await browser.close()
            except Exception as e:
                logger.error(f"Error closing browser: {str(e)}")
        
        self.browsers = []
        
        # Close playwright if initialized
        if self.initialized and self.playwright:
            await self.playwright.stop()
            self.initialized = False
