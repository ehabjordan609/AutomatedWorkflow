"""
Desktop automation module handling mouse, keyboard, and screen interactions.
"""
import logging
import time
from typing import Dict, Any, Tuple, Optional
import pyautogui
import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# Configure PyAutoGUI to be safer
pyautogui.PAUSE = 0.1  # Add slight delay between actions
pyautogui.FAILSAFE = True  # Move mouse to corner to abort

class DesktopAutomation:
    """
    Handles desktop automation using PyAutoGUI for mouse/keyboard actions and screen recognition.
    """
    
    def __init__(self):
        """Initialize the desktop automation module."""
        self.screen_width, self.screen_height = pyautogui.size()
        logger.info(f"Desktop resolution: {self.screen_width}x{self.screen_height}")
    
    def execute_action(self, action: str, params: Dict[str, Any]) -> bool:
        """
        Execute a desktop automation action.
        
        Args:
            action: Type of action to perform (click, type, etc.)
            params: Parameters for the action
            
        Returns:
            bool: True if action executed successfully, False otherwise
        """
        try:
            if action == 'click':
                return self._perform_click(params)
            elif action == 'right_click':
                return self._perform_right_click(params)
            elif action == 'double_click':
                return self._perform_double_click(params)
            elif action == 'type':
                return self._perform_type(params)
            elif action == 'key_press':
                return self._perform_key_press(params)
            elif action == 'move':
                return self._perform_move(params)
            elif action == 'drag':
                return self._perform_drag(params)
            elif action == 'scroll':
                return self._perform_scroll(params)
            elif action == 'find_image':
                return self._find_image(params)
            elif action == 'wait_for_image':
                return self._wait_for_image(params)
            else:
                logger.error(f"Unknown desktop action: {action}")
                return False
        except Exception as e:
            logger.error(f"Desktop action '{action}' failed: {str(e)}")
            return False
    
    def _get_coordinates(self, params: Dict[str, Any]) -> Tuple[int, int]:
        """
        Get coordinates from parameters, either directly or by image recognition.
        
        Args:
            params: Parameters containing coordinate information
            
        Returns:
            tuple: (x, y) coordinates
        """
        if 'image' in params:
            # Find coordinates by image recognition
            location = self._find_on_screen(params['image'], params.get('confidence', 0.9))
            if location:
                return location
            else:
                raise ValueError(f"Image not found on screen: {params['image']}")
        elif 'x' in params and 'y' in params:
            # Use direct coordinates
            return params['x'], params['y']
        else:
            raise ValueError("No valid coordinates specified in parameters")
    
    def _perform_click(self, params: Dict[str, Any]) -> bool:
        """Perform a mouse click action."""
        x, y = self._get_coordinates(params)
        pyautogui.click(x, y)
        logger.info(f"Clicked at ({x}, {y})")
        return True
    
    def _perform_right_click(self, params: Dict[str, Any]) -> bool:
        """Perform a right mouse click action."""
        x, y = self._get_coordinates(params)
        pyautogui.rightClick(x, y)
        logger.info(f"Right-clicked at ({x}, {y})")
        return True
    
    def _perform_double_click(self, params: Dict[str, Any]) -> bool:
        """Perform a double mouse click action."""
        x, y = self._get_coordinates(params)
        pyautogui.doubleClick(x, y)
        logger.info(f"Double-clicked at ({x}, {y})")
        return True
    
    def _perform_type(self, params: Dict[str, Any]) -> bool:
        """Type text at the current cursor position."""
        text = params.get('text', '')
        if not text:
            logger.warning("Empty text provided for typing action")
            return False
        
        interval = params.get('interval', 0.01)  # Time between keypresses
        pyautogui.write(text, interval=interval)
        logger.info(f"Typed text: {text}")
        return True
    
    def _perform_key_press(self, params: Dict[str, Any]) -> bool:
        """Press a keyboard key or key combination."""
        key = params.get('key', '')
        if not key:
            logger.warning("No key specified for key press action")
            return False
        
        # Handle key combinations
        if '+' in key:
            # Split by '+' and press keys together
            keys = [k.strip() for k in key.split('+')]
            pyautogui.hotkey(*keys)
            logger.info(f"Pressed key combination: {key}")
        else:
            # Press a single key
            pyautogui.press(key)
            logger.info(f"Pressed key: {key}")
            
        return True
    
    def _perform_move(self, params: Dict[str, Any]) -> bool:
        """Move mouse cursor to specified position."""
        x, y = self._get_coordinates(params)
        duration = params.get('duration', 0.5)  # Movement duration
        pyautogui.moveTo(x, y, duration=duration)
        logger.info(f"Moved cursor to ({x}, {y})")
        return True
    
    def _perform_drag(self, params: Dict[str, Any]) -> bool:
        """Drag from current position to target position."""
        # Get start position
        start_x, start_y = self._get_coordinates(params)
        
        # Move to start position
        pyautogui.moveTo(start_x, start_y, duration=0.2)
        
        # Get end position
        end_params = params.get('to', {})
        if not end_params:
            logger.error("No target position specified for drag action")
            return False
            
        end_x, end_y = self._get_coordinates(end_params)
        
        # Perform drag
        duration = params.get('duration', 0.5)
        pyautogui.dragTo(end_x, end_y, duration=duration, button='left')
        logger.info(f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})")
        return True
    
    def _perform_scroll(self, params: Dict[str, Any]) -> bool:
        """Scroll the mouse wheel by specified amount."""
        clicks = params.get('clicks', 0)
        if clicks == 0:
            logger.warning("Scroll amount (clicks) not specified")
            return False
            
        pyautogui.scroll(clicks)
        direction = "down" if clicks < 0 else "up"
        logger.info(f"Scrolled {direction} by {abs(clicks)} clicks")
        return True
    
    def _find_on_screen(self, image_path: str, confidence: float = 0.9) -> Optional[Tuple[int, int]]:
        """
        Find an image on the screen and return its coordinates.
        
        Args:
            image_path: Path to the image file to search for
            confidence: Confidence threshold for the match (0-1)
            
        Returns:
            tuple: (x, y) coordinates of the image center, or None if not found
        """
        try:
            location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
            return location
        except Exception as e:
            logger.error(f"Error finding image on screen: {str(e)}")
            return None
    
    def _find_image(self, params: Dict[str, Any]) -> bool:
        """Find an image on the screen."""
        image_path = params.get('image', '')
        if not image_path:
            logger.error("No image path specified for find_image action")
            return False
            
        confidence = params.get('confidence', 0.9)
        location = self._find_on_screen(image_path, confidence)
        
        if location:
            logger.info(f"Found image '{image_path}' at ({location[0]}, {location[1]})")
            return True
        else:
            logger.warning(f"Image '{image_path}' not found on screen")
            return False
    
    def _wait_for_image(self, params: Dict[str, Any]) -> bool:
        """Wait for an image to appear on the screen."""
        image_path = params.get('image', '')
        if not image_path:
            logger.error("No image path specified for wait_for_image action")
            return False
            
        timeout = params.get('timeout', 30)  # Default 30 second timeout
        confidence = params.get('confidence', 0.9)
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            location = self._find_on_screen(image_path, confidence)
            if location:
                logger.info(f"Found image '{image_path}' at ({location[0]}, {location[1]}) after {time.time() - start_time:.2f} seconds")
                return True
            time.sleep(0.5)
        
        logger.warning(f"Image '{image_path}' not found within {timeout} seconds")
        return False
