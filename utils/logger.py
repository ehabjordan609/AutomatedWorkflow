"""
Logger configuration module for the Automation Tool application.
"""
import os
import sys
import logging
import time
from logging.handlers import RotatingFileHandler

def setup_logger():
    """
    Configure application-wide logging.
    
    Sets up:
    - Console logging for warnings and above
    - File logging for all messages, with rotation
    """
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)
    
    # Generate log filename with timestamp
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    log_file = os.path.join(logs_dir, f"autotool_{timestamp}.log")
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler (for warnings and above)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Create file handler (for all messages, with rotation)
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Log startup message
    root_logger.info(f"Logging initialized to {log_file}")
    
    return root_logger

def get_logger(name):
    """
    Get a logger for a specific module.
    
    Args:
        name: Name of the module (typically __name__)
        
    Returns:
        Logger instance for the module
    """
    return logging.getLogger(name)
