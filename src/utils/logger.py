"""Logging configuration"""

import logging
import logging.handlers
import json
from pathlib import Path
from datetime import datetime
import os


def setup_logging(log_level=None, log_file=None):
    """Configure logging for the application
    
    Args:
        log_level: Logging level (default: INFO)
        log_file: Path to log file (default: logs/trading_agent.log)
    """
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO")
    
    if log_file is None:
        log_file = os.getenv("LOG_FILE", "logs/trading_agent.log")
    
    # Create logs directory if it doesn't exist
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    max_bytes = int(os.getenv("LOG_MAX_BYTES", 104857600))  # 100MB
    backup_count = int(os.getenv("LOG_BACKUP_COUNT", 10))
    
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    return root_logger


def get_logger(name):
    """Get logger instance
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
