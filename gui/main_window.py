"""
Main window of the Automation Tool application.
"""
import sys
import os
import logging
from typing import Optional, List, Dict, Any
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QLabel, QStatusBar, QAction, QToolBar, QFileDialog,
    QMessageBox, QSplitter, QListWidget, QListWidgetItem, QMenu, QDialog
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QFont

from gui.script_editor import ScriptEditorWidget
from gui.recorder import RecorderWidget
from gui.player import PlayerWidget
from script_manager import ScriptManager
from automation_engine import AutomationEngine

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """
    Main window of the Automation Tool application.
    """
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        self.script_manager = ScriptManager()
        self.automation_engine = AutomationEngine()
        
        self.setWindowTitle("Automation Tool")
        self.setMinimumSize(1000, 700)
        
        self._create_ui()
        self._create_menus()
        self._create_toolbar()
        self._create_status_bar()
        
        # Connect signals and slots
        self._connect_signals()
        
        logger.info("Main window initialized")
    
    def _create_ui(self):
        """Create the main UI components."""
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Main splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)
        
        # Left panel for script list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Script list
        script_list_label = QLabel("Available Scripts")
        script_list_label.setStyleSheet("font-weight: bold;")
        left_layout.addWidget(script_list_label)
        
        self.script_list = QListWidget()
        self.script_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.script_list.customContextMenuRequested.connect(self._show_script_context_menu)
        left_layout.addWidget(self.script_list)
        
        # New script button
        new_script_button = QPushButton("New Script")
        new_script_button.clicked.connect(self._create_new_script)
        left_layout.addWidget(new_script_button)
        
        # Add left panel to splitter
        self.main_splitter.addWidget(left_panel)
        
        # Right panel with tabs
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Script editor tab
        self.script_editor = ScriptEditorWidget(self.script_manager)
        self.tab_widget.addTab(self.script_editor, "Script Editor")
        
        # Recorder tab
        self.recorder = RecorderWidget(self.script_manager)
        self.tab_widget.addTab(self.recorder, "Recorder")
        
        # Player tab
        self.player = PlayerWidget(self.script_manager, self.automation_engine)
        self.tab_widget.addTab(self.player, "Player")
        
        right_layout.addWidget(self.tab_widget)
        
        # Add right panel to splitter
        self.main_splitter.addWidget(right_panel)
        
        # Set splitter sizes
        self.main_splitter.setSizes([200, 800])
        
        # Populate script list
        self._refresh_script_list()
    
    def _create_menus(self):
        """Create the application menus."""
        # File menu
        file_menu = self.menuBar().addMenu("&File")
        
        new_action = QAction("&New Script", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._create_new_script)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open Script", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_script)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save Script", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_script)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save Script &As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self._save_script_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = self.menuBar().addMenu("&Edit")
        
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        preferences_action = QAction("&Preferences", self)
        edit_menu.addAction(preferences_action)
        
        # Run menu
        run_menu = self.menuBar().addMenu("&Run")
        
        run_action = QAction("&Run Script", self)
        run_action.setShortcut("F5")
        run_action.triggered.connect(self._run_script)
        run_menu.addAction(run_action)
        
        run_step_action = QAction("Run &Step by Step", self)
        run_step_action.setShortcut("F6")
        run_step_action.triggered.connect(self._run_script_step_by_step)
        run_menu.addAction(run_step_action)
        
        stop_action = QAction("&Stop Execution", self)
        stop_action.setShortcut("F8")
        stop_action.triggered.connect(self._stop_script)
        run_menu.addAction(stop_action)
        
        # Help menu
        help_menu = self.menuBar().addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)
    
    def _create_toolbar(self):
        """Create the application toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # New script action
        new_action = QAction("New", self)
        new_action.triggered.connect(self._create_new_script)
        toolbar.addAction(new_action)
        
        # Open script action
        open_action = QAction("Open", self)
        open_action.triggered.connect(self._open_script)
        toolbar.addAction(open_action)
        
        # Save script action
        save_action = QAction("Save", self)
        save_action.triggered.connect(self._save_script)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # Run script action
        run_action = QAction("Run", self)
        run_action.triggered.connect(self._run_script)
        toolbar.addAction(run_action)
        
        # Step-by-step action
        step_action = QAction("Step", self)
        step_action.triggered.connect(self._run_script_step_by_step)
        toolbar.addAction(step_action)
        
        # Stop action
        stop_action = QAction("Stop", self)
        stop_action.triggered.connect(self._stop_script)
        toolbar.addAction(stop_action)
    
    def _create_status_bar(self):
        """Create the application status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label, 1)
    
    def _connect_signals(self):
        """Connect signals and slots."""
        # Script list selection
        self.script_list.itemDoubleClicked.connect(self._on_script_double_clicked)
        
        # Tab widget signals
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        
        # Script editor signals
        self.script_editor.script_modified.connect(self._on_script_modified)
        
        # Player signals
        self.player.status_changed.connect(self._on_player_status_changed)
    
    def _refresh_script_list(self):
        """Refresh the list of available scripts."""
        self.script_list.clear()
        
        scripts = self.script_manager.get_scripts_list()
        for script_path in scripts:
            info = self.script_manager.get_script_info(script_path)
            if info:
                item = QListWidgetItem(info["name"])
                item.setData(Qt.UserRole, script_path)
                item.setToolTip(f"{info['description']}\n{info['steps_count']} steps")
                self.script_list.addItem(item)
    
    def _create_new_script(self):
        """Create a new script."""
        # Get script name
        from PyQt5.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(self, "New Script", "Enter script name:")
        if ok and name:
            self.script_manager.create_new_script(name)
            self.script_editor.update_ui()
            
            # Switch to editor tab
            self.tab_widget.setCurrentWidget(self.script_editor)
            
            # Update UI state
            self._update_window_title()
            self.status_label.setText(f"Created new script: {name}")
            
            # Save the script to file
            self._save_script()
            
            # Refresh script list
            self._refresh_script_list()
    
    def _open_script(self, file_path=None):
        """Open a script file."""
        if not file_path:
            # Show file dialog
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open Script", 
                self.script_manager.scripts_dir,
                "Script Files (*.json);;All Files (*)"
            )
        
        if file_path:
            script = self.script_manager.load_script(file_path)
            if script:
                self.script_editor.update_ui()
                self.player.update_ui()
                
                # Switch to editor tab
                self.tab_widget.setCurrentWidget(self.script_editor)
                
                # Update UI state
                self._update_window_title()
                self.status_label.setText(f"Opened script: {script['name']}")
            else:
                QMessageBox.critical(self, "Error", f"Failed to load script from {file_path}")
    
    def _save_script(self):
        """Save the current script."""
        if self.script_manager.current_script:
            if self.script_manager.current_script_path:
                # Save to existing path
                if self.script_manager.save_script():
                    self.status_label.setText("Script saved")
                else:
                    QMessageBox.critical(self, "Error", "Failed to save script")
            else:
                # No path yet, use save as
                self._save_script_as()
    
    def _save_script_as(self):
        """Save the current script with a new name."""
        if self.script_manager.current_script:
            # Show file dialog
            default_name = f"{self.script_manager.current_script['name'].replace(' ', '_').lower()}.json"
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Script As", 
                os.path.join(self.script_manager.scripts_dir, default_name),
                "Script Files (*.json);;All Files (*)"
            )
            
            if file_path:
                if self.script_manager.save_script(file_path):
                    self.status_label.setText(f"Script saved as: {file_path}")
                    self._update_window_title()
                    self._refresh_script_list()
                else:
                    QMessageBox.critical(self, "Error", "Failed to save script")
    
    def _run_script(self):
        """Run the current script."""
        if not self.script_manager.current_script:
            QMessageBox.warning(self, "Warning", "No script loaded")
            return
        
        # Switch to player tab
        self.tab_widget.setCurrentWidget(self.player)
        
        # Run the script
        self.player.run_script()
    
    def _run_script_step_by_step(self):
        """Run the current script step by step."""
        if not self.script_manager.current_script:
            QMessageBox.warning(self, "Warning", "No script loaded")
            return
        
        # Switch to player tab
        self.tab_widget.setCurrentWidget(self.player)
        
        # Run the script step by step
        self.player.run_script(step_by_step=True)
    
    def _stop_script(self):
        """Stop script execution."""
        self.player.stop_script()
    
    def _on_script_double_clicked(self, item):
        """Handle double-click on script list item."""
        script_path = item.data(Qt.UserRole)
        self._open_script(script_path)
    
    def _on_tab_changed(self, index):
        """Handle tab widget selection change."""
        # Update UI state based on selected tab
        selected_widget = self.tab_widget.widget(index)
        
        if selected_widget == self.script_editor:
            self.script_editor.update_ui()
        elif selected_widget == self.player:
            self.player.update_ui()
        elif selected_widget == self.recorder:
            self.recorder.update_ui()
    
    def _on_script_modified(self):
        """Handle script modification event."""
        # Update window title to indicate unsaved changes
        self._update_window_title(modified=True)
    
    def _on_player_status_changed(self, status):
        """Handle player status change."""
        self.status_label.setText(status)
    
    def _update_window_title(self, modified=False):
        """Update the window title with current script info."""
        if self.script_manager.current_script:
            script_name = self.script_manager.current_script['name']
            title = f"Automation Tool - {script_name}"
            
            if modified:
                title += " *"
                
            if self.script_manager.current_script_path:
                title += f" ({self.script_manager.current_script_path})"
                
            self.setWindowTitle(title)
        else:
            self.setWindowTitle("Automation Tool")
    
    def _show_script_context_menu(self, position):
        """Show context menu for script list items."""
        item = self.script_list.itemAt(position)
        if not item:
            return
        
        context_menu = QMenu(self)
        
        open_action = context_menu.addAction("Open")
        rename_action = context_menu.addAction("Rename")
        duplicate_action = context_menu.addAction("Duplicate")
        delete_action = context_menu.addAction("Delete")
        
        action = context_menu.exec_(self.script_list.mapToGlobal(position))
        
        if action == open_action:
            self._open_script(item.data(Qt.UserRole))
        elif action == rename_action:
            self._rename_script(item)
        elif action == duplicate_action:
            self._duplicate_script(item)
        elif action == delete_action:
            self._delete_script(item)
    
    def _rename_script(self, item):
        """Rename a script."""
        from PyQt5.QtWidgets import QInputDialog
        
        script_path = item.data(Qt.UserRole)
        info = self.script_manager.get_script_info(script_path)
        
        if info:
            new_name, ok = QInputDialog.getText(
                self, "Rename Script", 
                "Enter new name:", 
                text=info["name"]
            )
            
            if ok and new_name:
                # Load the script
                script = self.script_manager.load_script(script_path)
                if script:
                    # Update name
                    script["name"] = new_name
                    
                    # Save back to same file
                    if self.script_manager.save_script(script_path):
                        self.status_label.setText(f"Renamed script to: {new_name}")
                        self._refresh_script_list()
                    else:
                        QMessageBox.critical(self, "Error", "Failed to rename script")
    
    def _duplicate_script(self, item):
        """Duplicate a script."""
        script_path = item.data(Qt.UserRole)
        info = self.script_manager.get_script_info(script_path)
        
        if info:
            # Load the script
            script = self.script_manager.load_script(script_path)
            if script:
                # Update name to indicate copy
                script["name"] = f"{script['name']} (Copy)"
                
                # Reset the path to force "save as"
                self.script_manager.current_script_path = None
                
                # Save with new name
                self._save_script_as()
    
    def _delete_script(self, item):
        """Delete a script."""
        script_path = item.data(Qt.UserRole)
        info = self.script_manager.get_script_info(script_path)
        
        if info:
            # Confirm deletion
            response = QMessageBox.question(
                self, "Confirm Deletion",
                f"Are you sure you want to delete the script '{info['name']}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if response == QMessageBox.Yes:
                try:
                    # Delete the file
                    os.remove(script_path)
                    self.status_label.setText(f"Deleted script: {info['name']}")
                    
                    # If this was the current script, clear it
                    if (self.script_manager.current_script_path and 
                        self.script_manager.current_script_path == script_path):
                        self.script_manager.current_script = None
                        self.script_manager.current_script_path = None
                        self.script_editor.update_ui()
                        self.player.update_ui()
                        self._update_window_title()
                    
                    # Refresh the list
                    self._refresh_script_list()
                    
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to delete script: {str(e)}")
    
    def _show_about_dialog(self):
        """Show the about dialog."""
        QMessageBox.about(
            self, "About Automation Tool",
            "Automation Tool\n\n"
            "A desktop application for automating user actions including "
            "screen interactions, web browsing, and CAPTCHA handling.\n\n"
            "Version: 1.0"
        )
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Check for unsaved changes
        if self.script_manager.current_script:
            response = QMessageBox.question(
                self, "Confirm Exit",
                "Do you want to save changes before exiting?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if response == QMessageBox.Save:
                self._save_script()
                event.accept()
            elif response == QMessageBox.Cancel:
                event.ignore()
            else:  # Discard
                event.accept()
        else:
            event.accept()
