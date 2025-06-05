"""
Facebook Extractor Module - KPIs Social Extractor

This module implements Facebook-specific extraction logic using the hybrid approach:
1. Facebook Graph API (when credentials are available)
2. Advanced web scraping with Playwright
3. Human-like simulation for anti-detection
"""

import re
import json
import logging
import time
from typing import Dict, Any, Optional, List, Tuple

import requests
from playwright.sync_api import sync_playwright, Page, Browser
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from app.extractors.base_extractor import BaseExtractor
from app.utils.human_simulation import HumanSimulation

# Configure logging
logger = logging.getLogger(__name__)

class FacebookExtractor(BaseExtractor):
    """Facebook-specific implementation of the BaseExtractor"""
    
    def __init__(self):
        """Initialize the Facebook extractor"""
        super().__init__()
        self.api_key = self.config.FACEBOOK_API_KEY
        self.human_simulation = HumanSimulation()
        self.user_agent = UserAgent()
    
    def extract_followers(self, url: str) -> Optional[int]:
        """
        Extract followers count from a Facebook page
        
        Args:
            url: URL of the Facebook page
            
        Returns:
            int: Number of followers or None if extraction fails
        """
        # Level 1: Try API extraction if credentials are available
        if self.api_key:
            try:
                followers = self._extract_followers_via_api(url)
                if followers is not None:
                    return followers
            except Exception as e:
                logger.error(f"Facebook API extraction failed: {str(e)}")
        
        # Level 2: Try web scraping
        try:
            return self._extract_followers_via_scraping(url)
        except Exception as e:
            logger.error(f"Error scraping Facebook page: {str(e)}")
            return None
    
    def extract_engagement(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract engagement metrics from a Facebook page
        
        Args:
            url: URL of the Facebook page
            
        Returns:
            dict: Engagement metrics or None if extraction fails
        """
        # Level 1: Try API extraction if credentials are available
        if self.api_key:
            try:
                engagement = self._extract_engagement_via_api(url)
                if engagement is not None:
                    return engagement
            except Exception as e:
                logger.error(f"Facebook API engagement extraction failed: {str(e)}")
        
        # Level 2: Try web scraping
        try:
            return self._extract_engagement_via_scraping(url)
        except Exception as e:
            logger.error(f"Error scraping Facebook engagement: {str(e)}")
            return None
    
    def _extract_followers_via_api(self, url: str) -> Optional[int]:
        """
        Extract followers count using the Facebook Graph API
        
        Args:
            url: URL of the Facebook page
            
        Returns:
            int: Number of followers or None if extraction fails
        """
        # Extract page ID from URL
        page_id = self._extract_page_id_from_url(url)
        if not page_id:
            logger.error("Could not extract Facebook page ID from URL")
            return None
        
        # Make API request
        api_url = f"https://graph.facebook.com/v18.0/{page_id}"
        params = {
            "fields": "fan_count",
            "access_token": self.api_key
        }
        
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if "fan_count" in data:
                return data["fan_count"]
        
        logger.error(f"Facebook API request failed: {response.text}")
        return None
    
    def _extract_engagement_via_api(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract engagement metrics using the Facebook Graph API
        
        Args:
            url: URL of the Facebook page
            
        Returns:
            dict: Engagement metrics or None if extraction fails
        """
        # Extract page ID from URL
        page_id = self._extract_page_id_from_url(url)
        if not page_id:
            logger.error("Could not extract Facebook page ID from URL")
            return None
        
        # Make API request for posts
        api_url = f"https://graph.facebook.com/v18.0/{page_id}/posts"
        params = {
            "fields": "id,likes.summary(true),comments.summary(true),shares",
            "limit": 10,
            "access_token": self.api_key
        }
        
        response = requests.get(api_url, params=params)
        if response.status_code != 200:
            logger.error(f"Facebook API request failed: {response.text}")
            return None
        
        data = response.json()
        if "data" not in data or not data["data"]:
            logger.error("No posts found in Facebook API response")
            return None
        
        # Calculate engagement metrics
        posts = data["data"]
        total_likes = 0
        total_comments = 0
        total_shares = 0
        post_count = len(posts)
        
        for post in posts:
            # Extract likes
            if "likes" in post and "summary" in post["likes"]:
                total_likes += post["likes"]["summary"].get("total_count", 0)
            
            # Extract comments
            if "comments" in post and "summary" in post["comments"]:
                total_comments += post["comments"]["summary"].get("total_count", 0)
            
            # Extract shares
            if "shares" in post:
                total_shares += post["shares"].get("count", 0)
        
        # Calculate averages
        avg_likes = round(total_likes / post_count) if post_count > 0 else 0
        avg_comments = round(total_comments / post_count) if post_count > 0 else 0
        avg_shares = round(total_shares / post_count) if post_count > 0 else 0
        
        return {
            "posts": post_count,
            "avg_likes": avg_likes,
            "avg_comments": avg_comments,
            "avg_shares": avg_shares,
            "total_engagement": avg_likes + avg_comments + avg_shares
        }
    
    def _extract_followers_via_scraping(self, url: str) -> Optional[int]:
        """
        Extract followers count using web scraping with Playwright
        
        Args:
            url: URL of the Facebook page
            
        Returns:
            int: Number of followers or None if extraction fails
        """
        with sync_playwright() as playwright:
            # Launch browser with anti-detection measures
            browser_type = playwright.chromium
            browser = browser_type.launch(
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-site-isolation-trials'
                ]
            )
            
            try:
                # Create a new context with a custom user agent
                context = browser.new_context(
                    user_agent=self.user_agent.random,
                    viewport={'width': 1280, 'height': 800},
                    device_scale_factor=1,
                )
                
                # Add custom JavaScript to evade detection
                context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """)
                
                # Create a new page
                page = context.new_page()
                
                # Navigate to the Facebook page
                logger.info(f"Navigating to Facebook page: {url}")
                page.goto(url, wait_until="networkidle")
                
                # Simulate human-like behavior
                self.human_simulation.simulate_random_mouse_movement(page)
                self.random_delay(2, 4)
                
                # Handle cookie consent if it appears
                if page.locator('[data-testid="cookie-policy-manage-dialog"]').count() > 0:
                    logger.info("Handling cookie consent dialog")
                    page.click('button[data-testid="cookie-policy-manage-dialog-accept-button"]')
                    self.random_delay(1, 2)
                
                # Extract followers count using multiple selectors and methods
                followers = self._extract_followers_from_page(page)
                
                if followers is not None:
                    logger.info(f"Extracted {followers} followers from Facebook page")
                    return followers
                
                logger.warning("Could not extract followers from Facebook page")
                return None
                
            except Exception as e:
                logger.error(f"Error initializing browser: {str(e)}")
                raise
            finally:
                browser.close()
    
    def _extract_engagement_via_scraping(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract engagement metrics using web scraping with Playwright
        
        Args:
            url: URL of the Facebook page
            
        Returns:
            dict: Engagement metrics or None if extraction fails
        """
        with sync_playwright() as playwright:
            # Launch browser with anti-detection measures
            browser_type = playwright.chromium
            browser = browser_type.launch(
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-site-isolation-trials'
                ]
            )
            
            try:
                # Create a new context with a custom user agent
                context = browser.new_context(
                    user_agent=self.user_agent.random,
                    viewport={'width': 1280, 'height': 800},
                    device_scale_factor=1,
                )
                
                # Add custom JavaScript to evade detection
                context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """)
                
                # Create a new page
                page = context.new_page()
                
                # Navigate to the Facebook page
                logger.info(f"Navigating to Facebook page for engagement metrics: {url}")
                page.goto(url, wait_until="networkidle")
                
                # Simulate human-like behavior
                self.human_simulation.simulate_random_mouse_movement(page)
                self.random_delay(2, 4)
                
                # Handle cookie consent if it appears
                if page.locator('[data-testid="cookie-policy-manage-dialog"]').count() > 0:
                    logger.info("Handling cookie consent dialog")
                    page.click('button[data-testid="cookie-policy-manage-dialog-accept-button"]')
                    self.random_delay(1, 2)
                
                # Scroll down to load more posts
                self.human_simulation.simulate_scrolling(page, 3)
                
                # Extract post count
                post_count = self._extract_post_count(page)
                
                # Extract engagement metrics from visible posts
                engagement_metrics = self._extract_engagement_from_posts(page)
                
                if engagement_metrics:
                    engagement_metrics["posts"] = post_count
                    logger.info(f"Extracted engagement metrics from Facebook page")
                    return engagement_metrics
                
                logger.warning("Could not extract engagement metrics from Facebook page")
                return None
                
            except Exception as e:
                logger.error(f"Error in Facebook engagement scraping: {str(e)}")
                raise
            finally:
                browser.close()
    
    def _extract_followers_from_page(self, page: Page) -> Optional[int]:
        """
        Extract followers count from the loaded Facebook page
        
        Args:
            page: Playwright page object
            
        Returns:
            int: Number of followers or None if extraction fails
        """
        # Try multiple selectors and approaches
        
        # Method 1: Look for "people follow this" text
        try:
            follow_text = page.locator('text=/[0-9,.]+\s+people follow this/i').first.text_content()
            if follow_text:
                match = re.search(r'([\d,]+)\s+people follow this', follow_text, re.IGNORECASE)
                if match:
                    followers_str = match.group(1).replace(',', '')
                    return int(followers_str)
        except Exception:
            pass
        
        # Method 2: Look for specific selectors
        try:
            followers_element = page.locator('div[aria-label*="followers"]').first
            if followers_element:
                followers_text = followers_element.text_content()
                if followers_text:
                    match = re.search(r'([\d,]+)', followers_text)
                    if match:
                        followers_str = match.group(1).replace(',', '')
                        return int(followers_str)
        except Exception:
            pass
        
        # Method 3: Use JavaScript to extract from page content
        try:
            followers = page.evaluate("""() => {
                // Look for text containing followers count
                const elements = Array.from(document.querySelectorAll('*'));
                for (const el of elements) {
                    const text = el.textContent;
                    if (text && text.includes('people follow this')) {
                        const match = text.match(/([\d,]+)\s+people follow this/i);
                        if (match && match[1]) {
                            return parseInt(match[1].replace(/,/g, ''));
                        }
                    }
                    if (text && text.includes('followers')) {
                        const match = text.match(/([\d,]+)\s+followers/i);
                        if (match && match[1]) {
                            return parseInt(match[1].replace(/,/g, ''));
                        }
                    }
                }
                return null;
            }""")
            
            if followers:
                return followers
        except Exception:
            pass
        
        # Method 4: Extract from page HTML
        try:
            html_content = page.content()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for text containing followers
            for element in soup.find_all(text=re.compile(r'([\d,]+)\s+people follow this', re.IGNORECASE)):
                match = re.search(r'([\d,]+)\s+people follow this', element, re.IGNORECASE)
                if match:
                    followers_str = match.group(1).replace(',', '')
                    return int(followers_str)
            
            # Look for text containing followers (alternative format)
            for element in soup.find_all(text=re.compile(r'([\d,]+)\s+followers', re.IGNORECASE)):
                match = re.search(r'([\d,]+)\s+followers', element, re.IGNORECASE)
                if match:
                    followers_str = match.group(1).replace(',', '')
                    return int(followers_str)
        except Exception:
            pass
        
        return None
    
    def _extract_post_count(self, page: Page) -> int:
        """
        Extract post count from the Facebook page
        
        Args:
            page: Playwright page object
            
        Returns:
            int: Number of posts or 0 if extraction fails
        """
        try:
            # Count visible posts
            post_count = page.locator('div[role="article"]').count()
            return post_count
        except Exception:
            return 0
    
    def _extract_engagement_from_posts(self, page: Page) -> Optional[Dict[str, Any]]:
        """
        Extract engagement metrics from visible posts
        
        Args:
            page: Playwright page object
            
        Returns:
            dict: Engagement metrics or None if extraction fails
        """
        try:
            # Use JavaScript to extract engagement metrics
            engagement_data = page.evaluate("""() => {
                const posts = Array.from(document.querySelectorAll('div[role="article"]'));
                if (posts.length === 0) return null;
                
                let totalLikes = 0;
                let totalComments = 0;
                let totalShares = 0;
                let postsWithMetrics = 0;
                
                posts.forEach(post => {
                    // Extract likes
                    const likeElements = post.querySelectorAll('span[aria-label*="Like"]');
                    likeElements.forEach(el => {
                        const text = el.textContent;
                        if (text && /\\d/.test(text)) {
                            const match = text.match(/(\\d+[KkMm]?)/);
                            if (match && match[1]) {
                                let likes = parseInt(match[1].replace(/[KkMm]/g, ''));
                                if (match[1].match(/[Kk]/)) likes *= 1000;
                                if (match[1].match(/[Mm]/)) likes *= 1000000;
                                totalLikes += likes;
                                postsWithMetrics++;
                            }
                        }
                    });
                    
                    // Extract comments
                    const commentElements = post.querySelectorAll('span[aria-label*="comment"]');
                    commentElements.forEach(el => {
                        const text = el.textContent;
                        if (text && /\\d/.test(text)) {
                            const match = text.match(/(\\d+[KkMm]?)/);
                            if (match && match[1]) {
                                let comments = parseInt(match[1].replace(/[KkMm]/g, ''));
                                if (match[1].match(/[Kk]/)) comments *= 1000;
                                if (match[1].match(/[Mm]/)) comments *= 1000000;
                                totalComments += comments;
                            }
                        }
                    });
                    
                    // Extract shares
                    const shareElements = post.querySelectorAll('span[aria-label*="share"]');
                    shareElements.forEach(el => {
                        const text = el.textContent;
                        if (text && /\\d/.test(text)) {
                            const match = text.match(/(\\d+[KkMm]?)/);
                            if (match && match[1]) {
                                let shares = parseInt(match[1].replace(/[KkMm]/g, ''));
                                if (match[1].match(/[Kk]/)) shares *= 1000;
                                if (match[1].match(/[Mm]/)) shares *= 1000000;
                                totalShares += shares;
                            }
                        }
                    });
                });
                
                // Calculate averages
                const avgLikes = postsWithMetrics > 0 ? Math.round(totalLikes / postsWithMetrics) : 0;
                const avgComments = postsWithMetrics > 0 ? Math.round(totalComments / postsWithMetrics) : 0;
                const avgShares = postsWithMetrics > 0 ? Math.round(totalShares / postsWithMetrics) : 0;
                
                return {
                    avg_likes: avgLikes,
                    avg_comments: avgComments,
                    avg_shares: avgShares,
                    total_engagement: avgLikes + avgComments + avgShares
                };
            }""")
            
            return engagement_data
        except Exception as e:
            logger.error(f"Error extracting engagement from posts: {str(e)}")
            return None
    
    def _extract_page_id_from_url(self, url: str) -> Optional[str]:
        """
        Extract Facebook page ID from URL
        
        Args:
            url: URL of the Facebook page
            
        Returns:
            str: Page ID or None if extraction fails
        """
        # Try to extract from URL patterns
        patterns = [
            r'facebook\.com/([^/]+)/?$',
            r'facebook\.com/pg/([^/]+)/?',
            r'facebook\.com/([^/]+)/about/?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
