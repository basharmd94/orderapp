import logging
import sys
from logging.handlers import RotatingFileHandler
import os

def setup_logger():
    logger = logging.getLogger('logs')
    
    if not logger.handlers:  # Prevent duplicate handlers
        logger.setLevel(logging.INFO)  # Changed from DEBUG to INFO level
        
        # Create formatters for different levels
        info_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        error_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s\n'
            'File: %(pathname)s, Line: %(lineno)d\n'
        )
        
        # File handler for app.log with rotation (general logs)
        app_handler = RotatingFileHandler(
            'app.log',
            maxBytes=1024 * 1024,  # 1MB
            backupCount=3,  # Reduced from 5 to 3
            encoding='utf-8'
        )
        app_handler.setLevel(logging.INFO)
        app_handler.setFormatter(info_formatter)
        logger.addHandler(app_handler)
        
        # Error handler with more detailed formatting
        error_handler = RotatingFileHandler(
            'error.log',
            maxBytes=1024 * 1024,
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(error_formatter)
        logger.addHandler(error_handler)
        
        # Console handler for development
        if os.getenv('FASTAPI_ENV') == 'development':
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(info_formatter)
            logger.addHandler(console_handler)
        
    return logger
