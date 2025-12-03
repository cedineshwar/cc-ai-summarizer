import logging
import os
from datetime import datetime

def setup_logger(debug=False):
    """
    Setup logging configuration.
    
    Args:
        debug (bool): If True, enables DEBUG level logging. If False, uses INFO level.
    
    Returns:
        logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"log_{timestamp}.txt"
    log_filepath = os.path.join(logs_dir, log_filename)
    
    # Set logging level based on debug flag
    log_level = logging.DEBUG if debug else logging.INFO
    
    # Create logger
    logger = logging.getLogger('cc_ai_summarizer')
    logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    # Create file handler
    file_handler = logging.FileHandler(log_filepath)
    file_handler.setLevel(log_level)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add formatter to handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Log initialization
    logger.info(f"Logger initialized. Log file: {log_filepath}")
    logger.info(f"Debug mode: {debug}")
    
    return logger

# Create a default logger instance
DEBUG = True
  # Set to True to enable debug logging
logger = setup_logger(debug=DEBUG)
