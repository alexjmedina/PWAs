"""
TikTok Extractor Module - KPIs Social Extractor

This module implements TikTok-specific extraction logic using the hybrid approach:
1. TikTok API (when credentials are available)
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

class TikTokExtractor(BaseExtractor):
    """TikTok-specific implementation of the BaseExtractor"""
    
    def __init__(self):
        """Initialize the TikTok extractor"""
        super().__init__()
        self.api_key = self.config.TIKTOK_API_KEY
        self.human_simulation = HumanSimulation()
        self.user_agent = UserAgent()
    
    def extract_followers(self, url: str) -> Optional[int]:
        """
        Extract followers count from a TikTok profile
        
        Args:
            url: URL of the TikTok profile
            
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
                logger.error(f"TikTok API extraction failed: {str(e)}")
        
        # Level 2: Try web scraping
        try:
            return self._extract_followers_via_scraping(url)
        except Exception as e:
            logger.error(f"Error scraping TikTok profile: {str(e)}")
            return None
    
    def extract_engagement(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract engagement metrics from a TikTok profile
        
        Args:
            url: URL of the TikTok profile
            
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
                logger.error(f"TikTok API engagement extraction failed: {str(e)}")
        
        # Level 2: Try web scraping
        try:
            return self._extract_engagement_via_scraping(url)
        except Exception as e:
            logger.error(f"Error scraping TikTok engagement: {str(e)}")
            return None
    
    def _extract_followers_via_api(self, url: str) -> Optional[int]:
        """
        Extract followers count using the TikTok API
        
        Args:
            url: URL of the TikTok profile
            
        Returns:
            int: Number of followers or None if extraction fails
        """
        # Extract username from URL
        username = self._extract_username_from_url(url)
        if not username:
            logger.error("Could not extract TikTok username from URL")
            return None
        
        # TikTok API requires business account and proper permissions
        # This is a simplified example and would need proper TikTok API setup
        
        logger.warning("TikTok API requires business account and proper permissions")
        return None
    
    def _extract_engagement_via_api(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract engagement metrics using the TikTok API
        
        Args:
            url: URL of the TikTok profile
            
        Returns:
            dict: Engagement metrics or None if extraction fails
        """
        # Extract username from URL
        username = self._extract_username_from_url(url)
        if not username:
            logger.error("Could not extract TikTok username from URL")
            return None
        
        # TikTok API requires business account and proper permissions
        # This is a simplified example and would need proper TikTok API setup
        
        logger.warning("TikTok API requires business account and proper permissions")
        return None
    
    def _extract_followers_via_scraping(self, url: str) -> Optional[int]:
        """
        Extract followers count using web scraping with Playwright
        
        Args:
            url: URL of the TikTok profile
            
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
                
                # Navigate to the TikTok profile
                logger.info(f"Navigating to TikTok profile: {url}")
                page.goto(url, wait_until="networkidle")
                
                # Simulate human-like behavior
                self.human_simulation.simulate_random_mouse_movement(page)
                self.random_delay(2, 4)
                
                # Handle cookie consent if it appears
                if page.locator('button[data-e2e="cookie-banner-accept"]').count() > 0:
                    logger.info("Handling cookie consent dialog")
                    page.click('button[data-e2e="cookie-banner-accept"]')
                    self.random_delay(1, 2)
                
                # Extract followers count using multiple methods
                followers = self._extract_followers_from_page(page)
                
                if followers is not None:
                    logger.info(f"Extracted {followers} followers from TikTok profile")
                    return followers
                
                logger.warning("Could not extract followers from TikTok profile")
                return None
                
            except Exception as e:
                logger.error(f"Error in TikTok scraping: {str(e)}")
                raise
            finally:
                browser.close()
    
    def _extract_engagement_via_scraping(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract engagement metrics using web scraping with Playwright
        
        Args:
            url: URL of the TikTok profile
            
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
                
                # Navigate to the TikTok profile
                logger.info(f"Navigating to TikTok profile for engagement metrics: {url}")
                page.goto(url, wait_until="networkidle")
                
                # Simulate human-like behavior
                self.human_simulation.simulate_random_mouse_movement(page)
                self.random_delay(2, 4)
                
                # Handle cookie consent if it appears
                if page.locator('button[data-e2e="cookie-banner-accept"]').count() > 0:
                    logger.info("Handling cookie consent dialog")
                    page.click('button[data-e2e="cookie-banner-accept"]')
                    self.random_delay(1, 2)
                
                # Extract video count
                video_count = self._extract_video_count(page)
                
                # Scroll down to load more videos
                self.human_simulation.simulate_scrolling(page, 3)
                
                # Extract engagement metrics from visible videos
                engagement_metrics = self._extract_engagement_from_videos(page)
                
                if engagement_metrics:
                    engagement_metrics["posts"] = video_count
                    logger.info(f"Extracted engagement metrics from TikTok profile")
                    return engagement_metrics
                
                logger.warning("Could not extract engagement metrics from TikTok profile")
                return None
                
            except Exception as e:
                logger.error(f"Error in TikTok engagement scraping: {str(e)}")
                raise
            finally:
                browser.close()
    
    def _extract_followers_from_page(self, page: Page) -> Optional[int]:
        """
        Extract followers count from the loaded TikTok page
        
        Args:
            page: Playwright page object
            
        Returns:
            int: Number of followers or None if extraction fails
        """
        # Try multiple selectors and approaches
        
        # Method 1: Look for followers count in profile info
        try:
            selectors = [
                'strong[data-e2e="followers-count"]',
                'strong[title="Followers"]',
                'h2[data-e2e="followers-count"]',
                '[data-e2e="followers-count"]'
            ]
            
            for selector in selectors:
                if page.locator(selector).count() > 0:
                    followers_text = page.locator(selector).first.text_content()
                    if followers_text:
                        # Handle TikTok's abbreviated numbers (e.g., 1.2K, 45.3M)
                        followers_text = followers_text.strip().lower()
                        
                        if 'k' in followers_text:
                            followers = float(followers_text.replace('k', '')) * 1000
                            return int(followers)
                        elif 'm' in followers_text:
                            followers = float(followers_text.replace('m', '')) * 1000000
                            return int(followers)
                        else:
                            # Try to extract numeric value
                            match = re.search(r'([\d,\.]+)', followers_text)
                            if match:
                                followers_str = match.group(1).replace(',', '')
                                return int(float(followers_str))
        except Exception:
            pass
        
        # Method 2: Use JavaScript to extract from page content
        try:
            followers = page.evaluate("""() => {
                // Look for followers count
                const elements = document.querySelectorAll('strong, h2, span');
                for (const el of elements) {
                    const text = el.textContent.trim();
                    if (text) {
                        // Check if this is a followers element
                        const nextSibling = el.nextSibling;
                        if (nextSibling && nextSibling.textContent && nextSibling.textContent.includes('Followers')) {
                            if (text.includes('K') || text.includes('k')) {
                                return Math.round(parseFloat(text.replace(/[^\\d\\.]/g, '')) * 1000);
                            } else if (text.includes('M') || text.includes('m')) {
                                return Math.round(parseFloat(text.replace(/[^\\d\\.]/g, '')) * 1000000);
                            } else {
                                return parseInt(text.replace(/[^\\d]/g, ''));
                            }
                        }
                    }
                }
                
                // Look for any element containing follower information
                const allElements = Array.from(document.querySelectorAll('*'));
                for (const el of allElements) {
                    const text = el.textContent;
                    if (text && text.includes('Followers')) {
                        const match = text.match(/([\d,\\.]+)[KkMm]?\\s+Followers/);
                        if (match && match[1]) {
                            let count = match[1].replace(/,/g, '');
                            if (text.includes('K') || text.includes('k')) {
                                return Math.round(parseFloat(count) * 1000);
                            } else if (text.includes('M') || text.includes('m')) {
                                return Math.round(parseFloat(count) * 1000000);
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
        
        # Method 3: Extract from page HTML
        try:
            html_content = page.content()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for text containing followers
            for element in soup.find_all(text=re.compile(r'([\d,\.]+)[KkMm]?\s+[Ff]ollowers')):
                match = re.search(r'([\d,\.]+)[KkMm]?\s+[Ff]ollowers', element)
                if match:
                    followers_str = match.group(1).replace(',', '')
                    if 'k' in element.lower():
                        return int(float(followers_str) * 1000)
                    elif 'm' in element.lower():
                        return int(float(followers_str) * 1000000)
                    else:
                        return int(followers_str)
        except Exception:
            pass
        
        return None
    
    def _extract_video_count(self, page: Page) -> int:
        """
        Extract video count from the TikTok profile
        
        Args:
            page: Playwright page object
            
        Returns:
            int: Number of videos or 0 if extraction fails
        """
        try:
            # Count visible videos
            video_count = page.locator('[data-e2e="user-post-item"]').count()
            if video_count > 0:
                return video_count
            
            # Try alternative selectors
            video_count = page.locator('.video-feed-item').count()
            if video_count > 0:
                return video_count
            
            # Try to extract from profile info
            video_count_text = page.evaluate("""() => {
                // Look for video count in profile info
                const elements = document.querySelectorAll('strong, h2, span');
                for (const el of elements) {
                    const text = el.textContent.trim();
                    if (text) {
                        // Check if this is a video count element
                        const nextSibling = el.nextSibling;
                        if (nextSibling && nextSibling.textContent && 
                            (nextSibling.textContent.includes('Videos') || nextSibling.textContent.includes('posts'))) {
                            return parseInt(text.replace(/[^\\d]/g, ''));
                        }
                    }
                }
                return 0;
            }""")
            
            return video_count_text or 0
        except Exception:
            return 0
    
    def _extract_engagement_from_videos(self, page: Page) -> Optional[Dict[str, Any]]:
        """
        Extract engagement metrics from visible videos
        
        Args:
            page: Playwright page object
            
        Returns:
            dict: Engagement metrics or None if extraction fails
        """
        try:
            # Use JavaScript to extract engagement metrics
            engagement_data = page.evaluate("""() => {
                // Find all video elements
                const videoElements = document.querySelectorAll('[data-e2e="user-post-item"], .video-feed-item');
                if (videoElements.length === 0) return null;
                
                // TikTok doesn't show likes/comments on video thumbnails in profile view
                // We need to estimate based on view counts or click on videos
                
                // For this implementation, we'll use industry averages
                // TikTok typically has ~5-10% like rate and ~1-2% comment rate of views
                
                return {
                    avg_likes: null,
                    avg_comments: null,
                    total_engagement: null,
                    estimated: true,
                    note: "TikTok requires clicking each video to view engagement metrics"
                };
            }""")
            
            # For TikTok, we need to click on videos to see engagement metrics
            # This is a simplified version that returns estimated metrics
            
            # Click on the first video if available
            if page.locator('[data-e2e="user-post-item"]').count() > 0:
                # Click the first video
                page.locator('[data-e2e="user-post-item"]').first.click()
                self.random_delay(2, 3)
                
                # Extract likes and comments from the video modal
                likes = self._extract_likes_from_video_modal(page)
                comments = self._extract_comments_from_video_modal(page)
                
                # Close the modal
                page.keyboard.press('Escape')
                self.random_delay(1, 2)
                
                if likes is not None or comments is not None:
                    return {
                        "avg_likes": likes or 0,
                        "avg_comments": comments or 0,
                        "total_engagement": (likes or 0) + (comments or 0)
                    }
            
            # If we couldn't get metrics from a video, estimate based on followers
            followers = self._extract_followers_from_page(page)
            if followers:
                return self._estimate_engagement_from_followers(followers)
            
            return engagement_data
        except Exception as e:
            logger.error(f"Error extracting engagement from videos: {str(e)}")
            return None
    
    def _extract_likes_from_video_modal(self, page: Page) -> Optional[int]:
        """
        Extract likes count from a TikTok video modal
        
        Args:
            page: Playwright page object
            
        Returns:
            int: Number of likes or None if extraction fails
        """
        try:
            # Try multiple selectors for likes
            selectors = [
                '[data-e2e="like-count"]',
                'span[data-e2e="like-count"]',
                '.video-meta-like strong',
                '.like-count'
            ]
            
            for selector in selectors:
                if page.locator(selector).count() > 0:
                    likes_text = page.locator(selector).first.text_content()
                    if likes_text:
                        # Handle TikTok's abbreviated numbers
                        likes_text = likes_text.strip().lower()
                        
                        if 'k' in likes_text:
                            likes = float(likes_text.replace('k', '')) * 1000
                            return int(likes)
                        elif 'm' in likes_text:
                            likes = float(likes_text.replace('m', '')) * 1000000
                            return int(likes)
                        else:
                            # Try to extract numeric value
                            match = re.search(r'([\d,\.]+)', likes_text)
                            if match:
                                likes_str = match.group(1).replace(',', '')
                                return int(float(likes_str))
        except Exception:
            pass
        
        return None
    
    def _extract_comments_from_video_modal(self, page: Page) -> Optional[int]:
        """
        Extract comments count from a TikTok video modal
        
        Args:
            page: Playwright page object
            
        Returns:
            int: Number of comments or None if extraction fails
        """
        try:
            # Try multiple selectors for comments
            selectors = [
                '[data-e2e="comment-count"]',
                'span[data-e2e="comment-count"]',
                '.video-meta-comment strong',
                '.comment-count'
            ]
            
            for selector in selectors:
                if page.locator(selector).count() > 0:
                    comments_text = page.locator(selector).first.text_content()
                    if comments_text:
                        # Handle TikTok's abbreviated numbers
                        comments_text = comments_text.strip().lower()
                        
                        if 'k' in comments_text:
                            comments = float(comments_text.replace('k', '')) * 1000
                            return int(comments)
                        elif 'm' in comments_text:
                            comments = float(comments_text.replace('m', '')) * 1000000
                            return int(comments)
                        else:
                            # Try to extract numeric value
                            match = re.search(r'([\d,\.]+)', comments_text)
                            if match:
                                comments_str = match.group(1).replace(',', '')
                                return int(float(comments_str))
        except Exception:
            pass
        
        return None
    
    def _estimate_engagement_from_followers(self, followers: int) -> Dict[str, Any]:
        """
        Estimate engagement metrics based on follower count
        
        Args:
            followers: Number of followers
            
        Returns:
            dict: Estimated engagement metrics
        """
        # TikTok typically has ~5-15% engagement rate (much higher than other platforms)
        engagement_rate = 0.10  # 10%
        
        # Estimate total engagement
        total_engagement = int(followers * engagement_rate)
        
        # Distribute between likes and comments (typically 90% likes, 10% comments)
        avg_likes = int(total_engagement * 0.9)
        avg_comments = int(total_engagement * 0.1)
        
        return {
            "avg_likes": avg_likes,
            "avg_comments": avg_comments,
            "total_engagement": total_engagement,
            "posts": 10,  # Assume 10 videos as default
            "estimated": True
        }
    
    def _extract_username_from_url(self, url: str) -> Optional[str]:
        """
        Extract TikTok username from URL
        
        Args:
            url: URL of the TikTok profile
            
        Returns:
            str: Username or None if extraction fails
        """
        # Try to extract from URL patterns
        patterns = [
            r'tiktok\.com/@([^/]+)/?$',
            r'tiktok\.com/@([^/]+)/$',
            r'tiktok\.com/@([^/]+)/video',
            r'vm\.tiktok\.com/([^/]+)/?$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
