"""
Recorder widget for capturing user actions and creating automation scripts.
This is a simplified version that runs in both GUI and headless environments.
"""
import logging
import time
import threading
from typing import Dict, List, Any, Optional, Tuple

# Import conditionally to handle environments without PyQt5
try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
        QTableWidgetItem, QComboBox, QLineEdit, QFormLayout, QGroupBox, QCheckBox,
        QSpinBox, QMessageBox, QHeaderView
    )
    from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QTimer
    from PyQt5.QtGui import QIcon, QFont, QColor
    USE_QT = True
except ImportError:
    USE_QT = False
    # Create mock types for type checking
    class QWidget: pass
    class pyqtSignal: 
        def __init__(self, *args): pass
        def emit(self, *args): pass

# Import conditionally to handle environments without pyautogui
try:
    import pyautogui
    USE_PYAUTOGUI = True
except ImportError:
    USE_PYAUTOGUI = False

# Mock mouse and keyboard classes for environments without pynput
class MockMouse:
    class Button:
        left = "left"
        right = "right"
    
    class Listener:
        def __init__(self, on_click=None, on_scroll=None):
            self.on_click = on_click
            self.on_scroll = on_scroll
        
        def start(self):
            pass
        
        def stop(self):
            pass

class MockKeyboard:
    class Listener:
        def __init__(self, on_press=None):
            self.on_press = on_press
        
        def start(self):
            pass
        
        def stop(self):
            pass

# Use mock objects if pynput is not available
try:
    from pynput import mouse, keyboard
except ImportError:
    mouse = MockMouse()
    keyboard = MockKeyboard()

from script_manager import ScriptManager

logger = logging.getLogger(__name__)

class RecorderWidget(QWidget):
    """
    Widget for recording user actions and creating automation scripts.
    """
    
    def __init__(self, script_manager: ScriptManager, automation_engine=None, parent=None):
        """Initialize the recorder widget."""
        super().__init__(parent)
        self.script_manager = script_manager
        self.automation_engine = automation_engine
        
        # Recording state
        self.is_recording = False
        self.recorded_steps = []
        self.mouse_listener = None
        self.keyboard_listener = None
        self.last_mouse_time = 0
        self.last_keyboard_time = 0
        self.last_position = (0, 0)
        
        # Recording settings
        self.min_mouse_interval = 0.3  # Minimum seconds between mouse events
        self.min_keyboard_interval = 0.1  # Minimum seconds between keyboard events
        self.record_mouse_movement = False
        self.mouse_movement_interval = 0.5  # Seconds between recording mouse movements
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the recorder widget UI."""
        layout = QVBoxLayout(self)
        
        # Recording settings
        settings_group = QGroupBox("Recording Settings")
        settings_layout = QFormLayout(settings_group)
        
        # Mouse movement recording
        self.record_movement_checkbox = QCheckBox("Record mouse movements")
        self.record_movement_checkbox.setChecked(self.record_mouse_movement)
        self.record_movement_checkbox.stateChanged.connect(self._on_record_movement_changed)
        settings_layout.addRow("", self.record_movement_checkbox)
        
        # Mouse events interval
        self.mouse_interval_spinbox = QSpinBox()
        self.mouse_interval_spinbox.setRange(1, 5000)
        self.mouse_interval_spinbox.setValue(int(self.min_mouse_interval * 1000))
        self.mouse_interval_spinbox.setSuffix(" ms")
        self.mouse_interval_spinbox.valueChanged.connect(self._on_mouse_interval_changed)
        settings_layout.addRow("Minimum interval between mouse events:", self.mouse_interval_spinbox)
        
        # Keyboard events interval
        self.keyboard_interval_spinbox = QSpinBox()
        self.keyboard_interval_spinbox.setRange(1, 1000)
        self.keyboard_interval_spinbox.setValue(int(self.min_keyboard_interval * 1000))
        self.keyboard_interval_spinbox.setSuffix(" ms")
        self.keyboard_interval_spinbox.valueChanged.connect(self._on_keyboard_interval_changed)
        settings_layout.addRow("Minimum interval between keyboard events:", self.keyboard_interval_spinbox)
        
        # Movement sampling interval
        self.movement_interval_spinbox = QSpinBox()
        self.movement_interval_spinbox.setRange(100, 2000)
        self.movement_interval_spinbox.setValue(int(self.mouse_movement_interval * 1000))
        self.movement_interval_spinbox.setSuffix(" ms")
        self.movement_interval_spinbox.valueChanged.connect(self._on_movement_interval_changed)
        settings_layout.addRow("Mouse movement sampling interval:", self.movement_interval_spinbox)
        
        layout.addWidget(settings_group)
        
        # Recorded steps display
        steps_group = QGroupBox("Recorded Steps")
        steps_layout = QVBoxLayout(steps_group)
        
        self.steps_table = QTableWidget()
        self.steps_table.setColumnCount(4)
        self.steps_table.setHorizontalHeaderLabels(["#", "Type", "Action", "Details"])
        self.steps_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.steps_table.horizontalHeader().setStretchLastSection(True)
        self.steps_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.steps_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        
        steps_layout.addWidget(self.steps_table)
        
        # Table buttons
        table_buttons_layout = QHBoxLayout()
        
        self.clear_button = QPushButton("Clear Steps")
        self.clear_button.clicked.connect(self._clear_steps)
        table_buttons_layout.addWidget(self.clear_button)
        
        self.save_script_button = QPushButton("Save As Script")
        self.save_script_button.clicked.connect(self._save_as_script)
        table_buttons_layout.addWidget(self.save_script_button)
        
        steps_layout.addLayout(table_buttons_layout)
        
        layout.addWidget(steps_group)
        
        # Recording controls
        controls_layout = QHBoxLayout()
        
        # Status label
        self.status_label = QLabel("Ready to record")
        self.status_label.setStyleSheet("font-weight: bold;")
        controls_layout.addWidget(self.status_label)
        
        controls_layout.addStretch()
        
        # Start/Stop button
        self.record_button = QPushButton("Start Recording")
        self.record_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.record_button.clicked.connect(self._toggle_recording)
        self.record_button.setMinimumWidth(150)
        controls_layout.addWidget(self.record_button)
        
        # Add manual step button
        self.add_manual_button = QPushButton("Add Wait Step")
        self.add_manual_button.clicked.connect(self._add_wait_step)
        controls_layout.addWidget(self.add_manual_button)
        
        layout.addLayout(controls_layout)
        
        # Set up a timer for checking mouse position (for movement recording)
        self.mouse_timer = QTimer()
        self.mouse_timer.timeout.connect(self._check_mouse_position)
    
    def update_ui(self):
        """Update the UI with current state."""
        # Update controls based on recording state
        if self.is_recording:
            self.record_button.setText("Stop Recording")
            self.record_button.setStyleSheet("background-color: #F44336; color: white; font-weight: bold;")
            self.status_label.setText("Recording...")
            self.clear_button.setEnabled(False)
            self.save_script_button.setEnabled(False)
            self.add_manual_button.setEnabled(True)
        else:
            self.record_button.setText("Start Recording")
            self.record_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
            self.status_label.setText("Ready to record")
            self.clear_button.setEnabled(True)
            self.save_script_button.setEnabled(len(self.recorded_steps) > 0)
            self.add_manual_button.setEnabled(False)
        
        # Update steps table
        self._update_steps_table()
    
    def _toggle_recording(self):
        """Toggle recording state."""
        if self.is_recording:
            self._stop_recording()
        else:
            self._start_recording()
    
    def _start_recording(self):
        """Start recording user actions."""
        if self.is_recording:
            return
        
        # Clear existing steps if requested
        if self.recorded_steps and QMessageBox.question(
            self, "Clear Steps?",
            "Do you want to clear existing recorded steps before starting?",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            self.recorded_steps.clear()
        
        # Set up mouse listener
        self.mouse_listener = mouse.Listener(
            on_click=self._on_mouse_click,
            on_scroll=self._on_mouse_scroll
        )
        
        # Set up keyboard listener
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press
        )
        
        # Reset timers
        self.last_mouse_time = time.time()
        self.last_keyboard_time = time.time()
        self.last_position = pyautogui.position()
        
        # Start listeners
        self.mouse_listener.start()
        self.keyboard_listener.start()
        
        # Start movement timer if needed
        if self.record_mouse_movement:
            self.mouse_timer.start(int(self.mouse_movement_interval * 1000))
        
        self.is_recording = True
        self.update_ui()
        
        logger.info("Recording started")
    
    def _stop_recording(self):
        """Stop recording user actions."""
        if not self.is_recording:
            return
        
        # Stop listeners
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
        
        # Stop movement timer
        self.mouse_timer.stop()
        
        self.is_recording = False
        self.update_ui()
        
        logger.info("Recording stopped")
    
    def _on_mouse_click(self, x, y, button, pressed):
        """Handle mouse click events."""
        if not pressed:  # Only capture press events, not releases
            return
        
        # Check if enough time has passed since last mouse event
        current_time = time.time()
        if current_time - self.last_mouse_time < self.min_mouse_interval:
            return
        
        self.last_mouse_time = current_time
        
        # Determine action type based on button
        action = "click"
        if button == mouse.Button.right:
            action = "right_click"
        
        # Add step
        step = {
            "type": "desktop",
            "action": action,
            "x": x,
            "y": y,
            "delay": 0.5
        }
        
        self.recorded_steps.append(step)
        
        # Update UI from the main thread
        QTimer.singleShot(0, self.update_ui)
    
    def _on_mouse_scroll(self, x, y, dx, dy):
        """Handle mouse scroll events."""
        # Check if enough time has passed since last mouse event
        current_time = time.time()
        if current_time - self.last_mouse_time < self.min_mouse_interval:
            return
        
        self.last_mouse_time = current_time
        
        # Add step (convert dy to scroll clicks)
        clicks = int(dy * 5)  # Adjust multiplier as needed
        
        step = {
            "type": "desktop",
            "action": "scroll",
            "clicks": clicks,
            "delay": 0.5
        }
        
        self.recorded_steps.append(step)
        
        # Update UI from the main thread
        QTimer.singleShot(0, self.update_ui)
    
    def _on_key_press(self, key):
        """Handle keyboard press events."""
        # Check if enough time has passed since last keyboard event
        current_time = time.time()
        if current_time - self.last_keyboard_time < self.min_keyboard_interval:
            return
        
        self.last_keyboard_time = current_time
        
        # Determine which key was pressed
        key_char = None
        
        try:
            # Try to get character representation
            key_char = key.char
        except AttributeError:
            # Special key, use name
            key_name = str(key).replace("Key.", "")
            
            # Only record certain special keys
            if key_name in ["enter", "tab", "space", "backspace", "esc", "delete"]:
                key_char = key_name
        
        if key_char:
            # Add step
            step = {
                "type": "desktop",
                "action": "key_press",
                "key": key_char,
                "delay": 0.5
            }
            
            self.recorded_steps.append(step)
            
            # Update UI from the main thread
            QTimer.singleShot(0, self.update_ui)
    
    def _check_mouse_position(self):
        """Check mouse position for movement recording."""
        if not self.is_recording or not self.record_mouse_movement:
            return
        
        current_pos = pyautogui.position()
        
        # Only record if position has changed significantly
        if (abs(current_pos[0] - self.last_position[0]) > 10 or 
            abs(current_pos[1] - self.last_position[1]) > 10):
            
            # Add movement step
            step = {
                "type": "desktop",
                "action": "move",
                "x": current_pos[0],
                "y": current_pos[1],
                "duration": 0.5,
                "delay": 0.1
            }
            
            self.recorded_steps.append(step)
            self.last_position = current_pos
            
            # Update UI
            self.update_ui()
    
    def _update_steps_table(self):
        """Update the steps table with recorded steps."""
        # Clear existing rows
        self.steps_table.setRowCount(0)
        
        # Add rows for each step
        for i, step in enumerate(self.recorded_steps):
            self.steps_table.insertRow(i)
            
            # Step number
            item = QTableWidgetItem(str(i + 1))
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.steps_table.setItem(i, 0, item)
            
            # Step type
            step_type = step.get("type", "").capitalize()
            type_item = QTableWidgetItem(step_type)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.steps_table.setItem(i, 1, type_item)
            
            # Action
            action = step.get("action", "")
            if step_type.lower() == "wait":
                action = f"Wait {step.get('duration', 1)}s"
                
            action_item = QTableWidgetItem(action)
            action_item.setFlags(action_item.flags() & ~Qt.ItemIsEditable)
            self.steps_table.setItem(i, 2, action_item)
            
            # Details
            details = self._get_step_details(step)
            details_item = QTableWidgetItem(details)
            details_item.setFlags(details_item.flags() & ~Qt.ItemIsEditable)
            self.steps_table.setItem(i, 3, details_item)
        
        # Adjust row heights
        for i in range(self.steps_table.rowCount()):
            self.steps_table.resizeRowToContents(i)
    
    def _get_step_details(self, step: Dict[str, Any]) -> str:
        """Generate a human-readable description of step details."""
        step_type = step.get("type", "").lower()
        
        if step_type == "desktop":
            action = step.get("action", "").lower()
            
            if action in ["click", "right_click", "double_click", "move"]:
                return f"At ({step.get('x', 0)}, {step.get('y', 0)})"
            
            elif action == "key_press":
                return f"Key: {step.get('key', '')}"
            
            elif action == "scroll":
                clicks = step.get("clicks", 0)
                direction = "down" if clicks < 0 else "up"
                return f"{direction} {abs(clicks)} clicks"
        
        elif step_type == "wait":
            return f"Duration: {step.get('duration', 1)} seconds"
        
        return ""
    
    def _clear_steps(self):
        """Clear all recorded steps."""
        if not self.recorded_steps:
            return
        
        # Confirm clearing
        if QMessageBox.question(
            self, "Confirm Clear",
            "Are you sure you want to clear all recorded steps?",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            self.recorded_steps.clear()
            self.update_ui()
    
    def _save_as_script(self):
        """Save recorded steps as a new script."""
        if not self.recorded_steps:
            QMessageBox.warning(self, "Warning", "No steps recorded")
            return
        
        # Get script name
        from PyQt5.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(self, "New Script", "Enter script name:")
        if not ok or not name:
            return
        
        # Create a new script
        script = self.script_manager.create_new_script(name)
        
        # Add recorded steps
        for step in self.recorded_steps:
            self.script_manager.add_step(step)
        
        # Save the script
        if self.script_manager.save_script():
            QMessageBox.information(
                self, "Success", 
                f"Recorded steps saved as script '{name}'"
            )
        else:
            QMessageBox.critical(
                self, "Error", 
                "Failed to save script"
            )
    
    def _add_wait_step(self):
        """Add a manual wait step during recording."""
        if not self.is_recording:
            return
        
        # Get wait duration
        from PyQt5.QtWidgets import QInputDialog
        
        duration, ok = QInputDialog.getInt(
            self, "Add Wait Step", 
            "Enter wait duration (seconds):",
            value=2, min=1, max=60
        )
        
        if ok:
            # Add wait step
            step = {
                "type": "wait",
                "duration": duration
            }
            
            self.recorded_steps.append(step)
            self.update_ui()
    
    def _on_record_movement_changed(self, state):
        """Handle record movement checkbox state change."""
        self.record_mouse_movement = (state == Qt.Checked)
        self.movement_interval_spinbox.setEnabled(self.record_mouse_movement)
    
    def _on_mouse_interval_changed(self, value):
        """Handle mouse interval change."""
        self.min_mouse_interval = value / 1000.0
    
    def _on_keyboard_interval_changed(self, value):
        """Handle keyboard interval change."""
        self.min_keyboard_interval = value / 1000.0
    
    def _on_movement_interval_changed(self, value):
        """Handle movement interval change."""
        self.mouse_movement_interval = value / 1000.0
        if self.is_recording and self.record_mouse_movement:
            self.mouse_timer.stop()
            self.mouse_timer.start(value)
