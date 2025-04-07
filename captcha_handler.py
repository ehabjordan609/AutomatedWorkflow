#!/usr/bin/env python3
"""
CAPTCHA handling module for various types of CAPTCHAs.
"""
import os
import re
import time
import logging
import tempfile
from typing import Dict, Any, Optional

# Import these conditionally within functions to avoid errors if not installed
# import cv2
# import numpy as np
# import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)

class CaptchaHandler:
    """
    Handles various types of CAPTCHAs including image-based, audio, and reCAPTCHA.
    """
    
    def __init__(self):
        """Initialize the CAPTCHA handler."""
        self.temp_dir = tempfile.gettempdir()
        self.captcha_images_dir = "captcha_images"
        
        # Create captcha images directory if it doesn't exist
        if not os.path.exists(self.captcha_images_dir):
            os.makedirs(self.captcha_images_dir)
        
        # Configure pytesseract path (update this with your Tesseract OCR installation path)
        # This is for Windows - adjust for your OS
        tesseract_path = os.environ.get('TESSERACT_PATH')
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        logger.info("CaptchaHandler initialized")
    
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
            logger.error(f"Error handling CAPTCHA: {str(e)}")
            return False
    
    def _handle_image_captcha(self, params: Dict[str, Any]) -> bool:
        """
        Handle an image-based CAPTCHA using OCR.
        
        Args:
            params: Parameters for handling the image CAPTCHA
            
        Returns:
            bool: True if CAPTCHA handled successfully, False otherwise
        """
        image_path = params.get('image_path', '')
        selector = params.get('selector', {})
        
        if not image_path and not selector:
            logger.error("No image path or selector provided")
            return False
        
        # If we have a selector, we need to get the image from a web element
        # This would be handled by the web automation module and passed as an image path
        
        try:
            # Create a timestamped filename if saving the image
            if params.get('save_image', False):
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                save_path = os.path.join(self.captcha_images_dir, f"captcha_{timestamp}.png")
                # Copy the image to the save location
                if image_path:
                    import shutil
                    shutil.copy2(image_path, save_path)
                    logger.info(f"Saved CAPTCHA image to {save_path}")
            
            # Preprocess and OCR the image
            text = self._ocr_captcha_image(image_path, params.get('preprocessing', 'default'))
            
            if not text:
                logger.warning("OCR failed to extract text from CAPTCHA image")
                return False
            
            logger.info(f"OCR extracted text from CAPTCHA: '{text}'")
            
            # Provide the text for web automation to fill in
            params['result'] = text
            
            return True
        except Exception as e:
            logger.error(f"Image CAPTCHA handling error: {str(e)}")
            return False
    
    def _ocr_captcha_image(self, image_path: str, preprocessing: str) -> Optional[str]:
        """
        Use OCR to extract text from a CAPTCHA image.
        
        Args:
            image_path: Path to the CAPTCHA image
            preprocessing: Type of preprocessing to apply ('default', 'threshold', etc.)
            
        Returns:
            str: Extracted text or None if failed
        """
        try:
            # Read the image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Failed to read image: {image_path}")
                return None
            
            # Apply preprocessing based on the type
            if preprocessing == 'threshold':
                # Convert to grayscale
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                # Apply threshold
                _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
                # Noise removal (optional)
                kernel = np.ones((2, 2), np.uint8)
                cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
                
                # Save preprocessed image for debugging if needed
                if os.environ.get('DEBUG', '').lower() == 'true':
                    cv2.imwrite(os.path.join(self.temp_dir, "captcha_preprocessed.png"), cleaned)
                
                # Convert back to PIL format for tesseract
                pil_image = Image.fromarray(cleaned)
                
            elif preprocessing == 'adaptive':
                # Convert to grayscale
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                # Apply adaptive threshold
                binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                               cv2.THRESH_BINARY, 11, 2)
                # Noise removal (optional)
                kernel = np.ones((1, 1), np.uint8)
                cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
                
                # Save preprocessed image for debugging if needed
                if os.environ.get('DEBUG', '').lower() == 'true':
                    cv2.imwrite(os.path.join(self.temp_dir, "captcha_preprocessed.png"), cleaned)
                
                # Convert back to PIL format for tesseract
                pil_image = Image.fromarray(cleaned)
                
            else:  # default or any other value
                # Use the original image with minimal processing
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(image_rgb)
            
            # Use pytesseract with specific config for CAPTCHA
            # psm 7 = treat image as single line of text
            # psm 8 = treat image as single word
            # psm 13 = treat image as single line of text with no specific script or language
            custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
            text = pytesseract.image_to_string(pil_image, config=custom_config)
            
            # Clean up the text (remove whitespace, newlines, etc.)
            text = re.sub(r'[\s\n]+', '', text).strip()
            
            return text
        except Exception as e:
            logger.error(f"OCR error: {str(e)}")
            return None
    
    def _handle_recaptcha(self, params: Dict[str, Any]) -> bool:
        """
        Handle a Google reCAPTCHA.
        For v2 reCAPTCHA, this is challenging to automate and often requires manual intervention.
        
        Args:
            params: Parameters for handling the reCAPTCHA
            
        Returns:
            bool: True if CAPTCHA handled successfully, False otherwise
        """
        recaptcha_version = params.get('version', 'v2')
        
        if recaptcha_version.lower() == 'v2':
            logger.warning("reCAPTCHA v2 typically requires manual intervention")
            
            # For v2 with checkbox, we can attempt to click the checkbox
            if params.get('checkbox', True):
                logger.info("Attempting to click reCAPTCHA checkbox")
                
                # The actual click would need to be handled by the web automation module
                # We just return an indication that manual intervention is likely needed
                params['result'] = {
                    'solved': False,
                    'needs_manual': True,
                    'message': "reCAPTCHA v2 likely needs manual intervention"
                }
                
                # We return True to continue the script, but the script should check the result
                return True
            else:
                # For invisible reCAPTCHA, we have limited options
                logger.warning("Invisible reCAPTCHA detected, continuing with script")
                params['result'] = {
                    'solved': False,
                    'needs_manual': True,
                    'message': "Invisible reCAPTCHA detected"
                }
                return True
                
        elif recaptcha_version.lower() == 'v3':
            # v3 doesn't require user interaction, it runs in the background
            logger.info("reCAPTCHA v3 detected, continuing with script")
            params['result'] = {
                'solved': True,
                'needs_manual': False,
                'message': "reCAPTCHA v3 should not require interaction"
            }
            return True
        
        else:
            logger.error(f"Unknown reCAPTCHA version: {recaptcha_version}")
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
        # Audio CAPTCHA handling is complex and typically requires:
        # 1. Clicking an audio button (handled by web automation)
        # 2. Downloading the audio file
        # 3. Converting audio to text using speech recognition
        
        logger.warning("Audio CAPTCHA handling is not fully implemented")
        
        # For now, we recommend manual intervention
        params['result'] = {
            'solved': False,
            'needs_manual': True,
            'message': "Audio CAPTCHA requires manual intervention"
        }
        
        return self._handle_manual_captcha(params)
    
    def _handle_text_captcha(self, params: Dict[str, Any]) -> bool:
        """
        Handle a text-based CAPTCHA (simple math or logic question).
        
        Args:
            params: Parameters for handling the text CAPTCHA
            
        Returns:
            bool: True if CAPTCHA handled successfully, False otherwise
        """
        question = params.get('question', '')
        
        if not question:
            logger.error("No question provided for text CAPTCHA")
            return False
        
        # Attempt to solve the text CAPTCHA
        answer = self._solve_text_captcha(question)
        
        if answer:
            logger.info(f"Solved text CAPTCHA: '{question}' -> '{answer}'")
            params['result'] = answer
            return True
        else:
            logger.warning(f"Could not solve text CAPTCHA: '{question}'")
            
            # If we can't solve it, we might need manual intervention
            return self._handle_manual_captcha(params)
    
    def _solve_text_captcha(self, question: str) -> Optional[str]:
        """
        Attempt to solve a text-based CAPTCHA (typically math problem).
        
        Args:
            question: The CAPTCHA question text
            
        Returns:
            str: The answer if found, None otherwise
        """
        # Handling simple math questions like "What is 5 + 3?"
        math_pattern = r'what\s+is\s+(\d+)\s*([\+\-\*\/])\s*(\d+)'
        matches = re.search(math_pattern, question.lower())
        
        if matches:
            num1 = int(matches.group(1))
            operator = matches.group(2)
            num2 = int(matches.group(3))
            
            if operator == '+':
                return str(num1 + num2)
            elif operator == '-':
                return str(num1 - num2)
            elif operator == '*':
                return str(num1 * num2)
            elif operator == '/':
                # Avoid division by zero
                if num2 == 0:
                    return None
                return str(int(num1 / num2))
        
        # Handling "type the characters you see" type questions
        if 'type the characters' in question.lower() or 'enter the text' in question.lower():
            # This would require OCR on an associated image, which should be
            # handled by _handle_image_captcha instead
            logger.warning("This appears to be an image CAPTCHA question")
            return None
        
        return None
    
    def _handle_manual_captcha(self, params: Dict[str, Any]) -> bool:
        """
        Wait for manual intervention to solve a CAPTCHA.
        
        Args:
            params: Parameters for handling the manual CAPTCHA
            
        Returns:
            bool: Always returns True after waiting
        """
        wait_time = params.get('wait_time', 30)  # Default wait time: 30 seconds
        
        logger.info(f"Waiting {wait_time} seconds for manual CAPTCHA intervention")
        
        # In a real implementation, you might want to show a notification or alert
        # to the user that manual intervention is needed
        
        # Simple wait implementation
        time.sleep(wait_time)
        
        logger.info("Resuming automation after manual intervention wait time")
        
        # We always return True after waiting, assuming the user handled the CAPTCHA
        return True