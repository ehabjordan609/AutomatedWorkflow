#!/usr/bin/env python3
"""
Main window module for the Automation Tool GUI.
"""
import os
import sys
import time
import logging
from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QAction, QFileDialog, QMessageBox, 
    QApplication, QLabel, QStatusBar, QToolBar, QDockWidget
)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QIcon, QPixmap

from gui.script_editor import ScriptEditorWidget
from gui.recorder import RecorderWidget
from gui.player import PlayerWidget
from automation_engine import AutomationEngine
from script_manager import ScriptManager

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main window of the Automation Tool GUI application."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        # Initialize components
        self.script_manager = ScriptManager()
        self.automation_engine = AutomationEngine()
        
        # Set up UI
        self._setup_ui()
        self._create_actions()
        self._create_menus()
        self._create_toolbars()
        self._create_status_bar()
        self._connect_signals()
        
        # Load settings
        self._load_settings()
        
        logger.info("Main window initialized")
    
    def _setup_ui(self):
        """Set up the user interface elements."""
        # Set window properties
        self.setWindowTitle("Automation Tool")
        self.setMinimumSize(800, 600)
        
        # Create central tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Create tab contents
        self.script_editor = ScriptEditorWidget(self.script_manager, self.automation_engine)
        self.recorder = RecorderWidget(self.script_manager, self.automation_engine)
        self.player = PlayerWidget(self.script_manager, self.automation_engine)
        
        # Add tabs
        self.tabs.addTab(self.script_editor, "Script Editor")
        self.tabs.addTab(self.recorder, "Recorder")
        self.tabs.addTab(self.player, "Player")
        
        # Set icons if available
        try:
            if os.path.exists("icons/script.png"):
                self.tabs.setTabIcon(0, QIcon("icons/script.png"))
            if os.path.exists("icons/record.png"):
                self.tabs.setTabIcon(1, QIcon("icons/record.png"))
            if os.path.exists("icons/play.png"):
                self.tabs.setTabIcon(2, QIcon("icons/play.png"))
        except Exception as e:
            logger.warning(f"Could not load tab icons: {str(e)}")
    
    def _create_actions(self):
        """Create all actions for the application."""
        # File actions
        self.new_action = QAction("New Script", self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.setStatusTip("Create a new script")
        self.new_action.triggered.connect(self._new_script)
        
        self.open_action = QAction("Open Script", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.setStatusTip("Open an existing script")
        self.open_action.triggered.connect(self._open_script)
        
        self.save_action = QAction("Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.setStatusTip("Save the current script")
        self.save_action.triggered.connect(self._save_script)
        
        self.save_as_action = QAction("Save As...", self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.setStatusTip("Save the current script with a new name")
        self.save_as_action.triggered.connect(self._save_script_as)
        
        self.exit_action = QAction("Exit", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.setStatusTip("Exit the application")
        self.exit_action.triggered.connect(self._exit_application)
        
        # Edit actions
        self.preferences_action = QAction("Preferences", self)
        self.preferences_action.setStatusTip("Configure application preferences")
        self.preferences_action.triggered.connect(self._show_preferences)
        
        # Script actions
        self.validate_action = QAction("Validate Script", self)
        self.validate_action.setStatusTip("Validate the current script")
        self.validate_action.triggered.connect(self._validate_script)
        
        # Help actions
        self.about_action = QAction("About", self)
        self.about_action.setStatusTip("Show information about the application")
        self.about_action.triggered.connect(self._show_about)
        
        self.help_action = QAction("Help", self)
        self.help_action.setShortcut("F1")
        self.help_action.setStatusTip("Show help documentation")
        self.help_action.triggered.connect(self._show_help)
    
    def _create_menus(self):
        """Create all menus for the application."""
        # File menu
        self.file_menu = self.menuBar().addMenu("&File")
        self.file_menu.addAction(self.new_action)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.save_as_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)
        
        # Edit menu
        self.edit_menu = self.menuBar().addMenu("&Edit")
        self.edit_menu.addAction(self.preferences_action)
        
        # Script menu
        self.script_menu = self.menuBar().addMenu("&Script")
        self.script_menu.addAction(self.validate_action)
        
        # Help menu
        self.help_menu = self.menuBar().addMenu("&Help")
        self.help_menu.addAction(self.help_action)
        self.help_menu.addSeparator()
        self.help_menu.addAction(self.about_action)
    
    def _create_toolbars(self):
        """Create all toolbars for the application."""
        # Main toolbar
        self.main_toolbar = QToolBar("Main Toolbar")
        self.main_toolbar.setMovable(False)
        self.main_toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.main_toolbar)
        
        # Add actions to main toolbar
        self.main_toolbar.addAction(self.new_action)
        self.main_toolbar.addAction(self.open_action)
        self.main_toolbar.addAction(self.save_action)
        self.main_toolbar.addSeparator()
        
        # Add specific actions based on current tab
        self.tabs.currentChanged.connect(self._update_toolbar)
        self._update_toolbar(0)  # Initial update
    
    def _update_toolbar(self, tab_index):
        """Update the toolbar based on the current tab."""
        # Clear existing actions after the separator
        actions = self.main_toolbar.actions()
        separator_found = False
        for action in actions[:]:
            if separator_found:
                self.main_toolbar.removeAction(action)
            elif action.isSeparator():
                separator_found = True
        
        # Add tab-specific actions
        if tab_index == 0:  # Script Editor
            pass  # No specific toolbar actions for Script Editor yet
        elif tab_index == 1:  # Recorder
            self.main_toolbar.addAction(self.recorder.start_action)
            self.main_toolbar.addAction(self.recorder.stop_action)
            self.main_toolbar.addAction(self.recorder.save_action)
        elif tab_index == 2:  # Player
            self.main_toolbar.addAction(self.player.run_action)
            self.main_toolbar.addAction(self.player.pause_action)
            self.main_toolbar.addAction(self.player.stop_action)
            self.main_toolbar.addAction(self.player.step_action)
    
    def _create_status_bar(self):
        """Create the status bar for the application."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add permanent widgets to status bar
        self.status_label = QLabel("Ready")
        self.status_bar.addPermanentWidget(self.status_label)
    
    def _connect_signals(self):
        """Connect signals from child widgets to main window slots."""
        # Script editor signals
        self.script_editor.script_changed.connect(self._handle_script_changed)
        
        # Player signals
        self.player.execution_started.connect(lambda: self.status_label.setText("Running script..."))
        self.player.execution_completed.connect(lambda success: self.status_label.setText("Script execution completed" if success else "Script execution failed"))
        self.player.status_changed.connect(lambda msg: self.status_label.setText(msg))
    
    def _load_settings(self):
        """Load application settings."""
        # This would typically load from a settings file
        # For now, just set default values
        self.resize(1024, 768)
        self.move(100, 100)
    
    def _new_script(self):
        """Create a new script."""
        # Check if there are unsaved changes
        if self._check_unsaved_changes():
            name, ok = QInputDialog.getText(self, "New Script", "Enter script name:")
            if ok and name:
                self.script_manager.create_new_script(name)
                self.script_editor.update_script_view()
                self.status_label.setText(f"Created new script: {name}")
    
    def _open_script(self):
        """Open an existing script."""
        # Check if there are unsaved changes
        if self._check_unsaved_changes():
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open Script", self.script_manager.scripts_dir, 
                "JSON Files (*.json);;All Files (*)"
            )
            if file_path:
                script = self.script_manager.load_script(file_path)
                if script:
                    self.script_editor.update_script_view()
                    self.status_label.setText(f"Opened script: {file_path}")
                else:
                    QMessageBox.warning(self, "Error", f"Failed to load script: {file_path}")
    
    def _save_script(self):
        """Save the current script."""
        if not self.script_manager.current_script:
            QMessageBox.warning(self, "Error", "No script loaded")
            return
        
        if self.script_manager.current_script_path:
            # Save to existing path
            success = self.script_manager.save_script()
            if success:
                self.status_label.setText(f"Saved script to: {self.script_manager.current_script_path}")
            else:
                QMessageBox.warning(self, "Error", "Failed to save script")
        else:
            # No path yet, use save as
            self._save_script_as()
    
    def _save_script_as(self):
        """Save the current script with a new name."""
        if not self.script_manager.current_script:
            QMessageBox.warning(self, "Error", "No script loaded")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Script As", self.script_manager.scripts_dir, 
            "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            success = self.script_manager.save_script(file_path)
            if success:
                self.status_label.setText(f"Saved script to: {file_path}")
            else:
                QMessageBox.warning(self, "Error", "Failed to save script")
    
    def _validate_script(self):
        """Validate the current script."""
        if not self.script_manager.current_script:
            QMessageBox.warning(self, "Error", "No script loaded")
            return
        
        errors = self.script_manager.validate_script()
        if errors:
            error_text = "\n".join(errors)
            QMessageBox.warning(self, "Validation Errors", f"The script has the following errors:\n\n{error_text}")
        else:
            QMessageBox.information(self, "Validation", "The script is valid.")
    
    def _show_preferences(self):
        """Show the preferences dialog."""
        # This would be implemented with a PreferencesDialog class
        QMessageBox.information(self, "Preferences", "Preferences dialog would be shown here.")
    
    def _show_about(self):
        """Show the about dialog."""
        QMessageBox.about(self, "About Automation Tool", 
                         "Automation Tool\n\n"
                         "Version 1.0\n\n"
                         "A desktop automation tool for automating repetitive tasks.")
    
    def _show_help(self):
        """Show the help documentation."""
        # This would open a help window or a web browser with documentation
        QMessageBox.information(self, "Help", "Help documentation would be shown here.")
    
    def _exit_application(self):
        """Exit the application."""
        # Check if there are unsaved changes
        if self._check_unsaved_changes():
            QApplication.quit()
    
    def _check_unsaved_changes(self):
        """
        Check if there are unsaved changes and ask the user what to do.
        
        Returns:
            bool: True if it's okay to proceed, False to cancel
        """
        # This is a simplified implementation
        # In a real app, would track modifications and only prompt if needed
        if self.script_manager.current_script and self.script_editor.has_unsaved_changes:
            result = QMessageBox.question(
                self, "Unsaved Changes", 
                "There are unsaved changes. Do you want to save them?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if result == QMessageBox.Save:
                return self._save_script()
            elif result == QMessageBox.Cancel:
                return False
        
        return True
    
    def _handle_script_changed(self):
        """Handle script content changes."""
        # Update the window title to indicate unsaved changes
        if self.script_manager.current_script:
            script_name = self.script_manager.current_script.get('name', 'Untitled')
            self.setWindowTitle(f"Automation Tool - {script_name} *")
    
    def closeEvent(self, event):
        """Handle the window close event."""
        if self._check_unsaved_changes():
            event.accept()
        else:
            event.ignore()