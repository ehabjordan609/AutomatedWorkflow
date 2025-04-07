#!/usr/bin/env python3
"""
Main entry point for the Automation Tool application.
This script attempts to run the GUI version if possible, 
and automatically falls back to the console version if not.
"""
import sys
import os
import logging

# Set up fallback mechanism for GUI
try:
    from PyQt5.QtWidgets import QApplication
    from utils.logger import setup_logger
    from gui.main_window import MainWindow
    HAS_GUI = True
except ImportError:
    HAS_GUI = False
    import simple_app

def main():
    """Main function to start the application."""
    # Set up logging
    if HAS_GUI:
        setup_logger()
    logger = logging.getLogger(__name__)
    
    # Check if the scripts directory exists
    if not os.path.exists("scripts"):
        os.makedirs("scripts")
        logger.info("Created scripts directory")
    
    if HAS_GUI:
        try:
            # Create QApplication instance
            app = QApplication(sys.argv)
            app.setApplicationName("Automation Tool")
            app.setApplicationVersion("1.0.0")
            
            # Create and show the main window
            window = MainWindow()
            window.show()
            
            # Start the event loop
            logger.info("GUI application started")
            sys.exit(app.exec_())
        except Exception as e:
            logger.error(f"Error starting GUI: {e}")
            logger.info("Falling back to console application")
            simple_app.main()
    else:
        # Run the console application if GUI is not available
        logger.info("GUI not available, running console application")
        simple_app.main()

if __name__ == "__main__":
    main()