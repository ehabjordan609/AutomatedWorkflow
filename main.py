#!/usr/bin/env python3
"""
Main entry point for the Automation Tool application.
"""
import sys
import os
import logging
from PyQt5.QtWidgets import QApplication

from utils.logger import setup_logger
from gui.main_window import MainWindow

def main():
    """Main function to start the application."""
    # Set up logging
    setup_logger()
    logger = logging.getLogger(__name__)
    
    # Check if the scripts directory exists
    if not os.path.exists("scripts"):
        os.makedirs("scripts")
        logger.info("Created scripts directory")
    
    # Create QApplication instance
    app = QApplication(sys.argv)
    app.setApplicationName("Automation Tool")
    app.setApplicationVersion("1.0.0")
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Start the event loop
    logger.info("Application started")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()