"""
Instagram Extractor Module - KPIs Social Extractor

This module implements Instagram-specific extraction logic using the hybrid approach:
1. Instagram Graph API (when credentials are available)
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

class InstagramExtractor(BaseExtractor):
    """Instagram-specific implementation of the BaseExtractor"""
    
    def __init__(self):
        """Initialize the Instagram extractor"""
        super().__init__()
        self.api_key = self.config.INSTAGRAM_API_KEY
        self.human_simulation = HumanSimulation()
        self.user_agent = UserAgent()
    
    def extract_followers(self, url: str) -> Optional[int]:
        """
        Extract followers count from an Instagram profile
        
        Args:
            url: URL of the Instagram profile
            
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
                logger.error(f"Instagram API extraction failed: {str(e)}")
        
        # Level 2: Try web scraping
        try:
            return self._extract_followers_via_scraping(url)
        except Exception as e:
            logger.error(f"Error scraping Instagram profile: {str(e)}")
            return None
    
    def extract_engagement(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract engagement metrics from an Instagram profile
        
        Args:
            url: URL of the Instagram profile
            
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
                logger.error(f"Instagram API engagement extraction failed: {str(e)}")
        
        # Level 2: Try web scraping
        try:
            return self._extract_engagement_via_scraping(url)
        except Exception as e:
            logger.error(f"Error scraping Instagram engagement: {str(e)}")
            return None
    
    def _extract_followers_via_api(self, url: str) -> Optional[int]:
        """
        Extract followers count using the Instagram Graph API
        
        Args:
            url: URL of the Instagram profile
            
        Returns:
            int: Number of followers or None if extraction fails
        """
        # Extract username from URL
        username = self._extract_username_from_url(url)
        if not username:
            logger.error("Could not extract Instagram username from URL")
            return None
        
        # Make API request (using Facebook Graph API for Instagram)
        api_url = f"https://graph.facebook.com/v18.0/instagram_oembed"
        params = {
            "url": url,
            "access_token": self.api_key
        }
        
        response = requests.get(api_url, params=params)
        if response.status_code != 200:
            logger.error(f"Instagram API request failed: {response.text}")
            return None
        
        # The oembed endpoint doesn't provide follower count directly
        # We need to use the Instagram Business Account ID to get this info
        # This is a simplified example and would need proper Instagram Business API setup
        
        logger.warning("Instagram API does not provide follower count through public endpoints")
        return None
    
    def _extract_engagement_via_api(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract engagement metrics using the Instagram Graph API
        
        Args:
            url: URL of the Instagram profile
            
        Returns:
            dict: Engagement metrics or None if extraction fails
        """
        # Extract username from URL
        username = self._extract_username_from_url(url)
        if not username:
            logger.error("Could not extract Instagram username from URL")
            return None
        
        # Instagram Graph API requires business account permissions
        # This is a simplified example and would need proper Instagram Business API setup
        
        logger.warning("Instagram API does not provide engagement metrics through public endpoints")
        return None
    
    def _extract_followers_via_scraping(self, url: str) -> Optional[int]:
        """
        Extract followers count using web scraping with Playwright
        
        Args:
            url: URL of the Instagram profile
            
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
                
                # Navigate to the Instagram profile
                logger.info(f"Navigating to Instagram profile: {url}")
                page.goto(url, wait_until="networkidle")
                
                # Simulate human-like behavior
                self.human_simulation.simulate_random_mouse_movement(page)
                self.random_delay(2, 4)
                
                # Handle cookie consent if it appears
                if page.locator('[data-testid="cookie-policy-dialog"]').count() > 0:
                    logger.info("Handling cookie consent dialog")
                    page.click('[data-testid="cookie-policy-dialog-accept"]')
                    self.random_delay(1, 2)
                
                # Extract followers count using multiple methods
                followers = self._extract_followers_from_page(page)
                
                if followers is not None:
                    logger.info(f"Extracted {followers} followers from Instagram profile")
                    return followers
                
                # Try alternative method: extract from JSON data in page
                followers = self._extract_followers_from_json_data(page)
                
                if followers is not None:
                    logger.info(f"Extracted {followers} followers from Instagram JSON data")
                    return followers
                
                logger.warning("Could not extract followers from Instagram profile")
                return None
                
            except Exception as e:
                logger.error(f"Error in Instagram scraping: {str(e)}")
                raise
            finally:
                browser.close()
    
    def _extract_engagement_via_scraping(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract engagement metrics using web scraping with Playwright
        
        Args:
            url: URL of the Instagram profile
            
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
                
                # Navigate to the Instagram profile
                logger.info(f"Navigating to Instagram profile for engagement metrics: {url}")
                page.goto(url, wait_until="networkidle")
                
                # Simulate human-like behavior
                self.human_simulation.simulate_random_mouse_movement(page)
                self.random_delay(2, 4)
                
                # Handle cookie consent if it appears
                if page.locator('[data-testid="cookie-policy-dialog"]').count() > 0:
                    logger.info("Handling cookie consent dialog")
                    page.click('[data-testid="cookie-policy-dialog-accept"]')
                    self.random_delay(1, 2)
                
                # Extract post count
                post_count = self._extract_post_count(page)
                
                # Scroll down to load more posts
                self.human_simulation.simulate_scrolling(page, 3)
                
                # Extract engagement metrics from visible posts
                engagement_metrics = self._extract_engagement_from_posts(page)
                
                if engagement_metrics:
                    engagement_metrics["posts"] = post_count
                    logger.info(f"Extracted engagement metrics from Instagram profile")
                    return engagement_metrics
                
                logger.warning("Could not extract engagement metrics from Instagram profile")
                return None
                
            except Exception as e:
                logger.error(f"Error in Instagram engagement scraping: {str(e)}")
                raise
            finally:
                browser.close()
    
    def _extract_followers_from_page(self, page: Page) -> Optional[int]:
        """
        Extract followers count from the loaded Instagram page
        
        Args:
            page: Playwright page object
            
        Returns:
            int: Number of followers or None if extraction fails
        """
        # Try multiple selectors and approaches
        
        # Method 1: Look for meta tags
        try:
            meta_content = page.evaluate("""() => {
                const metaTags = document.querySelectorAll('meta[property="og:description"]');
                for (const tag of metaTags) {
                    return tag.getAttribute('content');
                }
                return null;
            }""")
            
            if meta_content:
                match = re.search(r'([\d,.]+)\s+[Ff]ollowers', meta_content)
                if match:
                    followers_str = match.group(1).replace(',', '').replace('.', '')
                    return int(followers_str)
        except Exception:
            pass
        
        # Method 2: Look for specific selectors
        try:
            # Instagram often uses different selectors, try multiple options
            selectors = [
                'a[href*="followers"] span',
                'a[href$="/followers/"] span',
                'ul li:nth-child(2) span',
                'section ul li:nth-child(2) span'
            ]
            
            for selector in selectors:
                if page.locator(selector).count() > 0:
                    followers_text = page.locator(selector).first.text_content()
                    if followers_text:
                        # Handle Instagram's abbreviated numbers (e.g., 1.2m, 45.3k)
                        followers_text = followers_text.strip().lower()
                        if 'k' in followers_text:
                            followers = float(followers_text.replace('k', '')) * 1000
                            return int(followers)
                        elif 'm' in followers_text:
                            followers = float(followers_text.replace('m', '')) * 1000000
                            return int(followers)
                        else:
                            # Try to extract numeric value
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
                    if (text && text.includes('followers')) {
                        const match = text.match(/([\d,.]+)[\\s]*followers/i);
                        if (match && match[1]) {
                            let count = match[1].replace(/,/g, '');
                            if (count.includes('k')) {
                                return Math.round(parseFloat(count.replace('k', '')) * 1000);
                            } else if (count.includes('m')) {
                                return Math.round(parseFloat(count.replace('m', '')) * 1000000);
                            } else {
                                return parseInt(count);
                            }
                        }
                    }
                }
                return null;
            }""")
            
            if followers:
                return followers
        except Exception:
            pass
        
        return None
    
    def _extract_followers_from_json_data(self, page: Page) -> Optional[int]:
        """
        Extract followers count from JSON data embedded in the page
        
        Args:
            page: Playwright page object
            
        Returns:
            int: Number of followers or None if extraction fails
        """
        try:
            # Instagram often embeds profile data in a JSON script tag
            json_data = page.evaluate("""() => {
                const scriptTags = document.querySelectorAll('script[type="application/ld+json"]');
                for (const tag of scriptTags) {
                    try {
                        const data = JSON.parse(tag.textContent);
                        if (data && data.mainEntityofPage && data.mainEntityofPage.interactionStatistic) {
                            return data;
                        }
                    } catch (e) {
                        continue;
                    }
                }
                
                // Try to find data in other script tags
                const allScripts = document.querySelectorAll('script');
                for (const script of allScripts) {
                    const content = script.textContent;
                    if (content && content.includes('edge_followed_by') && content.includes('count')) {
                        const match = content.match(/"edge_followed_by":\\s*?\\{"count":\\s*(\\d+)\\}/);
                        if (match && match[1]) {
                            return { followerCount: parseInt(match[1]) };
                        }
                    }
                }
                
                return null;
            }""")
            
            if json_data and 'followerCount' in json_data:
                return json_data['followerCount']
            
            if json_data and 'mainEntityofPage' in json_data:
                for stat in json_data['mainEntityofPage'].get('interactionStatistic', []):
                    if stat.get('name') == 'followers':
                        return stat.get('userInteractionCount')
        except Exception as e:
            logger.error(f"Error extracting followers from JSON data: {str(e)}")
        
        return None
    
    def _extract_post_count(self, page: Page) -> int:
        """
        Extract post count from the Instagram profile
        
        Args:
            page: Playwright page object
            
        Returns:
            int: Number of posts or 0 if extraction fails
        """
        try:
            # Try multiple methods to extract post count
            
            # Method 1: Look for specific selectors
            selectors = [
                'span:-has-text("posts")',
                'ul li:first-child span',
                'section ul li:first-child span'
            ]
            
            for selector in selectors:
                if page.locator(selector).count() > 0:
                    posts_text = page.locator(selector).first.text_content()
                    if posts_text:
                        match = re.search(r'([\d,]+)', posts_text)
                        if match:
                            posts_str = match.group(1).replace(',', '')
                            return int(posts_str)
            
            # Method 2: Count visible posts
            post_count = page.locator('article a').count()
            if post_count > 0:
                return post_count
            
            # Method 3: Extract from JSON data
            post_count = page.evaluate("""() => {
                const scriptTags = document.querySelectorAll('script');
                for (const tag of scriptTags) {
                    const content = tag.textContent;
                    if (content && content.includes('edge_owner_to_timeline_media') && content.includes('count')) {
                        const match = content.match(/"edge_owner_to_timeline_media":\\s*?\\{"count":\\s*(\\d+)\\}/);
                        if (match && match[1]) {
                            return parseInt(match[1]);
                        }
                    }
                }
                return 0;
            }""")
            
            return post_count or 0
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
                // Find all post links
                const postLinks = Array.from(document.querySelectorAll('article a'));
                if (postLinks.length === 0) return null;
                
                // We can't directly access likes/comments without clicking each post
                // For Instagram, we'll estimate based on visible data or return placeholder
                
                return {
                    avg_likes: null,
                    avg_comments: null,
                    total_engagement: null,
                    note: "Instagram requires clicking each post to view engagement metrics"
                };
            }""")
            
            # For Instagram, we need to click on posts to see engagement metrics
            # This is a simplified version that returns estimated metrics
            
            # Click on the first post if available
            if page.locator('article a').count() > 0:
                # Click the first post
                page.locator('article a').first.click()
                self.random_delay(2, 3)
                
                # Extract likes and comments from the post modal
                likes = self._extract_likes_from_post_modal(page)
                comments = self._extract_comments_from_post_modal(page)
                
                # Close the modal
                page.keyboard.press('Escape')
                self.random_delay(1, 2)
                
                if likes is not None or comments is not None:
                    return {
                        "avg_likes": likes or 0,
                        "avg_comments": comments or 0,
                        "total_engagement": (likes or 0) + (comments or 0)
                    }
            
            return engagement_data
        except Exception as e:
            logger.error(f"Error extracting engagement from posts: {str(e)}")
            return None
    
    def _extract_likes_from_post_modal(self, page: Page) -> Optional[int]:
        """
        Extract likes count from an Instagram post modal
        
        Args:
            page: Playwright page object
            
        Returns:
            int: Number of likes or None if extraction fails
        """
        try:
            # Try multiple selectors for likes
            selectors = [
                'section span:-has-text("likes")',
                'section span:-has-text("like this")',
                'section span[class*="like"]'
            ]
            
            for selector in selectors:
                if page.locator(selector).count() > 0:
                    likes_text = page.locator(selector).first.text_content()
                    if likes_text:
                        match = re.search(r'([\d,]+)', likes_text)
                        if match:
                            likes_str = match.group(1).replace(',', '')
                            return int(likes_str)
            
            # Try JavaScript extraction
            likes = page.evaluate("""() => {
                const elements = Array.from(document.querySelectorAll('*'));
                for (const el of elements) {
                    const text = el.textContent;
                    if (text && (text.includes('likes') || text.includes('like this'))) {
                        const match = text.match(/([\d,]+)/);
                        if (match && match[1]) {
                            return parseInt(match[1].replace(/,/g, ''));
                        }
                    }
                }
                return null;
            }""")
            
            return likes
        except Exception:
            return None
    
    def _extract_comments_from_post_modal(self, page: Page) -> Optional[int]:
        """
        Extract comments count from an Instagram post modal
        
        Args:
            page: Playwright page object
            
        Returns:
            int: Number of comments or None if extraction fails
        """
        try:
            # Try multiple selectors for comments
            selectors = [
                'span:-has-text("comments")',
                'span:-has-text("comment")',
                'a[href*="comments"]'
            ]
            
            for selector in selectors:
                if page.locator(selector).count() > 0:
                    comments_text = page.locator(selector).first.text_content()
                    if comments_text:
                        match = re.search(r'([\d,]+)', comments_text)
                        if match:
                            comments_str = match.group(1).replace(',', '')
                            return int(comments_str)
            
            # Count visible comments
            comments_count = page.locator('ul > li').count()
            if comments_count > 0:
                return comments_count
            
            # Try JavaScript extraction
            comments = page.evaluate("""() => {
                const elements = Array.from(document.querySelectorAll('*'));
                for (const el of elements) {
                    const text = el.textContent;
                    if (text && text.includes('comments')) {
                        const match = text.match(/([\d,]+)/);
                        if (match && match[1]) {
                            return parseInt(match[1].replace(/,/g, ''));
                        }
                    }
                }
                return null;
            }""")
            
            return comments
        except Exception:
            return None
    
    def _extract_username_from_url(self, url: str) -> Optional[str]:
        """
        Extract Instagram username from URL
        
        Args:
            url: URL of the Instagram profile
            
        Returns:
            str: Username or None if extraction fails
        """
        # Try to extract from URL patterns
        patterns = [
            r'instagram\.com/([^/]+)/?$',
            r'instagram\.com/([^/]+)/$',
            r'instagram\.com/([^/]+)/\?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                username = match.group(1)
                # Filter out non-username paths
                if username not in ['p', 'explore', 'reels', 'stories']:
                    return username
        
        return None
