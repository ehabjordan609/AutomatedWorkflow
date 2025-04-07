#!/usr/bin/env python3
"""
Script editor module for the Automation Tool GUI.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, 
    QListWidgetItem, QStackedWidget, QGroupBox, QFormLayout, QLineEdit, 
    QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox, QDialog,
    QDialogButtonBox, QTabWidget, QFileDialog, QMessageBox, QSplitter,
    QTreeWidget, QTreeWidgetItem, QMenu, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QModelIndex
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor, QContextMenuEvent

from automation_engine import AutomationEngine
from script_manager import ScriptManager

logger = logging.getLogger(__name__)

class StepEditor(QWidget):
    """Base class for step editors."""
    
    # Signal emitted when the step is modified
    step_changed = pyqtSignal(dict)
    
    def __init__(self):
        """Initialize the step editor."""
        super().__init__()
        self.current_step = {}
        
    def set_step(self, step: Dict[str, Any]):
        """Set the step data to edit."""
        self.current_step = step.copy()
        self._update_ui()
        
    def _update_ui(self):
        """Update the UI with the current step data."""
        pass
        
    def _emit_step_changed(self):
        """Emit the step_changed signal with the current step data."""
        self.step_changed.emit(self.current_step)


class DesktopStepEditor(StepEditor):
    """Editor for desktop automation steps."""
    
    def __init__(self):
        """Initialize the desktop step editor."""
        super().__init__()
        layout = QFormLayout()
        self.setLayout(layout)
        
        # Action type selector
        self.action_combo = QComboBox()
        self.action_combo.addItems([
            "click", "right_click", "double_click", "type", "key_press", 
            "move", "drag", "scroll", "find_image", "wait_for_image", 
            "screenshot", "select_all", "copy", "paste", "cut", 
            "new_tab", "close_tab", "switch_tab", "read_from_file", 
            "write_to_file", "append_to_file", "wait_for_clipboard"
        ])
        self.action_combo.currentTextChanged.connect(self._on_action_changed)
        layout.addRow("Action:", self.action_combo)
        
        # Common parameters (will customize based on action)
        self.params_widget = QWidget()
        self.params_layout = QFormLayout()
        self.params_widget.setLayout(self.params_layout)
        layout.addRow(self.params_widget)
        
    def _update_ui(self):
        """Update the UI with the current step data."""
        action = self.current_step.get("action", "click")
        self.action_combo.setCurrentText(action)
        self._update_params_ui()
        
    def _on_action_changed(self, action):
        """Handle action type changes."""
        self.current_step["action"] = action
        self._update_params_ui()
        self._emit_step_changed()
        
    def _update_params_ui(self):
        """Update the parameters UI based on the current action."""
        # Clear existing params UI
        while self.params_layout.rowCount() > 0:
            self.params_layout.removeRow(0)
            
        # Add parameters based on action type
        action = self.current_step.get("action", "click")
        
        # Add specific parameters based on action type
        # This is simplified - in a real implementation, 
        # you'd add the appropriate widgets for each parameter
        if action in ["click", "right_click", "double_click", "move"]:
            # Add coordinate inputs
            self._add_coordinate_inputs()
            
    def _add_coordinate_inputs(self):
        """Add coordinate input fields."""
        # X coordinate
        x_spin = QSpinBox()
        x_spin.setRange(0, 9999)
        x_spin.setValue(self.current_step.get("x", 0))
        x_spin.valueChanged.connect(lambda v: self._update_param("x", v))
        self.params_layout.addRow("X:", x_spin)
        
        # Y coordinate
        y_spin = QSpinBox()
        y_spin.setRange(0, 9999)
        y_spin.setValue(self.current_step.get("y", 0))
        y_spin.valueChanged.connect(lambda v: self._update_param("y", v))
        self.params_layout.addRow("Y:", y_spin)
        
    def _update_param(self, param, value):
        """Update a parameter value."""
        self.current_step[param] = value
        self._emit_step_changed()


class WebStepEditor(StepEditor):
    """Editor for web automation steps."""
    
    def __init__(self):
        """Initialize the web step editor."""
        super().__init__()
        layout = QFormLayout()
        self.setLayout(layout)
        
        # Action type selector
        self.action_combo = QComboBox()
        self.action_combo.addItems([
            "start_browser", "start_browser_with_profile", "close_browser", 
            "navigate", "click", "type", "clear", "submit", "select", 
            "wait", "extract", "scroll", "switch_frame", "switch_window", 
            "execute_script", "take_screenshot"
        ])
        self.action_combo.currentTextChanged.connect(self._on_action_changed)
        layout.addRow("Action:", self.action_combo)
        
        # Common parameters
        self.params_widget = QWidget()
        self.params_layout = QFormLayout()
        self.params_widget.setLayout(self.params_layout)
        layout.addRow(self.params_widget)
        
        # Initialize step data
        self.step = {}
        
    def _update_ui(self):
        """Update the UI with the current step data."""
        action = self.current_step.get("action", "navigate")
        self.action_combo.setCurrentText(action)
        self._update_params_ui()
    
    def set_step_data(self, step: Dict[str, Any]) -> None:
        """
        Set the step data to be edited.
        
        Args:
            step: The step data
        """
        self.step = step
        self.current_step = step  # For backward compatibility
        # Call _update_ui instead of _update_ui_from_step to be compatible with both implementations
        self._update_ui()
    
    def _update_ui_from_step(self) -> None:
        """Update the UI with the current step data."""
        action = self.step.get("action", "navigate")
        self.action_combo.setCurrentText(action)
        self._update_params_ui()
        
    def _update_step_from_ui(self) -> None:
        """Update the step data from the UI and emit the step_changed signal."""
        self.step["action"] = self.action_combo.currentText()
        self._emit_step_changed()
        
    def _on_action_changed(self, action):
        """Handle action type changes."""
        self.current_step["action"] = action
        self.step["action"] = action
        self._update_params_ui()
        self._emit_step_changed()
        
    def _update_params_ui(self):
        """Update the parameters UI based on the current action."""
        # Implementation would be similar to DesktopStepEditor
        pass


class CaptchaStepEditor(StepEditor):
    """Editor for CAPTCHA handling steps."""
    
    def __init__(self):
        """Initialize the CAPTCHA step editor."""
        super().__init__()
        layout = QFormLayout()
        self.setLayout(layout)
        
        # CAPTCHA type selector
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "image", "recaptcha", "audio", "text", "manual"
        ])
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        layout.addRow("CAPTCHA Type:", self.type_combo)
        
        # Parameters
        self.params_widget = QWidget()
        self.params_layout = QFormLayout()
        self.params_widget.setLayout(self.params_layout)
        layout.addRow(self.params_widget)
    
    def set_step_data(self, step: Dict[str, Any]) -> None:
        """
        Set the step data to be edited.
        
        Args:
            step: The step data
        """
        self.current_step = step
        self._update_ui()
        
    def _update_ui(self):
        """Update the UI with the current step data."""
        captcha_type = self.current_step.get("captcha_type", "image")
        self.type_combo.setCurrentText(captcha_type)
        self._update_params_ui()
        
    def _on_type_changed(self, captcha_type):
        """Handle CAPTCHA type changes."""
        self.current_step["captcha_type"] = captcha_type
        self._update_params_ui()
        self._emit_step_changed()
        
    def _update_params_ui(self):
        """Update the parameters UI based on the current CAPTCHA type."""
        # Implementation similar to other editors
        pass


class WaitStepEditor(StepEditor):
    """Editor for wait/delay steps."""
    
    def __init__(self):
        """Initialize the wait step editor."""
        super().__init__()
        layout = QFormLayout()
        self.setLayout(layout)
        
        # Wait type selector
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "fixed", "random", "until_image", "until_element"
        ])
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        layout.addRow("Wait Type:", self.type_combo)
        
        # Duration
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(0.1, 3600)
        self.duration_spin.setValue(1.0)
        self.duration_spin.valueChanged.connect(self._on_duration_changed)
        layout.addRow("Duration (s):", self.duration_spin)
    
    def set_step_data(self, step: Dict[str, Any]) -> None:
        """
        Set the step data to be edited.
        
        Args:
            step: The step data
        """
        self.current_step = step
        self._update_ui()
        
    def _update_ui(self):
        """Update the UI with the current step data."""
        wait_type = self.current_step.get("wait_type", "fixed")
        self.type_combo.setCurrentText(wait_type)
        
        duration = self.current_step.get("duration", 1.0)
        self.duration_spin.setValue(duration)
        
    def _on_type_changed(self, wait_type):
        """Handle wait type changes."""
        self.current_step["wait_type"] = wait_type
        self._emit_step_changed()
        
    def _on_duration_changed(self, duration):
        """Handle duration changes."""
        self.current_step["duration"] = duration
        self._emit_step_changed()


class VariableStepEditor(StepEditor):
    """Editor for variable manipulation steps."""
    
    def __init__(self):
        """Initialize the variable step editor."""
        super().__init__()
        layout = QFormLayout()
        self.setLayout(layout)
        
        # Variable operation selector
        self.operation_combo = QComboBox()
        self.operation_combo.addItems([
            "set", "increment", "decrement", "append", "clear"
        ])
        self.operation_combo.currentTextChanged.connect(self._on_operation_changed)
        layout.addRow("Operation:", self.operation_combo)
        
        # Variable name
        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(self._on_name_changed)
        layout.addRow("Variable Name:", self.name_edit)
        
        # Value
        self.value_edit = QLineEdit()
        self.value_edit.textChanged.connect(self._on_value_changed)
        layout.addRow("Value:", self.value_edit)
    
    def set_step_data(self, step: Dict[str, Any]) -> None:
        """
        Set the step data to be edited.
        
        Args:
            step: The step data
        """
        self.current_step = step
        self._update_ui()
        
    def _update_ui(self):
        """Update the UI with the current step data."""
        operation = self.current_step.get("operation", "set")
        self.operation_combo.setCurrentText(operation)
        
        name = self.current_step.get("name", "")
        self.name_edit.setText(name)
        
        value = self.current_step.get("value", "")
        self.value_edit.setText(str(value))
        
    def _on_operation_changed(self, operation):
        """Handle operation changes."""
        self.current_step["operation"] = operation
        self._emit_step_changed()
        
    def _on_name_changed(self, name):
        """Handle variable name changes."""
        self.current_step["name"] = name
        self._emit_step_changed()
        
    def _on_value_changed(self, value):
        """Handle value changes."""
        self.current_step["value"] = value
        self._emit_step_changed()


class ConditionStepEditor(StepEditor):
    """Editor for conditional logic steps."""
    
    def __init__(self):
        """Initialize the condition step editor."""
        super().__init__()
        layout = QFormLayout()
        self.setLayout(layout)
        
        # Condition type selector
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "if_equal", "if_not_equal", "if_greater", "if_less", 
            "if_contains", "if_exists", "if_image_found"
        ])
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        layout.addRow("Condition Type:", self.type_combo)
        
        # Left value
        self.left_edit = QLineEdit()
        self.left_edit.textChanged.connect(self._on_left_changed)
        layout.addRow("Left Value:", self.left_edit)
        
        # Right value
        self.right_edit = QLineEdit()
        self.right_edit.textChanged.connect(self._on_right_changed)
        layout.addRow("Right Value:", self.right_edit)
        
    def set_step_data(self, step: Dict[str, Any]) -> None:
        """
        Set the step data to be edited.
        
        Args:
            step: The step data
        """
        self.current_step = step
        self._update_ui()
        
    def _update_ui(self):
        """Update the UI with the current step data."""
        condition_type = self.current_step.get("condition_type", "if_equal")
        self.type_combo.setCurrentText(condition_type)
        
        left = self.current_step.get("left", "")
        self.left_edit.setText(str(left))
        
        right = self.current_step.get("right", "")
        self.right_edit.setText(str(right))
        
    def _on_type_changed(self, condition_type):
        """Handle condition type changes."""
        self.current_step["condition_type"] = condition_type
        self._emit_step_changed()
        
    def _on_left_changed(self, left):
        """Handle left value changes."""
        self.current_step["left"] = left
        self._emit_step_changed()
        
    def _on_right_changed(self, right):
        """Handle right value changes."""
        self.current_step["right"] = right
        self._emit_step_changed()


class ScriptEditorWidget(QWidget):
    """Widget for editing automation scripts."""
    
    # Signals
    script_changed = pyqtSignal()
    
    def __init__(self, script_manager: ScriptManager, automation_engine: AutomationEngine):
        """
        Initialize the script editor widget.
        
        Args:
            script_manager: The script manager instance
            automation_engine: The automation engine instance
        """
        super().__init__()
        
        self.script_manager = script_manager
        self.automation_engine = automation_engine
        self.has_unsaved_changes = False
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the user interface elements."""
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Script header section
        header_group = QGroupBox("Script Information")
        header_layout = QFormLayout()
        header_group.setLayout(header_layout)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter script name")
        self.name_edit.textChanged.connect(self._on_script_info_changed)
        header_layout.addRow("Name:", self.name_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(60)
        self.description_edit.setPlaceholderText("Enter script description")
        self.description_edit.textChanged.connect(self._on_script_info_changed)
        header_layout.addRow("Description:", self.description_edit)
        
        main_layout.addWidget(header_group)
        
        # Splitter for steps list and step editor
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter, 1)  # Give the splitter most of the space
        
        # Steps list
        steps_group = QGroupBox("Script Steps")
        steps_layout = QVBoxLayout()
        steps_group.setLayout(steps_layout)
        
        self.steps_list = QListWidget()
        self.steps_list.setDragDropMode(QListWidget.InternalMove)
        self.steps_list.currentRowChanged.connect(self._on_step_selected)
        steps_layout.addWidget(self.steps_list)
        
        # Step control buttons
        btn_layout = QHBoxLayout()
        
        self.add_step_btn = QPushButton("Add Step")
        self.add_step_btn.clicked.connect(self._add_step)
        btn_layout.addWidget(self.add_step_btn)
        
        self.remove_step_btn = QPushButton("Remove Step")
        self.remove_step_btn.clicked.connect(self._remove_step)
        btn_layout.addWidget(self.remove_step_btn)
        
        self.move_up_btn = QPushButton("Move Up")
        self.move_up_btn.clicked.connect(self._move_step_up)
        btn_layout.addWidget(self.move_up_btn)
        
        self.move_down_btn = QPushButton("Move Down")
        self.move_down_btn.clicked.connect(self._move_step_down)
        btn_layout.addWidget(self.move_down_btn)
        
        steps_layout.addLayout(btn_layout)
        
        # Add the steps group to the splitter
        splitter.addWidget(steps_group)
        
        # Step editor
        editor_group = QGroupBox("Step Editor")
        editor_layout = QVBoxLayout()
        editor_group.setLayout(editor_layout)
        
        # Step type selector
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Step Type:"))
        
        self.step_type_combo = QComboBox()
        self.step_type_combo.addItems(["Desktop", "Web", "CAPTCHA", "Wait", "Variable", "Condition"])
        self.step_type_combo.currentIndexChanged.connect(self._on_step_type_changed)
        type_layout.addWidget(self.step_type_combo)
        
        editor_layout.addLayout(type_layout)
        
        # Step editor stack - each type gets its own editor widget
        self.editor_stack = QStackedWidget()
        
        # Desktop action editor
        self.desktop_editor = DesktopStepEditor()
        self.desktop_editor.step_changed.connect(self._on_step_edited)
        self.editor_stack.addWidget(self.desktop_editor)
        
        # Web action editor
        self.web_editor = WebStepEditor()
        self.web_editor.step_changed.connect(self._on_step_edited)
        self.editor_stack.addWidget(self.web_editor)
        
        # CAPTCHA action editor
        self.captcha_editor = CaptchaStepEditor()
        self.captcha_editor.step_changed.connect(self._on_step_edited)
        self.editor_stack.addWidget(self.captcha_editor)
        
        # Wait action editor
        self.wait_editor = WaitStepEditor()
        self.wait_editor.step_changed.connect(self._on_step_edited)
        self.editor_stack.addWidget(self.wait_editor)
        
        # Variable action editor
        self.variable_editor = VariableStepEditor()
        self.variable_editor.step_changed.connect(self._on_step_edited)
        self.editor_stack.addWidget(self.variable_editor)
        
        # Condition action editor
        self.condition_editor = ConditionStepEditor()
        self.condition_editor.step_changed.connect(self._on_step_edited)
        self.editor_stack.addWidget(self.condition_editor)
        
        editor_layout.addWidget(self.editor_stack)
        
        # Add the editor group to the splitter
        splitter.addWidget(editor_group)
        
        # Set initial splitter sizes
        splitter.setSizes([300, 500])
    
    def _connect_signals(self):
        """Connect signals from UI elements to slots."""
        # Connected in _setup_ui for clarity
        pass
    
    def update_script_view(self):
        """
        Update the UI to reflect the current script.
        Call this after loading a new script.
        """
        script = self.script_manager.current_script
        
        if script:
            # Update header information
            self.name_edit.setText(script.get('name', ''))
            self.description_edit.setText(script.get('description', ''))
            
            # Update steps list
            self._populate_steps_list()
            
            # Reset the unsaved changes flag
            self.has_unsaved_changes = False
        else:
            # Clear the UI
            self.name_edit.clear()
            self.description_edit.clear()
            self.steps_list.clear()
    
    def _populate_steps_list(self):
        """Populate the steps list with the current script steps."""
        self.steps_list.clear()
        
        if not self.script_manager.current_script:
            return
        
        for i, step in enumerate(self.script_manager.current_script.get('steps', [])):
            step_type = step.get('type', '').capitalize()
            step_action = ''
            
            if step_type.lower() == 'desktop' or step_type.lower() == 'web':
                step_action = step.get('action', '')
            elif step_type.lower() == 'captcha':
                step_action = step.get('captcha_type', '')
            elif step_type.lower() == 'wait':
                step_action = f"{step.get('duration', 0)}s"
            elif step_type.lower() == 'variable':
                step_action = f"{step.get('action', '')} {step.get('name', '')}"
            elif step_type.lower() == 'condition':
                step_action = 'If/Else'
            
            item_text = f"{i+1}. [{step_type}] {step_action}"
            if 'description' in step and step['description']:
                item_text += f" - {step['description']}"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, step)  # Store the step data in the item
            
            self.steps_list.addItem(item)
    
    def _on_script_info_changed(self):
        """Handle changes to script information fields."""
        if not self.script_manager.current_script:
            return
        
        self.script_manager.current_script['name'] = self.name_edit.text()
        self.script_manager.current_script['description'] = self.description_edit.toPlainText()
        
        self.has_unsaved_changes = True
        self.script_changed.emit()
    
    def _on_step_selected(self, row: int):
        """
        Handle selection of a step in the steps list.
        
        Args:
            row: The row that was selected
        """
        if row < 0:
            # No step selected, disable the step editor
            return
        
        # Get the step data from the item
        item = self.steps_list.item(row)
        step = item.data(Qt.UserRole)
        
        # Set the step type combo box
        step_type = step.get('type', '').lower()
        index = 0  # Default to desktop
        
        if step_type == 'desktop':
            index = 0
        elif step_type == 'web':
            index = 1
        elif step_type == 'captcha':
            index = 2
        elif step_type == 'wait':
            index = 3
        elif step_type == 'variable':
            index = 4
        elif step_type == 'condition':
            index = 5
        
        # This will trigger _on_step_type_changed which will set up the editor
        self.step_type_combo.setCurrentIndex(index)
        
        # Update the editor with the step data
        current_editor = self.editor_stack.currentWidget()
        current_editor.set_step_data(step)
    
    def _on_step_type_changed(self, index: int):
        """
        Handle change of step type in the combo box.
        
        Args:
            index: The index that was selected
        """
        # Switch to the appropriate editor
        self.editor_stack.setCurrentIndex(index)
        
        # If a step is selected, update its type
        row = self.steps_list.currentRow()
        if row >= 0:
            item = self.steps_list.item(row)
            step = item.data(Qt.UserRole)
            
            # Update the step type
            if index == 0:
                step['type'] = 'desktop'
            elif index == 1:
                step['type'] = 'web'
            elif index == 2:
                step['type'] = 'captcha'
            elif index == 3:
                step['type'] = 'wait'
            elif index == 4:
                step['type'] = 'variable'
            elif index == 5:
                step['type'] = 'condition'
            
            # Update the editor with the step data
            current_editor = self.editor_stack.currentWidget()
            current_editor.set_step_data(step)
    
    def _on_step_edited(self, step: Dict[str, Any]):
        """
        Handle edits to a step in one of the editors.
        
        Args:
            step: The updated step data
        """
        row = self.steps_list.currentRow()
        if row >= 0:
            item = self.steps_list.item(row)
            item.setData(Qt.UserRole, step)
            
            # Update the item text
            step_type = step.get('type', '').capitalize()
            step_action = ''
            
            if step_type.lower() == 'desktop' or step_type.lower() == 'web':
                step_action = step.get('action', '')
            elif step_type.lower() == 'captcha':
                step_action = step.get('captcha_type', '')
            elif step_type.lower() == 'wait':
                step_action = f"{step.get('duration', 0)}s"
            elif step_type.lower() == 'variable':
                step_action = f"{step.get('action', '')} {step.get('name', '')}"
            elif step_type.lower() == 'condition':
                step_action = 'If/Else'
            
            item_text = f"{row+1}. [{step_type}] {step_action}"
            if 'description' in step and step['description']:
                item_text += f" - {step['description']}"
            
            item.setText(item_text)
            
            # Update the script
            if self.script_manager.current_script:
                self.script_manager.current_script['steps'][row] = step
                self.has_unsaved_changes = True
                self.script_changed.emit()
    
    def _add_step(self):
        """Add a new step to the script."""
        if not self.script_manager.current_script:
            QMessageBox.warning(self, "Error", "No script loaded")
            return
        
        # Create a default step based on the current type
        step_type = self.step_type_combo.currentText().lower()
        
        if step_type == 'desktop':
            step = {
                'type': 'desktop',
                'action': 'click',
                'x': 0,
                'y': 0,
                'delay': 0.5,
                'description': ''
            }
        elif step_type == 'web':
            step = {
                'type': 'web',
                'action': 'navigate',
                'url': 'https://',
                'delay': 0.5,
                'description': ''
            }
        elif step_type == 'captcha':
            step = {
                'type': 'captcha',
                'captcha_type': 'image',
                'delay': 0.5,
                'description': ''
            }
        elif step_type == 'wait':
            step = {
                'type': 'wait',
                'duration': 1,
                'delay': 0.5,
                'description': ''
            }
        elif step_type == 'variable':
            step = {
                'type': 'variable',
                'action': 'set',
                'name': 'variable_name',
                'value': '',
                'delay': 0.5,
                'description': ''
            }
        elif step_type == 'condition':
            step = {
                'type': 'condition',
                'condition': {
                    'type': 'variable_exists',
                    'variable': 'variable_name'
                },
                'if_steps': [],
                'else_steps': [],
                'delay': 0.5,
                'description': ''
            }
        
        # Add the step to the script
        if self.script_manager.add_step(step):
            # Update the steps list
            self._populate_steps_list()
            
            # Select the new step
            self.steps_list.setCurrentRow(len(self.script_manager.current_script['steps']) - 1)
            
            self.has_unsaved_changes = True
            self.script_changed.emit()
    
    def _remove_step(self):
        """Remove the selected step from the script."""
        row = self.steps_list.currentRow()
        if row < 0:
            return
        
        if self.script_manager.remove_step(row):
            # Update the steps list
            self._populate_steps_list()
            
            # Select the next step, or the last step if the removed step was the last one
            if self.steps_list.count() > 0:
                if row < self.steps_list.count():
                    self.steps_list.setCurrentRow(row)
                else:
                    self.steps_list.setCurrentRow(self.steps_list.count() - 1)
            
            self.has_unsaved_changes = True
            self.script_changed.emit()
    
    def _move_step_up(self):
        """Move the selected step up in the script."""
        row = self.steps_list.currentRow()
        if row <= 0:
            return
        
        if self.script_manager.move_step(row, row - 1):
            # Update the steps list
            self._populate_steps_list()
            
            # Select the moved step
            self.steps_list.setCurrentRow(row - 1)
            
            self.has_unsaved_changes = True
            self.script_changed.emit()
    
    def _move_step_down(self):
        """Move the selected step down in the script."""
        row = self.steps_list.currentRow()
        if row < 0 or row >= self.steps_list.count() - 1:
            return
        
        if self.script_manager.move_step(row, row + 1):
            # Update the steps list
            self._populate_steps_list()
            
            # Select the moved step
            self.steps_list.setCurrentRow(row + 1)
            
            self.has_unsaved_changes = True
            self.script_changed.emit()


class StepEditor(QWidget):
    """Base class for step editors."""
    
    # Signal emitted when the step data is changed
    step_changed = pyqtSignal(dict)
    
    def __init__(self):
        """Initialize the step editor."""
        super().__init__()
        self.step = {}
    
    def set_step_data(self, step: Dict[str, Any]) -> None:
        """
        Set the step data to be edited.
        
        Args:
            step: The step data
        """
        self.step = step
        self._update_ui_from_step()
    
    def _update_ui_from_step(self) -> None:
        """Update the UI with the current step data."""
        raise NotImplementedError("Subclasses must implement this method")
    
    def _update_step_from_ui(self) -> None:
        """Update the step data from the UI and emit the step_changed signal."""
        raise NotImplementedError("Subclasses must implement this method")


class DesktopStepEditor(StepEditor):
    """Editor for desktop automation steps."""
    
    def __init__(self):
        """Initialize the desktop step editor."""
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface elements."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Action selection
        action_layout = QHBoxLayout()
        action_layout.addWidget(QLabel("Action:"))
        
        self.action_combo = QComboBox()
        self.action_combo.addItems([
            "click", "right_click", "double_click", "type", "key_press", 
            "move", "drag", "scroll", "find_image", "wait_for_image", "screenshot"
        ])
        self.action_combo.currentTextChanged.connect(self._on_action_changed)
        action_layout.addWidget(self.action_combo)
        
        layout.addLayout(action_layout)
        
        # Stacked widget for action-specific controls
        self.action_stack = QStackedWidget()
        layout.addWidget(self.action_stack)
        
        # Click, right_click, double_click, move actions
        click_widget = QWidget()
        click_layout = QFormLayout()
        click_widget.setLayout(click_layout)
        
        self.use_image_checkbox = QCheckBox("Use image for targeting")
        self.use_image_checkbox.stateChanged.connect(self._on_use_image_changed)
        click_layout.addRow(self.use_image_checkbox)
        
        self.image_path_edit = QLineEdit()
        self.image_path_edit.setPlaceholderText("Image path")
        self.image_path_edit.textChanged.connect(self._update_step_from_ui)
        click_layout.addRow("Image:", self.image_path_edit)
        
        self.browse_image_btn = QPushButton("Browse...")
        self.browse_image_btn.clicked.connect(self._browse_image)
        click_layout.addWidget(self.browse_image_btn)
        
        self.image_confidence_spin = QDoubleSpinBox()
        self.image_confidence_spin.setRange(0.1, 1.0)
        self.image_confidence_spin.setValue(0.9)
        self.image_confidence_spin.setSingleStep(0.05)
        self.image_confidence_spin.setDecimals(2)
        self.image_confidence_spin.valueChanged.connect(self._update_step_from_ui)
        click_layout.addRow("Confidence:", self.image_confidence_spin)
        
        # Coordinates group (hidden when using image)
        self.coords_group = QGroupBox("Coordinates")
        coords_layout = QFormLayout()
        self.coords_group.setLayout(coords_layout)
        
        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, 9999)
        self.x_spin.valueChanged.connect(self._update_step_from_ui)
        coords_layout.addRow("X:", self.x_spin)
        
        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, 9999)
        self.y_spin.valueChanged.connect(self._update_step_from_ui)
        coords_layout.addRow("Y:", self.y_spin)
        
        click_layout.addWidget(self.coords_group)
        
        self.action_stack.addWidget(click_widget)
        
        # Type action
        type_widget = QWidget()
        type_layout = QFormLayout()
        type_widget.setLayout(type_layout)
        
        self.text_edit = QLineEdit()
        self.text_edit.setPlaceholderText("Text to type")
        self.text_edit.textChanged.connect(self._update_step_from_ui)
        type_layout.addRow("Text:", self.text_edit)
        
        self.interval_spin = QDoubleSpinBox()
        self.interval_spin.setRange(0.0, 1.0)
        self.interval_spin.setValue(0.0)
        self.interval_spin.setSingleStep(0.01)
        self.interval_spin.setDecimals(2)
        self.interval_spin.valueChanged.connect(self._update_step_from_ui)
        type_layout.addRow("Interval:", self.interval_spin)
        
        self.action_stack.addWidget(type_widget)
        
        # Key press action
        key_widget = QWidget()
        key_layout = QFormLayout()
        key_widget.setLayout(key_layout)
        
        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText("Key or key combination (e.g., enter, ctrl+c)")
        self.key_edit.textChanged.connect(self._update_step_from_ui)
        key_layout.addRow("Key:", self.key_edit)
        
        self.action_stack.addWidget(key_widget)
        
        # Drag action
        drag_widget = QWidget()
        drag_layout = QFormLayout()
        drag_widget.setLayout(drag_layout)
        
        # From coordinates
        from_group = QGroupBox("From")
        from_layout = QFormLayout()
        from_group.setLayout(from_layout)
        
        self.from_x_spin = QSpinBox()
        self.from_x_spin.setRange(0, 9999)
        self.from_x_spin.valueChanged.connect(self._update_step_from_ui)
        from_layout.addRow("X:", self.from_x_spin)
        
        self.from_y_spin = QSpinBox()
        self.from_y_spin.setRange(0, 9999)
        self.from_y_spin.valueChanged.connect(self._update_step_from_ui)
        from_layout.addRow("Y:", self.from_y_spin)
        
        drag_layout.addWidget(from_group)
        
        # To coordinates
        to_group = QGroupBox("To")
        to_layout = QFormLayout()
        to_group.setLayout(to_layout)
        
        self.to_x_spin = QSpinBox()
        self.to_x_spin.setRange(0, 9999)
        self.to_x_spin.valueChanged.connect(self._update_step_from_ui)
        to_layout.addRow("X:", self.to_x_spin)
        
        self.to_y_spin = QSpinBox()
        self.to_y_spin.setRange(0, 9999)
        self.to_y_spin.valueChanged.connect(self._update_step_from_ui)
        to_layout.addRow("Y:", self.to_y_spin)
        
        drag_layout.addWidget(to_group)
        
        self.drag_duration_spin = QDoubleSpinBox()
        self.drag_duration_spin.setRange(0.1, 10.0)
        self.drag_duration_spin.setValue(0.5)
        self.drag_duration_spin.setSingleStep(0.1)
        self.drag_duration_spin.setDecimals(1)
        self.drag_duration_spin.valueChanged.connect(self._update_step_from_ui)
        drag_layout.addRow("Duration:", self.drag_duration_spin)
        
        self.action_stack.addWidget(drag_widget)
        
        # Scroll action
        scroll_widget = QWidget()
        scroll_layout = QFormLayout()
        scroll_widget.setLayout(scroll_layout)
        
        self.clicks_spin = QSpinBox()
        self.clicks_spin.setRange(-100, 100)
        self.clicks_spin.setValue(0)
        self.clicks_spin.setToolTip("Negative values scroll down, positive values scroll up")
        self.clicks_spin.valueChanged.connect(self._update_step_from_ui)
        scroll_layout.addRow("Clicks:", self.clicks_spin)
        
        self.action_stack.addWidget(scroll_widget)
        
        # Find image / Wait for image actions
        image_widget = QWidget()
        image_layout = QFormLayout()
        image_widget.setLayout(image_layout)
        
        self.image_path_edit2 = QLineEdit()
        self.image_path_edit2.setPlaceholderText("Image path")
        self.image_path_edit2.textChanged.connect(self._update_step_from_ui)
        image_layout.addRow("Image:", self.image_path_edit2)
        
        self.browse_image_btn2 = QPushButton("Browse...")
        self.browse_image_btn2.clicked.connect(self._browse_image2)
        image_layout.addWidget(self.browse_image_btn2)
        
        self.image_confidence_spin2 = QDoubleSpinBox()
        self.image_confidence_spin2.setRange(0.1, 1.0)
        self.image_confidence_spin2.setValue(0.9)
        self.image_confidence_spin2.setSingleStep(0.05)
        self.image_confidence_spin2.setDecimals(2)
        self.image_confidence_spin2.valueChanged.connect(self._update_step_from_ui)
        image_layout.addRow("Confidence:", self.image_confidence_spin2)
        
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 300)
        self.timeout_spin.setValue(30)
        self.timeout_spin.valueChanged.connect(self._update_step_from_ui)
        image_layout.addRow("Timeout (s):", self.timeout_spin)
        
        self.variable_edit = QLineEdit()
        self.variable_edit.setPlaceholderText("Variable name (optional)")
        self.variable_edit.textChanged.connect(self._update_step_from_ui)
        image_layout.addRow("Store in variable:", self.variable_edit)
        
        self.action_stack.addWidget(image_widget)
        
        # Screenshot action
        screenshot_widget = QWidget()
        screenshot_layout = QFormLayout()
        screenshot_widget.setLayout(screenshot_layout)
        
        self.filename_edit = QLineEdit()
        self.filename_edit.setPlaceholderText("Screenshot filename (optional)")
        self.filename_edit.textChanged.connect(self._update_step_from_ui)
        screenshot_layout.addRow("Filename:", self.filename_edit)
        
        # Region group
        self.region_checkbox = QCheckBox("Capture region")
        self.region_checkbox.stateChanged.connect(self._on_region_changed)
        screenshot_layout.addRow(self.region_checkbox)
        
        self.region_group = QGroupBox("Region")
        self.region_group.setVisible(False)
        region_layout = QFormLayout()
        self.region_group.setLayout(region_layout)
        
        self.region_x_spin = QSpinBox()
        self.region_x_spin.setRange(0, 9999)
        self.region_x_spin.valueChanged.connect(self._update_step_from_ui)
        region_layout.addRow("X:", self.region_x_spin)
        
        self.region_y_spin = QSpinBox()
        self.region_y_spin.setRange(0, 9999)
        self.region_y_spin.valueChanged.connect(self._update_step_from_ui)
        region_layout.addRow("Y:", self.region_y_spin)
        
        self.region_width_spin = QSpinBox()
        self.region_width_spin.setRange(1, 9999)
        self.region_width_spin.setValue(100)
        self.region_width_spin.valueChanged.connect(self._update_step_from_ui)
        region_layout.addRow("Width:", self.region_width_spin)
        
        self.region_height_spin = QSpinBox()
        self.region_height_spin.setRange(1, 9999)
        self.region_height_spin.setValue(100)
        self.region_height_spin.valueChanged.connect(self._update_step_from_ui)
        region_layout.addRow("Height:", self.region_height_spin)
        
        screenshot_layout.addWidget(self.region_group)
        
        self.variable_edit2 = QLineEdit()
        self.variable_edit2.setPlaceholderText("Variable name (optional)")
        self.variable_edit2.textChanged.connect(self._update_step_from_ui)
        screenshot_layout.addRow("Store in variable:", self.variable_edit2)
        
        self.action_stack.addWidget(screenshot_widget)
        
        # Common controls (delay, description)
        common_group = QGroupBox("Common Properties")
        common_layout = QFormLayout()
        common_group.setLayout(common_layout)
        
        self.delay_spin = QDoubleSpinBox()
        self.delay_spin.setRange(0.0, 60.0)
        self.delay_spin.setValue(0.5)
        self.delay_spin.setSingleStep(0.1)
        self.delay_spin.setDecimals(1)
        self.delay_spin.valueChanged.connect(self._update_step_from_ui)
        common_layout.addRow("Delay (s):", self.delay_spin)
        
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Step description (optional)")
        self.description_edit.textChanged.connect(self._update_step_from_ui)
        common_layout.addRow("Description:", self.description_edit)
        
        self.continue_on_error_checkbox = QCheckBox("Continue on error")
        self.continue_on_error_checkbox.stateChanged.connect(self._update_step_from_ui)
        common_layout.addRow(self.continue_on_error_checkbox)
        
        layout.addWidget(common_group)
        
        # Set initial state
        self._on_action_changed(self.action_combo.currentText())
    
    def _on_action_changed(self, action: str):
        """
        Handle change of action in the combo box.
        
        Args:
            action: The action that was selected
        """
        # Set the appropriate widget in the stack
        if action in ['click', 'right_click', 'double_click', 'move']:
            self.action_stack.setCurrentIndex(0)
        elif action == 'type':
            self.action_stack.setCurrentIndex(1)
        elif action == 'key_press':
            self.action_stack.setCurrentIndex(2)
        elif action == 'drag':
            self.action_stack.setCurrentIndex(3)
        elif action == 'scroll':
            self.action_stack.setCurrentIndex(4)
        elif action in ['find_image', 'wait_for_image']:
            self.action_stack.setCurrentIndex(5)
            self.timeout_spin.setVisible(action == 'wait_for_image')
            self.action_stack.widget(5).layout().labelForField(self.timeout_spin).setVisible(action == 'wait_for_image')
        elif action == 'screenshot':
            self.action_stack.setCurrentIndex(6)
        
        # Update the step data
        if self.step:
            self.step['action'] = action
            self._update_step_from_ui()
    
    def _on_use_image_changed(self, state: int):
        """
        Handle state change of the use image checkbox.
        
        Args:
            state: The new state of the checkbox
        """
        use_image = state == Qt.Checked
        self.image_path_edit.setVisible(use_image)
        self.browse_image_btn.setVisible(use_image)
        self.image_confidence_spin.setVisible(use_image)
        self.coords_group.setVisible(not use_image)
        self.action_stack.widget(0).layout().labelForField(self.image_path_edit).setVisible(use_image)
        self.action_stack.widget(0).layout().labelForField(self.image_confidence_spin).setVisible(use_image)
        
        # Update the step data
        self._update_step_from_ui()
    
    def _on_region_changed(self, state: int):
        """
        Handle state change of the region checkbox.
        
        Args:
            state: The new state of the checkbox
        """
        capture_region = state == Qt.Checked
        self.region_group.setVisible(capture_region)
        
        # Update the step data
        self._update_step_from_ui()
    
    def _browse_image(self):
        """Open a file dialog to select an image file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)"
        )
        if file_path:
            self.image_path_edit.setText(file_path)
    
    def _browse_image2(self):
        """Open a file dialog to select an image file for the find_image/wait_for_image actions."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)"
        )
        if file_path:
            self.image_path_edit2.setText(file_path)
    
    def _update_ui_from_step(self):
        """Update the UI with the current step data."""
        if not self.step:
            return
        
        # Set action
        action = self.step.get('action', '')
        self.action_combo.setCurrentText(action)
        
        # Set common properties
        self.delay_spin.setValue(self.step.get('delay', 0.5))
        self.description_edit.setText(self.step.get('description', ''))
        self.continue_on_error_checkbox.setChecked(self.step.get('continue_on_error', False))
        
        # Set action-specific properties
        if action in ['click', 'right_click', 'double_click', 'move']:
            # Set coordinates or image
            if 'image' in self.step:
                self.use_image_checkbox.setChecked(True)
                self.image_path_edit.setText(self.step['image'])
                self.image_confidence_spin.setValue(self.step.get('confidence', 0.9))
            else:
                self.use_image_checkbox.setChecked(False)
                self.x_spin.setValue(self.step.get('x', 0))
                self.y_spin.setValue(self.step.get('y', 0))
            
        elif action == 'type':
            self.text_edit.setText(self.step.get('text', ''))
            self.interval_spin.setValue(self.step.get('interval', 0.0))
            
        elif action == 'key_press':
            self.key_edit.setText(self.step.get('key', ''))
            
        elif action == 'drag':
            self.from_x_spin.setValue(self.step.get('x', 0))
            self.from_y_spin.setValue(self.step.get('y', 0))
            to_data = self.step.get('to', {})
            self.to_x_spin.setValue(to_data.get('x', 0))
            self.to_y_spin.setValue(to_data.get('y', 0))
            self.drag_duration_spin.setValue(self.step.get('duration', 0.5))
            
        elif action == 'scroll':
            self.clicks_spin.setValue(self.step.get('clicks', 0))
            
        elif action in ['find_image', 'wait_for_image']:
            self.image_path_edit2.setText(self.step.get('image', ''))
            self.image_confidence_spin2.setValue(self.step.get('confidence', 0.9))
            self.timeout_spin.setValue(self.step.get('timeout', 30))
            self.variable_edit.setText(self.step.get('variable', ''))
            
        elif action == 'screenshot':
            self.filename_edit.setText(self.step.get('filename', ''))
            region = self.step.get('region', None)
            if region:
                self.region_checkbox.setChecked(True)
                self.region_x_spin.setValue(region[0])
                self.region_y_spin.setValue(region[1])
                self.region_width_spin.setValue(region[2])
                self.region_height_spin.setValue(region[3])
            else:
                self.region_checkbox.setChecked(False)
            self.variable_edit2.setText(self.step.get('variable', ''))
    
    def _update_step_from_ui(self):
        """Update the step data from the UI and emit the step_changed signal."""
        if not self.step:
            return
        
        # Get action
        action = self.action_combo.currentText()
        self.step['action'] = action
        
        # Get common properties
        self.step['delay'] = self.delay_spin.value()
        self.step['description'] = self.description_edit.text()
        self.step['continue_on_error'] = self.continue_on_error_checkbox.isChecked()
        
        # Get action-specific properties
        if action in ['click', 'right_click', 'double_click', 'move']:
            # Get coordinates or image
            if self.use_image_checkbox.isChecked():
                self.step['image'] = self.image_path_edit.text()
                self.step['confidence'] = self.image_confidence_spin.value()
                # Remove coordinates if present
                if 'x' in self.step:
                    del self.step['x']
                if 'y' in self.step:
                    del self.step['y']
            else:
                self.step['x'] = self.x_spin.value()
                self.step['y'] = self.y_spin.value()
                # Remove image properties if present
                if 'image' in self.step:
                    del self.step['image']
                if 'confidence' in self.step:
                    del self.step['confidence']
            
        elif action == 'type':
            self.step['text'] = self.text_edit.text()
            self.step['interval'] = self.interval_spin.value()
            
        elif action == 'key_press':
            self.step['key'] = self.key_edit.text()
            
        elif action == 'drag':
            self.step['x'] = self.from_x_spin.value()
            self.step['y'] = self.from_y_spin.value()
            self.step['to'] = {
                'x': self.to_x_spin.value(),
                'y': self.to_y_spin.value()
            }
            self.step['duration'] = self.drag_duration_spin.value()
            
        elif action == 'scroll':
            self.step['clicks'] = self.clicks_spin.value()
            
        elif action in ['find_image', 'wait_for_image']:
            self.step['image'] = self.image_path_edit2.text()
            self.step['confidence'] = self.image_confidence_spin2.value()
            
            if action == 'wait_for_image':
                self.step['timeout'] = self.timeout_spin.value()
            elif 'timeout' in self.step:
                del self.step['timeout']
                
            variable = self.variable_edit.text().strip()
            if variable:
                self.step['variable'] = variable
            elif 'variable' in self.step:
                del self.step['variable']
                
        elif action == 'screenshot':
            filename = self.filename_edit.text().strip()
            if filename:
                self.step['filename'] = filename
            elif 'filename' in self.step:
                del self.step['filename']
                
            if self.region_checkbox.isChecked():
                self.step['region'] = [
                    self.region_x_spin.value(),
                    self.region_y_spin.value(),
                    self.region_width_spin.value(),
                    self.region_height_spin.value()
                ]
            elif 'region' in self.step:
                del self.step['region']
                
            variable = self.variable_edit2.text().strip()
            if variable:
                self.step['variable'] = variable
            elif 'variable' in self.step:
                del self.step['variable']
        
        # Emit the step_changed signal
        self.step_changed.emit(self.step)