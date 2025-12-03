"""
Simple logger for LINA
Provides basic logging functionality
"""
import logging
import sys
from typing import Any

class SimpleLogger:
    """Simple logger that provides info, error, warning, and debug methods"""
    
    def __init__(self):
        self.logger = logging.getLogger('lina')
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers to avoid duplicates
        if not self.logger.handlers:
            # Console handler
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def info(self, message: str, *args, **kwargs):
        """Log info message"""
        self.logger.info(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log error message"""
        self.logger.error(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log warning message"""
        self.logger.warning(message, *args, **kwargs)
    
    def debug(self, message: str, *args, **kwargs):
        """Log debug message"""
        self.logger.debug(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Log critical message"""
        self.logger.critical(message, *args, **kwargs)

# Create singleton instance
log = SimpleLogger()

