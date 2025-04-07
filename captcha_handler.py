"""
CAPTCHA handling module for various types of CAPTCHAs.
"""
import logging
import time
import os
import io
import base64
from typing import Dict, Any, Optional, Tuple
from PIL import Image
import pytesseract
import cv2
import numpy as np

# Import Selenium components for web-based CAPTCHAs
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

class CaptchaHandler:
    """
    Handles various types of CAPTCHAs including image-based, audio, and reCAPTCHA.
    """
    
    def __init__(self):
        """Initialize the CAPTCHA handler."""
        # Configuration for Tesseract OCR
        self.tesseract_path = os.environ.get('TESSERACT_PATH', 'tesseract')
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
    
    def handle_captcha(self, params: Dict[str, Any]) -> bool:
        """
        Handle a CAPTCHA challenge.
        
        Args:
            params: Parameters for handling the CAPTCHA
            
        Returns:
            bool: True if CAPTCHA handled successfully, False otherwise
        """
        captcha_type = params.get('captcha_type', '').lower()
        
        try:
            if captcha_type == 'image':
                return self._handle_image_captcha(params)
            elif captcha_type == 'recaptcha':
                return self._handle_recaptcha(params)
            elif captcha_type == 'audio':
                return self._handle_audio_captcha(params)
            elif captcha_type == 'text':
                return self._handle_text_captcha(params)
            elif captcha_type == 'manual':
                return self._handle_manual_captcha(params)
            else:
                logger.error(f"Unknown CAPTCHA type: {captcha_type}")
                return False
        except Exception as e:
            logger.error(f"CAPTCHA handling failed: {str(e)}")
            return False
    
    def _handle_image_captcha(self, params: Dict[str, Any]) -> bool:
        """
        Handle an image-based CAPTCHA using OCR.
        
        Args:
            params: Parameters for handling the image CAPTCHA
            
        Returns:
            bool: True if CAPTCHA handled successfully, False otherwise
        """
        from web_automation import WebAutomation
        
        # Get the web automation instance from params
        web = params.get('web_automation')
        if not web or not isinstance(web, WebAutomation) or not web.driver:
            logger.error("Valid WebAutomation instance required for image CAPTCHA handling")
            return False
        
        # Get the image element
        image_selector = params.get('image_selector', {})
        if not image_selector:
            logger.error("No image selector provided for image CAPTCHA")
            return False
        
        # Get the input field where to enter the CAPTCHA solution
        input_selector = params.get('input_selector', {})
        if not input_selector:
            logger.error("No input selector provided for image CAPTCHA")
            return False
        
        # Find the image element
        image_element = web._find_element(image_selector)
        if not image_element:
            logger.error("CAPTCHA image element not found")
            return False
        
        try:
            # Get the image data
            # Method 1: Take a screenshot of the element
            image_element.screenshot('temp_captcha.png')
            
            # Preprocess the image
            image = cv2.imread('temp_captcha.png')
            
            # Apply preprocessing to improve OCR accuracy
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
            
            # Noise removal
            kernel = np.ones((2, 2), np.uint8)
            opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
            
            # Save preprocessed image
            cv2.imwrite('processed_captcha.png', opening)
            
            # OCR to get text
            captcha_text = pytesseract.image_to_string(Image.open('processed_captcha.png'), 
                                                      config='--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
            
            # Clean up the recognized text
            captcha_text = captcha_text.strip()
            
            if not captcha_text:
                logger.warning("OCR failed to recognize CAPTCHA text")
                # Clean up
                if os.path.exists('temp_captcha.png'):
                    os.remove('temp_captcha.png')
                if os.path.exists('processed_captcha.png'):
                    os.remove('processed_captcha.png')
                return False
            
            logger.info(f"Recognized CAPTCHA text: {captcha_text}")
            
            # Find and fill the input field
            input_element = web._find_element(input_selector)
            if not input_element:
                logger.error("CAPTCHA input element not found")
                return False
            
            # Clear and enter the recognized text
            input_element.clear()
            input_element.send_keys(captcha_text)
            
            # Submit if required
            if params.get('submit', False):
                submit_selector = params.get('submit_selector')
                if submit_selector:
                    submit_element = web._find_element(submit_selector)
                    if submit_element:
                        submit_element.click()
                    else:
                        logger.warning("Submit element not found, trying to submit form")
                        input_element.submit()
                else:
                    logger.info("Submitting form")
                    input_element.submit()
            
            # Clean up
            if os.path.exists('temp_captcha.png'):
                os.remove('temp_captcha.png')
            if os.path.exists('processed_captcha.png'):
                os.remove('processed_captcha.png')
            
            logger.info("Image CAPTCHA handled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Image CAPTCHA handling failed: {str(e)}")
            
            # Clean up
            if os.path.exists('temp_captcha.png'):
                os.remove('temp_captcha.png')
            if os.path.exists('processed_captcha.png'):
                os.remove('processed_captcha.png')
                
            return False
    
    def _handle_recaptcha(self, params: Dict[str, Any]) -> bool:
        """
        Handle a Google reCAPTCHA.
        For v2 reCAPTCHA, this is challenging to automate and often requires manual intervention.
        
        Args:
            params: Parameters for handling the reCAPTCHA
            
        Returns:
            bool: True if CAPTCHA handled successfully, False otherwise
        """
        from web_automation import WebAutomation
        
        # Get the web automation instance from params
        web = params.get('web_automation')
        if not web or not isinstance(web, WebAutomation) or not web.driver:
            logger.error("Valid WebAutomation instance required for reCAPTCHA handling")
            return False
        
        try:
            # Switch to the reCAPTCHA frame
            frames = web.driver.find_elements(By.TAG_NAME, "iframe")
            recaptcha_frame = None
            
            for frame in frames:
                if "recaptcha" in frame.get_attribute("src").lower():
                    recaptcha_frame = frame
                    break
            
            if not recaptcha_frame:
                logger.error("reCAPTCHA frame not found")
                return False
            
            # Switch to the reCAPTCHA frame
            web.driver.switch_to.frame(recaptcha_frame)
            
            # Find and click the checkbox (for v2 reCAPTCHA)
            checkbox = WebDriverWait(web.driver, 10).until(
                EC.presence_of_element_located((By.ID, "recaptcha-anchor"))
            )
            checkbox.click()
            
            # Switch back to the main content
            web.driver.switch_to.default_content()
            
            # Wait for user to solve the challenge if needed
            # This is where we'd need to handle image challenges, but that's very complex
            # For now, we'll wait for manual intervention if automatic clicking doesn't work
            
            logger.info("Attempted to handle reCAPTCHA - may require manual intervention")
            
            # Pause to allow manual solving if needed
            if params.get('allow_manual', True):
                logger.info("Waiting for manual reCAPTCHA intervention if needed")
                wait_time = params.get('manual_wait', 30)  # Default 30 seconds
                time.sleep(wait_time)
            
            return True
        except Exception as e:
            logger.error(f"reCAPTCHA handling failed: {str(e)}")
            return False
    
    def _handle_audio_captcha(self, params: Dict[str, Any]) -> bool:
        """
        Handle an audio CAPTCHA.
        This is a placeholder for audio CAPTCHA handling, which would require speech recognition.
        
        Args:
            params: Parameters for handling the audio CAPTCHA
            
        Returns:
            bool: True if CAPTCHA handled successfully, False otherwise
        """
        logger.warning("Audio CAPTCHA handling is not fully implemented")
        
        # This would require speech recognition capabilities
        # For now, we'll recommend manual intervention
        if params.get('allow_manual', True):
            logger.info("Waiting for manual audio CAPTCHA intervention")
            wait_time = params.get('manual_wait', 30)  # Default 30 seconds
            time.sleep(wait_time)
            return True
        
        return False
    
    def _handle_text_captcha(self, params: Dict[str, Any]) -> bool:
        """
        Handle a text-based CAPTCHA (simple math or logic question).
        
        Args:
            params: Parameters for handling the text CAPTCHA
            
        Returns:
            bool: True if CAPTCHA handled successfully, False otherwise
        """
        from web_automation import WebAutomation
        
        # Get the web automation instance from params
        web = params.get('web_automation')
        if not web or not isinstance(web, WebAutomation) or not web.driver:
            logger.error("Valid WebAutomation instance required for text CAPTCHA handling")
            return False
        
        # Get the question element
        question_selector = params.get('question_selector', {})
        if not question_selector:
            logger.error("No question selector provided for text CAPTCHA")
            return False
        
        # Get the input field where to enter the CAPTCHA solution
        input_selector = params.get('input_selector', {})
        if not input_selector:
            logger.error("No input selector provided for text CAPTCHA")
            return False
        
        try:
            # Find the question element
            question_element = web._find_element(question_selector)
            if not question_element:
                logger.error("CAPTCHA question element not found")
                return False
            
            # Get the question text
            question_text = question_element.text.strip()
            logger.info(f"Text CAPTCHA question: {question_text}")
            
            # Attempt to solve the question (basic math operations)
            answer = self._solve_text_captcha(question_text)
            if answer is None:
                logger.warning("Failed to solve text CAPTCHA")
                
                # Wait for manual intervention if allowed
                if params.get('allow_manual', True):
                    logger.info("Waiting for manual text CAPTCHA intervention")
                    wait_time = params.get('manual_wait', 30)
                    time.sleep(wait_time)
                    return True
                
                return False
            
            logger.info(f"Calculated CAPTCHA answer: {answer}")
            
            # Find and fill the input field
            input_element = web._find_element(input_selector)
            if not input_element:
                logger.error("CAPTCHA input element not found")
                return False
            
            # Clear and enter the answer
            input_element.clear()
            input_element.send_keys(str(answer))
            
            # Submit if required
            if params.get('submit', False):
                submit_selector = params.get('submit_selector')
                if submit_selector:
                    submit_element = web._find_element(submit_selector)
                    if submit_element:
                        submit_element.click()
                    else:
                        logger.warning("Submit element not found, trying to submit form")
                        input_element.submit()
                else:
                    logger.info("Submitting form")
                    input_element.submit()
            
            logger.info("Text CAPTCHA handled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Text CAPTCHA handling failed: {str(e)}")
            return False
    
    def _solve_text_captcha(self, question: str) -> Optional[str]:
        """
        Attempt to solve a text-based CAPTCHA (typically math problem).
        
        Args:
            question: The CAPTCHA question text
            
        Returns:
            str: The answer if found, None otherwise
        """
        import re
        
        # Basic math problem solver (addition, subtraction, multiplication)
        # Pattern: "What is X operator Y?"
        math_pattern = r"what is (\d+)\s*([+\-*])\s*(\d+)"
        match = re.search(math_pattern, question.lower())
        
        if match:
            num1 = int(match.group(1))
            operator = match.group(2)
            num2 = int(match.group(3))
            
            if operator == '+':
                return str(num1 + num2)
            elif operator == '-':
                return str(num1 - num2)
            elif operator == '*':
                return str(num1 * num2)
        
        # Check for "enter the number X" type challenges
        number_pattern = r"enter the number (\d+)"
        match = re.search(number_pattern, question.lower())
        if match:
            return match.group(1)
        
        # Add more patterns as needed for different text CAPTCHA types
        
        return None
    
    def _handle_manual_captcha(self, params: Dict[str, Any]) -> bool:
        """
        Wait for manual intervention to solve a CAPTCHA.
        
        Args:
            params: Parameters for handling the manual CAPTCHA
            
        Returns:
            bool: Always returns True after waiting
        """
        wait_time = params.get('wait_time', 30)  # Default 30 seconds
        logger.info(f"Waiting {wait_time} seconds for manual CAPTCHA intervention")
        time.sleep(wait_time)
        
        # Add a "continue" message to let the user know automation will resume
        logger.info("Resuming automation after manual CAPTCHA handling")
        return True
