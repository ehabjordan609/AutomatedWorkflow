"""
Core automation engine that coordinates between different automation types and executes scripts.
"""
import logging
import json
import time
from typing import Dict, List, Any, Optional

from desktop_automation import DesktopAutomation
from web_automation import WebAutomation
from captcha_handler import CaptchaHandler

logger = logging.getLogger(__name__)

class AutomationEngine:
    """
    Manages automation script execution and coordinates between different automation modules.
    """
    
    def __init__(self):
        """Initialize the automation engine with required components."""
        self.desktop = DesktopAutomation()
        self.web = WebAutomation()
        self.captcha = CaptchaHandler()
        self.current_script = None
        self.is_running = False
        self.is_paused = False
        self.step_by_step = False
        self.current_step = 0
        
    def load_script(self, file_path: str) -> bool:
        """
        Load an automation script from a JSON file.
        
        Args:
            file_path: Path to the script JSON file
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            with open(file_path, 'r') as f:
                self.current_script = json.load(f)
            logger.info(f"Script loaded successfully from {file_path}")
            self.current_step = 0
            return True
        except Exception as e:
            logger.error(f"Failed to load script: {str(e)}")
            return False
    
    def execute_script(self, step_by_step: bool = False) -> bool:
        """
        Execute the currently loaded script.
        
        Args:
            step_by_step: If True, stops after each step for manual continuation
            
        Returns:
            bool: True if executed successfully, False otherwise
        """
        if not self.current_script:
            logger.error("No script loaded")
            return False
        
        self.is_running = True
        self.is_paused = False
        self.step_by_step = step_by_step
        self.current_step = 0
        
        steps = self.current_script.get('steps', [])
        total_steps = len(steps)
        
        try:
            while self.current_step < total_steps and self.is_running:
                if self.is_paused:
                    time.sleep(0.1)
                    continue
                
                step = steps[self.current_step]
                success = self._execute_step(step)
                
                if not success:
                    logger.error(f"Step {self.current_step + 1} failed: {step}")
                    return False
                
                self.current_step += 1
                
                # Wait if in step-by-step mode
                if self.step_by_step and self.current_step < total_steps:
                    self.is_paused = True
            
            logger.info("Script executed successfully")
            self.is_running = False
            return True
            
        except Exception as e:
            logger.error(f"Script execution failed: {str(e)}")
            self.is_running = False
            return False
    
    def pause(self):
        """Pause script execution."""
        if self.is_running and not self.is_paused:
            self.is_paused = True
            logger.info("Script execution paused")
    
    def resume(self):
        """Resume script execution."""
        if self.is_running and self.is_paused:
            self.is_paused = False
            logger.info("Script execution resumed")
    
    def stop(self):
        """Stop script execution."""
        if self.is_running:
            self.is_running = False
            self.is_paused = False
            logger.info("Script execution stopped")
    
    def _execute_step(self, step: Dict[str, Any]) -> bool:
        """
        Execute a single step from the script.
        
        Args:
            step: Dictionary containing step information
            
        Returns:
            bool: True if step executed successfully, False otherwise
        """
        step_type = step.get('type', '').lower()
        action = step.get('action', '').lower()
        
        logger.info(f"Executing step: {step_type} - {action}")
        
        # Add a small delay between actions to avoid overwhelming the system
        time.sleep(step.get('delay', 0.5))
        
        try:
            if step_type == 'desktop':
                return self.desktop.execute_action(action, step)
            elif step_type == 'web':
                return self.web.execute_action(action, step)
            elif step_type == 'captcha':
                return self.captcha.handle_captcha(step)
            elif step_type == 'wait':
                time.sleep(step.get('duration', 1))
                return True
            else:
                logger.error(f"Unknown step type: {step_type}")
                return False
        except Exception as e:
            logger.error(f"Step execution failed: {str(e)}")
            return False
