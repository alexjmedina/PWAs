"""
Human Simulation Module - KPIs Social Extractor

This module implements human-like behavior simulation for browser automation
to avoid detection by anti-bot systems.
"""

import random
import time
import logging
from typing import List, Tuple, Optional

# Configure logging
logger = logging.getLogger(__name__)

class HumanSimulation:
    """
    Class for simulating human-like behavior in browser automation
    to avoid detection by anti-bot systems.
    """
    
    def simulate_random_mouse_movement(self, page) -> None:
        """
        Simulate random mouse movements to mimic human behavior
        
        Args:
            page: Playwright page object
        """
        try:
            # Generate random points for mouse movement
            points = self._generate_random_points(3, 8)
            
            # Move mouse through the random points
            for x, y in points:
                page.mouse.move(x, y)
                # Random delay between movements
                time.sleep(random.uniform(0.1, 0.3))
                
            logger.debug("Simulated random mouse movement")
        except Exception as e:
            logger.error(f"Error simulating mouse movement: {str(e)}")
    
    def simulate_scrolling(self, page, num_scrolls: int = 3) -> None:
        """
        Simulate human-like scrolling behavior
        
        Args:
            page: Playwright page object
            num_scrolls: Number of scroll actions to perform
        """
        try:
            viewport_height = page.viewport_size["height"]
            
            for i in range(num_scrolls):
                # Calculate a random scroll distance
                scroll_distance = random.randint(int(viewport_height * 0.5), int(viewport_height * 0.8))
                
                # Execute scroll with easing
                page.evaluate(f"""() => {{
                    const duration = {random.randint(800, 1200)};
                    const distance = {scroll_distance};
                    const start = window.pageYOffset;
                    const startTime = performance.now();
                    
                    function easeInOutQuad(t) {{
                        return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
                    }}
                    
                    function scroll() {{
                        const elapsed = performance.now() - startTime;
                        const progress = Math.min(elapsed / duration, 1);
                        const ease = easeInOutQuad(progress);
                        window.scrollTo(0, start + distance * ease);
                        
                        if (progress < 1) {{
                            window.requestAnimationFrame(scroll);
                        }}
                    }}
                    
                    window.requestAnimationFrame(scroll);
                }}""")
                
                # Wait for scrolling to complete with a bit of extra time
                time.sleep(random.uniform(1.2, 2.5))
                
                # Pause between scrolls
                if i < num_scrolls - 1:
                    time.sleep(random.uniform(0.8, 2.0))
            
            logger.debug(f"Simulated {num_scrolls} human-like scrolls")
        except Exception as e:
            logger.error(f"Error simulating scrolling: {str(e)}")
    
    def simulate_reading(self, min_seconds: float = 2.0, max_seconds: float = 5.0) -> None:
        """
        Simulate human reading time
        
        Args:
            min_seconds: Minimum reading time in seconds
            max_seconds: Maximum reading time in seconds
        """
        reading_time = random.uniform(min_seconds, max_seconds)
        logger.debug(f"Simulating reading for {reading_time:.2f} seconds")
        time.sleep(reading_time)
    
    def simulate_typing(self, page, selector: str, text: str, min_delay: float = 0.05, max_delay: float = 0.2) -> None:
        """
        Simulate human typing with variable speed
        
        Args:
            page: Playwright page object
            selector: CSS selector for the input element
            text: Text to type
            min_delay: Minimum delay between keystrokes in seconds
            max_delay: Maximum delay between keystrokes in seconds
        """
        try:
            # Click on the input field
            page.click(selector)
            time.sleep(random.uniform(0.3, 0.7))
            
            # Type text with variable speed
            for char in text:
                page.type(selector, char, delay=random.uniform(min_delay * 1000, max_delay * 1000))
                
                # Occasionally pause for a longer time (simulating thinking)
                if random.random() < 0.1:
                    time.sleep(random.uniform(0.3, 0.8))
            
            logger.debug(f"Simulated typing: '{text}'")
        except Exception as e:
            logger.error(f"Error simulating typing: {str(e)}")
    
    def _generate_random_points(self, min_points: int = 3, max_points: int = 8) -> List[Tuple[int, int]]:
        """
        Generate random points for mouse movement
        
        Args:
            min_points: Minimum number of points
            max_points: Maximum number of points
            
        Returns:
            List of (x, y) coordinate tuples
        """
        num_points = random.randint(min_points, max_points)
        points = []
        
        for _ in range(num_points):
            x = random.randint(100, 1100)
            y = random.randint(100, 700)
            points.append((x, y))
        
        return points
    
    def add_random_delays_to_requests(self, page) -> None:
        """
        Add random delays to network requests to mimic human behavior
        
        Args:
            page: Playwright page object
        """
        try:
            page.route("**/*", lambda route: self._handle_route_with_delay(route))
            logger.debug("Added random delays to network requests")
        except Exception as e:
            logger.error(f"Error adding request delays: {str(e)}")
    
    def _handle_route_with_delay(self, route) -> None:
        """
        Handle route with a random delay
        
        Args:
            route: Playwright route object
        """
        # Only delay certain resource types
        resource_type = route.request.resource_type
        if resource_type in ["document", "xhr", "fetch"]:
            time.sleep(random.uniform(0.1, 0.5))
        
        # Continue the request
        route.continue_()
    
    def randomize_viewport(self, page) -> None:
        """
        Set a randomized viewport size to avoid fingerprinting
        
        Args:
            page: Playwright page object
        """
        try:
            # Common desktop resolutions with slight variations
            width = random.choice([1280, 1366, 1440, 1920]) + random.randint(-10, 10)
            height = random.choice([720, 768, 900, 1080]) + random.randint(-10, 10)
            
            page.set_viewport_size({"width": width, "height": height})
            logger.debug(f"Set randomized viewport: {width}x{height}")
        except Exception as e:
            logger.error(f"Error setting viewport: {str(e)}")
