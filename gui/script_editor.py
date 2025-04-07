"""
Script editor widget for creating and editing automation scripts.
"""
import logging
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QComboBox, QLineEdit, QFormLayout, QDialog, QDialogButtonBox,
    QTabWidget, QSplitter, QFrame, QGroupBox, QTextEdit, QSpinBox, QCheckBox,
    QMessageBox, QFileDialog, QMenu, QHeaderView, QScrollArea, QToolButton,
    QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QFont, QColor

from script_manager import ScriptManager

logger = logging.getLogger(__name__)

class StepEditorDialog(QDialog):
    """
    Dialog for editing a single automation step.
    """
    
    def __init__(self, step: Optional[Dict[str, Any]] = None, parent=None):
        """Initialize the step editor dialog."""
        super().__init__(parent)
        self.setWindowTitle("Edit Automation Step")
        self.setMinimumWidth(600)
        
        self.step = step.copy() if step else {"type": "desktop", "action": "click"}
        
        self._create_ui()
        self._populate_fields()
    
    def _create_ui(self):
        """Create the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Tab widget for different step types
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Step type selection
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Step Type:"))
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Desktop", "Web", "Captcha", "Wait"])
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        type_layout.addWidget(self.type_combo)
        
        layout.addLayout(type_layout)
        
        # Desktop tab
        self.desktop_widget = QWidget()
        desktop_layout = QVBoxLayout(self.desktop_widget)
        
        self.desktop_action_combo = QComboBox()
        self.desktop_action_combo.addItems([
            "click", "right_click", "double_click", "type", "key_press", 
            "move", "drag", "scroll", "find_image", "wait_for_image"
        ])
        self.desktop_action_combo.currentTextChanged.connect(self._on_desktop_action_changed)
        
        action_layout = QHBoxLayout()
        action_layout.addWidget(QLabel("Action:"))
        action_layout.addWidget(self.desktop_action_combo)
        desktop_layout.addLayout(action_layout)
        
        # Desktop parameters form
        self.desktop_params_form = QFormLayout()
        desktop_layout.addLayout(self.desktop_params_form)
        
        # Web tab
        self.web_widget = QWidget()
        web_layout = QVBoxLayout(self.web_widget)
        
        self.web_action_combo = QComboBox()
        self.web_action_combo.addItems([
            "start_browser", "close_browser", "navigate", "click", "type", 
            "clear", "submit", "select", "wait", "extract", "scroll", 
            "switch_frame", "switch_window", "execute_script", "screenshot"
        ])
        self.web_action_combo.currentTextChanged.connect(self._on_web_action_changed)
        
        web_action_layout = QHBoxLayout()
        web_action_layout.addWidget(QLabel("Action:"))
        web_action_layout.addWidget(self.web_action_combo)
        web_layout.addLayout(web_action_layout)
        
        # Web parameters form
        self.web_params_form = QFormLayout()
        web_layout.addLayout(self.web_params_form)
        
        # CAPTCHA tab
        self.captcha_widget = QWidget()
        captcha_layout = QVBoxLayout(self.captcha_widget)
        
        self.captcha_type_combo = QComboBox()
        self.captcha_type_combo.addItems([
            "image", "recaptcha", "audio", "text", "manual"
        ])
        self.captcha_type_combo.currentTextChanged.connect(self._on_captcha_type_changed)
        
        captcha_type_layout = QHBoxLayout()
        captcha_type_layout.addWidget(QLabel("CAPTCHA Type:"))
        captcha_type_layout.addWidget(self.captcha_type_combo)
        captcha_layout.addLayout(captcha_type_layout)
        
        # CAPTCHA parameters form
        self.captcha_params_form = QFormLayout()
        captcha_layout.addLayout(self.captcha_params_form)
        
        # Wait tab
        self.wait_widget = QWidget()
        wait_layout = QFormLayout(self.wait_widget)
        
        self.wait_duration = QSpinBox()
        self.wait_duration.setRange(1, 3600)
        self.wait_duration.setValue(1)
        self.wait_duration.setSuffix(" seconds")
        wait_layout.addRow("Duration:", self.wait_duration)
        
        # Add tabs to tab widget
        self.tab_widget.addTab(self.desktop_widget, "Desktop")
        self.tab_widget.addTab(self.web_widget, "Web")
        self.tab_widget.addTab(self.captcha_widget, "CAPTCHA")
        self.tab_widget.addTab(self.wait_widget, "Wait")
        
        # Common fields
        common_group = QGroupBox("Common Parameters")
        common_layout = QFormLayout(common_group)
        
        self.delay_spinbox = QSpinBox()
        self.delay_spinbox.setRange(0, 60)
        self.delay_spinbox.setValue(1)
        self.delay_spinbox.setSuffix(" seconds")
        common_layout.addRow("Delay before action:", self.delay_spinbox)
        
        self.description_edit = QLineEdit()
        common_layout.addRow("Description:", self.description_edit)
        
        layout.addWidget(common_group)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _populate_fields(self):
        """Populate dialog fields with step data."""
        # Set step type
        step_type = self.step.get("type", "desktop").capitalize()
        index = self.type_combo.findText(step_type)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)
        
        # Select appropriate tab
        if step_type.lower() == "desktop":
            self.tab_widget.setCurrentWidget(self.desktop_widget)
            
            # Set desktop action
            action = self.step.get("action", "click")
            index = self.desktop_action_combo.findText(action)
            if index >= 0:
                self.desktop_action_combo.setCurrentIndex(index)
                
        elif step_type.lower() == "web":
            self.tab_widget.setCurrentWidget(self.web_widget)
            
            # Set web action
            action = self.step.get("action", "click")
            index = self.web_action_combo.findText(action)
            if index >= 0:
                self.web_action_combo.setCurrentIndex(index)
                
        elif step_type.lower() == "captcha":
            self.tab_widget.setCurrentWidget(self.captcha_widget)
            
            # Set captcha type
            captcha_type = self.step.get("captcha_type", "image")
            index = self.captcha_type_combo.findText(captcha_type)
            if index >= 0:
                self.captcha_type_combo.setCurrentIndex(index)
                
        elif step_type.lower() == "wait":
            self.tab_widget.setCurrentWidget(self.wait_widget)
            self.wait_duration.setValue(self.step.get("duration", 1))
        
        # Set common fields
        self.delay_spinbox.setValue(self.step.get("delay", 1))
        self.description_edit.setText(self.step.get("description", ""))
        
        # Update parameter forms based on selected actions
        if step_type.lower() == "desktop":
            self._populate_desktop_params()
        elif step_type.lower() == "web":
            self._populate_web_params()
        elif step_type.lower() == "captcha":
            self._populate_captcha_params()
    
    def _populate_desktop_params(self):
        """Populate desktop action parameters."""
        self._clear_form_layout(self.desktop_params_form)
        action = self.desktop_action_combo.currentText()
        
        if action in ["click", "right_click", "double_click", "move"]:
            # Coordinate fields
            x_spinbox = QSpinBox()
            x_spinbox.setRange(0, 9999)
            x_spinbox.setValue(self.step.get("x", 0))
            self.desktop_params_form.addRow("X coordinate:", x_spinbox)
            
            y_spinbox = QSpinBox()
            y_spinbox.setRange(0, 9999)
            y_spinbox.setValue(self.step.get("y", 0))
            self.desktop_params_form.addRow("Y coordinate:", y_spinbox)
            
            # Option to use image recognition
            use_image_checkbox = QCheckBox("Use image recognition instead of coordinates")
            use_image_checkbox.setChecked("image" in self.step)
            self.desktop_params_form.addRow("", use_image_checkbox)
            
            if "image" in self.step:
                # Image path field
                image_path_edit = QLineEdit(self.step.get("image", ""))
                browse_button = QPushButton("Browse...")
                
                image_layout = QHBoxLayout()
                image_layout.addWidget(image_path_edit)
                image_layout.addWidget(browse_button)
                
                self.desktop_params_form.addRow("Image path:", image_layout)
                
                # Confidence slider
                confidence_spinbox = QSpinBox()
                confidence_spinbox.setRange(50, 100)
                confidence_spinbox.setValue(int(self.step.get("confidence", 0.9) * 100))
                confidence_spinbox.setSuffix("%")
                self.desktop_params_form.addRow("Confidence:", confidence_spinbox)
        
        elif action == "type":
            # Text field
            text_edit = QLineEdit(self.step.get("text", ""))
            self.desktop_params_form.addRow("Text to type:", text_edit)
            
            # Interval between keystrokes
            interval_spinbox = QSpinBox()
            interval_spinbox.setRange(0, 1000)
            interval_spinbox.setValue(int(self.step.get("interval", 0.01) * 1000))
            interval_spinbox.setSuffix(" ms")
            self.desktop_params_form.addRow("Interval between keystrokes:", interval_spinbox)
        
        elif action == "key_press":
            # Key field
            key_edit = QLineEdit(self.step.get("key", ""))
            self.desktop_params_form.addRow("Key or combination (e.g., 'ctrl+c'):", key_edit)
        
        elif action == "drag":
            # Start coordinates
            x_spinbox = QSpinBox()
            x_spinbox.setRange(0, 9999)
            x_spinbox.setValue(self.step.get("x", 0))
            self.desktop_params_form.addRow("Start X:", x_spinbox)
            
            y_spinbox = QSpinBox()
            y_spinbox.setRange(0, 9999)
            y_spinbox.setValue(self.step.get("y", 0))
            self.desktop_params_form.addRow("Start Y:", y_spinbox)
            
            # End coordinates
            to_values = self.step.get("to", {})
            end_x_spinbox = QSpinBox()
            end_x_spinbox.setRange(0, 9999)
            end_x_spinbox.setValue(to_values.get("x", 0))
            self.desktop_params_form.addRow("End X:", end_x_spinbox)
            
            end_y_spinbox = QSpinBox()
            end_y_spinbox.setRange(0, 9999)
            end_y_spinbox.setValue(to_values.get("y", 0))
            self.desktop_params_form.addRow("End Y:", end_y_spinbox)
            
            # Duration
            duration_spinbox = QSpinBox()
            duration_spinbox.setRange(1, 60)
            duration_spinbox.setValue(int(self.step.get("duration", 0.5) * 10))
            duration_spinbox.setSuffix(" (1/10 sec)")
            self.desktop_params_form.addRow("Duration:", duration_spinbox)
        
        elif action == "scroll":
            # Scroll amount
            clicks_spinbox = QSpinBox()
            clicks_spinbox.setRange(-100, 100)
            clicks_spinbox.setValue(self.step.get("clicks", 0))
            self.desktop_params_form.addRow("Scroll amount (clicks):", clicks_spinbox)
        
        elif action in ["find_image", "wait_for_image"]:
            # Image path field
            image_path_edit = QLineEdit(self.step.get("image", ""))
            browse_button = QPushButton("Browse...")
            
            image_layout = QHBoxLayout()
            image_layout.addWidget(image_path_edit)
            image_layout.addWidget(browse_button)
            
            self.desktop_params_form.addRow("Image path:", image_layout)
            
            # Confidence slider
            confidence_spinbox = QSpinBox()
            confidence_spinbox.setRange(50, 100)
            confidence_spinbox.setValue(int(self.step.get("confidence", 0.9) * 100))
            confidence_spinbox.setSuffix("%")
            self.desktop_params_form.addRow("Confidence:", confidence_spinbox)
            
            if action == "wait_for_image":
                # Timeout field
                timeout_spinbox = QSpinBox()
                timeout_spinbox.setRange(1, 3600)
                timeout_spinbox.setValue(self.step.get("timeout", 30))
                timeout_spinbox.setSuffix(" seconds")
                self.desktop_params_form.addRow("Timeout:", timeout_spinbox)
    
    def _populate_web_params(self):
        """Populate web action parameters."""
        self._clear_form_layout(self.web_params_form)
        action = self.web_action_combo.currentText()
        
        if action == "start_browser":
            # Browser type
            browser_combo = QComboBox()
            browser_combo.addItems(["chrome", "firefox"])
            
            browser_type = self.step.get("browser", "chrome")
            index = browser_combo.findText(browser_type)
            if index >= 0:
                browser_combo.setCurrentIndex(index)
                
            self.web_params_form.addRow("Browser:", browser_combo)
            
            # Headless mode
            headless_checkbox = QCheckBox("Run in headless mode")
            headless_checkbox.setChecked(self.step.get("headless", False))
            self.web_params_form.addRow("", headless_checkbox)
        
        elif action == "navigate":
            # URL field
            url_edit = QLineEdit(self.step.get("url", ""))
            self.web_params_form.addRow("URL:", url_edit)
            
            # Wait for element
            wait_checkbox = QCheckBox("Wait for element to appear")
            wait_checkbox.setChecked("wait_for" in self.step)
            self.web_params_form.addRow("", wait_checkbox)
            
            if "wait_for" in self.step:
                # Selector type combo
                wait_for = self.step.get("wait_for", {})
                selector_type_combo = QComboBox()
                selector_type_combo.addItems(["id", "name", "xpath", "css", "class", "tag", "link_text"])
                
                selector_type = wait_for.get("type", "id")
                index = selector_type_combo.findText(selector_type)
                if index >= 0:
                    selector_type_combo.setCurrentIndex(index)
                
                self.web_params_form.addRow("Selector type:", selector_type_combo)
                
                # Selector value field
                selector_value_edit = QLineEdit(wait_for.get("value", ""))
                self.web_params_form.addRow("Selector value:", selector_value_edit)
                
                # Timeout field
                timeout_spinbox = QSpinBox()
                timeout_spinbox.setRange(1, 300)
                timeout_spinbox.setValue(self.step.get("timeout", 30))
                timeout_spinbox.setSuffix(" seconds")
                self.web_params_form.addRow("Timeout:", timeout_spinbox)
        
        elif action in ["click", "type", "clear", "submit", "wait", "extract"]:
            # Selector fields
            selector = self.step.get("selector", {})
            
            # Selector type
            selector_type_combo = QComboBox()
            selector_type_combo.addItems(["id", "name", "xpath", "css", "class", "tag", "link_text"])
            
            selector_type = selector.get("type", "id")
            index = selector_type_combo.findText(selector_type)
            if index >= 0:
                selector_type_combo.setCurrentIndex(index)
            
            self.web_params_form.addRow("Selector type:", selector_type_combo)
            
            # Selector value
            selector_value_edit = QLineEdit(selector.get("value", ""))
            self.web_params_form.addRow("Selector value:", selector_value_edit)
            
            if action == "type":
                # Text to type
                text_edit = QLineEdit(self.step.get("text", ""))
                self.web_params_form.addRow("Text to type:", text_edit)
                
                # Clear before typing
                clear_checkbox = QCheckBox("Clear field before typing")
                clear_checkbox.setChecked(self.step.get("clear", True))
                self.web_params_form.addRow("", clear_checkbox)
                
                # Press Enter after typing
                enter_checkbox = QCheckBox("Press Enter after typing")
                enter_checkbox.setChecked(self.step.get("press_enter", False))
                self.web_params_form.addRow("", enter_checkbox)
            
            elif action == "wait":
                # Wait condition
                condition_combo = QComboBox()
                condition_combo.addItems(["presence", "visible", "clickable", "invisible"])
                
                condition = self.step.get("condition", "presence")
                index = condition_combo.findText(condition)
                if index >= 0:
                    condition_combo.setCurrentIndex(index)
                
                self.web_params_form.addRow("Wait condition:", condition_combo)
                
                # Timeout
                timeout_spinbox = QSpinBox()
                timeout_spinbox.setRange(1, 300)
                timeout_spinbox.setValue(self.step.get("timeout", 30))
                timeout_spinbox.setSuffix(" seconds")
                self.web_params_form.addRow("Timeout:", timeout_spinbox)
            
            elif action == "extract":
                # Extract type
                extract_combo = QComboBox()
                extract_combo.addItems(["text", "html", "attribute"])
                
                extract_type = self.step.get("extract", "text")
                index = extract_combo.findText(extract_type)
                if index >= 0:
                    extract_combo.setCurrentIndex(index)
                
                self.web_params_form.addRow("Extract:", extract_combo)
                
                # Attribute name (for attribute extraction)
                if extract_type == "attribute":
                    attribute_edit = QLineEdit(self.step.get("attribute", ""))
                    self.web_params_form.addRow("Attribute name:", attribute_edit)
                
                # Variable name
                variable_edit = QLineEdit(self.step.get("variable", "extracted_data"))
                self.web_params_form.addRow("Store in variable:", variable_edit)
        
        elif action == "select":
            # Selector fields
            selector = self.step.get("selector", {})
            
            # Selector type
            selector_type_combo = QComboBox()
            selector_type_combo.addItems(["id", "name", "xpath", "css", "class", "tag"])
            
            selector_type = selector.get("type", "id")
            index = selector_type_combo.findText(selector_type)
            if index >= 0:
                selector_type_combo.setCurrentIndex(index)
            
            self.web_params_form.addRow("Selector type:", selector_type_combo)
            
            # Selector value
            selector_value_edit = QLineEdit(selector.get("value", ""))
            self.web_params_form.addRow("Selector value:", selector_value_edit)
            
            # Selection method
            method_combo = QComboBox()
            method_combo.addItems(["value", "text", "index"])
            
            method = "value"
            if "value" in self.step:
                method = "value"
            elif "text" in self.step:
                method = "text"
            elif "index" in self.step:
                method = "index"
            
            index = method_combo.findText(method)
            if index >= 0:
                method_combo.setCurrentIndex(index)
            
            self.web_params_form.addRow("Selection method:", method_combo)
            
            # Selection value
            value_edit = QLineEdit()
            if method == "value":
                value_edit.setText(str(self.step.get("value", "")))
            elif method == "text":
                value_edit.setText(str(self.step.get("text", "")))
            elif method == "index":
                value_edit.setText(str(self.step.get("index", "0")))
            
            self.web_params_form.addRow("Selection value:", value_edit)
        
        elif action == "scroll":
            # Scroll method
            method_combo = QComboBox()
            method_combo.addItems(["position", "element", "amount"])
            
            method = "position"
            if "selector" in self.step:
                method = "element"
            elif "x" in self.step and "y" in self.step:
                method = "amount"
            
            index = method_combo.findText(method)
            if index >= 0:
                method_combo.setCurrentIndex(index)
            
            self.web_params_form.addRow("Scroll method:", method_combo)
            
            if method == "position":
                # Position options
                position_combo = QComboBox()
                position_combo.addItems(["top", "bottom"])
                
                position = self.step.get("position", "top")
                index = position_combo.findText(position)
                if index >= 0:
                    position_combo.setCurrentIndex(index)
                
                self.web_params_form.addRow("Position:", position_combo)
            
            elif method == "element":
                # Element selector
                selector = self.step.get("selector", {})
                
                # Selector type
                selector_type_combo = QComboBox()
                selector_type_combo.addItems(["id", "name", "xpath", "css", "class", "tag", "link_text"])
                
                selector_type = selector.get("type", "id")
                index = selector_type_combo.findText(selector_type)
                if index >= 0:
                    selector_type_combo.setCurrentIndex(index)
                
                self.web_params_form.addRow("Selector type:", selector_type_combo)
                
                # Selector value
                selector_value_edit = QLineEdit(selector.get("value", ""))
                self.web_params_form.addRow("Selector value:", selector_value_edit)
            
            elif method == "amount":
                # X coordinate
                x_spinbox = QSpinBox()
                x_spinbox.setRange(0, 9999)
                x_spinbox.setValue(self.step.get("x", 0))
                self.web_params_form.addRow("X coordinate:", x_spinbox)
                
                # Y coordinate
                y_spinbox = QSpinBox()
                y_spinbox.setRange(0, 9999)
                y_spinbox.setValue(self.step.get("y", 0))
                self.web_params_form.addRow("Y coordinate:", y_spinbox)
        
        elif action == "switch_frame":
            # Frame selection method
            method_combo = QComboBox()
            method_combo.addItems(["selector", "index", "id", "parent", "default"])
            
            method = "selector"
            if "index" in self.step:
                method = "index"
            elif "id" in self.step:
                method = "id"
            elif self.step.get("parent", False):
                method = "parent"
            elif self.step.get("default", False):
                method = "default"
            
            index = method_combo.findText(method)
            if index >= 0:
                method_combo.setCurrentIndex(index)
            
            self.web_params_form.addRow("Frame selection method:", method_combo)
            
            if method == "selector":
                # Element selector
                selector = self.step.get("selector", {})
                
                # Selector type
                selector_type_combo = QComboBox()
                selector_type_combo.addItems(["id", "name", "xpath", "css", "class", "tag"])
                
                selector_type = selector.get("type", "id")
                index = selector_type_combo.findText(selector_type)
                if index >= 0:
                    selector_type_combo.setCurrentIndex(index)
                
                self.web_params_form.addRow("Selector type:", selector_type_combo)
                
                # Selector value
                selector_value_edit = QLineEdit(selector.get("value", ""))
                self.web_params_form.addRow("Selector value:", selector_value_edit)
            
            elif method == "index":
                # Frame index
                index_spinbox = QSpinBox()
                index_spinbox.setRange(0, 99)
                index_spinbox.setValue(self.step.get("index", 0))
                self.web_params_form.addRow("Frame index:", index_spinbox)
            
            elif method == "id":
                # Frame ID or name
                id_edit = QLineEdit(self.step.get("id", ""))
                self.web_params_form.addRow("Frame ID or name:", id_edit)
        
        elif action == "switch_window":
            # Window selection method
            method_combo = QComboBox()
            method_combo.addItems(["index", "title", "url", "new"])
            
            method = "index"
            if "title" in self.step:
                method = "title"
            elif "url" in self.step:
                method = "url"
            elif self.step.get("new", False):
                method = "new"
            
            index = method_combo.findText(method)
            if index >= 0:
                method_combo.setCurrentIndex(index)
            
            self.web_params_form.addRow("Window selection method:", method_combo)
            
            if method == "index":
                # Window index
                index_spinbox = QSpinBox()
                index_spinbox.setRange(0, 99)
                index_spinbox.setValue(self.step.get("index", 0))
                self.web_params_form.addRow("Window index:", index_spinbox)
            
            elif method == "title":
                # Window title
                title_edit = QLineEdit(self.step.get("title", ""))
                self.web_params_form.addRow("Window title contains:", title_edit)
            
            elif method == "url":
                # Window URL
                url_edit = QLineEdit(self.step.get("url", ""))
                self.web_params_form.addRow("Window URL contains:", url_edit)
        
        elif action == "execute_script":
            # JavaScript code
            script_edit = QTextEdit(self.step.get("script", ""))
            script_edit.setMinimumHeight(150)
            self.web_params_form.addRow("JavaScript code:", script_edit)
        
        elif action == "screenshot":
            # Filename
            filename_edit = QLineEdit(self.step.get("filename", f"screenshot_{int(time.time())}.png"))
            self.web_params_form.addRow("Filename:", filename_edit)
    
    def _populate_captcha_params(self):
        """Populate CAPTCHA parameters."""
        self._clear_form_layout(self.captcha_params_form)
        captcha_type = self.captcha_type_combo.currentText()
        
        if captcha_type == "image":
            # Image selector
            selector = self.step.get("image_selector", {})
            
            # Selector type
            selector_type_combo = QComboBox()
            selector_type_combo.addItems(["id", "name", "xpath", "css", "class", "tag"])
            
            selector_type = selector.get("type", "id")
            index = selector_type_combo.findText(selector_type)
            if index >= 0:
                selector_type_combo.setCurrentIndex(index)
            
            self.captcha_params_form.addRow("Image selector type:", selector_type_combo)
            
            # Selector value
            selector_value_edit = QLineEdit(selector.get("value", ""))
            self.captcha_params_form.addRow("Image selector value:", selector_value_edit)
            
            # Input selector
            input_selector = self.step.get("input_selector", {})
            
            # Input selector type
            input_type_combo = QComboBox()
            input_type_combo.addItems(["id", "name", "xpath", "css", "class", "tag"])
            
            input_type = input_selector.get("type", "id")
            index = input_type_combo.findText(input_type)
            if index >= 0:
                input_type_combo.setCurrentIndex(index)
            
            self.captcha_params_form.addRow("Input selector type:", input_type_combo)
            
            # Input selector value
            input_value_edit = QLineEdit(input_selector.get("value", ""))
            self.captcha_params_form.addRow("Input selector value:", input_value_edit)
            
            # Submit after solving
            submit_checkbox = QCheckBox("Submit form after solving")
            submit_checkbox.setChecked(self.step.get("submit", False))
            self.captcha_params_form.addRow("", submit_checkbox)
            
            if self.step.get("submit", False):
                # Submit selector
                submit_selector = self.step.get("submit_selector", {})
                
                # Submit selector type
                submit_type_combo = QComboBox()
                submit_type_combo.addItems(["id", "name", "xpath", "css", "class", "tag"])
                
                submit_type = submit_selector.get("type", "id")
                index = submit_type_combo.findText(submit_type)
                if index >= 0:
                    submit_type_combo.setCurrentIndex(index)
                
                self.captcha_params_form.addRow("Submit button selector type:", submit_type_combo)
                
                # Submit selector value
                submit_value_edit = QLineEdit(submit_selector.get("value", ""))
                self.captcha_params_form.addRow("Submit button selector value:", submit_value_edit)
        
        elif captcha_type == "recaptcha":
            # Allow manual intervention
            manual_checkbox = QCheckBox("Allow manual intervention if needed")
            manual_checkbox.setChecked(self.step.get("allow_manual", True))
            self.captcha_params_form.addRow("", manual_checkbox)
            
            # Wait time for manual intervention
            manual_wait_spinbox = QSpinBox()
            manual_wait_spinbox.setRange(5, 300)
            manual_wait_spinbox.setValue(self.step.get("manual_wait", 30))
            manual_wait_spinbox.setSuffix(" seconds")
            self.captcha_params_form.addRow("Manual intervention wait time:", manual_wait_spinbox)
        
        elif captcha_type == "text":
            # Question selector
            selector = self.step.get("question_selector", {})
            
            # Selector type
            selector_type_combo = QComboBox()
            selector_type_combo.addItems(["id", "name", "xpath", "css", "class", "tag"])
            
            selector_type = selector.get("type", "id")
            index = selector_type_combo.findText(selector_type)
            if index >= 0:
                selector_type_combo.setCurrentIndex(index)
            
            self.captcha_params_form.addRow("Question selector type:", selector_type_combo)
            
            # Selector value
            selector_value_edit = QLineEdit(selector.get("value", ""))
            self.captcha_params_form.addRow("Question selector value:", selector_value_edit)
            
            # Input selector
            input_selector = self.step.get("input_selector", {})
            
            # Input selector type
            input_type_combo = QComboBox()
            input_type_combo.addItems(["id", "name", "xpath", "css", "class", "tag"])
            
            input_type = input_selector.get("type", "id")
            index = input_type_combo.findText(input_type)
            if index >= 0:
                input_type_combo.setCurrentIndex(index)
            
            self.captcha_params_form.addRow("Input selector type:", input_type_combo)
            
            # Input selector value
            input_value_edit = QLineEdit(input_selector.get("value", ""))
            self.captcha_params_form.addRow("Input selector value:", input_value_edit)
            
            # Submit after solving
            submit_checkbox = QCheckBox("Submit form after solving")
            submit_checkbox.setChecked(self.step.get("submit", False))
            self.captcha_params_form.addRow("", submit_checkbox)
            
            # Allow manual intervention
            manual_checkbox = QCheckBox("Allow manual intervention if automatic solving fails")
            manual_checkbox.setChecked(self.step.get("allow_manual", True))
            self.captcha_params_form.addRow("", manual_checkbox)
        
        elif captcha_type == "manual":
            # Wait time
            wait_spinbox = QSpinBox()
            wait_spinbox.setRange(5, 300)
            wait_spinbox.setValue(self.step.get("wait_time", 30))
            wait_spinbox.setSuffix(" seconds")
            self.captcha_params_form.addRow("Wait time for manual intervention:", wait_spinbox)
    
    def _on_type_changed(self, type_text):
        """Handle step type change."""
        if type_text.lower() == "desktop":
            self.tab_widget.setCurrentWidget(self.desktop_widget)
        elif type_text.lower() == "web":
            self.tab_widget.setCurrentWidget(self.web_widget)
        elif type_text.lower() == "captcha":
            self.tab_widget.setCurrentWidget(self.captcha_widget)
        elif type_text.lower() == "wait":
            self.tab_widget.setCurrentWidget(self.wait_widget)
    
    def _on_desktop_action_changed(self, action):
        """Handle desktop action change."""
        self._populate_desktop_params()
    
    def _on_web_action_changed(self, action):
        """Handle web action change."""
        self._populate_web_params()
    
    def _on_captcha_type_changed(self, captcha_type):
        """Handle CAPTCHA type change."""
        self._populate_captcha_params()
    
    def _clear_form_layout(self, form_layout):
        """Clear all widgets from a form layout."""
        while form_layout.rowCount() > 0:
            # Remove the last row
            form_layout.removeRow(form_layout.rowCount() - 1)
    
    def get_step_data(self) -> Dict[str, Any]:
        """
        Get the edited step data.
        
        Returns:
            dict: Step data
        """
        # Get step type
        step_type = self.type_combo.currentText().lower()
        
        # Initialize step data
        step_data = {
            "type": step_type,
            "delay": self.delay_spinbox.value()
        }
        
        # Add description if provided
        if self.description_edit.text():
            step_data["description"] = self.description_edit.text()
        
        # Add type-specific data
        if step_type == "desktop":
            self._add_desktop_data(step_data)
        elif step_type == "web":
            self._add_web_data(step_data)
        elif step_type == "captcha":
            self._add_captcha_data(step_data)
        elif step_type == "wait":
            step_data["duration"] = self.wait_duration.value()
        
        return step_data
    
    def _add_desktop_data(self, step_data):
        """Add desktop-specific data to step data."""
        action = self.desktop_action_combo.currentText()
        step_data["action"] = action
        
        # Find form widgets to get values
        if action in ["click", "right_click", "double_click", "move"]:
            # Check if using image recognition
            use_image_checkbox = None
            for i in range(self.desktop_params_form.rowCount()):
                widget = self.desktop_params_form.itemAt(i, QFormLayout.FieldRole).widget()
                if isinstance(widget, QCheckBox) and widget.text() == "Use image recognition instead of coordinates":
                    use_image_checkbox = widget
                    break
            
            if use_image_checkbox and use_image_checkbox.isChecked():
                # Using image recognition
                image_path_edit = None
                confidence_spinbox = None
                
                for i in range(self.desktop_params_form.rowCount()):
                    label_item = self.desktop_params_form.itemAt(i, QFormLayout.LabelRole)
                    field_item = self.desktop_params_form.itemAt(i, QFormLayout.FieldRole)
                    
                    if label_item and field_item:
                        label_widget = label_item.widget()
                        if isinstance(label_widget, QLabel) and label_widget.text() == "Image path:":
                            layout_widget = field_item.widget()
                            if isinstance(layout_widget, QWidget):
                                for j in range(layout_widget.layout().count()):
                                    if isinstance(layout_widget.layout().itemAt(j).widget(), QLineEdit):
                                        image_path_edit = layout_widget.layout().itemAt(j).widget()
                        
                        if isinstance(label_widget, QLabel) and label_widget.text() == "Confidence:":
                            confidence_spinbox = field_item.widget()
                
                if image_path_edit and confidence_spinbox:
                    step_data["image"] = image_path_edit.text()
                    step_data["confidence"] = confidence_spinbox.value() / 100.0
            else:
                # Using coordinates
                x_spinbox = None
                y_spinbox = None
                
                for i in range(self.desktop_params_form.rowCount()):
                    label_item = self.desktop_params_form.itemAt(i, QFormLayout.LabelRole)
                    field_item = self.desktop_params_form.itemAt(i, QFormLayout.FieldRole)
                    
                    if label_item and field_item:
                        label_widget = label_item.widget()
                        if isinstance(label_widget, QLabel):
                            if label_widget.text() in ["X coordinate:", "Start X:"]:
                                x_spinbox = field_item.widget()
                            elif label_widget.text() in ["Y coordinate:", "Start Y:"]:
                                y_spinbox = field_item.widget()
                
                if x_spinbox and y_spinbox:
                    step_data["x"] = x_spinbox.value()
                    step_data["y"] = y_spinbox.value()
            
            # For drag action, add end coordinates
            if action == "drag":
                end_x_spinbox = None
                end_y_spinbox = None
                duration_spinbox = None
                
                for i in range(self.desktop_params_form.rowCount()):
                    label_item = self.desktop_params_form.itemAt(i, QFormLayout.LabelRole)
                    field_item = self.desktop_params_form.itemAt(i, QFormLayout.FieldRole)
                    
                    if label_item and field_item:
                        label_widget = label_item.widget()
                        if isinstance(label_widget, QLabel):
                            if label_widget.text() == "End X:":
                                end_x_spinbox = field_item.widget()
                            elif label_widget.text() == "End Y:":
                                end_y_spinbox = field_item.widget()
                            elif label_widget.text() == "Duration:":
                                duration_spinbox = field_item.widget()
                
                if end_x_spinbox and end_y_spinbox:
                    step_data["to"] = {
                        "x": end_x_spinbox.value(),
                        "y": end_y_spinbox.value()
                    }
                
                if duration_spinbox:
                    step_data["duration"] = duration_spinbox.value() / 10.0
        
        elif action == "type":
            text_edit = None
            interval_spinbox = None
            
            for i in range(self.desktop_params_form.rowCount()):
                label_item = self.desktop_params_form.itemAt(i, QFormLayout.LabelRole)
                field_item = self.desktop_params_form.itemAt(i, QFormLayout.FieldRole)
                
                if label_item and field_item:
                    label_widget = label_item.widget()
                    if isinstance(label_widget, QLabel):
                        if label_widget.text() == "Text to type:":
                            text_edit = field_item.widget()
                        elif label_widget.text() == "Interval between keystrokes:":
                            interval_spinbox = field_item.widget()
            
            if text_edit:
                step_data["text"] = text_edit.text()
            
            if interval_spinbox:
                step_data["interval"] = interval_spinbox.value() / 1000.0
        
        elif action == "key_press":
            key_edit = None
            
            for i in range(self.desktop_params_form.rowCount()):
                label_item = self.desktop_params_form.itemAt(i, QFormLayout.LabelRole)
                field_item = self.desktop_params_form.itemAt(i, QFormLayout.FieldRole)
                
                if label_item and field_item:
                    label_widget = label_item.widget()
                    if isinstance(label_widget, QLabel) and label_widget.text() == "Key or combination (e.g., 'ctrl+c'):":
                        key_edit = field_item.widget()
            
            if key_edit:
                step_data["key"] = key_edit.text()
        
        elif action == "scroll":
            clicks_spinbox = None
            
            for i in range(self.desktop_params_form.rowCount()):
                label_item = self.desktop_params_form.itemAt(i, QFormLayout.LabelRole)
                field_item = self.desktop_params_form.itemAt(i, QFormLayout.FieldRole)
                
                if label_item and field_item:
                    label_widget = label_item.widget()
                    if isinstance(label_widget, QLabel) and label_widget.text() == "Scroll amount (clicks):":
                        clicks_spinbox = field_item.widget()
            
            if clicks_spinbox:
                step_data["clicks"] = clicks_spinbox.value()
        
        elif action in ["find_image", "wait_for_image"]:
            image_path_edit = None
            confidence_spinbox = None
            timeout_spinbox = None
            
            for i in range(self.desktop_params_form.rowCount()):
                label_item = self.desktop_params_form.itemAt(i, QFormLayout.LabelRole)
                field_item = self.desktop_params_form.itemAt(i, QFormLayout.FieldRole)
                
                if label_item and field_item:
                    label_widget = label_item.widget()
                    if isinstance(label_widget, QLabel):
                        if label_widget.text() == "Image path:":
                            layout_widget = field_item.widget()
                            if isinstance(layout_widget, QWidget):
                                for j in range(layout_widget.layout().count()):
                                    if isinstance(layout_widget.layout().itemAt(j).widget(), QLineEdit):
                                        image_path_edit = layout_widget.layout().itemAt(j).widget()
                        elif label_widget.text() == "Confidence:":
                            confidence_spinbox = field_item.widget()
                        elif label_widget.text() == "Timeout:":
                            timeout_spinbox = field_item.widget()
            
            if image_path_edit:
                step_data["image"] = image_path_edit.text()
            
            if confidence_spinbox:
                step_data["confidence"] = confidence_spinbox.value() / 100.0
            
            if timeout_spinbox and action == "wait_for_image":
                step_data["timeout"] = timeout_spinbox.value()
    
    def _add_web_data(self, step_data):
        """Add web-specific data to step data."""
        action = self.web_action_combo.currentText()
        step_data["action"] = action
        
        # Add action-specific data based on the form
        if action == "start_browser":
            browser_combo = None
            headless_checkbox = None
            
            for i in range(self.web_params_form.rowCount()):
                label_item = self.web_params_form.itemAt(i, QFormLayout.LabelRole)
                field_item = self.web_params_form.itemAt(i, QFormLayout.FieldRole)
                
                if label_item and field_item:
                    label_widget = label_item.widget()
                    if isinstance(label_widget, QLabel) and label_widget.text() == "Browser:":
                        browser_combo = field_item.widget()
                elif field_item:
                    widget = field_item.widget()
                    if isinstance(widget, QCheckBox) and widget.text() == "Run in headless mode":
                        headless_checkbox = widget
            
            if browser_combo:
                step_data["browser"] = browser_combo.currentText()
            
            if headless_checkbox:
                step_data["headless"] = headless_checkbox.isChecked()
        
        elif action == "navigate":
            url_edit = None
            wait_checkbox = None
            selector_type_combo = None
            selector_value_edit = None
            timeout_spinbox = None
            
            for i in range(self.web_params_form.rowCount()):
                label_item = self.web_params_form.itemAt(i, QFormLayout.LabelRole)
                field_item = self.web_params_form.itemAt(i, QFormLayout.FieldRole)
                
                if label_item and field_item:
                    label_widget = label_item.widget()
                    if isinstance(label_widget, QLabel):
                        if label_widget.text() == "URL:":
                            url_edit = field_item.widget()
                        elif label_widget.text() == "Selector type:":
                            selector_type_combo = field_item.widget()
                        elif label_widget.text() == "Selector value:":
                            selector_value_edit = field_item.widget()
                        elif label_widget.text() == "Timeout:":
                            timeout_spinbox = field_item.widget()
                elif field_item:
                    widget = field_item.widget()
                    if isinstance(widget, QCheckBox) and widget.text() == "Wait for element to appear":
                        wait_checkbox = widget
            
            if url_edit:
                step_data["url"] = url_edit.text()
            
            if wait_checkbox and wait_checkbox.isChecked() and selector_type_combo and selector_value_edit:
                step_data["wait_for"] = {
                    "type": selector_type_combo.currentText(),
                    "value": selector_value_edit.text()
                }
                
                if timeout_spinbox:
                    step_data["timeout"] = timeout_spinbox.value()
        
        elif action in ["click", "type", "clear", "submit", "wait", "extract"]:
            # Get selector information
            selector_type_combo = None
            selector_value_edit = None
            
            for i in range(self.web_params_form.rowCount()):
                label_item = self.web_params_form.itemAt(i, QFormLayout.LabelRole)
                field_item = self.web_params_form.itemAt(i, QFormLayout.FieldRole)
                
                if label_item and field_item:
                    label_widget = label_item.widget()
                    if isinstance(label_widget, QLabel):
                        if label_widget.text() == "Selector type:":
                            selector_type_combo = field_item.widget()
                        elif label_widget.text() == "Selector value:":
                            selector_value_edit = field_item.widget()
            
            if selector_type_combo and selector_value_edit:
                step_data["selector"] = {
                    "type": selector_type_combo.currentText(),
                    "value": selector_value_edit.text()
                }
            
            # Action-specific fields
            if action == "type":
                text_edit = None
                clear_checkbox = None
                enter_checkbox = None
                
                for i in range(self.web_params_form.rowCount()):
                    label_item = self.web_params_form.itemAt(i, QFormLayout.LabelRole)
                    field_item = self.web_params_form.itemAt(i, QFormLayout.FieldRole)
                    
                    if label_item and field_item:
                        label_widget = label_item.widget()
                        if isinstance(label_widget, QLabel) and label_widget.text() == "Text to type:":
                            text_edit = field_item.widget()
                    elif field_item:
                        widget = field_item.widget()
                        if isinstance(widget, QCheckBox):
                            if widget.text() == "Clear field before typing":
                                clear_checkbox = widget
                            elif widget.text() == "Press Enter after typing":
                                enter_checkbox = widget
                
                if text_edit:
                    step_data["text"] = text_edit.text()
                
                if clear_checkbox:
                    step_data["clear"] = clear_checkbox.isChecked()
                
                if enter_checkbox:
                    step_data["press_enter"] = enter_checkbox.isChecked()
            
            elif action == "wait":
                condition_combo = None
                timeout_spinbox = None
                
                for i in range(self.web_params_form.rowCount()):
                    label_item = self.web_params_form.itemAt(i, QFormLayout.LabelRole)
                    field_item = self.web_params_form.itemAt(i, QFormLayout.FieldRole)
                    
                    if label_item and field_item:
                        label_widget = label_item.widget()
                        if isinstance(label_widget, QLabel):
                            if label_widget.text() == "Wait condition:":
                                condition_combo = field_item.widget()
                            elif label_widget.text() == "Timeout:":
                                timeout_spinbox = field_item.widget()
                
                if condition_combo:
                    step_data["condition"] = condition_combo.currentText()
                
                if timeout_spinbox:
                    step_data["timeout"] = timeout_spinbox.value()
            
            elif action == "extract":
                extract_combo = None
                attribute_edit = None
                variable_edit = None
                
                for i in range(self.web_params_form.rowCount()):
                    label_item = self.web_params_form.itemAt(i, QFormLayout.LabelRole)
                    field_item = self.web_params_form.itemAt(i, QFormLayout.FieldRole)
                    
                    if label_item and field_item:
                        label_widget = label_item.widget()
                        if isinstance(label_widget, QLabel):
                            if label_widget.text() == "Extract:":
                                extract_combo = field_item.widget()
                            elif label_widget.text() == "Attribute name:":
                                attribute_edit = field_item.widget()
                            elif label_widget.text() == "Store in variable:":
                                variable_edit = field_item.widget()
                
                if extract_combo:
                    step_data["extract"] = extract_combo.currentText()
                    
                    if extract_combo.currentText() == "attribute" and attribute_edit:
                        step_data["attribute"] = attribute_edit.text()
                
                if variable_edit:
                    step_data["variable"] = variable_edit.text()
        
        elif action == "select":
            # Get selector information
            selector_type_combo = None
            selector_value_edit = None
            method_combo = None
            value_edit = None
            
            for i in range(self.web_params_form.rowCount()):
                label_item = self.web_params_form.itemAt(i, QFormLayout.LabelRole)
                field_item = self.web_params_form.itemAt(i, QFormLayout.FieldRole)
                
                if label_item and field_item:
                    label_widget = label_item.widget()
                    if isinstance(label_widget, QLabel):
                        if label_widget.text() == "Selector type:":
                            selector_type_combo = field_item.widget()
                        elif label_widget.text() == "Selector value:":
                            selector_value_edit = field_item.widget()
                        elif label_widget.text() == "Selection method:":
                            method_combo = field_item.widget()
                        elif label_widget.text() == "Selection value:":
                            value_edit = field_item.widget()
            
            if selector_type_combo and selector_value_edit:
                step_data["selector"] = {
                    "type": selector_type_combo.currentText(),
                    "value": selector_value_edit.text()
                }
            
            if method_combo and value_edit:
                method = method_combo.currentText()
                if method == "index":
                    try:
                        step_data["index"] = int(value_edit.text())
                    except ValueError:
                        step_data["index"] = 0
                else:
                    step_data[method] = value_edit.text()
        
        elif action == "scroll":
            method_combo = None
            
            for i in range(self.web_params_form.rowCount()):
                label_item = self.web_params_form.itemAt(i, QFormLayout.LabelRole)
                field_item = self.web_params_form.itemAt(i, QFormLayout.FieldRole)
                
                if label_item and field_item:
                    label_widget = label_item.widget()
                    if isinstance(label_widget, QLabel) and label_widget.text() == "Scroll method:":
                        method_combo = field_item.widget()
            
            if method_combo:
                method = method_combo.currentText()
                
                if method == "position":
                    position_combo = None
                    
                    for i in range(self.web_params_form.rowCount()):
                        label_item = self.web_params_form.itemAt(i, QFormLayout.LabelRole)
                        field_item = self.web_params_form.itemAt(i, QFormLayout.FieldRole)
                        
                        if label_item and field_item:
                            label_widget = label_item.widget()
                            if isinstance(label_widget, QLabel) and label_widget.text() == "Position:":
                                position_combo = field_item.widget()
                    
                    if position_combo:
                        step_data["position"] = position_combo.currentText()
                
                elif method == "element":
                    selector_type_combo = None
                    selector_value_edit = None
                    
                    for i in range(self.web_params_form.rowCount()):
                        label_item = self.web_params_form.itemAt(i, QFormLayout.LabelRole)
                        field_item = self.web_params_form.itemAt(i, QFormLayout.FieldRole)
                        
                        if label_item and field_item:
                            label_widget = label_item.widget()
                            if isinstance(label_widget, QLabel):
                                if label_widget.text() == "Selector type:":
                                    selector_type_combo = field_item.widget()
                                elif label_widget.text() == "Selector value:":
                                    selector_value_edit = field_item.widget()
                    
                    if selector_type_combo and selector_value_edit:
                        step_data["selector"] = {
                            "type": selector_type_combo.currentText(),
                            "value": selector_value_edit.text()
                        }
                
                elif method == "amount":
                    x_spinbox = None
                    y_spinbox = None
                    
                    for i in range(self.web_params_form.rowCount()):
                        label_item = self.web_params_form.itemAt(i, QFormLayout.LabelRole)
                        field_item = self.web_params_form.itemAt(i, QFormLayout.FieldRole)
                        
                        if label_item and field_item:
                            label_widget = label_item.widget()
                            if isinstance(label_widget, QLabel):
                                if label_widget.text() == "X coordinate:":
                                    x_spinbox = field_item.widget()
                                elif label_widget.text() == "Y coordinate:":
                                    y_spinbox = field_item.widget()
                    
                    if x_spinbox and y_spinbox:
                        step_data["x"] = x_spinbox.value()
                        step_data["y"] = y_spinbox.value()
        
        elif action == "switch_frame":
            method_combo = None
            
            for i in range(self.web_params_form.rowCount()):
                label_item = self.web_params_form.itemAt(i, QFormLayout.LabelRole)
                field_item = self.web_params_form.itemAt(i, QFormLayout.FieldRole)
                
                if label_item and field_item:
                    label_widget = label_item.widget()
                    if isinstance(label_widget, QLabel) and label_widget.text() == "Frame selection method:":
                        method_combo = field_item.widget()
            
            if method_combo:
                method = method_combo.currentText()
                
                if method == "selector":
                    selector_type_combo = None
                    selector_value_edit = None
                    
                    for i in range(self.web_params_form.rowCount()):
                        label_item = self.web_params_form.itemAt(i, QFormLayout.LabelRole)
                        field_item = self.web_params_form.itemAt(i, QFormLayout.FieldRole)
                        
                        if label_item and field_item:
                            label_widget = label_item.widget()
                            if isinstance(label_widget, QLabel):
                                if label_widget.text() == "Selector type:":
                                    selector_type_combo = field_item.widget()
                                elif label_widget.text() == "Selector value:":
                                    selector_value_edit = field_item.widget()
                    
                    if selector_type_combo and selector_value_edit:
                        step_data["selector"] = {
                            "type": selector_type_combo.currentText(),
                            "value": selector_value_edit.text()
                        }
                
                elif method == "index":
                    index_spinbox = None
                    
                    for i in range(self.web_params_form.rowCount()):
                        label_item = self.web_params_form.itemAt(i, QFormLayout.LabelRole)
                        field_item = self.web_params_form.itemAt(i, QFormLayout.FieldRole)
                        
                        if label_item and field_item:
                            label_widget = label_item.widget()
                            if isinstance(label_widget, QLabel) and label_widget.text() == "Frame index:":
                                index_spinbox = field_item.widget()
                    
                    if index_spinbox:
                        step_data["index"] = index_spinbox.value()
                
                elif method == "id":
                    id_edit = None
                    
                    for i in range(self.web_params_form.rowCount()):
                        label_item = self.web_params_form.itemAt(i, QFormLayout.LabelRole)
                        field_item = self.web_params_form.itemAt(i, QFormLayout.FieldRole)
                        
                        if label_item and field_item:
                            label_widget = label_item.widget()
                            if isinstance(label_widget, QLabel) and label_widget.text() == "Frame ID or name:":
                                id_edit = field_item.widget()
                    
                    if id_edit:
                        step_data["id"] = id_edit.text()
                
                elif method == "parent":
                    step_data["parent"] = True
                
                elif method == "default":
                    step_data["default"] = True
        
        elif action == "switch_window":
            method_combo = None
            
            for i in range(self.web_params_form.rowCount()):
                label_item = self.web_params_form.itemAt(i, QFormLayout.LabelRole)
                field_item = self.web_params_form.itemAt(i, QFormLayout.FieldRole)
                
                if label_item and field_item:
                    label_widget = label_item.widget()
                    if isinstance(label_widget, QLabel) and label_widget.text() == "Window selection method:":
                        method_combo = field_item.widget()
            
            if method_combo:
                method = method_combo.currentText()
                
                if method == "index":
                    index_spinbox = None
                    
                    for i in range(self.web_params_form.rowCount()):
                        label_item = self.web_params_form.itemAt(i, QFormLayout.LabelRole)
                        field_item = self.web_params_form.itemAt(i, QFormLayout.FieldRole)
                        
                        if label_item and field_item:
                            label_widget = label_item.widget()
                            if isinstance(label_widget, QLabel) and label_widget.text() == "Window index:":
                                index_spinbox = field_item.widget()
                    
                    if index_spinbox:
                        step_data["index"] = index_spinbox.value()
                
                elif method == "title":
                    title_edit = None
                    
                    for i in range(self.web_params_form.rowCount()):
                        label_item = self.web_params_form.itemAt(i, QFormLayout.LabelRole)
                        field_item = self.web_params_form.itemAt(i, QFormLayout.FieldRole)
                        
                        if label_item and field_item:
                            label_widget = label_item.widget()
                            if isinstance(label_widget, QLabel) and label_widget.text() == "Window title contains:":
                                title_edit = field_item.widget()
                    
                    if title_edit:
                        step_data["title"] = title_edit.text()
                
                elif method == "url":
                    url_edit = None
                    
                    for i in range(self.web_params_form.rowCount()):
                        label_item = self.web_params_form.itemAt(i, QFormLayout.LabelRole)
                        field_item = self.web_params_form.itemAt(i, QFormLayout.FieldRole)
                        
                        if label_item and field_item:
                            label_widget = label_item.widget()
                            if isinstance(label_widget, QLabel) and label_widget.text() == "Window URL contains:":
                                url_edit = field_item.widget()
                    
                    if url_edit:
                        step_data["url"] = url_edit.text()
                
                elif method == "new":
                    step_data["new"] = True
        
        elif action == "execute_script":
            script_edit = None
            
            for i in range(self.web_params_form.rowCount()):
                label_item = self.web_params_form.itemAt(i, QFormLayout.LabelRole)
                field_item = self.web_params_form.itemAt(i, QFormLayout.FieldRole)
                
                if label_item and field_item:
                    label_widget = label_item.widget()
                    if isinstance(label_widget, QLabel) and label_widget.text() == "JavaScript code:":
                        script_edit = field_item.widget()
            
            if script_edit:
                step_data["script"] = script_edit.toPlainText()
        
        elif action == "screenshot":
            filename_edit = None
            
            for i in range(self.web_params_form.rowCount()):
                label_item = self.web_params_form.itemAt(i, QFormLayout.LabelRole)
                field_item = self.web_params_form.itemAt(i, QFormLayout.FieldRole)
                
                if label_item and field_item:
                    label_widget = label_item.widget()
                    if isinstance(label_widget, QLabel) and label_widget.text() == "Filename:":
                        filename_edit = field_item.widget()
            
            if filename_edit:
                step_data["filename"] = filename_edit.text()
    
    def _add_captcha_data(self, step_data):
        """Add CAPTCHA-specific data to step data."""
        captcha_type = self.captcha_type_combo.currentText()
        step_data["captcha_type"] = captcha_type
        
        if captcha_type == "image":
            # Get image selector
            image_selector_type_combo = None
            image_selector_value_edit = None
            
            for i in range(self.captcha_params_form.rowCount()):
                label_item = self.captcha_params_form.itemAt(i, QFormLayout.LabelRole)
                field_item = self.captcha_params_form.itemAt(i, QFormLayout.FieldRole)
                
                if label_item and field_item:
                    label_widget = label_item.widget()
                    if isinstance(label_widget, QLabel):
                        if label_widget.text() == "Image selector type:":
                            image_selector_type_combo = field_item.widget()
                        elif label_widget.text() == "Image selector value:":
                            image_selector_value_edit = field_item.widget()
            
            if image_selector_type_combo and image_selector_value_edit:
                step_data["image_selector"] = {
                    "type": image_selector_type_combo.currentText(),
                    "value": image_selector_value_edit.text()
                }
            
            # Get input selector
            input_selector_type_combo = None
            input_selector_value_edit = None
            
            for i in range(self.captcha_params_form.rowCount()):
                label_item = self.captcha_params_form.itemAt(i, QFormLayout.LabelRole)
                field_item = self.captcha_params_form.itemAt(i, QFormLayout.FieldRole)
                
                if label_item and field_item:
                    label_widget = label_item.widget()
                    if isinstance(label_widget, QLabel):
                        if label_widget.text() == "Input selector type:":
                            input_selector_type_combo = field_item.widget()
                        elif label_widget.text() == "Input selector value:":
                            input_selector_value_edit = field_item.widget()
            
            if input_selector_type_combo and input_selector_value_edit:
                step_data["input_selector"] = {
                    "type": input_selector_type_combo.currentText(),
                    "value": input_selector_value_edit.text()
                }
            
            # Check if submit after solving
            submit_checkbox = None
            
            for i in range(self.captcha_params_form.rowCount()):
                field_item = self.captcha_params_form.itemAt(i, QFormLayout.FieldRole)
                if field_item:
                    widget = field_item.widget()
                    if isinstance(widget, QCheckBox) and widget.text() == "Submit form after solving":
                        submit_checkbox = widget
            
            if submit_checkbox:
                step_data["submit"] = submit_checkbox.isChecked()
                
                if submit_checkbox.isChecked():
                    # Get submit selector
                    submit_selector_type_combo = None
                    submit_selector_value_edit = None
                    
                    for i in range(self.captcha_params_form.rowCount()):
                        label_item = self.captcha_params_form.itemAt(i, QFormLayout.LabelRole)
                        field_item = self.captcha_params_form.itemAt(i, QFormLayout.FieldRole)
                        
                        if label_item and field_item:
                            label_widget = label_item.widget()
                            if isinstance(label_widget, QLabel):
                                if label_widget.text() == "Submit button selector type:":
                                    submit_selector_type_combo = field_item.widget()
                                elif label_widget.text() == "Submit button selector value:":
                                    submit_selector_value_edit = field_item.widget()
                    
                    if submit_selector_type_combo and submit_selector_value_edit:
                        step_data["submit_selector"] = {
                            "type": submit_selector_type_combo.currentText(),
                            "value": submit_selector_value_edit.text()
                        }
        
        elif captcha_type == "recaptcha":
            manual_checkbox = None
            manual_wait_spinbox = None
            
            for i in range(self.captcha_params_form.rowCount()):
                label_item = self.captcha_params_form.itemAt(i, QFormLayout.LabelRole)
                field_item = self.captcha_params_form.itemAt(i, QFormLayout.FieldRole)
                
                if field_item:
                    widget = field_item.widget()
                    if isinstance(widget, QCheckBox) and widget.text() == "Allow manual intervention if needed":
                        manual_checkbox = widget
                
                if label_item and field_item:
                    label_widget = label_item.widget()
                    if isinstance(label_widget, QLabel) and label_widget.text() == "Manual intervention wait time:":
                        manual_wait_spinbox = field_item.widget()
            
            if manual_checkbox:
                step_data["allow_manual"] = manual_checkbox.isChecked()
            
            if manual_wait_spinbox:
                step_data["manual_wait"] = manual_wait_spinbox.value()
        
        elif captcha_type == "text":
            # Get question selector
            question_selector_type_combo = None
            question_selector_value_edit = None
            
            for i in range(self.captcha_params_form.rowCount()):
                label_item = self.captcha_params_form.itemAt(i, QFormLayout.LabelRole)
                field_item = self.captcha_params_form.itemAt(i, QFormLayout.FieldRole)
                
                if label_item and field_item:
                    label_widget = label_item.widget()
                    if isinstance(label_widget, QLabel):
                        if label_widget.text() == "Question selector type:":
                            question_selector_type_combo = field_item.widget()
                        elif label_widget.text() == "Question selector value:":
                            question_selector_value_edit = field_item.widget()
            
            if question_selector_type_combo and question_selector_value_edit:
                step_data["question_selector"] = {
                    "type": question_selector_type_combo.currentText(),
                    "value": question_selector_value_edit.text()
                }
            
            # Get input selector
            input_selector_type_combo = None
            input_selector_value_edit = None
            
            for i in range(self.captcha_params_form.rowCount()):
                label_item = self.captcha_params_form.itemAt(i, QFormLayout.LabelRole)
                field_item = self.captcha_params_form.itemAt(i, QFormLayout.FieldRole)
                
                if label_item and field_item:
                    label_widget = label_item.widget()
                    if isinstance(label_widget, QLabel):
                        if label_widget.text() == "Input selector type:":
                            input_selector_type_combo = field_item.widget()
                        elif label_widget.text() == "Input selector value:":
                            input_selector_value_edit = field_item.widget()
            
            if input_selector_type_combo and input_selector_value_edit:
                step_data["input_selector"] = {
                    "type": input_selector_type_combo.currentText(),
                    "value": input_selector_value_edit.text()
                }
            
            # Check other options
            for i in range(self.captcha_params_form.rowCount()):
                field_item = self.captcha_params_form.itemAt(i, QFormLayout.FieldRole)
                if field_item:
                    widget = field_item.widget()
                    if isinstance(widget, QCheckBox):
                        if widget.text() == "Submit form after solving":
                            step_data["submit"] = widget.isChecked()
                        elif widget.text() == "Allow manual intervention if automatic solving fails":
                            step_data["allow_manual"] = widget.isChecked()
        
        elif captcha_type == "manual":
            wait_spinbox = None
            
            for i in range(self.captcha_params_form.rowCount()):
                label_item = self.captcha_params_form.itemAt(i, QFormLayout.LabelRole)
                field_item = self.captcha_params_form.itemAt(i, QFormLayout.FieldRole)
                
                if label_item and field_item:
                    label_widget = label_item.widget()
                    if isinstance(label_widget, QLabel) and label_widget.text() == "Wait time for manual intervention:":
                        wait_spinbox = field_item.widget()
            
            if wait_spinbox:
                step_data["wait_time"] = wait_spinbox.value()


class ScriptEditorWidget(QWidget):
    """
    Widget for editing automation scripts.
    """
    
    # Signal emitted when script is modified
    script_modified = pyqtSignal()
    
    def __init__(self, script_manager: ScriptManager, parent=None):
        """Initialize the script editor widget."""
        super().__init__(parent)
        self.script_manager = script_manager
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the widget UI."""
        layout = QVBoxLayout(self)
        
        # Script info section
        info_layout = QHBoxLayout()
        
        self.script_name_label = QLabel("No script loaded")
        self.script_name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        info_layout.addWidget(self.script_name_label)
        
        info_layout.addStretch()
        
        self.step_count_label = QLabel("Steps: 0")
        info_layout.addWidget(self.step_count_label)
        
        layout.addLayout(info_layout)
        
        # Main splitter
        splitter = QSplitter(Qt.Vertical)
        
        # Steps list
        steps_group = QGroupBox("Script Steps")
        steps_layout = QVBoxLayout(steps_group)
        
        # Steps table
        self.steps_table = QTableWidget()
        self.steps_table.setColumnCount(5)
        self.steps_table.setHorizontalHeaderLabels(["#", "Type", "Action", "Details", "Description"])
        self.steps_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.steps_table.setSelectionMode(QTableWidget.SingleSelection)
        self.steps_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.steps_table.customContextMenuRequested.connect(self._show_steps_context_menu)
        
        # Set column widths
        self.steps_table.horizontalHeader().setStretchLastSection(True)
        self.steps_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.steps_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.steps_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        steps_layout.addWidget(self.steps_table)
        
        # Step buttons
        buttons_layout = QHBoxLayout()
        
        self.add_step_button = QPushButton("Add Step")
        self.add_step_button.clicked.connect(self._add_step)
        buttons_layout.addWidget(self.add_step_button)
        
        self.edit_step_button = QPushButton("Edit Step")
        self.edit_step_button.clicked.connect(self._edit_selected_step)
        buttons_layout.addWidget(self.edit_step_button)
        
        self.delete_step_button = QPushButton("Delete Step")
        self.delete_step_button.clicked.connect(self._delete_selected_step)
        buttons_layout.addWidget(self.delete_step_button)
        
        self.move_up_button = QPushButton("Move Up")
        self.move_up_button.clicked.connect(self._move_step_up)
        buttons_layout.addWidget(self.move_up_button)
        
        self.move_down_button = QPushButton("Move Down")
        self.move_down_button.clicked.connect(self._move_step_down)
        buttons_layout.addWidget(self.move_down_button)
        
        steps_layout.addLayout(buttons_layout)
        
        # Script properties
        properties_group = QGroupBox("Script Properties")
        properties_layout = QFormLayout(properties_group)
        
        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(self._on_name_changed)
        properties_layout.addRow("Name:", self.name_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        self.description_edit.textChanged.connect(self._on_description_changed)
        properties_layout.addRow("Description:", self.description_edit)
        
        # Add components to splitter
        splitter.addWidget(steps_group)
        splitter.addWidget(properties_group)
        
        # Set splitter sizes
        splitter.setSizes([400, 100])
        
        layout.addWidget(splitter)
    
    def update_ui(self):
        """Update the UI with current script data."""
        # Update script info
        if self.script_manager.current_script:
            script = self.script_manager.current_script
            self.script_name_label.setText(script.get("name", "Unnamed Script"))
            steps_count = len(script.get("steps", []))
            self.step_count_label.setText(f"Steps: {steps_count}")
            
            # Update properties
            self.name_edit.setText(script.get("name", ""))
            self.description_edit.setText(script.get("description", ""))
            
            # Update steps table
            self._update_steps_table()
        else:
            # No script loaded
            self.script_name_label.setText("No script loaded")
            self.step_count_label.setText("Steps: 0")
            self.name_edit.setText("")
            self.description_edit.setText("")
            self.steps_table.setRowCount(0)
    
    def _update_steps_table(self):
        """Update the steps table with current script steps."""
        if not self.script_manager.current_script:
            return
        
        steps = self.script_manager.current_script.get("steps", [])
        
        # Clear existing rows
        self.steps_table.setRowCount(0)
        
        # Add rows for each step
        for i, step in enumerate(steps):
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
            if step_type.lower() == "wait":
                action_text = f"Wait {step.get('duration', 1)}s"
            else:
                action_text = step.get("action", "")
                if step_type.lower() == "captcha":
                    action_text = step.get("captcha_type", "")
                    
            action_item = QTableWidgetItem(action_text)
            action_item.setFlags(action_item.flags() & ~Qt.ItemIsEditable)
            self.steps_table.setItem(i, 2, action_item)
            
            # Details
            details = self._get_step_details(step)
            details_item = QTableWidgetItem(details)
            details_item.setFlags(details_item.flags() & ~Qt.ItemIsEditable)
            self.steps_table.setItem(i, 3, details_item)
            
            # Description
            description = step.get("description", "")
            desc_item = QTableWidgetItem(description)
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemIsEditable)
            self.steps_table.setItem(i, 4, desc_item)
        
        # Adjust row heights
        for i in range(self.steps_table.rowCount()):
            self.steps_table.resizeRowToContents(i)
    
    def _get_step_details(self, step: Dict[str, Any]) -> str:
        """Generate a human-readable description of step details."""
        step_type = step.get("type", "").lower()
        
        if step_type == "desktop":
            action = step.get("action", "").lower()
            
            if action in ["click", "right_click", "double_click", "move"]:
                if "image" in step:
                    return f"On image: {step['image']}"
                else:
                    return f"At ({step.get('x', 0)}, {step.get('y', 0)})"
            
            elif action == "type":
                return f"Text: '{step.get('text', '')}'"
            
            elif action == "key_press":
                return f"Key: {step.get('key', '')}"
            
            elif action == "drag":
                start = f"({step.get('x', 0)}, {step.get('y', 0)})"
                to_data = step.get("to", {})
                end = f"({to_data.get('x', 0)}, {to_data.get('y', 0)})"
                return f"From {start} to {end}"
            
            elif action == "scroll":
                clicks = step.get("clicks", 0)
                direction = "down" if clicks < 0 else "up"
                return f"{direction} {abs(clicks)} clicks"
            
            elif action in ["find_image", "wait_for_image"]:
                return f"Image: {step.get('image', '')}"
        
        elif step_type == "web":
            action = step.get("action", "").lower()
            
            if action == "navigate":
                return f"URL: {step.get('url', '')}"
            
            elif action in ["click", "type", "clear", "submit", "wait", "extract"]:
                selector = step.get("selector", {})
                selector_text = f"{selector.get('type', '')}='{selector.get('value', '')}'"
                
                if action == "type":
                    return f"'{step.get('text', '')}' into {selector_text}"
                elif action == "wait":
                    return f"For {selector_text} to be {step.get('condition', 'present')}"
                else:
                    return f"Element {selector_text}"
            
            elif action == "select":
                selector = step.get("selector", {})
                selector_text = f"{selector.get('type', '')}='{selector.get('value', '')}'"
                
                if "value" in step:
                    return f"Value '{step['value']}' in {selector_text}"
                elif "text" in step:
                    return f"Text '{step['text']}' in {selector_text}"
                elif "index" in step:
                    return f"Index {step['index']} in {selector_text}"
                else:
                    return f"Element {selector_text}"
        
        elif step_type == "captcha":
            captcha_type = step.get("captcha_type", "").lower()
            
            if captcha_type == "manual":
                return f"Wait {step.get('wait_time', 30)}s for manual solving"
            else:
                return f"{captcha_type.capitalize()} CAPTCHA"
        
        elif step_type == "wait":
            return f"Duration: {step.get('duration', 1)} seconds"
        
        return ""
    
    def _add_step(self):
        """Add a new step to the script."""
        if not self.script_manager.current_script:
            QMessageBox.warning(self, "Warning", "No script loaded")
            return
        
        dialog = StepEditorDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            step_data = dialog.get_step_data()
            
            if self.script_manager.add_step(step_data):
                self._update_steps_table()
                self.script_modified.emit()
    
    def _edit_selected_step(self):
        """Edit the selected step."""
        if not self.script_manager.current_script:
            return
        
        selected_row = self.steps_table.currentRow()
        if selected_row >= 0:
            step = self.script_manager.current_script["steps"][selected_row]
            
            dialog = StepEditorDialog(step, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                updated_step = dialog.get_step_data()
                
                if self.script_manager.update_step(selected_row, updated_step):
                    self._update_steps_table()
                    self.script_modified.emit()
    
    def _delete_selected_step(self):
        """Delete the selected step."""
        if not self.script_manager.current_script:
            return
        
        selected_row = self.steps_table.currentRow()
        if selected_row >= 0:
            # Confirm deletion
            response = QMessageBox.question(
                self, "Confirm Deletion",
                "Are you sure you want to delete this step?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if response == QMessageBox.Yes:
                if self.script_manager.remove_step(selected_row):
                    self._update_steps_table()
                    self.script_modified.emit()
    
    def _move_step_up(self):
        """Move the selected step up in the list."""
        if not self.script_manager.current_script:
            return
        
        selected_row = self.steps_table.currentRow()
        if selected_row > 0:
            if self.script_manager.move_step(selected_row, selected_row - 1):
                self._update_steps_table()
                self.steps_table.selectRow(selected_row - 1)
                self.script_modified.emit()
    
    def _move_step_down(self):
        """Move the selected step down in the list."""
        if not self.script_manager.current_script:
            return
        
        selected_row = self.steps_table.currentRow()
        steps = self.script_manager.current_script.get("steps", [])
        
        if selected_row >= 0 and selected_row < len(steps) - 1:
            if self.script_manager.move_step(selected_row, selected_row + 1):
                self._update_steps_table()
                self.steps_table.selectRow(selected_row + 1)
                self.script_modified.emit()
    
    def _on_name_changed(self):
        """Handle script name change."""
        if self.script_manager.current_script:
            self.script_manager.current_script["name"] = self.name_edit.text()
            self.script_name_label.setText(self.name_edit.text() or "Unnamed Script")
            self.script_modified.emit()
    
    def _on_description_changed(self):
        """Handle script description change."""
        if self.script_manager.current_script:
            self.script_manager.current_script["description"] = self.description_edit.toPlainText()
            self.script_modified.emit()
    
    def _show_steps_context_menu(self, position):
        """Show context menu for steps table."""
        if not self.script_manager.current_script:
            return
        
        selected_row = self.steps_table.currentRow()
        if selected_row < 0:
            return
        
        context_menu = QMenu(self)
        
        edit_action = context_menu.addAction("Edit")
        delete_action = context_menu.addAction("Delete")
        context_menu.addSeparator()
        move_up_action = context_menu.addAction("Move Up")
        move_down_action = context_menu.addAction("Move Down")
        context_menu.addSeparator()
        duplicate_action = context_menu.addAction("Duplicate")
        
        # Disable actions if they don't apply
        if selected_row == 0:
            move_up_action.setEnabled(False)
        
        steps = self.script_manager.current_script.get("steps", [])
        if selected_row >= len(steps) - 1:
            move_down_action.setEnabled(False)
        
        action = context_menu.exec_(self.steps_table.mapToGlobal(position))
        
        if action == edit_action:
            self._edit_selected_step()
        elif action == delete_action:
            self._delete_selected_step()
        elif action == move_up_action:
            self._move_step_up()
        elif action == move_down_action:
            self._move_step_down()
        elif action == duplicate_action:
            self._duplicate_step(selected_row)
    
    def _duplicate_step(self, row_index):
        """Duplicate a step."""
        if not self.script_manager.current_script:
            return
        
        steps = self.script_manager.current_script.get("steps", [])
        if 0 <= row_index < len(steps):
            # Make a deep copy of the step
            import copy
            step_copy = copy.deepcopy(steps[row_index])
            
            # Add "copy" to description if it exists
            if "description" in step_copy:
                step_copy["description"] = f"{step_copy['description']} (Copy)"
            else:
                step_copy["description"] = "Copy"
            
            # Add the copy after the original
            if self.script_manager.add_step(step_copy, row_index + 1):
                self._update_steps_table()
                self.steps_table.selectRow(row_index + 1)
                self.script_modified.emit()
