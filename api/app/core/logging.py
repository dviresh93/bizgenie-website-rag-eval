import logging
import sys
import os
from typing import Any

def setup_logging(log_level: str = "INFO", log_file: str = "api/app/logs/rag_system.log"):
    """
    Configure structured logging for the application.
    Writes to both console (stdout) and a file.
    """
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except Exception as e:
            print(f"Warning: Could not create log directory {log_dir}: {e}")

    # Create logger
    logger = logging.getLogger("website_rag")
    logger.setLevel(log_level)
    
    # Prevent adding handlers multiple times if function called repeatedly
    if logger.handlers:
        return logger

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 1. Console Handler (Stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. File Handler
    try:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not set up file logging to {log_file}: {e}")

    return logger

# Global logger instance
logger = setup_logging()

def get_logger(name: str):
    """Get a logger with the specified name prefix"""
    return logging.getLogger(f"website_rag.{name}")
