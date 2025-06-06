"""
YouTube Extractor Module - KPIs Social Extractor

This module implements YouTube-specific extraction logic using the hybrid approach:
1. YouTube Data API (when credentials are available)
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

class YouTubeExtractor(BaseExtractor):
    """YouTube-specific implementation of the BaseExtractor"""
    
    def __init__(self):
        """Initialize the YouTube extractor"""
        super().__init__()
        self.api_key = self.config.YOUTUBE_API_KEY
        self.human_simulation = HumanSimulation()
        self.user_agent = UserAgent()
    
    def extract_followers(self, url: str) -> Optional[int]:
        """
        Extract subscribers count from a YouTube channel
        
        Args:
            url: URL of the YouTube channel
            
        Returns:
            int: Number of subscribers or None if extraction fails
        """
        # Level 1: Try API extraction if credentials are available
        if self.api_key:
            try:
                subscribers = self._extract_subscribers_via_api(url)
                if subscribers is not None:
                    return subscribers
            except Exception as e:
                logger.error(f"YouTube API extraction failed: {str(e)}")
        
        # Level 2: Try web scraping
        try:
            return self._extract_subscribers_via_scraping(url)
        except Exception as e:
            logger.error(f"Error scraping YouTube channel: {str(e)}")
            return None
    
    def extract_engagement(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract engagement metrics from a YouTube channel
        
        Args:
            url: URL of the YouTube channel
            
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
                logger.error(f"YouTube API engagement extraction failed: {str(e)}")
        
        # Level 2: Try web scraping
        try:
            return self._extract_engagement_via_scraping(url)
        except Exception as e:
            logger.error(f"Error scraping YouTube engagement: {str(e)}")
            return None
    
    def _extract_subscribers_via_api(self, url: str) -> Optional[int]:
        """
        Extract subscribers count using the YouTube Data API
        
        Args:
            url: URL of the YouTube channel
            
        Returns:
            int: Number of subscribers or None if extraction fails
        """
        # Extract channel ID from URL
        channel_id = self._extract_channel_id_from_url(url)
        if not channel_id:
            logger.error("Could not extract YouTube channel ID from URL")
            return None
        
        # Make API request
        api_url = "https://www.googleapis.com/youtube/v3/channels"
        params = {
            "part": "statistics",
            "id": channel_id,
            "key": self.api_key
        }
        
        response = requests.get(api_url, params=params)
        if response.status_code != 200:
            logger.error(f"YouTube API request failed: {response.text}")
            return None
        
        data = response.json()
        if "items" not in data or not data["items"]:
            logger.error("No channel found in YouTube API response")
            return None
        
        # Extract subscriber count
        statistics = data["items"][0].get("statistics", {})
        if "subscriberCount" in statistics:
            return int(statistics["subscriberCount"])
        
        logger.error("Subscriber count not found in YouTube API response")
        return None
    
    def _extract_engagement_via_api(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract engagement metrics using the YouTube Data API
        
        Args:
            url: URL of the YouTube channel
            
        Returns:
            dict: Engagement metrics or None if extraction fails
        """
        # Extract channel ID from URL
        channel_id = self._extract_channel_id_from_url(url)
        if not channel_id:
            logger.error("Could not extract YouTube channel ID from URL")
            return None
        
        # Make API request for channel uploads playlist
        api_url = "https://www.googleapis.com/youtube/v3/channels"
        params = {
            "part": "contentDetails",
            "id": channel_id,
            "key": self.api_key
        }
        
        response = requests.get(api_url, params=params)
        if response.status_code != 200:
            logger.error(f"YouTube API request failed: {response.text}")
            return None
        
        data = response.json()
        if "items" not in data or not data["items"]:
            logger.error("No channel found in YouTube API response")
            return None
        
        # Extract uploads playlist ID
        uploads_playlist_id = data["items"][0].get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")
        if not uploads_playlist_id:
            logger.error("Uploads playlist ID not found in YouTube API response")
            return None
        
        # Make API request for recent videos
        api_url = "https://www.googleapis.com/youtube/v3/playlistItems"
        params = {
            "part": "snippet,contentDetails",
            "playlistId": uploads_playlist_id,
            "maxResults": 10,
            "key": self.api_key
        }
        
        response = requests.get(api_url, params=params)
        if response.status_code != 200:
            logger.error(f"YouTube API request failed: {response.text}")
            return None
        
        data = response.json()
        if "items" not in data or not data["items"]:
            logger.error("No videos found in YouTube API response")
            return None
        
        # Extract video IDs
        video_ids = [item.get("contentDetails", {}).get("videoId") for item in data["items"] if "contentDetails" in item]
        if not video_ids:
            logger.error("No video IDs found in YouTube API response")
            return None
        
        # Make API request for video statistics
        api_url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "statistics",
            "id": ",".join(video_ids),
            "key": self.api_key
        }
        
        response = requests.get(api_url, params=params)
        if response.status_code != 200:
            logger.error(f"YouTube API request failed: {response.text}")
            return None
        
        data = response.json()
        if "items" not in data or not data["items"]:
            logger.error("No video statistics found in YouTube API response")
            return None
        
        # Calculate engagement metrics
        videos = data["items"]
        total_views = 0
        total_likes = 0
        total_comments = 0
        video_count = len(videos)
        
        for video in videos:
            statistics = video.get("statistics", {})
            total_views += int(statistics.get("viewCount", 0))
            total_likes += int(statistics.get("likeCount", 0))
            total_comments += int(statistics.get("commentCount", 0))
        
        # Calculate averages
        avg_views = round(total_views / video_count) if video_count > 0 else 0
        avg_likes = round(total_likes / video_count) if video_count > 0 else 0
        avg_comments = round(total_comments / video_count) if video_count > 0 else 0
        
        return {
            "posts": video_count,
            "avg_views": avg_views,
            "avg_likes": avg_likes,
            "avg_comments": avg_comments,
            "total_engagement": avg_likes + avg_comments
        }
    
    def _extract_subscribers_via_scraping(self, url: str) -> Optional[int]:
        """
        Extract subscribers count using web scraping with Playwright
        
        Args:
            url: URL of the YouTube channel
            
        Returns:
            int: Number of subscribers or None if extraction fails
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
                
                # Navigate to the YouTube channel
                logger.info(f"Navigating to YouTube channel: {url}")
                page.goto(url, wait_until="networkidle")
                
                # Simulate human-like behavior
                self.human_simulation.simulate_random_mouse_movement(page)
                self.random_delay(2, 4)
                
                # Handle cookie consent if it appears
                if page.locator('button[aria-label*="Accept"]').count() > 0:
                    logger.info("Handling cookie consent dialog")
                    page.click('button[aria-label*="Accept"]')
                    self.random_delay(1, 2)
                
                # Extract subscribers count using multiple methods
                subscribers = self._extract_subscribers_from_page(page)
                
                if subscribers is not None:
                    logger.info(f"Extracted {subscribers} subscribers from YouTube channel")
                    return subscribers
                
                logger.warning("Could not extract subscribers from YouTube channel")
                return None
                
            except Exception as e:
                logger.error(f"Error in YouTube scraping: {str(e)}")
                raise
            finally:
                browser.close()
    
    def _extract_engagement_via_scraping(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract engagement metrics using web scraping with Playwright
        
        Args:
            url: URL of the YouTube channel
            
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
                
                # Navigate to the YouTube channel's videos tab
                videos_url = url + "/videos" if not url.endswith("/videos") else url
                logger.info(f"Navigating to YouTube channel videos: {videos_url}")
                page.goto(videos_url, wait_until="networkidle")
                
                # Simulate human-like behavior
                self.human_simulation.simulate_random_mouse_movement(page)
                self.random_delay(2, 4)
                
                # Handle cookie consent if it appears
                if page.locator('button[aria-label*="Accept"]').count() > 0:
                    logger.info("Handling cookie consent dialog")
                    page.click('button[aria-label*="Accept"]')
                    self.random_delay(1, 2)
                
                # Extract video count
                video_count = self._extract_video_count(page)
                
                # Extract engagement metrics from visible videos
                engagement_metrics = self._extract_engagement_from_videos(page)
                
                if engagement_metrics:
                    engagement_metrics["posts"] = video_count
                    logger.info(f"Extracted engagement metrics from YouTube channel")
                    return engagement_metrics
                
                logger.warning("Could not extract engagement metrics from YouTube channel")
                return None
                
            except Exception as e:
                logger.error(f"Error in YouTube engagement scraping: {str(e)}")
                raise
            finally:
                browser.close()
    
    def _extract_subscribers_from_page(self, page: Page) -> Optional[int]:
        """
        Extract subscribers count from the loaded YouTube page
        
        Args:
            page: Playwright page object
            
        Returns:
            int: Number of subscribers or None if extraction fails
        """
        # Try multiple selectors and approaches
        
        # Method 1: Look for subscriber count in channel info
        try:
            selectors = [
                '#subscriber-count',
                '#channel-header-container #subscriber-count',
                'span[id="subscriber-count"]',
                'yt-formatted-string[id="subscriber-count"]'
            ]
            
            for selector in selectors:
                if page.locator(selector).count() > 0:
                    subscribers_text = page.locator(selector).first.text_content()
                    if subscribers_text:
                        # Handle YouTube's abbreviated numbers (e.g., 1.2M, 45.3K)
                        subscribers_text = subscribers_text.strip().lower()
                        
                        # Remove "subscribers" text if present
                        subscribers_text = subscribers_text.replace("subscribers", "").strip()
                        
                        if 'k' in subscribers_text:
                            subscribers = float(subscribers_text.replace('k', '')) * 1000
                            return int(subscribers)
                        elif 'm' in subscribers_text:
                            subscribers = float(subscribers_text.replace('m', '')) * 1000000
                            return int(subscribers)
                        else:
                            # Try to extract numeric value
                            match = re.search(r'([\d,\.]+)', subscribers_text)
                            if match:
                                subscribers_str = match.group(1).replace(',', '')
                                return int(float(subscribers_str))
        except Exception as e:
            logger.error(f"Error in method 1: {str(e)}")
        
        # Method 2: Use JavaScript to extract from page content
        try:
            subscribers = page.evaluate("""() => {
                // Look for subscriber count
                const subscriberElement = document.querySelector('#subscriber-count');
                if (subscriberElement) {
                    const text = subscriberElement.textContent.trim().toLowerCase();
                    if (text.includes('k')) {
                        return Math.round(parseFloat(text.replace('k subscribers', '').replace('k', '').trim()) * 1000);
                    } else if (text.includes('m')) {
                        return Math.round(parseFloat(text.replace('m subscribers', '').replace('m', '').trim()) * 1000000);
                    } else {
                        return parseInt(text.replace('subscribers', '').replace(/,/g, '').trim());
                    }
                }
                
                // Look for any element containing subscriber information
                const elements = Array.from(document.querySelectorAll('*'));
                for (const el of elements) {
                    const text = el.textContent;
                    if (text && text.includes('subscriber')) {
                        const match = text.match(/([\d,.]+)[KkMm]?\\s*subscriber/);
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
            
            if subscribers:
                return subscribers
        except Exception as e:
            logger.error(f"Error in method 2: {str(e)}")
        
        # Method 3: Extract from page HTML
        try:
            html_content = page.content()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for subscriber count
            subscriber_element = soup.find(id="subscriber-count")
            if subscriber_element:
                subscribers_text = subscriber_element.text.strip().lower()
                subscribers_text = subscribers_text.replace("subscribers", "").strip()
                
                if 'k' in subscribers_text:
                    subscribers = float(subscribers_text.replace('k', '')) * 1000
                    return int(subscribers)
                elif 'm' in subscribers_text:
                    subscribers = float(subscribers_text.replace('m', '')) * 1000000
                    return int(subscribers)
                else:
                    # Try to extract numeric value
                    match = re.search(r'([\d,\.]+)', subscribers_text)
                    if match:
                        subscribers_str = match.group(1).replace(',', '')
                        return int(float(subscribers_str))
        except Exception as e:
            logger.error(f"Error in method 3: {str(e)}")
        
        return None
    
    def _extract_video_count(self, page: Page) -> int:
        """
        Extract video count from the YouTube channel
        
        Args:
            page: Playwright page object
            
        Returns:
            int: Number of videos or 0 if extraction fails
        """
        try:
            # Count visible videos
            video_count = page.locator('#contents ytd-grid-video-renderer').count()
            if video_count > 0:
                return video_count
            
            # Try alternative selectors
            video_count = page.locator('ytd-grid-video-renderer').count()
            if video_count > 0:
                return video_count
            
            # Try to extract from channel info
            video_count_text = page.evaluate("""() => {
                // Look for video count in channel info
                const tabs = document.querySelectorAll('tp-yt-paper-tab');
                for (const tab of tabs) {
                    if (tab.textContent.includes('Videos')) {
                        const match = tab.textContent.match(/([\d,]+)/);
                        if (match && match[1]) {
                            return parseInt(match[1].replace(/,/g, ''));
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
                const videoElements = document.querySelectorAll('ytd-grid-video-renderer');
                if (videoElements.length === 0) return null;
                
                // YouTube doesn't show likes/comments on video thumbnails
                // We need to estimate based on view counts
                let totalViews = 0;
                let videoCount = 0;
                
                videoElements.forEach(video => {
                    // Extract view count
                    const viewCountElement = video.querySelector('#metadata-line span');
                    if (viewCountElement) {
                        const viewText = viewCountElement.textContent.trim();
                        if (viewText.includes('views')) {
                            let views = viewText.replace('views', '').trim();
                            if (views.includes('K')) {
                                views = parseFloat(views.replace('K', '')) * 1000;
                            } else if (views.includes('M')) {
                                views = parseFloat(views.replace('M', '')) * 1000000;
                            } else {
                                views = parseInt(views.replace(/,/g, ''));
                            }
                            totalViews += views;
                            videoCount++;
                        }
                    }
                });
                
                // Calculate average views
                const avgViews = videoCount > 0 ? Math.round(totalViews / videoCount) : 0;
                
                // Estimate likes and comments based on industry averages
                // YouTube typically has ~2% like rate and ~0.5% comment rate
                const avgLikes = Math.round(avgViews * 0.02);
                const avgComments = Math.round(avgViews * 0.005);
                
                return {
                    avg_views: avgViews,
                    avg_likes: avgLikes,
                    avg_comments: avgComments,
                    total_engagement: avgLikes + avgComments,
                    estimated: true
                };
            }""")
            
            return engagement_data
        except Exception as e:
            logger.error(f"Error extracting engagement from videos: {str(e)}")
            return None
    
    def _extract_channel_id_from_url(self, url: str) -> Optional[str]:
        """
        Extract YouTube channel ID from URL
        
        Args:
            url: URL of the YouTube channel
            
        Returns:
            str: Channel ID or None if extraction fails
        """
        # Try to extract from URL patterns
        patterns = [
            r'youtube\.com/channel/([^/]+)',
            r'youtube\.com/c/([^/]+)',
            r'youtube\.com/user/([^/]+)',
            r'youtube\.com/@([^/]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                channel_id = match.group(1)
                
                # For /c/ and /user/ URLs, we need to make an additional request
                # to get the actual channel ID, but for this example we'll return
                # the username as a simplification
                return channel_id
        
        return None
