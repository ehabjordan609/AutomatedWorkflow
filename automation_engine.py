#!/usr/bin/env python3
"""
Core automation engine that coordinates between different automation types and executes scripts.
"""
import os
import json
import time
import logging
from typing import Dict, Any, List, Optional, Tuple

# Import automation modules
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
        self.desktop_automation = DesktopAutomation()
        self.web_automation = WebAutomation()
        self.captcha_handler = CaptchaHandler()
        
        self.current_script = None
        self.is_running = False
        self.is_paused = False
        self.current_step_index = 0
        self.variables = {}  # Script variables for storing data between steps
        
        logger.info("AutomationEngine initialized")
    
    def load_script(self, file_path: str) -> bool:
        """
        Load an automation script from a JSON file.
        
        Args:
            file_path: Path to the script JSON file
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            with open(file_path, 'r') as file:
                self.current_script = json.load(file)
            logger.info(f"Script loaded from {file_path}")
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
        
        steps = self.current_script.get('steps', [])
        if not steps:
            logger.warning("Script has no steps to execute")
            return True
        
        self.is_running = True
        self.is_paused = False
        self.current_step_index = 0
        
        logger.info(f"Starting script execution with {len(steps)} steps")
        
        while self.current_step_index < len(steps) and self.is_running:
            if self.is_paused:
                time.sleep(0.1)
                continue
            
            step = steps[self.current_step_index]
            logger.info(f"Executing step {self.current_step_index + 1}/{len(steps)}: {step.get('description', 'No description')}")
            
            # Process step delay
            delay = step.get('delay', 0)
            if delay > 0:
                logger.debug(f"Waiting for delay: {delay}s")
                time.sleep(delay)
            
            # Execute the step
            success = self._execute_step(step)
            
            if not success:
                logger.error(f"Step {self.current_step_index + 1} failed")
                if not step.get('continue_on_error', False):
                    self.is_running = False
                    return False
            
            self.current_step_index += 1
            
            # If in step-by-step mode, pause after each step
            if step_by_step and self.current_step_index < len(steps):
                self.is_paused = True
        
        self.is_running = False
        self.is_paused = False
        logger.info("Script execution completed")
        return True
    
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
        
        try:
            # Handle different step types
            if step_type == 'desktop':
                action = step.get('action', '')
                return self.desktop_automation.execute_action(action, step)
                
            elif step_type == 'web':
                action = step.get('action', '')
                return self.web_automation.execute_action(action, step)
                
            elif step_type == 'captcha':
                return self.captcha_handler.handle_captcha(step)
                
            elif step_type == 'wait':
                duration = step.get('duration', 1)
                logger.info(f"Waiting for {duration} seconds")
                time.sleep(duration)
                return True
                
            elif step_type == 'variable':
                action = step.get('action', '')
                name = step.get('name', '')
                value = step.get('value', '')
                
                if action == 'set':
                    self.variables[name] = value
                    logger.debug(f"Set variable '{name}' to '{value}'")
                    return True
                elif action == 'clear':
                    if name in self.variables:
                        del self.variables[name]
                        logger.debug(f"Cleared variable '{name}'")
                    return True
                else:
                    logger.error(f"Unknown variable action: {action}")
                    return False
                    
            elif step_type == 'condition':
                condition = step.get('condition', {})
                if_steps = step.get('if_steps', [])
                else_steps = step.get('else_steps', [])
                
                condition_met = self._evaluate_condition(condition)
                
                if condition_met:
                    logger.info("Condition met, executing 'if' steps")
                    for if_step in if_steps:
                        if not self._execute_step(if_step):
                            return False
                else:
                    logger.info("Condition not met, executing 'else' steps")
                    for else_step in else_steps:
                        if not self._execute_step(else_step):
                            return False
                return True
                
            else:
                logger.error(f"Unknown step type: {step_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing step: {str(e)}")
            return False
    
    def _evaluate_condition(self, condition: Dict[str, Any]) -> bool:
        """
        Evaluate a condition from a conditional step.
        
        Args:
            condition: Dictionary containing condition information
            
        Returns:
            bool: True if condition is met, False otherwise
        """
        condition_type = condition.get('type', '')
        
        if condition_type == 'variable_exists':
            var_name = condition.get('variable', '')
            return var_name in self.variables
            
        elif condition_type == 'variable_equals':
            var_name = condition.get('variable', '')
            value = condition.get('value', '')
            return var_name in self.variables and self.variables[var_name] == value
            
        elif condition_type == 'variable_contains':
            var_name = condition.get('variable', '')
            value = condition.get('value', '')
            return var_name in self.variables and value in str(self.variables[var_name])
            
        else:
            logger.error(f"Unknown condition type: {condition_type}")
            return False