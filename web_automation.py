#!/usr/bin/env python3
"""
Web automation module for browser interaction using Selenium.
"""
import os
import time
import logging
from typing import Dict, Any, Optional, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

logger = logging.getLogger(__name__)

class WebAutomation:
    """
    Handles web automation using Selenium WebDriver.
    """
    
    def __init__(self):
        """Initialize the web automation module."""
        self.driver = None
        self.default_timeout = 30
        self.screenshots_dir = "screenshots"
        
        # Create screenshots directory if it doesn't exist
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)
        
        logger.info("WebAutomation initialized")
    
    def start_browser(self, browser_type: str = 'chrome', headless: bool = False) -> bool:
        """
        Start a browser session.
        
        Args:
            browser_type: Type of browser ('chrome', 'firefox', etc.)
            headless: Whether to run in headless mode
            
        Returns:
            bool: True if browser started successfully, False otherwise
        """
        try:
            if browser_type.lower() == 'chrome':
                from selenium.webdriver.chrome.options import Options
                from selenium.webdriver.chrome.service import Service
                from webdriver_manager.chrome import ChromeDriverManager
                
                options = Options()
                if headless:
                    options.add_argument('--headless')
                options.add_argument('--start-maximized')
                options.add_argument('--disable-notifications')
                options.add_argument('--disable-extensions')
                options.add_argument('--disable-gpu')
                
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
                self.driver.set_page_load_timeout(self.default_timeout)
                logger.info("Chrome browser started")
                return True
                
            elif browser_type.lower() == 'firefox':
                from selenium.webdriver.firefox.options import Options as FirefoxOptions
                from selenium.webdriver.firefox.service import Service as FirefoxService
                from webdriver_manager.firefox import GeckoDriverManager
                
                options = FirefoxOptions()
                if headless:
                    options.add_argument('--headless')
                
                service = FirefoxService(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service, options=options)
                self.driver.set_page_load_timeout(self.default_timeout)
                logger.info("Firefox browser started")
                return True
                
            else:
                logger.error(f"Unsupported browser type: {browser_type}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start browser: {str(e)}")
            return False
    
    def start_browser_with_profile(self, browser_type: str = 'chrome', profile_path: str = None, headless: bool = False) -> bool:
        """
        Start a browser session with a specific user profile.
        
        Args:
            browser_type: Type of browser ('chrome', 'firefox', etc.)
            profile_path: Path to Chrome user data directory or Firefox profile
            headless: Whether to run in headless mode
            
        Returns:
            bool: True if browser started successfully, False otherwise
        """
        try:
            if browser_type.lower() == 'chrome':
                from selenium.webdriver.chrome.options import Options
                from selenium.webdriver.chrome.service import Service
                from webdriver_manager.chrome import ChromeDriverManager
                
                options = Options()
                if headless:
                    options.add_argument('--headless')
                options.add_argument('--start-maximized')
                options.add_argument('--disable-notifications')
                options.add_argument('--disable-extensions')
                options.add_argument('--disable-gpu')
                
                # Add user data directory if specified
                if profile_path:
                    options.add_argument(f'--user-data-dir={profile_path}')
                
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
                self.driver.set_page_load_timeout(self.default_timeout)
                logger.info(f"Chrome browser started with profile: {profile_path}")
                return True
            
            elif browser_type.lower() == 'firefox':
                from selenium.webdriver.firefox.options import Options as FirefoxOptions
                from selenium.webdriver.firefox.service import Service as FirefoxService
                from webdriver_manager.firefox import GeckoDriverManager
                
                options = FirefoxOptions()
                if headless:
                    options.add_argument('--headless')
                
                # Add profile if specified
                if profile_path:
                    options.add_argument('-profile')
                    options.add_argument(profile_path)
                
                service = FirefoxService(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service, options=options)
                self.driver.set_page_load_timeout(self.default_timeout)
                logger.info(f"Firefox browser started with profile: {profile_path}")
                return True
            
            else:
                logger.error(f"Unsupported browser type: {browser_type}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start browser with profile: {str(e)}")
            return False
    
    def close_browser(self) -> bool:
        """
        Close the browser session.
        
        Returns:
            bool: True if browser closed successfully, False otherwise
        """
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                logger.info("Browser closed")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to close browser: {str(e)}")
            return False
    
    def execute_action(self, action: str, params: Dict[str, Any]) -> bool:
        """
        Execute a web automation action.
        
        Args:
            action: Type of action to perform
            params: Parameters for the action
            
        Returns:
            bool: True if action executed successfully, False otherwise
        """
        if not self.driver and action not in ['start_browser', 'start_browser_with_profile']:
            logger.error("Browser not started, cannot execute action")
            return False
        
        try:
            # Map actions to methods
            if action == 'start_browser':
                browser_type = params.get('browser', 'chrome')
                headless = params.get('headless', False)
                return self.start_browser(browser_type, headless)
                
            elif action == 'start_browser_with_profile':
                browser_type = params.get('browser', 'chrome')
                profile_path = params.get('profile_path', None)
                headless = params.get('headless', False)
                return self.start_browser_with_profile(browser_type, profile_path, headless)
                
            elif action == 'close_browser':
                return self.close_browser()
                
            elif action == 'navigate':
                url = params.get('url', '')
                return self._navigate(params)
                
            elif action == 'click':
                return self._click_element(params)
                
            elif action == 'type':
                return self._type_text(params)
                
            elif action == 'clear':
                return self._clear_text(params)
                
            elif action == 'submit':
                return self._submit_form(params)
                
            elif action == 'select':
                return self._select_option(params)
                
            elif action == 'wait':
                return self._wait_for_element(params)
                
            elif action == 'extract':
                return self._extract_data(params)
                
            elif action == 'scroll':
                return self._scroll(params)
                
            elif action == 'switch_frame':
                return self._switch_frame(params)
                
            elif action == 'switch_window':
                return self._switch_window(params)
                
            elif action == 'execute_script':
                return self._execute_script(params)
                
            elif action == 'take_screenshot':
                return self._take_screenshot(params)
                
            else:
                logger.error(f"Unknown web action: {action}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing web action '{action}': {str(e)}")
            return False
    
    def _find_element(self, selector: Dict[str, str], wait_time: int = 10) -> Optional[Any]:
        """
        Find an element using the specified selector.
        
        Args:
            selector: Dictionary with selector type and value
            wait_time: Time to wait for element to appear
            
        Returns:
            WebElement if found, None otherwise
        """
        selector_type = selector.get('type', '').lower()
        selector_value = selector.get('value', '')
        
        if not selector_type or not selector_value:
            logger.error("Invalid selector: missing type or value")
            return None
        
        try:
            by_type = self._get_by_type(selector_type)
            wait = WebDriverWait(self.driver, wait_time)
            element = wait.until(EC.presence_of_element_located((by_type, selector_value)))
            return element
        except TimeoutException:
            logger.error(f"Timeout waiting for element: {selector_type}='{selector_value}'")
            return None
        except Exception as e:
            logger.error(f"Error finding element: {str(e)}")
            return None
    
    def _navigate(self, params: Dict[str, Any]) -> bool:
        """Navigate to a URL."""
        url = params.get('url', '')
        if not url:
            logger.error("Missing URL for navigation")
            return False
        
        try:
            logger.info(f"Navigating to {url}")
            self.driver.get(url)
            
            # Wait for page to load
            wait_time = params.get('wait_time', 10)
            time.sleep(1)  # Small fixed delay for initial load
            
            current_url = self.driver.current_url
            logger.info(f"Navigation complete, current URL: {current_url}")
            
            return True
        except Exception as e:
            logger.error(f"Navigation error: {str(e)}")
            return False
    
    def _click_element(self, params: Dict[str, Any]) -> bool:
        """Click on an element."""
        selector = params.get('selector', {})
        wait_time = params.get('wait_time', 10)
        
        element = self._find_element(selector, wait_time)
        if not element:
            return False
        
        try:
            # Wait for element to be clickable
            wait = WebDriverWait(self.driver, wait_time)
            element = wait.until(EC.element_to_be_clickable((
                self._get_by_type(selector.get('type', '')), 
                selector.get('value', '')
            )))
            
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            time.sleep(0.5)  # Small delay after scrolling
            
            logger.info(f"Clicking element: {selector}")
            element.click()
            return True
        except Exception as e:
            logger.error(f"Click error: {str(e)}")
            return False
    
    def _type_text(self, params: Dict[str, Any]) -> bool:
        """Type text into an input field."""
        selector = params.get('selector', {})
        text = params.get('text', '')
        wait_time = params.get('wait_time', 10)
        
        element = self._find_element(selector, wait_time)
        if not element:
            return False
        
        try:
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            time.sleep(0.5)  # Small delay after scrolling
            
            logger.info(f"Typing text: '{text}' into element {selector}")
            
            # Clear the field first if specified
            if params.get('clear_first', True):
                element.clear()
            
            # Type with natural typing speed if specified
            if params.get('natural_typing', False):
                for char in text:
                    element.send_keys(char)
                    time.sleep(0.05)  # Slight delay between keypresses
            else:
                element.send_keys(text)
                
            return True
        except Exception as e:
            logger.error(f"Type error: {str(e)}")
            return False
    
    def _clear_text(self, params: Dict[str, Any]) -> bool:
        """Clear text from an input field."""
        selector = params.get('selector', {})
        wait_time = params.get('wait_time', 10)
        
        element = self._find_element(selector, wait_time)
        if not element:
            return False
        
        try:
            logger.info(f"Clearing text from element {selector}")
            element.clear()
            return True
        except Exception as e:
            logger.error(f"Clear error: {str(e)}")
            return False
    
    def _submit_form(self, params: Dict[str, Any]) -> bool:
        """Submit a form."""
        selector = params.get('selector', {})
        wait_time = params.get('wait_time', 10)
        
        element = self._find_element(selector, wait_time)
        if not element:
            return False
        
        try:
            logger.info(f"Submitting form with element {selector}")
            element.submit()
            return True
        except Exception as e:
            logger.error(f"Submit error: {str(e)}")
            return False
    
    def _select_option(self, params: Dict[str, Any]) -> bool:
        """Select an option from a dropdown."""
        selector = params.get('selector', {})
        wait_time = params.get('wait_time', 10)
        
        element = self._find_element(selector, wait_time)
        if not element:
            return False
        
        try:
            select = Select(element)
            
            # Different ways to select an option
            if 'value' in params:
                logger.info(f"Selecting option with value '{params['value']}'")
                select.select_by_value(params['value'])
            elif 'text' in params:
                logger.info(f"Selecting option with text '{params['text']}'")
                select.select_by_visible_text(params['text'])
            elif 'index' in params:
                logger.info(f"Selecting option with index {params['index']}")
                select.select_by_index(params['index'])
            else:
                logger.error("No selection method specified (value, text, or index)")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Select error: {str(e)}")
            return False
    
    def _wait_for_element(self, params: Dict[str, Any]) -> bool:
        """Wait for an element to appear/be visible."""
        selector = params.get('selector', {})
        condition = params.get('condition', 'presence').lower()
        timeout = params.get('timeout', 10)
        
        try:
            by_type = self._get_by_type(selector.get('type', ''))
            selector_value = selector.get('value', '')
            
            wait = WebDriverWait(self.driver, timeout)
            
            if condition == 'presence':
                logger.info(f"Waiting for presence of element {selector}")
                wait.until(EC.presence_of_element_located((by_type, selector_value)))
            elif condition == 'visible':
                logger.info(f"Waiting for visibility of element {selector}")
                wait.until(EC.visibility_of_element_located((by_type, selector_value)))
            elif condition == 'clickable':
                logger.info(f"Waiting for element to be clickable {selector}")
                wait.until(EC.element_to_be_clickable((by_type, selector_value)))
            elif condition == 'invisible':
                logger.info(f"Waiting for invisibility of element {selector}")
                wait.until(EC.invisibility_of_element_located((by_type, selector_value)))
            else:
                logger.error(f"Unknown wait condition: {condition}")
                return False
                
            logger.info("Wait condition satisfied")
            return True
        except TimeoutException:
            logger.error(f"Timeout waiting for element: {selector}")
            return False
        except Exception as e:
            logger.error(f"Wait error: {str(e)}")
            return False
    
    def _extract_data(self, params: Dict[str, Any]) -> bool:
        """Extract data from the page and store it in the script variables."""
        selector = params.get('selector', {})
        attribute = params.get('attribute', 'text')
        variable_name = params.get('variable', '')
        wait_time = params.get('wait_time', 10)
        
        if not variable_name:
            logger.error("Missing variable name for extracted data")
            return False
        
        element = self._find_element(selector, wait_time)
        if not element:
            return False
        
        try:
            if attribute.lower() == 'text':
                value = element.text
            else:
                value = element.get_attribute(attribute)
                
            logger.info(f"Extracted '{attribute}': '{value}' from {selector}")
            
            # Return the value through the result parameter
            params['result'] = value
            return True
        except Exception as e:
            logger.error(f"Extract error: {str(e)}")
            return False
    
    def _scroll(self, params: Dict[str, Any]) -> bool:
        """Scroll the page."""
        try:
            if 'selector' in params:
                # Scroll to element
                element = self._find_element(params['selector'], params.get('wait_time', 10))
                if not element:
                    return False
                
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                logger.info(f"Scrolled to element {params['selector']}")
            elif 'position' in params:
                # Scroll to specific position
                position = params['position']
                if isinstance(position, dict) and 'x' in position and 'y' in position:
                    self.driver.execute_script(f"window.scrollTo({position['x']}, {position['y']});")
                    logger.info(f"Scrolled to position x:{position['x']}, y:{position['y']}")
                else:
                    logger.error("Invalid scroll position format")
                    return False
            elif 'direction' in params:
                # Scroll in a direction
                direction = params['direction'].lower()
                amount = params.get('amount', 300)
                
                if direction == 'up':
                    self.driver.execute_script(f"window.scrollBy(0, -{amount});")
                    logger.info(f"Scrolled up by {amount} pixels")
                elif direction == 'down':
                    self.driver.execute_script(f"window.scrollBy(0, {amount});")
                    logger.info(f"Scrolled down by {amount} pixels")
                elif direction == 'left':
                    self.driver.execute_script(f"window.scrollBy(-{amount}, 0);")
                    logger.info(f"Scrolled left by {amount} pixels")
                elif direction == 'right':
                    self.driver.execute_script(f"window.scrollBy({amount}, 0);")
                    logger.info(f"Scrolled right by {amount} pixels")
                else:
                    logger.error(f"Unknown scroll direction: {direction}")
                    return False
            else:
                logger.error("Missing scroll parameters")
                return False
                
            # Wait a moment after scrolling
            time.sleep(params.get('wait_after', 0.5))
            return True
        except Exception as e:
            logger.error(f"Scroll error: {str(e)}")
            return False
    
    def _switch_frame(self, params: Dict[str, Any]) -> bool:
        """Switch to an iframe."""
        try:
            if 'selector' in params:
                # Switch to frame by element
                element = self._find_element(params['selector'], params.get('wait_time', 10))
                if not element:
                    return False
                
                logger.info(f"Switching to frame using element {params['selector']}")
                self.driver.switch_to.frame(element)
            elif 'index' in params:
                # Switch to frame by index
                index = params['index']
                logger.info(f"Switching to frame with index {index}")
                self.driver.switch_to.frame(index)
            elif 'id' in params:
                # Switch to frame by id or name
                id_name = params['id']
                logger.info(f"Switching to frame with id/name '{id_name}'")
                self.driver.switch_to.frame(id_name)
            elif params.get('parent', False):
                # Switch to parent frame
                logger.info("Switching to parent frame")
                self.driver.switch_to.parent_frame()
            elif params.get('default', False):
                # Switch to default content
                logger.info("Switching to default content")
                self.driver.switch_to.default_content()
            else:
                logger.error("Missing frame switch parameters")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Frame switch error: {str(e)}")
            return False
    
    def _switch_window(self, params: Dict[str, Any]) -> bool:
        """Switch to a different browser window/tab."""
        try:
            if 'index' in params:
                # Switch to window by index
                index = params['index']
                handles = self.driver.window_handles
                
                if index >= len(handles):
                    logger.error(f"Window index {index} out of range (max: {len(handles)-1})")
                    return False
                
                logger.info(f"Switching to window with index {index}")
                self.driver.switch_to.window(handles[index])
                
            elif 'title' in params:
                # Switch to window by partial title
                title = params['title']
                current_handle = self.driver.current_window_handle
                
                found = False
                for handle in self.driver.window_handles:
                    self.driver.switch_to.window(handle)
                    if title in self.driver.title:
                        found = True
                        logger.info(f"Switched to window with title containing '{title}'")
                        break
                
                if not found:
                    logger.error(f"No window found with title containing '{title}'")
                    self.driver.switch_to.window(current_handle)
                    return False
                    
            elif 'url' in params:
                # Switch to window by partial URL
                url = params['url']
                current_handle = self.driver.current_window_handle
                
                found = False
                for handle in self.driver.window_handles:
                    self.driver.switch_to.window(handle)
                    if url in self.driver.current_url:
                        found = True
                        logger.info(f"Switched to window with URL containing '{url}'")
                        break
                
                if not found:
                    logger.error(f"No window found with URL containing '{url}'")
                    self.driver.switch_to.window(current_handle)
                    return False
                    
            elif 'new' in params and params['new']:
                # Open a new tab
                logger.info("Opening new tab")
                self.driver.execute_script("window.open('about:blank', '_blank');")
                self.driver.switch_to.window(self.driver.window_handles[-1])
                
            else:
                logger.error("Missing window switch parameters")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Window switch error: {str(e)}")
            return False
    
    def _execute_script(self, params: Dict[str, Any]) -> bool:
        """Execute JavaScript in the browser."""
        script = params.get('script', '')
        if not script:
            logger.error("Missing JavaScript for execution")
            return False
        
        try:
            args = params.get('args', [])
            logger.info(f"Executing JavaScript: {script[:50]}...")
            result = self.driver.execute_script(script, *args)
            
            # Store the result if variable name is provided
            if 'variable' in params:
                params['result'] = result
                logger.info(f"JavaScript execution result stored in variable '{params['variable']}'")
            
            return True
        except Exception as e:
            logger.error(f"JavaScript execution error: {str(e)}")
            return False
    
    def _take_screenshot(self, params: Dict[str, Any]) -> bool:
        """Take a screenshot of the current page."""
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
            
            logger.info(f"Taking screenshot: {filepath}")
            self.driver.save_screenshot(filepath)
            
            return True
        except Exception as e:
            logger.error(f"Screenshot error: {str(e)}")
            return False
    
    def _get_by_type(self, selector_type: str) -> Any:
        """Convert selector type string to Selenium By type."""
        selector_map = {
            'id': By.ID,
            'name': By.NAME,
            'class': By.CLASS_NAME,
            'tag': By.TAG_NAME,
            'link_text': By.LINK_TEXT,
            'partial_link_text': By.PARTIAL_LINK_TEXT,
            'css': By.CSS_SELECTOR,
            'xpath': By.XPATH
        }
        
        return selector_map.get(selector_type.lower(), By.CSS_SELECTOR)