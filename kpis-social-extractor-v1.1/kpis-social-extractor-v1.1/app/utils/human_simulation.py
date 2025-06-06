"""
Human Simulation Module - KPIs Social Extractor (Optimized)

This module implements advanced human-like behavior simulation for web scraping
to avoid detection by anti-bot systems.
"""

import random
import asyncio
import logging
from typing import List, Tuple, Optional

from playwright.async_api import Page

# Configure logging
logger = logging.getLogger(__name__)

class HumanSimulation:
    """
    Simulates human-like behavior for web scraping
    """
    
    def __init__(self, simulation_level: str = None):
        """
        Initialize the human simulation module
        
        Args:
            simulation_level: Level of simulation detail ('low', 'medium', 'high')
        """
        from app.config.config import Config
        self.config = Config()
        self.simulation_level = simulation_level or self.config.HUMAN_SIMULATION_LEVEL
    
    async def simulate_random_mouse_movement(self, page: Page, movements: int = None) -> None:
        """
        Simulate random mouse movements on the page
        
        Args:
            page: Playwright page object
            movements: Number of mouse movements to simulate
        """
        if self.simulation_level == 'low':
            return
        
        # Determine number of movements based on simulation level
        if movements is None:
            if self.simulation_level == 'medium':
                movements = random.randint(2, 5)
            else:  # high
                movements = random.randint(5, 10)
        
        viewport_size = await page.viewport_size()
        if not viewport_size:
            viewport_size = {'width': 1280, 'height': 800}
        
        width = viewport_size['width']
        height = viewport_size['height']
        
        # Current position (start in the middle)
        current_x = width // 2
        current_y = height // 2
        
        for _ in range(movements):
            # Generate random target position
            target_x = random.randint(100, width - 100)
            target_y = random.randint(100, height - 100)
            
            # Generate intermediate points for natural movement
            points = self._generate_natural_curve(
                (current_x, current_y),
                (target_x, target_y),
                random.randint(5, 15)
            )
            
            # Move through the points
            for x, y in points:
                await page.mouse.move(x, y)
                await asyncio.sleep(random.uniform(0.01, 0.05))
            
            # Update current position
            current_x = target_x
            current_y = target_y
            
            # Random pause between movements
            await asyncio.sleep(random.uniform(0.1, 0.5))
    
    async def simulate_scrolling(self, page: Page, scroll_count: int = None) -> None:
        """
        Simulate human-like scrolling behavior
        
        Args:
            page: Playwright page object
            scroll_count: Number of scroll actions to perform
        """
        # Determine scroll count based on configuration
        if scroll_count is None:
            scroll_count = self.config.SCROLL_COUNT
        
        logger.debug(f"Simulating {scroll_count} scrolls")
        
        for i in range(scroll_count):
            # Random scroll distance
            scroll_distance = random.randint(300, 800)
            
            # Scroll with variable speed
            if self.simulation_level == 'high':
                # Smooth scrolling with variable speed
                steps = random.randint(5, 15)
                step_size = scroll_distance / steps
                
                for j in range(steps):
                    # Variable step size to simulate acceleration/deceleration
                    current_step = step_size * (1 + 0.2 * random.random())
                    await page.evaluate(f"window.scrollBy(0, {current_step})")
                    await asyncio.sleep(random.uniform(0.05, 0.15))
            else:
                # Simple scrolling
                await page.evaluate(f"window.scrollBy(0, {scroll_distance})")
            
            # Pause after scrolling to simulate reading
            await asyncio.sleep(random.uniform(0.5, 2.0))
            
            # Occasionally move the mouse after scrolling
            if random.random() < 0.3 and self.simulation_level != 'low':
                await self.simulate_random_mouse_movement(page, 1)
    
    async def simulate_typing(self, page: Page, selector: str, text: str) -> None:
        """
        Simulate human-like typing behavior
        
        Args:
            page: Playwright page object
            selector: CSS selector for the input element
            text: Text to type
        """
        # Click on the input field
        await page.click(selector)
        await asyncio.sleep(random.uniform(0.2, 0.5))
        
        # Type with variable speed
        if self.simulation_level == 'high':
            for char in text:
                await page.keyboard.type(char)
                # Variable delay between keystrokes
                await asyncio.sleep(random.uniform(0.05, 0.2))
        else:
            # Type with consistent speed
            await page.fill(selector, text)
        
        # Pause after typing
        await asyncio.sleep(random.uniform(0.3, 0.7))
    
    async def simulate_page_interaction(self, page: Page) -> None:
        """
        Simulate general page interaction including scrolling, mouse movements,
        and random pauses to appear more human-like
        
        Args:
            page: Playwright page object
        """
        # Initial pause to simulate page reading
        await asyncio.sleep(random.uniform(1.0, 3.0))
        
        # Random mouse movement
        await self.simulate_random_mouse_movement(page)
        
        # Scroll down a bit
        await self.simulate_scrolling(page, random.randint(1, 3))
        
        # More mouse movement
        await self.simulate_random_mouse_movement(page)
        
        # Occasionally scroll back up
        if random.random() < 0.3:
            await page.evaluate(f"window.scrollBy(0, {-random.randint(200, 500)})")
            await asyncio.sleep(random.uniform(0.5, 1.5))
    
    def _generate_natural_curve(
        self, 
        start: Tuple[int, int], 
        end: Tuple[int, int], 
        points: int
    ) -> List[Tuple[int, int]]:
        """
        Generate a natural curve between two points using Bezier curve
        
        Args:
            start: Starting point (x, y)
            end: Ending point (x, y)
            points: Number of points in the curve
            
        Returns:
            list: List of (x, y) coordinates along the curve
        """
        # Generate control points for the Bezier curve
        control_x = random.randint(
            min(start[0], end[0]), 
            max(start[0], end[0])
        )
        control_y = random.randint(
            min(start[1], end[1]), 
            max(start[1], end[1])
        )
        
        # Add some randomness to control point
        control_x += random.randint(-100, 100)
        control_y += random.randint(-100, 100)
        
        result = []
        for i in range(points):
            # Parameter t goes from 0 to 1
            t = i / (points - 1)
            
            # Quadratic Bezier curve formula
            x = int((1 - t)**2 * start[0] + 2 * (1 - t) * t * control_x + t**2 * end[0])
            y = int((1 - t)**2 * start[1] + 2 * (1 - t) * t * control_y + t**2 * end[1])
            
            result.append((x, y))
        
        return result
