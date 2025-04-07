#!/usr/bin/env python3
"""
Desktop automation module handling mouse, keyboard, and screen interactions.
"""
import os
import time
import logging
import tempfile
from typing import Dict, Any, Tuple, Optional, List
import pyautogui

# Import these conditionally within functions to avoid errors if not installed
# import cv2
# import numpy as np
# import pyperclip

# Setup PyAutoGUI to be safer
pyautogui.FAILSAFE = True  # Move mouse to top-left corner to abort
pyautogui.PAUSE = 0.1  # Add small pause between PyAutoGUI actions

logger = logging.getLogger(__name__)

class DesktopAutomation:
    """
    Handles desktop automation using PyAutoGUI for mouse/keyboard actions and screen recognition.
    """
    
    def __init__(self):
        """Initialize the desktop automation module."""
        self.screenshots_dir = "screenshots"
        self.images_dir = "images"
        
        # Create directories if they don't exist
        for directory in [self.screenshots_dir, self.images_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
        
        # Get screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        logger.info(f"Screen dimensions: {self.screen_width}x{self.screen_height}")
        
        logger.info("DesktopAutomation initialized")
    
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
            # Map actions to methods
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
                
            elif action == 'screenshot':
                return self._take_screenshot(params)
            
            # New actions for common keyboard shortcuts
            elif action == 'select_all':
                return self._perform_key_press({'key': 'select_all'})
                
            elif action == 'copy':
                return self._perform_key_press({'key': 'copy'})
                
            elif action == 'paste':
                return self._perform_key_press({'key': 'paste'})
                
            elif action == 'cut':
                return self._perform_key_press({'key': 'cut'})
                
            elif action == 'new_tab':
                return self._perform_key_press({'key': 'new_tab'})
                
            elif action == 'close_tab':
                return self._perform_key_press({'key': 'close_tab'})
                
            elif action == 'switch_tab':
                tab_number = params.get('tab_number', 1)
                return self._perform_key_press({'key': 'switch_tab', 'tab_number': tab_number})
                
            # New file operations
            elif action == 'read_from_file':
                return self._read_from_file(params)
                
            elif action == 'write_to_file':
                return self._write_to_file(params)
                
            elif action == 'append_to_file':
                return self._append_to_file(params)
                
            # Clipboard monitoring
            elif action == 'wait_for_clipboard':
                return self._wait_for_clipboard(params)
                
            else:
                logger.error(f"Unknown desktop action: {action}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing desktop action '{action}': {str(e)}")
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
            image_path = params['image']
            confidence = params.get('confidence', 0.9)
            
            coords = self._find_on_screen(image_path, confidence)
            if coords:
                return coords
            else:
                logger.error(f"Image not found on screen: {image_path}")
                raise ValueError(f"Image not found: {image_path}")
        else:
            # Get coordinates directly from parameters
            x = params.get('x', 0)
            y = params.get('y', 0)
            
            # Validate coordinates are within screen bounds
            if 0 <= x <= self.screen_width and 0 <= y <= self.screen_height:
                return (x, y)
            else:
                logger.error(f"Coordinates ({x}, {y}) out of screen bounds ({self.screen_width}x{self.screen_height})")
                raise ValueError(f"Coordinates out of bounds: ({x}, {y})")
    
    def _perform_click(self, params: Dict[str, Any]) -> bool:
        """Perform a mouse click action."""
        try:
            x, y = self._get_coordinates(params)
            duration = params.get('duration', 0.1)  # Movement duration
            
            logger.info(f"Clicking at ({x}, {y})")
            pyautogui.moveTo(x, y, duration=duration)
            pyautogui.click(x, y)
            return True
        except Exception as e:
            logger.error(f"Click error: {str(e)}")
            return False
    
    def _perform_right_click(self, params: Dict[str, Any]) -> bool:
        """Perform a right mouse click action."""
        try:
            x, y = self._get_coordinates(params)
            duration = params.get('duration', 0.1)  # Movement duration
            
            logger.info(f"Right-clicking at ({x}, {y})")
            pyautogui.moveTo(x, y, duration=duration)
            pyautogui.rightClick(x, y)
            return True
        except Exception as e:
            logger.error(f"Right-click error: {str(e)}")
            return False
    
    def _perform_double_click(self, params: Dict[str, Any]) -> bool:
        """Perform a double mouse click action."""
        try:
            x, y = self._get_coordinates(params)
            duration = params.get('duration', 0.1)  # Movement duration
            
            logger.info(f"Double-clicking at ({x}, {y})")
            pyautogui.moveTo(x, y, duration=duration)
            pyautogui.doubleClick(x, y)
            return True
        except Exception as e:
            logger.error(f"Double-click error: {str(e)}")
            return False
    
    def _perform_type(self, params: Dict[str, Any]) -> bool:
        """Type text at the current cursor position."""
        try:
            text = params.get('text', '')
            if not text:
                logger.warning("No text provided for typing")
                return False
            
            interval = params.get('interval', 0.0)  # Time between keypresses
            
            logger.info(f"Typing text: '{text}'")
            pyautogui.typewrite(text, interval=interval)
            return True
        except Exception as e:
            logger.error(f"Type error: {str(e)}")
            return False
    
    def _perform_key_press(self, params: Dict[str, Any]) -> bool:
        """Press a keyboard key or key combination."""
        try:
            key = params.get('key', '')
            if not key:
                logger.warning("No key specified for key press")
                return False
            
            # Handle predefined actions
            if key == 'select_all':
                logger.info("Selecting all text (Ctrl+A)")
                pyautogui.hotkey('ctrl', 'a')
                return True
            elif key == 'copy':
                logger.info("Copying selected text (Ctrl+C)")
                pyautogui.hotkey('ctrl', 'c')
                return True
            elif key == 'paste':
                logger.info("Pasting text (Ctrl+V)")
                pyautogui.hotkey('ctrl', 'v')
                return True
            elif key == 'cut':
                logger.info("Cutting selected text (Ctrl+X)")
                pyautogui.hotkey('ctrl', 'x')
                return True
            elif key == 'new_tab':
                logger.info("Opening new tab (Ctrl+T)")
                pyautogui.hotkey('ctrl', 't')
                return True
            elif key == 'close_tab':
                logger.info("Closing current tab (Ctrl+W)")
                pyautogui.hotkey('ctrl', 'w')
                return True
            elif key == 'switch_tab':
                # Tab number can be provided in the "tab_number" parameter
                tab_number = params.get('tab_number', 1)
                if 1 <= tab_number <= 8:
                    logger.info(f"Switching to tab {tab_number} (Ctrl+{tab_number})")
                    pyautogui.hotkey('ctrl', str(tab_number))
                    return True
                else:
                    logger.warning(f"Invalid tab number: {tab_number}")
                    return False
            
            # Handle key combinations (e.g., 'ctrl+c')
            elif '+' in key:
                keys = key.split('+')
                logger.info(f"Pressing key combination: {key}")
                pyautogui.hotkey(*keys)
                return True
            else:
                logger.info(f"Pressing key: {key}")
                pyautogui.press(key)
                return True
                
        except Exception as e:
            logger.error(f"Key press error: {str(e)}")
            return False
    
    def _perform_move(self, params: Dict[str, Any]) -> bool:
        """Move mouse cursor to specified position."""
        try:
            x, y = self._get_coordinates(params)
            duration = params.get('duration', 0.5)  # Movement duration
            
            logger.info(f"Moving cursor to ({x}, {y})")
            pyautogui.moveTo(x, y, duration=duration)
            return True
        except Exception as e:
            logger.error(f"Move error: {str(e)}")
            return False
    
    def _perform_drag(self, params: Dict[str, Any]) -> bool:
        """Drag from current position to target position."""
        try:
            # Get start coordinates
            start_x, start_y = self._get_coordinates(params)
            
            # Get end coordinates
            to_params = params.get('to', {})
            if 'image' in to_params:
                end_x, end_y = self._get_coordinates(to_params)
            else:
                end_x = to_params.get('x', 0)
                end_y = to_params.get('y', 0)
            
            duration = params.get('duration', 0.5)  # Drag duration
            
            logger.info(f"Dragging from ({start_x}, {start_y}) to ({end_x}, {end_y})")
            pyautogui.moveTo(start_x, start_y, duration=duration/2)
            pyautogui.dragTo(end_x, end_y, duration=duration)
            return True
        except Exception as e:
            logger.error(f"Drag error: {str(e)}")
            return False
    
    def _perform_scroll(self, params: Dict[str, Any]) -> bool:
        """Scroll the mouse wheel by specified amount."""
        try:
            clicks = params.get('clicks', 0)
            if clicks == 0:
                logger.warning("Scroll amount (clicks) is zero")
                return True
            
            x = params.get('x', None)
            y = params.get('y', None)
            
            # Move to position first if coordinates provided
            if x is not None and y is not None:
                pyautogui.moveTo(x, y, duration=0.1)
            
            logger.info(f"Scrolling by {clicks} clicks")
            pyautogui.scroll(clicks)
            return True
        except Exception as e:
            logger.error(f"Scroll error: {str(e)}")
            return False
    
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
            # Ensure the image path exists
            if not os.path.exists(image_path):
                image_path = os.path.join(self.images_dir, image_path)
                if not os.path.exists(image_path):
                    logger.error(f"Image file not found: {image_path}")
                    return None
            
            logger.info(f"Looking for image: {image_path} (confidence: {confidence})")
            # Use OpenCV for more advanced image recognition if available
            try:
                import cv2
                import numpy as np
                
                # Take a screenshot
                screen = pyautogui.screenshot()
                screen_np = np.array(screen)
                screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
                
                # Load the template image
                template = cv2.imread(image_path)
                if template is None:
                    logger.error(f"Failed to load image: {image_path}")
                    return None
                
                # Get template dimensions
                template_h, template_w = template.shape[:2]
                
                # Try different preprocessing techniques
                methods = [
                    # Try original images first
                    (screen_bgr, template, "Original"),
                    
                    # Try grayscale for simpler matching
                    (cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2GRAY), 
                     cv2.cvtColor(template, cv2.COLOR_BGR2GRAY), "Grayscale"),
                    
                    # Try edge detection for shape-based matching
                    (cv2.Canny(cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2GRAY), 50, 200), 
                     cv2.Canny(cv2.cvtColor(template, cv2.COLOR_BGR2GRAY), 50, 200), "Edge")
                ]
                
                # Try different template matching methods
                matching_methods = [
                    (cv2.TM_CCOEFF_NORMED, "Correlation Coefficient"),
                    (cv2.TM_CCORR_NORMED, "Cross Correlation"),
                    (cv2.TM_SQDIFF_NORMED, "Square Difference")
                ]
                
                best_match_val = -1
                best_match_loc = None
                best_match_method = None
                
                for screen_img, templ_img, preprocess_name in methods:
                    for method, method_name in matching_methods:
                        try:
                            # Perform template matching
                            result = cv2.matchTemplate(screen_img, templ_img, method)
                            
                            # Handle method-specific min/max logic
                            if method == cv2.TM_SQDIFF_NORMED:
                                # For SQDIFF, smaller values are better
                                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                                curr_loc = min_loc
                                # Convert to confidence value (1 - distance)
                                match_val = 1.0 - min_val
                            else:
                                # For other methods, larger values are better
                                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                                curr_loc = max_loc
                                match_val = max_val
                            
                            logger.debug(f"Method: {method_name}, Preprocess: {preprocess_name}, Match: {match_val:.4f}")
                            
                            # Track best match across all methods
                            if match_val > best_match_val:
                                best_match_val = match_val
                                best_match_loc = curr_loc
                                best_match_method = f"{preprocess_name} with {method_name}"
                                
                        except Exception as e:
                            logger.debug(f"Error with {method_name} on {preprocess_name}: {str(e)}")
                
                # If we found a reasonable match
                if best_match_val >= confidence:
                    # Get the center of the matched region
                    center_x = best_match_loc[0] + template_w // 2
                    center_y = best_match_loc[1] + template_h // 2
                    
                    logger.info(f"Image found at: ({center_x}, {center_y}) with confidence {best_match_val:.2f}")
                    logger.info(f"Best matching method: {best_match_method}")
                    return (center_x, center_y)
                
                # If we have a possible match but below confidence
                elif best_match_val > 0.5:  # A reasonable lower threshold to report "near matches"
                    logger.info(f"Possible match found but below threshold: {best_match_val:.2f} < {confidence}")
                    logger.info(f"Best matching method: {best_match_method}")
                
                # Try a multi-scale approach as a last resort
                logger.info("Attempting multi-scale template matching...")
                
                # Convert to grayscale for multi-scale search
                gray_screen = cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2GRAY)
                gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
                
                # Define scale range
                scales = [0.8, 0.9, 1.0, 1.1, 1.2]
                best_scale_val = -1
                best_scale_loc = None
                
                for scale in scales:
                    # Resize the template
                    width = int(template_w * scale)
                    height = int(template_h * scale)
                    if width <= 0 or height <= 0:
                        continue
                    
                    resized_template = cv2.resize(gray_template, (width, height))
                    
                    # Perform template matching
                    try:
                        result = cv2.matchTemplate(gray_screen, resized_template, cv2.TM_CCOEFF_NORMED)
                        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                        
                        logger.debug(f"Scale: {scale}, Match: {max_val:.4f}")
                        
                        if max_val > best_scale_val:
                            best_scale_val = max_val
                            best_scale_loc = max_loc
                            best_scale_method = f"Multi-scale at {scale}x"
                    except Exception as e:
                        logger.debug(f"Error with scale {scale}: {str(e)}")
                
                # If multi-scale improved the match
                if best_scale_val >= confidence:
                    # Get the center of the matched region
                    center_x = best_scale_loc[0] + template_w // 2
                    center_y = best_scale_loc[1] + template_h // 2
                    
                    logger.info(f"Image found with multi-scale at: ({center_x}, {center_y}) with confidence {best_scale_val:.2f}")
                    logger.info(f"Best matching method: {best_scale_method}")
                    return (center_x, center_y)
                
                # Try color/contrast adjustments if still no match
                logger.info("Attempting color and contrast adjustments...")
                
                # Try different brightness and contrast settings
                alpha_values = [0.8, 1.0, 1.2]  # Contrast
                beta_values = [-20, 0, 20]      # Brightness
                
                best_adjust_val = -1
                best_adjust_loc = None
                
                for alpha in alpha_values:
                    for beta in beta_values:
                        try:
                            # Adjust the screenshot
                            adjusted = cv2.convertScaleAbs(gray_screen, alpha=alpha, beta=beta)
                            
                            # Match with the template
                            result = cv2.matchTemplate(adjusted, gray_template, cv2.TM_CCOEFF_NORMED)
                            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                            
                            logger.debug(f"Alpha: {alpha}, Beta: {beta}, Match: {max_val:.4f}")
                            
                            if max_val > best_adjust_val:
                                best_adjust_val = max_val
                                best_adjust_loc = max_loc
                                best_adjust_method = f"Contrast/Brightness (α={alpha}, β={beta})"
                        except Exception as e:
                            logger.debug(f"Error with alpha={alpha}, beta={beta}: {str(e)}")
                
                # If adjustments improved the match
                if best_adjust_val >= confidence:
                    # Get the center of the matched region
                    center_x = best_adjust_loc[0] + template_w // 2
                    center_y = best_adjust_loc[1] + template_h // 2
                    
                    logger.info(f"Image found with adjustments at: ({center_x}, {center_y}) with confidence {best_adjust_val:.2f}")
                    logger.info(f"Best matching method: {best_adjust_method}")
                    return (center_x, center_y)
                
                # Get the best match among all techniques
                best_overall_val = max(best_match_val, 
                                      best_scale_val if 'best_scale_val' in locals() else -1,
                                      best_adjust_val if 'best_adjust_val' in locals() else -1)
                                  
                # Return the best match even if below threshold, if requested
                if params and 'return_best' in params and params.get('return_best', False) and best_overall_val > 0.4:
                    # Determine which technique had the best result
                    best_loc = None
                    best_method = "Unknown"
                    
                    if best_overall_val == best_match_val and best_match_loc is not None:
                        best_loc = best_match_loc
                        best_method = best_match_method
                    elif 'best_scale_val' in locals() and best_overall_val == best_scale_val and 'best_scale_loc' in locals() and best_scale_loc is not None:
                        best_loc = best_scale_loc
                        best_method = best_scale_method if 'best_scale_method' in locals() else "Multi-scale matching"
                    elif 'best_adjust_val' in locals() and best_overall_val == best_adjust_val and 'best_adjust_loc' in locals() and best_adjust_loc is not None:
                        best_loc = best_adjust_loc
                        best_method = best_adjust_method if 'best_adjust_method' in locals() else "Brightness/contrast adjustment"
                        
                    # If for some reason we still don't have a valid location, skip this block
                    if best_loc is None:
                        logger.error("Failed to determine best match location")
                        return None
                        
                    # Get the center of the matched region
                    center_x = best_loc[0] + template_w // 2
                    center_y = best_loc[1] + template_h // 2
                    
                    logger.info(f"Best possible match: ({center_x}, {center_y}) with confidence {best_overall_val:.2f}")
                    logger.info(f"Below threshold but returned as requested. Method: {best_method}")
                    return (center_x, center_y)
                
                # Still no good match
                logger.info(f"Image not found after all attempts (best match: {best_overall_val:.2f})")
                return None
                    
            except ImportError:
                # Fall back to pyautogui's locateCenterOnScreen if OpenCV is not available
                logger.info("OpenCV not available, falling back to PyAutoGUI")
                
                # Try with different confidence levels if needed
                confidence_levels = [confidence, confidence - 0.1, confidence - 0.2]
                for conf in confidence_levels:
                    if conf < 0.5:  # Don't go too low to avoid false positives
                        break
                    
                    logger.info(f"Trying PyAutoGUI with confidence: {conf}")
                    try:
                        # Try first with grayscale for speed (if pyautogui supports this parameter)
                        try:
                            location = pyautogui.locateCenterOnScreen(image_path, confidence=float(conf))
                            if location:
                                logger.info(f"Image found at: {location} (confidence: {conf})")
                                return location
                        except Exception as inner_e:
                            logger.debug(f"Initial pyautogui locateCenterOnScreen error: {str(inner_e)}")
                            pass
                            
                        # Additional fallback attempt - this should be minimal
                        try:
                            # Use a basic approach with just the confidence setting
                            args = {'confidence': float(conf)}
                            location = pyautogui.locateCenterOnScreen(image_path, **args)
                            if location:
                                logger.info(f"Image found at: {location} (basic, confidence: {conf})")
                                return location
                        except Exception as fallback_e:
                            logger.debug(f"Fallback pyautogui call failed: {str(fallback_e)}")
                            # Last resort - try without any special parameters if everything else fails
                            try:
                                location = pyautogui.locateCenterOnScreen(image_path)
                                if location:
                                    logger.info(f"Image found at: {location} (no params)")
                                    return location
                            except Exception:
                                pass  # Already in an exception handler, just continue
                    except Exception as e:
                        logger.warning(f"PyAutoGUI error at confidence {conf}: {str(e)}")
                
                logger.info(f"Image not found using PyAutoGUI across all confidence levels")
                return None
                
        except Exception as e:
            logger.error(f"Image search error: {str(e)}")
            return None
    
    def _find_image(self, params: Dict[str, Any]) -> bool:
        """Find an image on the screen."""
        try:
            image_path = params.get('image', '')
            if not image_path:
                logger.error("No image path provided")
                return False
            
            confidence = params.get('confidence', 0.9)
            
            # If variable name is provided, store result
            variable_name = params.get('variable', '')
            
            location = self._find_on_screen(image_path, confidence)
            if location:
                # Store coordinates in variable if requested
                if variable_name:
                    x, y = location
                    params['result'] = {'x': x, 'y': y, 'found': True}
                return True
            else:
                if variable_name:
                    params['result'] = {'found': False}
                return False
                
        except Exception as e:
            logger.error(f"Find image error: {str(e)}")
            return False
    
    def _wait_for_image(self, params: Dict[str, Any]) -> bool:
        """Wait for an image to appear on the screen."""
        try:
            image_path = params.get('image', '')
            if not image_path:
                logger.error("No image path provided")
                return False
            
            confidence = params.get('confidence', 0.9)
            timeout = params.get('timeout', 30)  # Timeout in seconds
            interval = params.get('interval', 0.5)  # Check interval
            
            # If variable name is provided, prepare to store result
            variable_name = params.get('variable', '')
            
            logger.info(f"Waiting for image to appear: {image_path} (timeout: {timeout}s)")
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                location = self._find_on_screen(image_path, confidence)
                if location:
                    logger.info(f"Image appeared after {time.time() - start_time:.1f} seconds")
                    
                    # Store coordinates in variable if requested
                    if variable_name:
                        x, y = location
                        params['result'] = {'x': x, 'y': y, 'found': True}
                    return True
                
                time.sleep(interval)
            
            # Timeout reached
            logger.warning(f"Timeout waiting for image: {image_path}")
            if variable_name:
                params['result'] = {'found': False}
            return False
            
        except Exception as e:
            logger.error(f"Wait for image error: {str(e)}")
            return False
    
    def _take_screenshot(self, params: Dict[str, Any]) -> bool:
        """Take a screenshot of the screen or a region."""
        try:
            # Create filename with timestamp if not provided
            filename = params.get('filename', '')
            if not filename:
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            # Ensure the filename has .png extension
            if not filename.lower().endswith('.png'):
                filename += '.png'
            
            # Combine with screenshots directory
            filepath = os.path.join(self.screenshots_dir, filename)
            
            # Check if we're capturing a region
            region = params.get('region', None)
            if region:
                x, y, width, height = region
                logger.info(f"Taking screenshot of region ({x}, {y}, {width}, {height}): {filepath}")
                screenshot = pyautogui.screenshot(region=(x, y, width, height))
            else:
                logger.info(f"Taking full screen screenshot: {filepath}")
                screenshot = pyautogui.screenshot()
            
            screenshot.save(filepath)
            
            # Store the path in result if variable name is provided
            variable_name = params.get('variable', '')
            if variable_name:
                params['result'] = filepath
                
            return True
        except Exception as e:
            logger.error(f"Screenshot error: {str(e)}")
            return False
            
    def _read_from_file(self, params: Dict[str, Any]) -> bool:
        """Read content from a file and store it in a variable."""
        try:
            file_path = params.get('file_path', '')
            if not file_path:
                logger.error("No file path provided")
                return False
                
            encoding = params.get('encoding', 'utf-8')
            variable_name = params.get('variable', '')
            
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return False
                
            logger.info(f"Reading from file: {file_path}")
            
            with open(file_path, 'r', encoding=encoding) as file:
                content = file.read()
                
            if variable_name:
                params['result'] = content
                logger.info(f"Stored file content in variable: {len(content)} characters")
            
            return True
            
        except Exception as e:
            logger.error(f"File read error: {str(e)}")
            return False
            
    def _write_to_file(self, params: Dict[str, Any]) -> bool:
        """Write content to a file."""
        try:
            file_path = params.get('file_path', '')
            content = params.get('content', '')
            
            if not file_path:
                logger.error("No file path provided")
                return False
                
            encoding = params.get('encoding', 'utf-8')
            
            logger.info(f"Writing to file: {file_path}")
            
            # Create directory if it doesn't exist
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                
            with open(file_path, 'w', encoding=encoding) as file:
                file.write(content)
                
            return True
            
        except Exception as e:
            logger.error(f"File write error: {str(e)}")
            return False
            
    def _append_to_file(self, params: Dict[str, Any]) -> bool:
        """Append content to a file."""
        try:
            file_path = params.get('file_path', '')
            content = params.get('content', '')
            
            if not file_path:
                logger.error("No file path provided")
                return False
                
            encoding = params.get('encoding', 'utf-8')
            
            logger.info(f"Appending to file: {file_path}")
            
            # Create directory if it doesn't exist
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                
            with open(file_path, 'a', encoding=encoding) as file:
                file.write(content)
                
            return True
            
        except Exception as e:
            logger.error(f"File append error: {str(e)}")
            return False
            
    def _wait_for_clipboard(self, params: Dict[str, Any]) -> bool:
        """Wait for clipboard content to change and store it in a variable."""
        try:
            try:
                import pyperclip
            except ImportError:
                logger.error("pyperclip module not available. Install with 'pip install pyperclip'")
                return False
                
            initial_content = pyperclip.paste()
            timeout = params.get('timeout', 30)  # Timeout in seconds
            interval = params.get('interval', 0.5)  # Check interval
            variable_name = params.get('variable', '')
            
            logger.info(f"Waiting for clipboard content to change (timeout: {timeout}s)")
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                current_content = pyperclip.paste()
                
                if current_content != initial_content:
                    logger.info(f"Clipboard content changed after {time.time() - start_time:.1f} seconds")
                    
                    if variable_name:
                        params['result'] = current_content
                        logger.info(f"Stored clipboard content in variable: {len(current_content)} characters")
                        
                    return True
                    
                time.sleep(interval)
                
            # Timeout reached
            logger.warning(f"Timeout waiting for clipboard to change")
            return False
            
        except Exception as e:
            logger.error(f"Clipboard monitoring error: {str(e)}")
            return False