"""
Logging Configuration
Sets up logging for the ETL pipeline.
"""

import logging
import sys
from pathlib import Path


def setup_logging(log_file: str = 'odoo_etl.log', log_level: str = 'INFO'):
    """
    Setup logging configuration.
    
    Args:
        log_file: Path to log file
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Create logger
    logger = logging.getLogger()
    logger.info(f"Logging initialized - Level: {log_level}, File: {log_file}")
    
    return logger
