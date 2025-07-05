"""
Logging utilities.
"""
import logging
import sys
from typing import Optional

from src.app.core.config import settings


def setup_logger(name: Optional[str] = None) -> logging.Logger:
    """Setup application logger."""
    logger = logging.getLogger(name or __name__)
    
    if not logger.handlers:
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        
        # Create formatter
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Set log level based on environment
        if settings.DEBUG:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
    
    return logger


# Create default logger
logger = setup_logger("app")