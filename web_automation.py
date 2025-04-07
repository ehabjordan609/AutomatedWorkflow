"""
Web automation module for browser interaction using Selenium.
"""
import logging
import time
import os
from typing import Dict, Any, Optional, List, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, ElementNotInteractableException,
    WebDriverException, StaleElementReferenceException
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

logger = logging.getLogger(__name__)

class WebAutomation:
    """
    Handles web automation using Selenium WebDriver.
    """
    
    def __init__(self):
        """Initialize the web automation module."""
        self.driver = None
        self.default_timeout = 30  # Default timeout in seconds
    
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
                options = Options()
                if headless:
                    options.add_argument('--headless')
                options.add_argument('--start-maximized')
                options.add_argument('--disable-notifications')
                options.add_argument('--disable-extensions')
                options.add_argument('--disable-gpu')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--no-sandbox')
                
                self.driver = webdriver.Chrome(options=options)
                self.driver.set_page_load_timeout(self.default_timeout)
                logger.info("Chrome browser started successfully")
                return True
            
            elif browser_type.lower() == 'firefox':
                from selenium.webdriver.firefox.options import Options as FirefoxOptions
                
                options = FirefoxOptions()
                if headless:
                    options.add_argument('--headless')
                
                self.driver = webdriver.Firefox(options=options)
                self.driver.set_page_load_timeout(self.default_timeout)
                logger.info("Firefox browser started successfully")
                return True
            
            else:
                logger.error(f"Unsupported browser type: {browser_type}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start browser: {str(e)}")
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
                logger.info("Browser session closed")
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
        try:
            # Start browser if not already running
            if not self.driver and action != 'start_browser':
                if not self.start_browser():
                    return False
            
            if action == 'start_browser':
                browser_type = params.get('browser', 'chrome')
                headless = params.get('headless', False)
                return self.start_browser(browser_type, headless)
            
            elif action == 'close_browser':
                return self.close_browser()
            
            elif action == 'navigate':
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
            
            elif action == 'screenshot':
                return self._take_screenshot(params)
            
            else:
                logger.error(f"Unknown web action: {action}")
                return False
                
        except Exception as e:
            logger.error(f"Web action '{action}' failed: {str(e)}")
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
        if not self.driver:
            logger.error("Browser not started")
            return None
        
        selector_type = selector.get('type', '').lower()
        selector_value = selector.get('value', '')
        
        if not selector_type or not selector_value:
            logger.error("Invalid selector: type or value missing")
            return None
        
        try:
            by_type = None
            if selector_type == 'id':
                by_type = By.ID
            elif selector_type == 'name':
                by_type = By.NAME
            elif selector_type == 'xpath':
                by_type = By.XPATH
            elif selector_type == 'css':
                by_type = By.CSS_SELECTOR
            elif selector_type == 'link_text':
                by_type = By.LINK_TEXT
            elif selector_type == 'partial_link_text':
                by_type = By.PARTIAL_LINK_TEXT
            elif selector_type == 'tag':
                by_type = By.TAG_NAME
            elif selector_type == 'class':
                by_type = By.CLASS_NAME
            else:
                logger.error(f"Unsupported selector type: {selector_type}")
                return None
            
            wait = WebDriverWait(self.driver, wait_time)
            element = wait.until(EC.presence_of_element_located((by_type, selector_value)))
            return element
            
        except TimeoutException:
            logger.warning(f"Element not found within {wait_time} seconds: {selector_type}='{selector_value}'")
            return None
        except Exception as e:
            logger.error(f"Error finding element: {str(e)}")
            return None
    
    def _navigate(self, params: Dict[str, Any]) -> bool:
        """Navigate to a URL."""
        url = params.get('url', '')
        if not url:
            logger.error("No URL specified for navigate action")
            return False
        
        try:
            self.driver.get(url)
            logger.info(f"Navigated to URL: {url}")
            
            # Wait for page to load if specified
            if 'wait_for' in params:
                wait_selector = params['wait_for']
                wait_time = params.get('timeout', 30)
                
                if self._find_element(wait_selector, wait_time):
                    logger.info(f"Page loaded successfully, element found: {wait_selector}")
                else:
                    logger.warning(f"Page loaded, but wait element not found: {wait_selector}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to URL: {str(e)}")
            return False
    
    def _click_element(self, params: Dict[str, Any]) -> bool:
        """Click on an element."""
        selector = params.get('selector', {})
        if not selector:
            logger.error("No selector specified for click action")
            return False
        
        wait_time = params.get('timeout', 10)
        element = self._find_element(selector, wait_time)
        
        if not element:
            return False
        
        try:
            # Wait for element to be clickable
            wait = WebDriverWait(self.driver, wait_time)
            clickable_element = wait.until(EC.element_to_be_clickable((
                self._get_by_type(selector['type']), selector['value']
            )))
            
            # Scroll element into view if needed
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", clickable_element)
            time.sleep(0.5)  # Small delay after scrolling
            
            clickable_element.click()
            logger.info(f"Clicked element: {selector}")
            return True
        except ElementNotInteractableException:
            # Try JavaScript click as fallback
            try:
                self.driver.execute_script("arguments[0].click();", element)
                logger.info(f"Clicked element using JavaScript: {selector}")
                return True
            except Exception as e:
                logger.error(f"Failed to click element with JavaScript: {str(e)}")
                return False
        except Exception as e:
            logger.error(f"Failed to click element: {str(e)}")
            return False
    
    def _type_text(self, params: Dict[str, Any]) -> bool:
        """Type text into an input field."""
        selector = params.get('selector', {})
        text = params.get('text', '')
        
        if not selector:
            logger.error("No selector specified for type action")
            return False
        
        if text is None:
            logger.warning("No text provided for typing action")
            return False
        
        # Convert text to string if it's not already
        text = str(text)
        
        element = self._find_element(selector)
        if not element:
            return False
        
        try:
            # Clear field if specified
            if params.get('clear', True):
                element.clear()
            
            # Type the text
            element.send_keys(text)
            logger.info(f"Typed text into element: {selector}")
            
            # Press Enter if specified
            if params.get('press_enter', False):
                element.send_keys(Keys.RETURN)
                logger.info("Pressed Enter after typing")
            
            return True
        except Exception as e:
            logger.error(f"Failed to type text: {str(e)}")
            return False
    
    def _clear_text(self, params: Dict[str, Any]) -> bool:
        """Clear text from an input field."""
        selector = params.get('selector', {})
        if not selector:
            logger.error("No selector specified for clear action")
            return False
        
        element = self._find_element(selector)
        if not element:
            return False
        
        try:
            element.clear()
            logger.info(f"Cleared text from element: {selector}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear text: {str(e)}")
            return False
    
    def _submit_form(self, params: Dict[str, Any]) -> bool:
        """Submit a form."""
        selector = params.get('selector', {})
        if not selector:
            logger.error("No selector specified for submit action")
            return False
        
        element = self._find_element(selector)
        if not element:
            return False
        
        try:
            element.submit()
            logger.info(f"Submitted form: {selector}")
            return True
        except Exception as e:
            logger.error(f"Failed to submit form: {str(e)}")
            
            # Try clicking as fallback
            try:
                element.click()
                logger.info(f"Submitted form by clicking: {selector}")
                return True
            except Exception as click_e:
                logger.error(f"Failed to submit form by clicking: {str(click_e)}")
                return False
    
    def _select_option(self, params: Dict[str, Any]) -> bool:
        """Select an option from a dropdown."""
        from selenium.webdriver.support.ui import Select
        
        selector = params.get('selector', {})
        if not selector:
            logger.error("No selector specified for select action")
            return False
        
        element = self._find_element(selector)
        if not element:
            return False
        
        try:
            select = Select(element)
            
            # Determine selection method
            if 'value' in params:
                select.select_by_value(params['value'])
                logger.info(f"Selected option by value '{params['value']}' from dropdown: {selector}")
            elif 'text' in params:
                select.select_by_visible_text(params['text'])
                logger.info(f"Selected option by text '{params['text']}' from dropdown: {selector}")
            elif 'index' in params:
                select.select_by_index(params['index'])
                logger.info(f"Selected option by index {params['index']} from dropdown: {selector}")
            else:
                logger.error("No selection method (value, text, or index) specified")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Failed to select option: {str(e)}")
            return False
    
    def _wait_for_element(self, params: Dict[str, Any]) -> bool:
        """Wait for an element to appear/be visible."""
        selector = params.get('selector', {})
        if not selector:
            logger.error("No selector specified for wait action")
            return False
        
        wait_time = params.get('timeout', 30)
        wait_type = params.get('condition', 'presence').lower()
        
        try:
            by_type = self._get_by_type(selector['type'])
            wait = WebDriverWait(self.driver, wait_time)
            
            if wait_type == 'presence':
                wait.until(EC.presence_of_element_located((by_type, selector['value'])))
                logger.info(f"Element is present: {selector}")
            elif wait_type == 'visible':
                wait.until(EC.visibility_of_element_located((by_type, selector['value'])))
                logger.info(f"Element is visible: {selector}")
            elif wait_type == 'clickable':
                wait.until(EC.element_to_be_clickable((by_type, selector['value'])))
                logger.info(f"Element is clickable: {selector}")
            elif wait_type == 'invisible':
                wait.until(EC.invisibility_of_element_located((by_type, selector['value'])))
                logger.info(f"Element is invisible: {selector}")
            else:
                logger.error(f"Unknown wait condition: {wait_type}")
                return False
            
            return True
        except TimeoutException:
            logger.warning(f"Timeout waiting for element {wait_type}: {selector}")
            return False
        except Exception as e:
            logger.error(f"Error waiting for element: {str(e)}")
            return False
    
    def _extract_data(self, params: Dict[str, Any]) -> bool:
        """Extract data from the page and store it in the script variables."""
        selector = params.get('selector', {})
        if not selector:
            logger.error("No selector specified for extract action")
            return False
        
        # What to extract
        extract_type = params.get('extract', 'text').lower()
        variable_name = params.get('variable', 'extracted_data')
        
        element = self._find_element(selector)
        if not element:
            return False
        
        try:
            result = None
            if extract_type == 'text':
                result = element.text
            elif extract_type == 'html':
                result = element.get_attribute('innerHTML')
            elif extract_type == 'attribute':
                attr_name = params.get('attribute', '')
                if not attr_name:
                    logger.error("No attribute name specified for extraction")
                    return False
                result = element.get_attribute(attr_name)
            else:
                logger.error(f"Unknown extraction type: {extract_type}")
                return False
            
            # Store the extracted data (this would be handled by script_manager in a full implementation)
            logger.info(f"Extracted {extract_type} from element: {result[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to extract data: {str(e)}")
            return False
    
    def _scroll(self, params: Dict[str, Any]) -> bool:
        """Scroll the page."""
        try:
            # Determine scroll method
            if 'selector' in params:
                # Scroll to element
                element = self._find_element(params['selector'])
                if not element:
                    return False
                
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                logger.info(f"Scrolled to element: {params['selector']}")
            
            elif 'position' in params:
                position = params['position'].lower()
                
                if position == 'top':
                    self.driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
                    logger.info("Scrolled to top of page")
                elif position == 'bottom':
                    self.driver.execute_script("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});")
                    logger.info("Scrolled to bottom of page")
                else:
                    logger.error(f"Unknown scroll position: {position}")
                    return False
            
            elif 'x' in params and 'y' in params:
                # Scroll to specific coordinates
                x = params['x']
                y = params['y']
                self.driver.execute_script(f"window.scrollTo({x}, {y});")
                logger.info(f"Scrolled to coordinates: ({x}, {y})")
            
            else:
                # Default scroll (down a bit)
                self.driver.execute_script("window.scrollBy(0, window.innerHeight / 2);")
                logger.info("Scrolled down by half a viewport")
            
            # Wait a moment after scrolling
            time.sleep(0.5)
            return True
        except Exception as e:
            logger.error(f"Failed to scroll: {str(e)}")
            return False
    
    def _switch_frame(self, params: Dict[str, Any]) -> bool:
        """Switch to an iframe."""
        try:
            if 'selector' in params:
                # Switch to frame by element
                element = self._find_element(params['selector'])
                if not element:
                    return False
                
                self.driver.switch_to.frame(element)
                logger.info(f"Switched to frame: {params['selector']}")
            
            elif 'index' in params:
                # Switch to frame by index
                index = params['index']
                self.driver.switch_to.frame(index)
                logger.info(f"Switched to frame at index: {index}")
            
            elif 'id' in params:
                # Switch to frame by id/name
                id_name = params['id']
                self.driver.switch_to.frame(id_name)
                logger.info(f"Switched to frame with id/name: {id_name}")
            
            elif params.get('parent', False):
                # Switch to parent frame
                self.driver.switch_to.parent_frame()
                logger.info("Switched to parent frame")
            
            elif params.get('default', False):
                # Switch to default content
                self.driver.switch_to.default_content()
                logger.info("Switched to default content")
            
            else:
                logger.error("No frame selection method specified")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Failed to switch frame: {str(e)}")
            return False
    
    def _switch_window(self, params: Dict[str, Any]) -> bool:
        """Switch to a different browser window/tab."""
        try:
            if 'index' in params:
                # Switch by window index
                index = params['index']
                handles = self.driver.window_handles
                
                if 0 <= index < len(handles):
                    self.driver.switch_to.window(handles[index])
                    logger.info(f"Switched to window at index: {index}")
                    return True
                else:
                    logger.error(f"Window index out of range: {index}, valid range: 0-{len(handles)-1}")
                    return False
            
            elif 'title' in params:
                # Switch by window title
                title = params['title']
                current_handle = self.driver.current_window_handle
                
                for handle in self.driver.window_handles:
                    self.driver.switch_to.window(handle)
                    if title in self.driver.title:
                        logger.info(f"Switched to window with title containing: {title}")
                        return True
                
                # If no matching window found, go back to original
                self.driver.switch_to.window(current_handle)
                logger.warning(f"No window found with title containing: {title}")
                return False
            
            elif 'url' in params:
                # Switch by window URL
                url = params['url']
                current_handle = self.driver.current_window_handle
                
                for handle in self.driver.window_handles:
                    self.driver.switch_to.window(handle)
                    if url in self.driver.current_url:
                        logger.info(f"Switched to window with URL containing: {url}")
                        return True
                
                # If no matching window found, go back to original
                self.driver.switch_to.window(current_handle)
                logger.warning(f"No window found with URL containing: {url}")
                return False
            
            elif 'new' in params and params['new']:
                # Switch to newly opened window
                handles = self.driver.window_handles
                self.driver.switch_to.window(handles[-1])
                logger.info("Switched to most recently opened window")
                return True
            
            else:
                logger.error("No window selection method specified")
                return False
                
        except Exception as e:
            logger.error(f"Failed to switch window: {str(e)}")
            return False
    
    def _execute_script(self, params: Dict[str, Any]) -> bool:
        """Execute JavaScript in the browser."""
        script = params.get('script', '')
        if not script:
            logger.error("No script specified for execute_script action")
            return False
        
        try:
            result = self.driver.execute_script(script)
            logger.info("Executed JavaScript successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to execute JavaScript: {str(e)}")
            return False
    
    def _take_screenshot(self, params: Dict[str, Any]) -> bool:
        """Take a screenshot of the current page."""
        filename = params.get('filename', f'screenshot_{int(time.time())}.png')
        
        try:
            self.driver.save_screenshot(filename)
            logger.info(f"Screenshot saved to: {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to take screenshot: {str(e)}")
            return False
    
    def _get_by_type(self, selector_type: str) -> Any:
        """Convert selector type string to Selenium By type."""
        selector_type = selector_type.lower()
        
        if selector_type == 'id':
            return By.ID
        elif selector_type == 'name':
            return By.NAME
        elif selector_type == 'xpath':
            return By.XPATH
        elif selector_type == 'css':
            return By.CSS_SELECTOR
        elif selector_type == 'link_text':
            return By.LINK_TEXT
        elif selector_type == 'partial_link_text':
            return By.PARTIAL_LINK_TEXT
        elif selector_type == 'tag':
            return By.TAG_NAME
        elif selector_type == 'class':
            return By.CLASS_NAME
        else:
            raise ValueError(f"Unsupported selector type: {selector_type}")
