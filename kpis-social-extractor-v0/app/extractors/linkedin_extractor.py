"""
LinkedIn Extractor Module - KPIs Social Extractor

This module implements LinkedIn-specific extraction logic using the hybrid approach:
1. LinkedIn API (when credentials are available)
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

class LinkedInExtractor(BaseExtractor):
    """LinkedIn-specific implementation of the BaseExtractor"""
    
    def __init__(self):
        """Initialize the LinkedIn extractor"""
        super().__init__()
        self.api_key = self.config.LINKEDIN_API_KEY
        self.human_simulation = HumanSimulation()
        self.user_agent = UserAgent()
    
    def extract_followers(self, url: str) -> Optional[int]:
        """
        Extract followers count from a LinkedIn page
        
        Args:
            url: URL of the LinkedIn page
            
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
                logger.error(f"LinkedIn API extraction failed: {str(e)}")
        
        # Level 2: Try web scraping
        try:
            return self._extract_followers_via_scraping(url)
        except Exception as e:
            logger.error(f"Error scraping LinkedIn page: {str(e)}")
            return None
    
    def extract_engagement(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract engagement metrics from a LinkedIn page
        
        Args:
            url: URL of the LinkedIn page
            
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
                logger.error(f"LinkedIn API engagement extraction failed: {str(e)}")
        
        # Level 2: Try web scraping
        try:
            return self._extract_engagement_via_scraping(url)
        except Exception as e:
            logger.error(f"Error scraping LinkedIn engagement: {str(e)}")
            return None
    
    def _extract_followers_via_api(self, url: str) -> Optional[int]:
        """
        Extract followers count using the LinkedIn API
        
        Args:
            url: URL of the LinkedIn page
            
        Returns:
            int: Number of followers or None if extraction fails
        """
        # Extract company/school ID from URL
        entity_id = self._extract_entity_id_from_url(url)
        if not entity_id:
            logger.error("Could not extract LinkedIn entity ID from URL")
            return None
        
        # LinkedIn API requires OAuth authentication and proper permissions
        # This is a simplified example and would need proper LinkedIn API setup
        
        logger.warning("LinkedIn API requires OAuth authentication and proper permissions")
        return None
    
    def _extract_engagement_via_api(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract engagement metrics using the LinkedIn API
        
        Args:
            url: URL of the LinkedIn page
            
        Returns:
            dict: Engagement metrics or None if extraction fails
        """
        # Extract company/school ID from URL
        entity_id = self._extract_entity_id_from_url(url)
        if not entity_id:
            logger.error("Could not extract LinkedIn entity ID from URL")
            return None
        
        # LinkedIn API requires OAuth authentication and proper permissions
        # This is a simplified example and would need proper LinkedIn API setup
        
        logger.warning("LinkedIn API requires OAuth authentication and proper permissions")
        return None
    
    def _extract_followers_via_scraping(self, url: str) -> Optional[int]:
        """
        Extract followers count using web scraping with Playwright
        
        Args:
            url: URL of the LinkedIn page
            
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
                
                # Navigate to the LinkedIn page
                logger.info(f"Navigating to LinkedIn page: {url}")
                page.goto(url, wait_until="networkidle")
                
                # Simulate human-like behavior
                self.human_simulation.simulate_random_mouse_movement(page)
                self.random_delay(2, 4)
                
                # Handle cookie consent if it appears
                if page.locator('button[action-type="ACCEPT"]').count() > 0:
                    logger.info("Handling cookie consent dialog")
                    page.click('button[action-type="ACCEPT"]')
                    self.random_delay(1, 2)
                
                # Handle login wall if it appears
                if self._is_login_wall_present(page):
                    logger.warning("LinkedIn login wall detected, using alternative extraction method")
                    return self._extract_followers_from_login_wall_page(page)
                
                # Extract followers count using multiple methods
                followers = self._extract_followers_from_page(page)
                
                if followers is not None:
                    logger.info(f"Extracted {followers} followers from LinkedIn page")
                    return followers
                
                logger.warning("Could not extract followers from LinkedIn page")
                return None
                
            except Exception as e:
                logger.error(f"Error in LinkedIn scraping: {str(e)}")
                raise
            finally:
                browser.close()
    
    def _extract_engagement_via_scraping(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract engagement metrics using web scraping with Playwright
        
        Args:
            url: URL of the LinkedIn page
            
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
                
                # Navigate to the LinkedIn page
                logger.info(f"Navigating to LinkedIn page for engagement metrics: {url}")
                page.goto(url, wait_until="networkidle")
                
                # Simulate human-like behavior
                self.human_simulation.simulate_random_mouse_movement(page)
                self.random_delay(2, 4)
                
                # Handle cookie consent if it appears
                if page.locator('button[action-type="ACCEPT"]').count() > 0:
                    logger.info("Handling cookie consent dialog")
                    page.click('button[action-type="ACCEPT"]')
                    self.random_delay(1, 2)
                
                # Handle login wall if it appears
                if self._is_login_wall_present(page):
                    logger.warning("LinkedIn login wall detected, using alternative extraction method")
                    # For engagement metrics, we need to navigate to posts which requires login
                    # Return estimated metrics based on followers
                    followers = self._extract_followers_from_login_wall_page(page)
                    if followers:
                        return self._estimate_engagement_from_followers(followers)
                    return None
                
                # Navigate to the posts tab if not already there
                if "/posts/" not in page.url:
                    posts_url = url + "/posts/" if not url.endswith("/") else url + "posts/"
                    logger.info(f"Navigating to posts tab: {posts_url}")
                    page.goto(posts_url, wait_until="networkidle")
                    self.random_delay(2, 3)
                
                # Extract post count
                post_count = self._extract_post_count(page)
                
                # Scroll down to load more posts
                self.human_simulation.simulate_scrolling(page, 3)
                
                # Extract engagement metrics from visible posts
                engagement_metrics = self._extract_engagement_from_posts(page)
                
                if engagement_metrics:
                    engagement_metrics["posts"] = post_count
                    logger.info(f"Extracted engagement metrics from LinkedIn page")
                    return engagement_metrics
                
                logger.warning("Could not extract engagement metrics from LinkedIn page")
                return None
                
            except Exception as e:
                logger.error(f"Error in LinkedIn engagement scraping: {str(e)}")
                raise
            finally:
                browser.close()
    
    def _is_login_wall_present(self, page: Page) -> bool:
        """
        Check if LinkedIn login wall is present
        
        Args:
            page: Playwright page object
            
        Returns:
            bool: True if login wall is present, False otherwise
        """
        # Check for login form
        login_form_present = page.locator('form.login__form').count() > 0
        
        # Check for login button
        login_button_present = page.locator('a.nav__button-secondary').count() > 0
        
        # Check for sign-in message
        sign_in_message = page.locator('p.org-top-card-summary__note').count() > 0
        
        return login_form_present or login_button_present or sign_in_message
    
    def _extract_followers_from_login_wall_page(self, page: Page) -> Optional[int]:
        """
        Extract followers count from LinkedIn page with login wall
        
        Args:
            page: Playwright page object
            
        Returns:
            int: Number of followers or None if extraction fails
        """
        try:
            # Method 1: Look for followers in meta tags
            meta_content = page.evaluate("""() => {
                const metaTags = document.querySelectorAll('meta[name="description"]');
                for (const tag of metaTags) {
                    return tag.getAttribute('content');
                }
                return null;
            }""")
            
            if meta_content:
                match = re.search(r'([\d,]+)\s+followers', meta_content)
                if match:
                    followers_str = match.group(1).replace(',', '')
                    return int(followers_str)
            
            # Method 2: Look for followers in page content
            followers = page.evaluate("""() => {
                // Look for text containing followers count
                const elements = Array.from(document.querySelectorAll('*'));
                for (const el of elements) {
                    const text = el.textContent;
                    if (text && text.includes('followers')) {
                        const match = text.match(/([\d,]+)\\s+followers/i);
                        if (match && match[1]) {
                            return parseInt(match[1].replace(/,/g, ''));
                        }
                    }
                }
                return null;
            }""")
            
            if followers:
                return followers
            
            # Method 3: Extract from HTML
            html_content = page.content()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for text containing followers
            for element in soup.find_all(text=re.compile(r'([\d,]+)\s+followers', re.IGNORECASE)):
                match = re.search(r'([\d,]+)\s+followers', element, re.IGNORECASE)
                if match:
                    followers_str = match.group(1).replace(',', '')
                    return int(followers_str)
            
            return None
        except Exception as e:
            logger.error(f"Error extracting followers from login wall page: {str(e)}")
            return None
    
    def _extract_followers_from_page(self, page: Page) -> Optional[int]:
        """
        Extract followers count from the loaded LinkedIn page
        
        Args:
            page: Playwright page object
            
        Returns:
            int: Number of followers or None if extraction fails
        """
        # Try multiple selectors and approaches
        
        # Method 1: Look for followers count in company/school info
        try:
            selectors = [
                '.org-top-card-summary__info-item',
                '.org-top-card-summary-info-list__info-item',
                '.org-page-details__followers-count',
                '.school-page-details__followers-count'
            ]
            
            for selector in selectors:
                elements = page.locator(selector).all()
                for i in range(len(elements)):
                    element = elements[i]
                    text = element.text_content()
                    if text and 'follower' in text.lower():
                        match = re.search(r'([\d,]+)', text)
                        if match:
                            followers_str = match.group(1).replace(',', '')
                            return int(followers_str)
        except Exception:
            pass
        
        # Method 2: Use JavaScript to extract from page content
        try:
            followers = page.evaluate("""() => {
                // Look for elements containing follower information
                const elements = Array.from(document.querySelectorAll('*'));
                for (const el of elements) {
                    const text = el.textContent;
                    if (text && text.includes('follower')) {
                        const match = text.match(/([\d,]+)\\s+follower/i);
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
        
        # Method 3: Extract from page HTML
        try:
            html_content = page.content()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for text containing followers
            for element in soup.find_all(text=re.compile(r'([\d,]+)\s+follower', re.IGNORECASE)):
                match = re.search(r'([\d,]+)\s+follower', element, re.IGNORECASE)
                if match:
                    followers_str = match.group(1).replace(',', '')
                    return int(followers_str)
        except Exception:
            pass
        
        return None
    
    def _extract_post_count(self, page: Page) -> int:
        """
        Extract post count from the LinkedIn page
        
        Args:
            page: Playwright page object
            
        Returns:
            int: Number of posts or 0 if extraction fails
        """
        try:
            # Count visible posts
            post_count = page.locator('.org-update-card').count()
            if post_count > 0:
                return post_count
            
            # Try alternative selectors
            post_count = page.locator('.org-updates__list-item').count()
            if post_count > 0:
                return post_count
            
            # Try another alternative
            post_count = page.locator('.update-components-actor').count()
            if post_count > 0:
                return post_count
            
            return 0
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
                // Find all post elements
                const postElements = document.querySelectorAll('.org-update-card, .org-updates__list-item, .update-components-actor');
                if (postElements.length === 0) return null;
                
                let totalLikes = 0;
                let totalComments = 0;
                let postsWithMetrics = 0;
                
                postElements.forEach(post => {
                    // Extract likes
                    const socialCounts = post.querySelectorAll('.social-details-social-counts__reactions-count, .social-details-social-counts__count-value');
                    if (socialCounts.length > 0) {
                        const likesText = socialCounts[0].textContent.trim();
                        if (likesText) {
                            let likes = 0;
                            if (likesText.includes('K')) {
                                likes = parseFloat(likesText.replace('K', '')) * 1000;
                            } else {
                                likes = parseInt(likesText.replace(/,/g, ''));
                            }
                            totalLikes += likes;
                            postsWithMetrics++;
                        }
                    }
                    
                    // Extract comments
                    const commentElements = post.querySelectorAll('.social-details-social-counts__comments-count, .social-details-social-counts__count-value');
                    if (commentElements.length > 1) {
                        const commentsText = commentElements[1].textContent.trim();
                        if (commentsText) {
                            let comments = 0;
                            if (commentsText.includes('K')) {
                                comments = parseFloat(commentsText.replace('K', '')) * 1000;
                            } else {
                                comments = parseInt(commentsText.replace(/,/g, ''));
                            }
                            totalComments += comments;
                        }
                    }
                });
                
                // Calculate averages
                const avgLikes = postsWithMetrics > 0 ? Math.round(totalLikes / postsWithMetrics) : 0;
                const avgComments = postsWithMetrics > 0 ? Math.round(totalComments / postsWithMetrics) : 0;
                
                return {
                    avg_likes: avgLikes,
                    avg_comments: avgComments,
                    total_engagement: avgLikes + avgComments
                };
            }""")
            
            return engagement_data
        except Exception as e:
            logger.error(f"Error extracting engagement from posts: {str(e)}")
            return None
    
    def _estimate_engagement_from_followers(self, followers: int) -> Dict[str, Any]:
        """
        Estimate engagement metrics based on follower count
        
        Args:
            followers: Number of followers
            
        Returns:
            dict: Estimated engagement metrics
        """
        # LinkedIn typically has ~1-2% engagement rate
        engagement_rate = 0.015  # 1.5%
        
        # Estimate total engagement
        total_engagement = int(followers * engagement_rate)
        
        # Distribute between likes and comments (typically 80% likes, 20% comments)
        avg_likes = int(total_engagement * 0.8)
        avg_comments = int(total_engagement * 0.2)
        
        return {
            "avg_likes": avg_likes,
            "avg_comments": avg_comments,
            "total_engagement": total_engagement,
            "posts": 10,  # Assume 10 posts as default
            "estimated": True
        }
    
    def _extract_entity_id_from_url(self, url: str) -> Optional[str]:
        """
        Extract LinkedIn entity ID from URL
        
        Args:
            url: URL of the LinkedIn page
            
        Returns:
            str: Entity ID or None if extraction fails
        """
        # Try to extract from URL patterns
        patterns = [
            r'linkedin\.com/company/([^/]+)',
            r'linkedin\.com/school/([^/]+)',
            r'linkedin\.com/showcase/([^/]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
