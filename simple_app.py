#!/usr/bin/env python3
"""
Simple version of the Automation Tool application for demonstration.
This version doesn't require desktop interaction libraries.
"""
import sys
import os
import json
import time
import logging
from datetime import datetime

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class ScriptManager:
    """Simple script manager for loading, saving automation scripts."""
    
    def __init__(self, scripts_dir="scripts"):
        """Initialize the script manager."""
        self.scripts_dir = scripts_dir
        self.current_script = None
        self.current_script_path = None
        
        # Create scripts directory if it doesn't exist
        os.makedirs(self.scripts_dir, exist_ok=True)
    
    def create_new_script(self, name):
        """Create a new empty script."""
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
    
    def load_script(self, file_path):
        """Load a script from a file."""
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
    
    def save_script(self, file_path=None):
        """Save the current script to a file."""
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
    
    def get_scripts_list(self):
        """Get a list of available script files."""
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

    def add_step(self, step, index=None):
        """Add a step to the current script."""
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

class AutomationEngine:
    """Simple automation engine for simulating script execution."""
    
    def __init__(self):
        """Initialize the automation engine."""
        self.current_script = None
        
    def load_script(self, file_path):
        """Load an automation script from a JSON file."""
        try:
            with open(file_path, 'r') as f:
                self.current_script = json.load(f)
            logger.info(f"Engine loaded script: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Engine failed to load script: {str(e)}")
            return False
            
    def execute_script(self, simulate=True):
        """Execute (or simulate) the loaded script."""
        if not self.current_script:
            logger.error("No script loaded")
            return False
        
        steps = self.current_script.get('steps', [])
        total_steps = len(steps)
        
        logger.info(f"Executing script with {total_steps} steps (simulation: {simulate})")
        
        for i, step in enumerate(steps):
            step_type = step.get('type', '')
            action = step.get('action', '')
            
            logger.info(f"Step {i+1}/{total_steps}: [{step_type}] {action}")
            
            if simulate:
                # In simulation mode, just log what would happen
                self._simulate_step(step)
                # Add a small delay to make it feel more realistic
                time.sleep(0.5)
            else:
                # This would be where real execution happens
                pass
                
        logger.info("Script execution completed")
        return True
    
    def _simulate_step(self, step):
        """Simulate a step execution by logging what would happen."""
        step_type = step.get('type', '').lower()
        
        if step_type == 'desktop':
            action = step.get('action', '').lower()
            
            if action in ['click', 'right_click', 'double_click']:
                if 'image' in step:
                    logger.info(f"  Would {action} on image: {step['image']}")
                else:
                    logger.info(f"  Would {action} at position: ({step.get('x', 0)}, {step.get('y', 0)})")
            
            elif action == 'type':
                logger.info(f"  Would type text: '{step.get('text', '')}'")
            
            elif action == 'key_press':
                logger.info(f"  Would press key: {step.get('key', '')}")
                
            elif action == 'drag':
                to_data = step.get('to', {})
                logger.info(f"  Would drag from ({step.get('x', 0)}, {step.get('y', 0)}) "
                          f"to ({to_data.get('x', 0)}, {to_data.get('y', 0)})")
            
            elif action == 'scroll':
                clicks = step.get('clicks', 0)
                direction = "down" if clicks < 0 else "up"
                logger.info(f"  Would scroll {direction} by {abs(clicks)} clicks")
                
            elif action in ['find_image', 'wait_for_image']:
                logger.info(f"  Would {action.replace('_', ' ')} '{step.get('image', '')}'")
                
        elif step_type == 'web':
            action = step.get('action', '').lower()
            
            if action == 'start_browser':
                logger.info(f"  Would start {step.get('browser', 'chrome')} browser")
                
            elif action == 'navigate':
                logger.info(f"  Would navigate to URL: {step.get('url', '')}")
                
            elif action in ['click', 'type', 'clear', 'submit', 'select', 'wait']:
                selector = step.get('selector', {})
                selector_str = f"{selector.get('type', '')}='{selector.get('value', '')}'"
                
                if action == 'type':
                    logger.info(f"  Would type '{step.get('text', '')}' into element {selector_str}")
                else:
                    logger.info(f"  Would {action} on element {selector_str}")
                    
        elif step_type == 'captcha':
            captcha_type = step.get('captcha_type', '')
            logger.info(f"  Would handle {captcha_type} CAPTCHA")
            
        elif step_type == 'wait':
            logger.info(f"  Would wait for {step.get('duration', 1)} seconds")

def display_main_menu():
    """Display the main menu of the application."""
    print("\n" + "="*50)
    print("AUTOMATION TOOL - MAIN MENU")
    print("="*50)
    print("1. Create new script")
    print("2. Load existing script")
    print("3. View loaded script")
    print("4. Add step to script")
    print("5. Save script")
    print("6. Simulate script execution")
    print("7. Exit")
    print("="*50)
    
    choice = input("Enter your choice (1-7): ")
    return choice

def create_new_script(script_manager):
    """Create a new script."""
    name = input("Enter a name for the new script: ")
    script_manager.create_new_script(name)
    print(f"Created new script: {name}")
    print("\nNext steps:")
    print("1. Add steps to your script using option 4 from the main menu")
    print("2. Save your script using option 5")
    print("3. Simulate execution with option 6 to preview how it will run")

def load_script(script_manager):
    """Load an existing script."""
    scripts = script_manager.get_scripts_list()
    
    if not scripts:
        print("No scripts found!")
        return
    
    print("\nAvailable scripts:")
    for i, script_path in enumerate(scripts):
        print(f"{i+1}. {os.path.basename(script_path)}")
    
    choice = input("\nEnter script number to load (or 0 to cancel): ")
    try:
        choice = int(choice)
        if choice == 0:
            return
        if 1 <= choice <= len(scripts):
            script_path = scripts[choice-1]
            script = script_manager.load_script(script_path)
            if script:
                print(f"Loaded script: {os.path.basename(script_path)}")
                print("\nNext steps:")
                print("1. View the script using option 3 from the main menu")
                print("2. Add more steps using option 4")
                print("3. Simulate execution with option 6 to preview how it will run")
            else:
                print(f"Failed to load script: {script_path}")
        else:
            print("Invalid selection!")
    except ValueError:
        print("Please enter a number!")

def view_script(script_manager):
    """View the currently loaded script."""
    if not script_manager.current_script:
        print("No script loaded!")
        return
    
    script = script_manager.current_script
    
    print("\n" + "="*50)
    print(f"SCRIPT: {script.get('name', 'Unnamed')}")
    print(f"Description: {script.get('description', '')}")
    print(f"Created: {datetime.fromtimestamp(script.get('created', 0))}")
    print(f"Modified: {datetime.fromtimestamp(script.get('modified', 0))}")
    print(f"Steps: {len(script.get('steps', []))}")
    print("="*50)
    
    steps = script.get('steps', [])
    for i, step in enumerate(steps):
        step_type = step.get('type', '').upper()
        action = ""
        
        if step_type == "DESKTOP" or step_type == "WEB":
            action = step.get('action', '')
        elif step_type == "CAPTCHA":
            action = step.get('captcha_type', '')
        elif step_type == "WAIT":
            action = f"{step.get('duration', 1)}s"
            
        print(f"{i+1}. [{step_type}] {action}")
        
        # Show step details based on type
        if step_type == "DESKTOP":
            if action in ['click', 'right_click', 'double_click', 'move']:
                if 'image' in step:
                    print(f"   Image: {step['image']}")
                else:
                    print(f"   Position: ({step.get('x', 0)}, {step.get('y', 0)})")
            elif action == 'type':
                print(f"   Text: '{step.get('text', '')}'")
            elif action == 'key_press':
                print(f"   Key: {step.get('key', '')}")
        elif step_type == "WEB":
            if action == 'navigate':
                print(f"   URL: {step.get('url', '')}")
            elif 'selector' in step:
                selector = step.get('selector', {})
                print(f"   Selector: {selector.get('type', '')}='{selector.get('value', '')}'")
                if action == 'type':
                    print(f"   Text: '{step.get('text', '')}'")
    
    print("="*50)

def add_step(script_manager):
    """Add a step to the current script."""
    if not script_manager.current_script:
        print("No script loaded! Please create or load a script first.")
        return
    
    print("\n" + "="*50)
    print("ADD STEP")
    print("="*50)
    print("Step types:")
    print("1. Desktop action")
    print("2. Web action")
    print("3. CAPTCHA handling")
    print("4. Wait")
    print("="*50)
    
    step_type_choice = input("Enter step type (1-4): ")
    
    step = {}
    
    try:
        step_type_choice = int(step_type_choice)
        
        if step_type_choice == 1:
            step['type'] = 'desktop'
            print("\nDesktop actions:")
            print("1. Click")
            print("2. Right click")
            print("3. Double click")
            print("4. Type text")
            print("5. Press key")
            print("6. Move cursor")
            print("7. Drag")
            print("8. Scroll")
            print("9. Find image")
            print("10. Wait for image")
            
            action_choice = int(input("\nEnter action (1-10): "))
            
            actions = ['click', 'right_click', 'double_click', 'type', 'key_press', 
                      'move', 'drag', 'scroll', 'find_image', 'wait_for_image']
            
            if 1 <= action_choice <= len(actions):
                step['action'] = actions[action_choice-1]
                
                # Get action-specific parameters
                if step['action'] in ['click', 'right_click', 'double_click', 'move']:
                    use_image = input("Use image for targeting? (y/n): ").lower() == 'y'
                    if use_image:
                        step['image'] = input("Enter image path: ")
                    else:
                        step['x'] = int(input("Enter X coordinate: "))
                        step['y'] = int(input("Enter Y coordinate: "))
                
                elif step['action'] == 'type':
                    step['text'] = input("Enter text to type: ")
                
                elif step['action'] == 'key_press':
                    step['key'] = input("Enter key to press (e.g., 'enter', 'ctrl+c'): ")
                
                elif step['action'] == 'drag':
                    step['x'] = int(input("Enter start X coordinate: "))
                    step['y'] = int(input("Enter start Y coordinate: "))
                    to_data = {}
                    to_data['x'] = int(input("Enter end X coordinate: "))
                    to_data['y'] = int(input("Enter end Y coordinate: "))
                    step['to'] = to_data
                
                elif step['action'] == 'scroll':
                    step['clicks'] = int(input("Enter scroll amount (+ for up, - for down): "))
                
                elif step['action'] in ['find_image', 'wait_for_image']:
                    step['image'] = input("Enter image path: ")
                    if step['action'] == 'wait_for_image':
                        step['timeout'] = int(input("Enter timeout in seconds: "))
            else:
                print("Invalid action choice!")
                return
        
        elif step_type_choice == 2:
            step['type'] = 'web'
            print("\nWeb actions:")
            print("1. Start browser")
            print("2. Navigate to URL")
            print("3. Click element")
            print("4. Type text")
            print("5. Clear input")
            print("6. Submit form")
            print("7. Select option")
            print("8. Wait for element")
            
            action_choice = int(input("\nEnter action (1-8): "))
            
            actions = ['start_browser', 'navigate', 'click', 'type', 
                      'clear', 'submit', 'select', 'wait']
            
            if 1 <= action_choice <= len(actions):
                step['action'] = actions[action_choice-1]
                
                # Get action-specific parameters
                if step['action'] == 'start_browser':
                    browser = input("Enter browser type (chrome/firefox): ")
                    step['browser'] = browser
                    headless = input("Run in headless mode? (y/n): ").lower() == 'y'
                    step['headless'] = headless
                
                elif step['action'] == 'navigate':
                    step['url'] = input("Enter URL: ")
                
                elif step['action'] in ['click', 'type', 'clear', 'submit', 'select', 'wait']:
                    selector = {}
                    selector['type'] = input("Enter selector type (id/name/xpath/css): ")
                    selector['value'] = input("Enter selector value: ")
                    step['selector'] = selector
                    
                    if step['action'] == 'type':
                        step['text'] = input("Enter text to type: ")
                    
                    elif step['action'] == 'select':
                        select_by = input("Select by (value/text/index): ")
                        if select_by == 'value':
                            step['value'] = input("Enter option value: ")
                        elif select_by == 'text':
                            step['text'] = input("Enter option text: ")
                        elif select_by == 'index':
                            step['index'] = int(input("Enter option index: "))
                    
                    elif step['action'] == 'wait':
                        step['condition'] = input("Wait condition (presence/visible/clickable): ")
                        step['timeout'] = int(input("Enter timeout in seconds: "))
            else:
                print("Invalid action choice!")
                return
        
        elif step_type_choice == 3:
            step['type'] = 'captcha'
            print("\nCAPTCHA types:")
            print("1. Image CAPTCHA")
            print("2. reCAPTCHA")
            print("3. Text CAPTCHA")
            print("4. Manual intervention")
            
            captcha_choice = int(input("\nEnter CAPTCHA type (1-4): "))
            
            captcha_types = ['image', 'recaptcha', 'text', 'manual']
            
            if 1 <= captcha_choice <= len(captcha_types):
                step['captcha_type'] = captcha_types[captcha_choice-1]
                
                # Get additional parameters based on CAPTCHA type
                if step['captcha_type'] == 'manual':
                    step['wait_time'] = int(input("Enter wait time for manual intervention (seconds): "))
            else:
                print("Invalid CAPTCHA type choice!")
                return
        
        elif step_type_choice == 4:
            step['type'] = 'wait'
            step['duration'] = int(input("Enter wait duration in seconds: "))
        
        else:
            print("Invalid step type choice!")
            return
        
        # Common parameters
        step['delay'] = float(input("\nEnter delay before action (seconds): ") or "0.5")
        step['description'] = input("Enter step description (optional): ")
        
        # Add the step to the script
        script_manager.add_step(step)
        print("Step added successfully!")
    
    except ValueError:
        print("Please enter a valid number!")
    except Exception as e:
        print(f"Error adding step: {str(e)}")

def save_script(script_manager):
    """Save the current script."""
    if not script_manager.current_script:
        print("No script loaded!")
        return
    
    new_path = input("Enter filename to save as (leave blank to use current name): ")
    
    if new_path:
        # Ensure it has .json extension
        if not new_path.endswith('.json'):
            new_path += '.json'
        
        # Add scripts directory
        new_path = os.path.join(script_manager.scripts_dir, new_path)
        
        success = script_manager.save_script(new_path)
    else:
        success = script_manager.save_script()
    
    if success:
        saved_path = script_manager.current_script_path if hasattr(script_manager, 'current_script_path') else "unknown path"
        print(f"Script saved successfully to: {saved_path}")
        print("\nNext steps:")
        print("1. You can simulate execution with option 6 to preview how it will run")
        print("2. To run with real automation, use the main.py file:")
        print("   $ python main.py --script", os.path.basename(saved_path))
    else:
        print("Failed to save script!")

def simulate_script(script_manager):
    """Simulate execution of the current script."""
    if not script_manager.current_script:
        print("No script loaded!")
        return
    
    engine = AutomationEngine()
    engine.current_script = script_manager.current_script
    
    print("\nSimulating script execution...")
    print("\n=== SIMULATION START ===")
    engine.execute_script(simulate=True)
    print("=== SIMULATION END ===")
    print("\nSimulation completed!")
    
    # Provide guidance on running with real automation
    print("\nTo run this script with real automation:")
    print("1. Save your script using option 5 from the main menu")
    print("2. The script will be saved in the 'scripts' folder")
    print("3. To run the script with real automation, use the main.py file:")
    print("   $ python main.py --script <script_filename>")
    print("   Example: python main.py --script my_script.json")
    print("\nNote: Running with real automation requires all dependencies to be installed.")

def main():
    """Main entry point for the simple Automation Tool application."""
    print("Welcome to the Automation Tool!")
    print("This is a simplified console version for demonstration.")
    
    script_manager = ScriptManager()
    
    while True:
        choice = display_main_menu()
        
        if choice == '1':
            create_new_script(script_manager)
        elif choice == '2':
            load_script(script_manager)
        elif choice == '3':
            view_script(script_manager)
        elif choice == '4':
            add_step(script_manager)
        elif choice == '5':
            save_script(script_manager)
        elif choice == '6':
            simulate_script(script_manager)
        elif choice == '7':
            print("Thank you for using Automation Tool!")
            break
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main()