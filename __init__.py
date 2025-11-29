"""
MAY - Multi-Agent AI System
Main package initialization
"""

__version__ = "0.1.0"
__author__ = "MAY Development Team"

from .utils.logger import setup_logger
from .utils.config import load_config

# Initialize global logger
logger = setup_logger()

# Load configuration
config = load_config()

__all__ = ["logger", "config", "__version__"]
