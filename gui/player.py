"""
Player widget for executing automation scripts.
"""
import logging
import time
import threading
from typing import Dict, List, Any, Optional, Tuple
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QComboBox, QLineEdit, QFormLayout, QGroupBox, QCheckBox,
    QSpinBox, QMessageBox, QHeaderView, QProgressBar, QTextEdit, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QThread, QMutex, QTimer
from PyQt5.QtGui import QIcon, QFont, QColor, QTextCursor

from script_manager import ScriptManager
from automation_engine import AutomationEngine

logger = logging.getLogger(__name__)

class WorkerThread(QThread):
    """
    Worker thread for executing automation scripts in the background.
    """
    # Signals for thread events
    step_started = pyqtSignal(int, dict)
    step_completed = pyqtSignal(int, bool)
    script_completed = pyqtSignal(bool)
    log_message = pyqtSignal(str)
    
    def __init__(self, engine: AutomationEngine, step_by_step: bool = False):
        """Initialize the worker thread."""
        super().__init__()
        self.engine = engine
        self.step_by_step = step_by_step
        self.mutex = QMutex()
        self.paused = False
        self.stopped = False
    
    def run(self):
        """Run method for the thread."""
        self.log_message.emit("Starting script execution")
        
        if not self.engine.current_script:
            self.log_message.emit("No script loaded")
            self.script_completed.emit(False)
            return
        
        steps = self.engine.current_script.get('steps', [])
        total_steps = len(steps)
        
        try:
            self.engine.is_running = True
            self.engine.is_paused = False
            self.engine.step_by_step = self.step_by_step
            self.engine.current_step = 0
            
            while self.engine.current_step < total_steps and self.engine.is_running:
                # Check if thread should stop
                self.mutex.lock()
                if self.stopped:
                    self.mutex.unlock()
                    break
                    
                # Check if thread should pause
                if self.paused or self.engine.is_paused:
                    self.mutex.unlock()
                    time.sleep(0.1)
                    continue
                self.mutex.unlock()
                
                step = steps[self.engine.current_step]
                
                # Emit signal before step execution
                self.step_started.emit(self.engine.current_step, step)
                
                # Execute the step
                success = self.engine._execute_step(step)
                
                # Emit signal after step execution
                self.step_completed.emit(self.engine.current_step, success)
                
                if not success:
                    self.log_message.emit(f"Step {self.engine.current_step + 1} failed")
                    self.script_completed.emit(False)
                    return
                
                self.engine.current_step += 1
                
                # Wait if in step-by-step mode
                if self.step_by_step and self.engine.current_step < total_steps:
                    self.engine.is_paused = True
                    self.paused = True
            
            if self.engine.current_step >= total_steps:
                self.log_message.emit("Script executed successfully")
                self.script_completed.emit(True)
            else:
                self.log_message.emit("Script execution stopped")
                self.script_completed.emit(False)
                
        except Exception as e:
            self.log_message.emit(f"Script execution failed: {str(e)}")
            self.script_completed.emit(False)
        finally:
            self.engine.is_running = False
            self.engine.is_paused = False
    
    def pause(self):
        """Pause the worker thread."""
        self.mutex.lock()
        self.paused = True
        self.mutex.unlock()
    
    def resume(self):
        """Resume the worker thread."""
        self.mutex.lock()
        self.paused = False
        self.engine.is_paused = False
        self.mutex.unlock()
    
    def stop(self):
        """Stop the worker thread."""
        self.mutex.lock()
        self.stopped = True
        self.mutex.unlock()
        self.engine.stop()


class PlayerWidget(QWidget):
    """
    Widget for executing automation scripts.
    """
    
    # Signals emitted during execution
    status_changed = pyqtSignal(str)
    execution_started = pyqtSignal()
    execution_paused = pyqtSignal()
    execution_resumed = pyqtSignal()
    execution_stopped = pyqtSignal()
    execution_completed = pyqtSignal(bool)
    step_started = pyqtSignal(int, dict)
    step_completed = pyqtSignal(int, bool)
    
    def __init__(self, script_manager: ScriptManager, automation_engine: AutomationEngine, parent=None):
        """Initialize the player widget."""
        super().__init__(parent)
        self.script_manager = script_manager
        self.automation_engine = automation_engine
        
        # Execution state
        self.worker_thread = None
        self.is_running = False
        self.is_paused = False
        self.step_by_step = False
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the player widget UI."""
        layout = QVBoxLayout(self)
        
        # Script info section
        info_layout = QHBoxLayout()
        
        self.script_name_label = QLabel("No script loaded")
        self.script_name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        info_layout.addWidget(self.script_name_label)
        
        info_layout.addStretch()
        
        self.step_count_label = QLabel("Steps: 0/0")
        info_layout.addWidget(self.step_count_label)
        
        layout.addLayout(info_layout)
        
        # Main splitter for steps and log
        splitter = QSplitter(Qt.Vertical)
        
        # Steps display
        steps_group = QGroupBox("Script Steps")
        steps_layout = QVBoxLayout(steps_group)
        
        self.steps_table = QTableWidget()
        self.steps_table.setColumnCount(5)
        self.steps_table.setHorizontalHeaderLabels(["#", "Type", "Action", "Details", "Status"])
        self.steps_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.steps_table.setSelectionMode(QTableWidget.SingleSelection)
        
        # Set column widths
        self.steps_table.horizontalHeader().setStretchLastSection(True)
        self.steps_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.steps_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.steps_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        steps_layout.addWidget(self.steps_table)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v/%m steps completed (%p%)")
        steps_layout.addWidget(self.progress_bar)
        
        splitter.addWidget(steps_group)
        
        # Log display
        log_group = QGroupBox("Execution Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setLineWrapMode(QTextEdit.NoWrap)
        self.log_text.setStyleSheet("font-family: monospace; font-size: 10pt;")
        log_layout.addWidget(self.log_text)
        
        splitter.addWidget(log_group)
        splitter.setSizes([200, 100])  # Initial sizes
        
        layout.addWidget(splitter, 1)  # Give splitter most of the space
        
        # Controls
        controls_layout = QHBoxLayout()
        
        # Playback mode
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Normal", "Step by Step"])
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        controls_layout.addWidget(QLabel("Playback mode:"))
        controls_layout.addWidget(self.mode_combo)
        
        controls_layout.addStretch()
        
        # Play button
        self.play_button = QPushButton("Run")
        self.play_button.setIcon(QIcon.fromTheme("media-playback-start"))
        self.play_button.clicked.connect(self._on_play_clicked)
        controls_layout.addWidget(self.play_button)
        
        # Pause button
        self.pause_button = QPushButton("Pause")
        self.pause_button.setIcon(QIcon.fromTheme("media-playback-pause"))
        self.pause_button.clicked.connect(self._on_pause_clicked)
        self.pause_button.setEnabled(False)
        controls_layout.addWidget(self.pause_button)
        
        # Stop button
        self.stop_button = QPushButton("Stop")
        self.stop_button.setIcon(QIcon.fromTheme("media-playback-stop"))
        self.stop_button.clicked.connect(self._on_stop_clicked)
        self.stop_button.setEnabled(False)
        controls_layout.addWidget(self.stop_button)
        
        # Next step button (for step-by-step mode)
        self.next_button = QPushButton("Next Step")
        self.next_button.setIcon(QIcon.fromTheme("media-skip-forward"))
        self.next_button.clicked.connect(self._on_next_clicked)
        self.next_button.setEnabled(False)
        controls_layout.addWidget(self.next_button)
        
        layout.addLayout(controls_layout)
    
    def update_ui(self):
        """Update the UI with current script data."""
        # Update script info
        if self.script_manager.current_script:
            script = self.script_manager.current_script
            self.script_name_label.setText(script.get("name", "Unnamed Script"))
            steps_count = len(script.get("steps", []))
            self.step_count_label.setText(f"Steps: 0/{steps_count}")
            
            # Configure progress bar
            self.progress_bar.setRange(0, steps_count)
            self.progress_bar.setValue(0)
            
            # Update steps table
            self._update_steps_table()
            
            # Enable/disable controls
            self.play_button.setEnabled(True)
        else:
            # No script loaded
            self.script_name_label.setText("No script loaded")
            self.step_count_label.setText("Steps: 0/0")
            self.progress_bar.setRange(0, 1)
            self.progress_bar.setValue(0)
            self.steps_table.setRowCount(0)
            
            # Disable controls
            self.play_button.setEnabled(False)
            self.pause_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.next_button.setEnabled(False)
    
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
            
            # Status (initially empty)
            status_item = QTableWidgetItem("")
            status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
            self.steps_table.setItem(i, 4, status_item)
        
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
    
    def run_script(self, step_by_step: bool = False):
        """
        Run the current script.
        
        Args:
            step_by_step: Whether to run in step-by-step mode
        """
        if self.is_running:
            return
        
        if not self.script_manager.current_script:
            QMessageBox.warning(self, "Warning", "No script loaded")
            return
        
        # Load script into automation engine
        script_path = self.script_manager.current_script_path
        if script_path and not self.automation_engine.load_script(script_path):
            QMessageBox.critical(self, "Error", "Failed to load script into automation engine")
            return
        
        # Update UI state
        self.is_running = True
        self.is_paused = False
        self.step_by_step = step_by_step
        
        # Reset step statuses
        self._reset_step_statuses()
        
        # Clear log
        self.log_text.clear()
        self._log_message("Starting script execution")
        
        # Configure progress bar
        steps_count = len(self.script_manager.current_script.get("steps", []))
        self.progress_bar.setRange(0, steps_count)
        self.progress_bar.setValue(0)
        
        # Update controls
        self.play_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        self.next_button.setEnabled(step_by_step)
        self.mode_combo.setEnabled(False)
        
        # Create and start worker thread
        self.worker_thread = WorkerThread(self.automation_engine, step_by_step)
        self.worker_thread.step_started.connect(self._on_step_started)
        self.worker_thread.step_completed.connect(self._on_step_completed)
        self.worker_thread.script_completed.connect(self._on_script_completed)
        self.worker_thread.log_message.connect(self._log_message)
        self.worker_thread.start()
        
        # Update status
        self.status_changed.emit("Script execution started")
    
    def stop_script(self):
        """Stop script execution."""
        if not self.is_running:
            return
        
        if self.worker_thread:
            self.worker_thread.stop()
            self.worker_thread.wait()  # Wait for thread to finish
            self.worker_thread = None
        
        self.is_running = False
        self.is_paused = False
        
        # Update controls
        self.play_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.mode_combo.setEnabled(True)
        
        # Update status
        self.status_changed.emit("Script execution stopped")
        self._log_message("Script execution stopped by user")
    
    def pause_script(self):
        """Pause script execution."""
        if not self.is_running or self.is_paused:
            return
        
        if self.worker_thread:
            self.worker_thread.pause()
        
        self.is_paused = True
        
        # Update controls
        self.pause_button.setText("Resume")
        self.next_button.setEnabled(self.step_by_step)
        
        # Update status
        self.status_changed.emit("Script execution paused")
        self._log_message("Script execution paused")
    
    def resume_script(self):
        """Resume script execution."""
        if not self.is_running or not self.is_paused:
            return
        
        if self.worker_thread:
            self.worker_thread.resume()
        
        self.is_paused = False
        
        # Update controls
        self.pause_button.setText("Pause")
        self.next_button.setEnabled(False)
        
        # Update status
        self.status_changed.emit("Script execution resumed")
        self._log_message("Script execution resumed")
    
    def next_step(self):
        """Execute the next step in step-by-step mode."""
        if not self.is_running or not self.is_paused or not self.step_by_step:
            return
        
        if self.worker_thread:
            self.worker_thread.resume()
            # It will automatically pause after the step
        
        # Update status
        self.status_changed.emit("Executing next step")
    
    def _on_play_clicked(self):
        """Handle play button click."""
        self.run_script(self.step_by_step)
    
    def _on_pause_clicked(self):
        """Handle pause/resume button click."""
        if self.is_paused:
            self.resume_script()
        else:
            self.pause_script()
    
    def _on_stop_clicked(self):
        """Handle stop button click."""
        self.stop_script()
    
    def _on_next_clicked(self):
        """Handle next step button click."""
        self.next_step()
    
    def _on_mode_changed(self, index):
        """Handle playback mode change."""
        self.step_by_step = (index == 1)  # Index 1 is "Step by Step"
    
    def _on_step_started(self, step_index, step):
        """Handle step started signal from worker thread."""
        # Update step status in table
        if 0 <= step_index < self.steps_table.rowCount():
            status_item = self.steps_table.item(step_index, 4)
            if status_item:
                status_item.setText("Running")
                status_item.setBackground(QColor("#FFF9C4"))  # Light yellow
            
            # Scroll to current step
            self.steps_table.scrollToItem(status_item)
            
            # Select the current row
            self.steps_table.selectRow(step_index)
        
        # Log message
        step_type = step.get("type", "").capitalize()
        if step_type.lower() == "wait":
            action_text = f"Wait {step.get('duration', 1)}s"
        else:
            action_text = step.get("action", "")
            if step_type.lower() == "captcha":
                action_text = step.get("captcha_type", "")
                
        self._log_message(f"Executing step {step_index + 1}: {step_type} - {action_text}")
    
    def _on_step_completed(self, step_index, success):
        """Handle step completed signal from worker thread."""
        # Update step status in table
        if 0 <= step_index < self.steps_table.rowCount():
            status_item = self.steps_table.item(step_index, 4)
            if status_item:
                if success:
                    status_item.setText("Success")
                    status_item.setBackground(QColor("#C8E6C9"))  # Light green
                else:
                    status_item.setText("Failed")
                    status_item.setBackground(QColor("#FFCDD2"))  # Light red
        
        # Update progress bar
        self.progress_bar.setValue(step_index + 1)
        
        # Update step count label
        total_steps = len(self.script_manager.current_script.get("steps", []))
        self.step_count_label.setText(f"Steps: {step_index + 1}/{total_steps}")
        
        # Log message
        if success:
            self._log_message(f"Step {step_index + 1} completed successfully")
        else:
            self._log_message(f"Step {step_index + 1} failed")
            
        # If in step-by-step mode and paused, enable next button
        if self.step_by_step and self.is_paused:
            self.next_button.setEnabled(True)
    
    def _on_script_completed(self, success):
        """Handle script completed signal from worker thread."""
        self.is_running = False
        self.is_paused = False
        
        # Update controls
        self.play_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.mode_combo.setEnabled(True)
        
        # Update status
        if success:
            status_message = "Script execution completed successfully"
            self.status_changed.emit(status_message)
            self._log_message(status_message)
        else:
            status_message = "Script execution failed"
            self.status_changed.emit(status_message)
            self._log_message(status_message)
    
    def _log_message(self, message):
        """Add a message to the log text edit."""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        self.log_text.append(log_entry)
        
        # Scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)
    
    def _reset_step_statuses(self):
        """Reset all step statuses in the table."""
        for i in range(self.steps_table.rowCount()):
            status_item = self.steps_table.item(i, 4)
            if status_item:
                status_item.setText("")
                status_item.setBackground(QColor(0, 0, 0, 0))  # Transparent
