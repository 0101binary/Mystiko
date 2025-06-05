import logging
import os
from datetime import datetime
from pathlib import Path

class Logger:
    def __init__(self, config):
        self.config = config
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Set up logging
        self.logger = logging.getLogger('ByDef')
        self.logger.setLevel(logging.INFO)
        
        # Create handlers
        self._setup_file_handler()
        self._setup_console_handler()
        
    def _setup_file_handler(self):
        """Set up file handler for logging"""
        log_file = self.log_dir / f"bydef_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
        
    def _setup_console_handler(self):
        """Set up console handler for logging"""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(console_handler)
        
    def info(self, message):
        """Log info message"""
        self.logger.info(message)
        
    def error(self, message):
        """Log error message"""
        self.logger.error(message)
        
    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)
        
    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)
