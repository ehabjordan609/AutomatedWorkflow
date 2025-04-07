"""
Script manager for loading, saving, and managing automation scripts.
"""
import os
import json
import logging
import time
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class ScriptManager:
    """
    Manages automation scripts, including loading, saving, and editing.
    """
    
    def __init__(self, scripts_dir: str = "scripts"):
        """
        Initialize the script manager.
        
        Args:
            scripts_dir: Directory where scripts are stored
        """
        self.scripts_dir = scripts_dir
        self.current_script = None
        self.current_script_path = None
        
        # Create scripts directory if it doesn't exist
        os.makedirs(self.scripts_dir, exist_ok=True)
    
    def create_new_script(self, name: str) -> Dict[str, Any]:
        """
        Create a new empty script.
        
        Args:
            name: Name of the script
            
        Returns:
            dict: The new script structure
        """
        script = {
            "name": name,
            "description": "",
            "created": time.time(),
            "modified": time.time(),
            "steps": []
        }
        
        self.current_script = script
        self.current_script_path = None
        logger.info(f"Created new script: {name}")
        return script
    
    def load_script(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Load a script from a file.
        
        Args:
            file_path: Path to the script file
            
        Returns:
            dict: The loaded script, or None if loading failed
        """
        try:
            with open(file_path, 'r') as f:
                script = json.load(f)
            
            self.current_script = script
            self.current_script_path = file_path
            logger.info(f"Loaded script from {file_path}")
            return script
        except Exception as e:
            logger.error(f"Error loading script: {str(e)}")
            return None
    
    def save_script(self, file_path: Optional[str] = None) -> bool:
        """
        Save the current script to a file.
        
        Args:
            file_path: Path where to save the script, or None to use current path
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        if not self.current_script:
            logger.error("No script to save")
            return False
        
        # Update modification time
        self.current_script['modified'] = time.time()
        
        # Determine file path
        path = file_path if file_path else self.current_script_path
        if not path:
            # Generate a file path if none exists
            script_name = self.current_script['name'].replace(' ', '_').lower()
            path = os.path.join(self.scripts_dir, f"{script_name}.json")
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            
            # Save the script
            with open(path, 'w') as f:
                json.dump(self.current_script, f, indent=2)
            
            self.current_script_path = path
            logger.info(f"Saved script to {path}")
            return True
        except Exception as e:
            logger.error(f"Error saving script: {str(e)}")
            return False
    
    def add_step(self, step: Dict[str, Any], index: Optional[int] = None) -> bool:
        """
        Add a step to the current script.
        
        Args:
            step: Step data to add
            index: Position to insert the step, or None to append
            
        Returns:
            bool: True if added successfully, False otherwise
        """
        if not self.current_script:
            logger.error("No script loaded")
            return False
        
        try:
            if index is None:
                # Append to the end
                self.current_script['steps'].append(step)
            else:
                # Insert at specified position
                self.current_script['steps'].insert(index, step)
            
            logger.info(f"Added step: {step['type']} - {step.get('action', '')}")
            return True
        except Exception as e:
            logger.error(f"Error adding step: {str(e)}")
            return False
    
    def remove_step(self, index: int) -> bool:
        """
        Remove a step from the current script.
        
        Args:
            index: Index of the step to remove
            
        Returns:
            bool: True if removed successfully, False otherwise
        """
        if not self.current_script:
            logger.error("No script loaded")
            return False
        
        try:
            if 0 <= index < len(self.current_script['steps']):
                removed = self.current_script['steps'].pop(index)
                logger.info(f"Removed step at index {index}: {removed['type']} - {removed.get('action', '')}")
                return True
            else:
                logger.error(f"Invalid step index: {index}")
                return False
        except Exception as e:
            logger.error(f"Error removing step: {str(e)}")
            return False
    
    def update_step(self, index: int, step: Dict[str, Any]) -> bool:
        """
        Update a step in the current script.
        
        Args:
            index: Index of the step to update
            step: New step data
            
        Returns:
            bool: True if updated successfully, False otherwise
        """
        if not self.current_script:
            logger.error("No script loaded")
            return False
        
        try:
            if 0 <= index < len(self.current_script['steps']):
                self.current_script['steps'][index] = step
                logger.info(f"Updated step at index {index}: {step['type']} - {step.get('action', '')}")
                return True
            else:
                logger.error(f"Invalid step index: {index}")
                return False
        except Exception as e:
            logger.error(f"Error updating step: {str(e)}")
            return False
    
    def move_step(self, from_index: int, to_index: int) -> bool:
        """
        Move a step to a different position in the script.
        
        Args:
            from_index: Current index of the step
            to_index: Desired index for the step
            
        Returns:
            bool: True if moved successfully, False otherwise
        """
        if not self.current_script:
            logger.error("No script loaded")
            return False
        
        steps = self.current_script['steps']
        
        try:
            if 0 <= from_index < len(steps) and 0 <= to_index < len(steps):
                # Store the step to move
                step = steps[from_index]
                
                # Remove from original position
                steps.pop(from_index)
                
                # Insert at new position
                steps.insert(to_index, step)
                
                logger.info(f"Moved step from index {from_index} to {to_index}")
                return True
            else:
                logger.error(f"Invalid indices: from={from_index}, to={to_index}")
                return False
        except Exception as e:
            logger.error(f"Error moving step: {str(e)}")
            return False
    
    def get_scripts_list(self) -> List[str]:
        """
        Get a list of available script files.
        
        Returns:
            list: List of script file paths
        """
        try:
            if not os.path.exists(self.scripts_dir):
                return []
            
            scripts = []
            for file in os.listdir(self.scripts_dir):
                if file.endswith('.json'):
                    scripts.append(os.path.join(self.scripts_dir, file))
            
            return scripts
        except Exception as e:
            logger.error(f"Error listing scripts: {str(e)}")
            return []
    
    def get_script_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get basic information about a script without loading it fully.
        
        Args:
            file_path: Path to the script file
            
        Returns:
            dict: Basic script info, or None if error
        """
        try:
            with open(file_path, 'r') as f:
                script = json.load(f)
            
            # Return only basic info
            return {
                "name": script.get("name", "Unknown"),
                "description": script.get("description", ""),
                "created": script.get("created", 0),
                "modified": script.get("modified", 0),
                "steps_count": len(script.get("steps", []))
            }
        except Exception as e:
            logger.error(f"Error getting script info: {str(e)}")
            return None
    
    def validate_script(self, script: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Validate a script structure and return any errors.
        
        Args:
            script: Script to validate, or current script if None
            
        Returns:
            list: List of validation error messages, empty if valid
        """
        script_to_validate = script if script is not None else self.current_script
        
        if not script_to_validate:
            return ["No script to validate"]
        
        errors = []
        
        # Check required fields
        if "name" not in script_to_validate or not script_to_validate["name"]:
            errors.append("Script name is required")
        
        if "steps" not in script_to_validate:
            errors.append("Steps array is required")
        elif not isinstance(script_to_validate["steps"], list):
            errors.append("Steps must be an array")
        
        # Validate individual steps
        for i, step in enumerate(script_to_validate.get("steps", [])):
            if not isinstance(step, dict):
                errors.append(f"Step {i} must be an object")
                continue
            
            if "type" not in step:
                errors.append(f"Step {i} missing 'type' field")
            
            # Different validations based on step type
            step_type = step.get("type", "").lower()
            
            if step_type == "desktop":
                if "action" not in step:
                    errors.append(f"Desktop step {i} missing 'action' field")
            
            elif step_type == "web":
                if "action" not in step:
                    errors.append(f"Web step {i} missing 'action' field")
                
                # Check for required fields based on action
                action = step.get("action", "").lower()
                if action in ["click", "type", "wait"]:
                    if "selector" not in step:
                        errors.append(f"Web step {i} ({action}) missing 'selector' field")
            
            elif step_type == "captcha":
                if "captcha_type" not in step:
                    errors.append(f"CAPTCHA step {i} missing 'captcha_type' field")
        
        return errors
