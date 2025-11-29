"""
Logging configuration for MAY system
"""

import sys
from pathlib import Path
from loguru import logger


def setup_logger(log_level: str = "INFO", log_file: str = None):
    """
    Configure loguru logger with appropriate settings
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file. If None, uses default location.
        
    Returns:
        Configured logger instance
    """
    # Remove default handler
    logger.remove()
    
    # Add console handler with colors
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True,
    )
    
    # Add file handler if specified
    if log_file is None:
        project_root = Path(__file__).parent.parent
        log_dir = project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "may.log"
    
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=log_level,
        rotation="10 MB",
        retention="30 days",
        compression="zip",
    )
    
    logger.info(f"Logger initialized with level: {log_level}")
    return logger


def get_logger(name: str):
    """
    Get a logger instance for a specific module
    
    Args:
        name: Module name
        
    Returns:
        Logger instance
    """
    return logger.bind(name=name)
