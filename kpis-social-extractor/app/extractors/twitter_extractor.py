"""
Twitter/X Extractor Module - KPIs Social Extractor

This module implements Twitter/X-specific extraction logic using the hybrid approach:
1. Twitter API v2 (when credentials are available)
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

class TwitterExtractor(BaseExtractor):
    """Twitter/X-specific implementation of the BaseExtractor"""
    
    def __init__(self):
        """Initialize the Twitter extractor"""
        super().__init__()
        self.api_key = self.config.TWITTER_API_KEY
        self.api_secret = self.config.TWITTER_API_SECRET
        self.bearer_token = self.config.TWITTER_BEARER_TOKEN
        self.human_simulation = HumanSimulation()
        self.user_agent = UserAgent()
    
    def extract_followers(self, url: str) -> Optional[int]:
        """
        Extract followers count from a Twitter/X profile
        
        Args:
            url: URL of the Twitter/X profile
            
        Returns:
            int: Number of followers or None if extraction fails
        """
        # Level 1: Try API extraction if credentials are available
        if self.bearer_token:
            try:
                followers = self._extract_followers_via_api(url)
                if followers is not None:
                    return followers
            except Exception as e:
                logger.error(f"Twitter API extraction failed: {str(e)}")
        
        # Level 2: Try web scraping
        try:
            return self._extract_followers_via_scraping(url)
        except Exception as e:
            logger.error(f"Error scraping Twitter profile: {str(e)}")
            return None
    
    def extract_engagement(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract engagement metrics from a Twitter/X profile
        
        Args:
            url: URL of the Twitter/X profile
            
        Returns:
            dict: Engagement metrics or None if extraction fails
        """
        # Level 1: Try API extraction if credentials are available
        if self.bearer_token:
            try:
                engagement = self._extract_engagement_via_api(url)
                if engagement is not None:
                    return engagement
            except Exception as e:
                logger.error(f"Twitter API engagement extraction failed: {str(e)}")
        
        # Level 2: Try web scraping
        try:
            return self._extract_engagement_via_scraping(url)
        except Exception as e:
            logger.error(f"Error scraping Twitter engagement: {str(e)}")
            return None
    
    def _extract_followers_via_api(self, url: str) -> Optional[int]:
        """
        Extract followers count using the Twitter API v2
        
        Args:
            url: URL of the Twitter/X profile
            
        Returns:
            int: Number of followers or None if extraction fails
        """
        # Extract username from URL
        username = self._extract_username_from_url(url)
        if not username:
            logger.error("Could not extract Twitter username from URL")
            return None
        
        # Make API request
        api_url = f"https://api.twitter.com/2/users/by/username/{username}"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}"
        }
        params = {
            "user.fields": "public_metrics"
        }
        
        response = requests.get(api_url, headers=headers, params=params)
        if response.status_code != 200:
            logger.error(f"Twitter API request failed: {response.text}")
            return None
        
        data = response.json()
        if "data" not in data:
            logger.error("No data found in Twitter API response")
            return None
        
        # Extract follower count
        public_metrics = data["data"].get("public_metrics", {})
        if "followers_count" in public_metrics:
            return public_metrics["followers_count"]
        
        logger.error("Follower count not found in Twitter API response")
        return None
    
    def _extract_engagement_via_api(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract engagement metrics using the Twitter API v2
        
        Args:
            url: URL of the Twitter/X profile
            
        Returns:
            dict: Engagement metrics or None if extraction fails
        """
        # Extract username from URL
        username = self._extract_username_from_url(url)
        if not username:
            logger.error("Could not extract Twitter username from URL")
            return None
        
        # Get user ID first
        api_url = f"https://api.twitter.com/2/users/by/username/{username}"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}"
        }
        
        response = requests.get(api_url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Twitter API request failed: {response.text}")
            return None
        
        data = response.json()
        if "data" not in data:
            logger.error("No data found in Twitter API response")
            return None
        
        user_id = data["data"].get("id")
        if not user_id:
            logger.error("User ID not found in Twitter API response")
            return None
        
        # Get recent tweets
        api_url = f"https://api.twitter.com/2/users/{user_id}/tweets"
        params = {
            "max_results": 10,
            "tweet.fields": "public_metrics",
            "exclude": "retweets,replies"
        }
        
        response = requests.get(api_url, headers=headers, params=params)
        if response.status_code != 200:
            logger.error(f"Twitter API request failed: {response.text}")
            return None
        
        data = response.json()
        if "data" not in data:
            logger.error("No tweets found in Twitter API response")
            return None
        
        # Calculate engagement metrics
        tweets = data["data"]
        total_likes = 0
        total_retweets = 0
        total_replies = 0
        tweet_count = len(tweets)
        
        for tweet in tweets:
            metrics = tweet.get("public_metrics", {})
            total_likes += metrics.get("like_count", 0)
            total_retweets += metrics.get("retweet_count", 0)
            total_replies += metrics.get("reply_count", 0)
        
        # Calculate averages
        avg_likes = round(total_likes / tweet_count) if tweet_count > 0 else 0
        avg_retweets = round(total_retweets / tweet_count) if tweet_count > 0 else 0
        avg_replies = round(total_replies / tweet_count) if tweet_count > 0 else 0
        
        return {
            "posts": tweet_count,
            "avg_likes": avg_likes,
            "avg_retweets": avg_retweets,
            "avg_replies": avg_replies,
            "total_engagement": avg_likes + avg_retweets + avg_replies
        }
    
    def _extract_followers_via_scraping(self, url: str) -> Optional[int]:
        """
        Extract followers count using web scraping with Playwright
        
        Args:
            url: URL of the Twitter/X profile
            
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
                
                # Navigate to the Twitter profile
                logger.info(f"Navigating to Twitter profile: {url}")
                page.goto(url, wait_until="networkidle")
                
                # Simulate human-like behavior
                self.human_simulation.simulate_random_mouse_movement(page)
                self.random_delay(2, 4)
                
                # Handle cookie consent if it appears
                if page.locator('[data-testid="cookie-consent-primary-button"]').count() > 0:
                    logger.info("Handling cookie consent dialog")
                    page.click('[data-testid="cookie-consent-primary-button"]')
                    self.random_delay(1, 2)
                
                # Handle login prompt if it appears
                if self._is_login_prompt_present(page):
                    logger.warning("Twitter login prompt detected, using alternative extraction method")
                    return self._extract_followers_from_login_prompt_page(page)
                
                # Extract followers count using multiple methods
                followers = self._extract_followers_from_page(page)
                
                if followers is not None:
                    logger.info(f"Extracted {followers} followers from Twitter profile")
                    return followers
                
                logger.warning("Could not extract followers from Twitter profile")
                return None
                
            except Exception as e:
                logger.error(f"Error in Twitter scraping: {str(e)}")
                raise
            finally:
                browser.close()
    
    def _extract_engagement_via_scraping(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract engagement metrics using web scraping with Playwright
        
        Args:
            url: URL of the Twitter/X profile
            
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
                
                # Navigate to the Twitter profile
                logger.info(f"Navigating to Twitter profile for engagement metrics: {url}")
                page.goto(url, wait_until="networkidle")
                
                # Simulate human-like behavior
                self.human_simulation.simulate_random_mouse_movement(page)
                self.random_delay(2, 4)
                
                # Handle cookie consent if it appears
                if page.locator('[data-testid="cookie-consent-primary-button"]').count() > 0:
                    logger.info("Handling cookie consent dialog")
                    page.click('[data-testid="cookie-consent-primary-button"]')
                    self.random_delay(1, 2)
                
                # Handle login prompt if it appears
                if self._is_login_prompt_present(page):
                    logger.warning("Twitter login prompt detected, using alternative extraction method")
                    # For engagement metrics, we need to see tweets which requires login
                    # Return estimated metrics based on followers
                    followers = self._extract_followers_from_login_prompt_page(page)
                    if followers:
                        return self._estimate_engagement_from_followers(followers)
                    return None
                
                # Extract tweet count
                tweet_count = self._extract_tweet_count(page)
                
                # Scroll down to load more tweets
                self.human_simulation.simulate_scrolling(page, 3)
                
                # Extract engagement metrics from visible tweets
                engagement_metrics = self._extract_engagement_from_tweets(page)
                
                if engagement_metrics:
                    engagement_metrics["posts"] = tweet_count
                    logger.info(f"Extracted engagement metrics from Twitter profile")
                    return engagement_metrics
                
                logger.warning("Could not extract engagement metrics from Twitter profile")
                return None
                
            except Exception as e:
                logger.error(f"Error in Twitter engagement scraping: {str(e)}")
                raise
            finally:
                browser.close()
    
    def _is_login_prompt_present(self, page: Page) -> bool:
        """
        Check if Twitter login prompt is present
        
        Args:
            page: Playwright page object
            
        Returns:
            bool: True if login prompt is present, False otherwise
        """
        # Check for login button
        login_button_present = page.locator('[data-testid="login"]').count() > 0
        
        # Check for sign up button
        signup_button_present = page.locator('[data-testid="signup"]').count() > 0
        
        # Check for login form
        login_form_present = page.locator('form[action="/sessions"]').count() > 0
        
        # Check for login wall
        login_wall_present = page.locator('[data-testid="loginButton"]').count() > 0
        
        return login_button_present or signup_button_present or login_form_present or login_wall_present
    
    def _extract_followers_from_login_prompt_page(self, page: Page) -> Optional[int]:
        """
        Extract followers count from Twitter page with login prompt
        
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
                match = re.search(r'([\d,\.]+)[KkMm]?\s+[Ff]ollowers', meta_content)
                if match:
                    followers_str = match.group(1).replace(',', '')
                    if 'k' in meta_content.lower():
                        return int(float(followers_str) * 1000)
                    elif 'm' in meta_content.lower():
                        return int(float(followers_str) * 1000000)
                    else:
                        return int(followers_str)
            
            # Method 2: Look for followers in page content
            followers = page.evaluate("""() => {
                // Look for text containing followers count
                const elements = Array.from(document.querySelectorAll('*'));
                for (const el of elements) {
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
            
            # Method 3: Extract from HTML
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
            
            return None
        except Exception as e:
            logger.error(f"Error extracting followers from login prompt page: {str(e)}")
            return None
    
    def _extract_followers_from_page(self, page: Page) -> Optional[int]:
        """
        Extract followers count from the loaded Twitter page
        
        Args:
            page: Playwright page object
            
        Returns:
            int: Number of followers or None if extraction fails
        """
        # Try multiple selectors and approaches
        
        # Method 1: Look for followers count in profile info
        try:
            selectors = [
                '[data-testid="UserProfileHeader_Items"] a[href$="/followers"]',
                'a[href$="/followers"] span',
                '[data-testid="primaryColumn"] a[href$="/followers"]'
            ]
            
            for selector in selectors:
                if page.locator(selector).count() > 0:
                    followers_text = page.locator(selector).first.text_content()
                    if followers_text:
                        # Handle Twitter's abbreviated numbers (e.g., 1.2K, 45.3M)
                        followers_text = followers_text.strip().lower()
                        
                        # Remove "followers" text if present
                        followers_text = followers_text.replace("followers", "").strip()
                        
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
                // Look for followers link
                const followersLinks = Array.from(document.querySelectorAll('a[href$="/followers"]'));
                for (const link of followersLinks) {
                    const text = link.textContent.trim();
                    if (text) {
                        if (text.includes('K') || text.includes('k')) {
                            return Math.round(parseFloat(text.replace(/[^\\d\\.]/g, '')) * 1000);
                        } else if (text.includes('M') || text.includes('m')) {
                            return Math.round(parseFloat(text.replace(/[^\\d\\.]/g, '')) * 1000000);
                        } else {
                            return parseInt(text.replace(/[^\\d]/g, ''));
                        }
                    }
                }
                
                // Look for any element containing follower information
                const elements = Array.from(document.querySelectorAll('*'));
                for (const el of elements) {
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
            
            # Look for followers link
            for link in soup.find_all('a', href=lambda href: href and href.endswith('/followers')):
                text = link.get_text().strip()
                if text:
                    if 'k' in text.lower():
                        followers = float(re.sub(r'[^\d\.]', '', text)) * 1000
                        return int(followers)
                    elif 'm' in text.lower():
                        followers = float(re.sub(r'[^\d\.]', '', text)) * 1000000
                        return int(followers)
                    else:
                        followers = int(re.sub(r'[^\d]', '', text))
                        return followers
        except Exception:
            pass
        
        return None
    
    def _extract_tweet_count(self, page: Page) -> int:
        """
        Extract tweet count from the Twitter profile
        
        Args:
            page: Playwright page object
            
        Returns:
            int: Number of tweets or 0 if extraction fails
        """
        try:
            # Try to extract from profile header
            tweet_count_text = page.evaluate("""() => {
                // Look for tweet count in profile header
                const elements = document.querySelectorAll('[data-testid="primaryColumn"] span');
                for (const el of elements) {
                    const text = el.textContent.trim();
                    if (text && text.includes('Tweet')) {
                        const match = text.match(/([\d,]+)/);
                        if (match && match[1]) {
                            return parseInt(match[1].replace(/,/g, ''));
                        }
                    }
                }
                return 0;
            }""")
            
            if tweet_count_text > 0:
                return tweet_count_text
            
            # Count visible tweets
            tweet_count = page.locator('[data-testid="tweet"]').count()
            if tweet_count > 0:
                return tweet_count
            
            return 0
        except Exception:
            return 0
    
    def _extract_engagement_from_tweets(self, page: Page) -> Optional[Dict[str, Any]]:
        """
        Extract engagement metrics from visible tweets
        
        Args:
            page: Playwright page object
            
        Returns:
            dict: Engagement metrics or None if extraction fails
        """
        try:
            # Use JavaScript to extract engagement metrics
            engagement_data = page.evaluate("""() => {
                // Find all tweet elements
                const tweetElements = document.querySelectorAll('[data-testid="tweet"]');
                if (tweetElements.length === 0) return null;
                
                let totalLikes = 0;
                let totalRetweets = 0;
                let totalReplies = 0;
                let tweetsWithMetrics = 0;
                
                tweetElements.forEach(tweet => {
                    // Extract likes
                    const likeElement = tweet.querySelector('[data-testid="like"]');
                    if (likeElement) {
                        const likeText = likeElement.textContent.trim();
                        if (likeText) {
                            let likes = 0;
                            if (likeText.includes('K')) {
                                likes = parseFloat(likeText.replace('K', '')) * 1000;
                            } else if (likeText.includes('M')) {
                                likes = parseFloat(likeText.replace('M', '')) * 1000000;
                            } else {
                                likes = parseInt(likeText || '0');
                            }
                            totalLikes += likes;
                            tweetsWithMetrics++;
                        }
                    }
                    
                    // Extract retweets
                    const retweetElement = tweet.querySelector('[data-testid="retweet"]');
                    if (retweetElement) {
                        const retweetText = retweetElement.textContent.trim();
                        if (retweetText) {
                            let retweets = 0;
                            if (retweetText.includes('K')) {
                                retweets = parseFloat(retweetText.replace('K', '')) * 1000;
                            } else if (retweetText.includes('M')) {
                                retweets = parseFloat(retweetText.replace('M', '')) * 1000000;
                            } else {
                                retweets = parseInt(retweetText || '0');
                            }
                            totalRetweets += retweets;
                        }
                    }
                    
                    // Extract replies
                    const replyElement = tweet.querySelector('[data-testid="reply"]');
                    if (replyElement) {
                        const replyText = replyElement.textContent.trim();
                        if (replyText) {
                            let replies = 0;
                            if (replyText.includes('K')) {
                                replies = parseFloat(replyText.replace('K', '')) * 1000;
                            } else if (replyText.includes('M')) {
                                replies = parseFloat(replyText.replace('M', '')) * 1000000;
                            } else {
                                replies = parseInt(replyText || '0');
                            }
                            totalReplies += replies;
                        }
                    }
                });
                
                // Calculate averages
                const avgLikes = tweetsWithMetrics > 0 ? Math.round(totalLikes / tweetsWithMetrics) : 0;
                const avgRetweets = tweetsWithMetrics > 0 ? Math.round(totalRetweets / tweetsWithMetrics) : 0;
                const avgReplies = tweetsWithMetrics > 0 ? Math.round(totalReplies / tweetsWithMetrics) : 0;
                
                return {
                    avg_likes: avgLikes,
                    avg_retweets: avgRetweets,
                    avg_replies: avgReplies,
                    total_engagement: avgLikes + avgRetweets + avgReplies
                };
            }""")
            
            return engagement_data
        except Exception as e:
            logger.error(f"Error extracting engagement from tweets: {str(e)}")
            return None
    
    def _estimate_engagement_from_followers(self, followers: int) -> Dict[str, Any]:
        """
        Estimate engagement metrics based on follower count
        
        Args:
            followers: Number of followers
            
        Returns:
            dict: Estimated engagement metrics
        """
        # Twitter typically has ~0.5-1% engagement rate
        engagement_rate = 0.007  # 0.7%
        
        # Estimate total engagement
        total_engagement = int(followers * engagement_rate)
        
        # Distribute between likes, retweets, and replies
        # Typically 70% likes, 20% retweets, 10% replies
        avg_likes = int(total_engagement * 0.7)
        avg_retweets = int(total_engagement * 0.2)
        avg_replies = int(total_engagement * 0.1)
        
        return {
            "avg_likes": avg_likes,
            "avg_retweets": avg_retweets,
            "avg_replies": avg_replies,
            "total_engagement": total_engagement,
            "posts": 10,  # Assume 10 tweets as default
            "estimated": True
        }
    
    def _extract_username_from_url(self, url: str) -> Optional[str]:
        """
        Extract Twitter username from URL
        
        Args:
            url: URL of the Twitter/X profile
            
        Returns:
            str: Username or None if extraction fails
        """
        # Try to extract from URL patterns
        patterns = [
            r'twitter\.com/([^/]+)/?$',
            r'twitter\.com/([^/]+)/$',
            r'twitter\.com/([^/]+)/with_replies',
            r'twitter\.com/([^/]+)/media',
            r'x\.com/([^/]+)/?$',
            r'x\.com/([^/]+)/$',
            r'x\.com/([^/]+)/with_replies',
            r'x\.com/([^/]+)/media'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                username = match.group(1)
                # Filter out non-username paths
                if username not in ['home', 'explore', 'notifications', 'messages', 'search']:
                    return username
        
        return None
