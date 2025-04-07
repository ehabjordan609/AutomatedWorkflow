#!/usr/bin/env python3
"""
Main entry point for the Automation Tool application.
"""
import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from gui.main_window import MainWindow
from utils.logger import setup_logger

def main():
    """Main function to start the application."""
    # Set up logging
    setup_logger()
    logger = logging.getLogger(__name__)
    logger.info("Starting Automation Tool application")

    # Create Qt application
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    app.setApplicationName("Automation Tool")
    app.setOrganizationName("AutoTool")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
