#!/usr/bin/env python3
"""
Logging utilities for the Automation Tool.
"""
import os
import sys
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(log_level=logging.INFO):
    """
    Set up and configure the logging system.
    
    Args:
        log_level: The logging level to use
    """
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler with a higher log level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Create file handler for all logs
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'automation.log'),
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    
    # Create formatters and add them to the handlers
    console_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)
    file_handler.setFormatter(file_format)
    
    # Add the handlers to the logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Return the configured logger
    return root_logger