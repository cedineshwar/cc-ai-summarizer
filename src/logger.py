import logging
import os
from datetime import datetime
from pathlib import Path


def get_logs_dir():
    """Get the logs directory path."""
    logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    return logs_dir


def get_today_log_file():
    """Get today's log file path with format: log_YYYYMMDD.txt"""
    logs_dir = get_logs_dir()
    date_str = datetime.now().strftime("%Y%m%d")
    log_filename = f"log_{date_str}.txt"
    return os.path.join(logs_dir, log_filename)


def get_all_log_files():
    """Get list of all log files sorted by date (newest first)."""
    logs_dir = get_logs_dir()
    log_files = []
    
    if os.path.exists(logs_dir):
        for file in os.listdir(logs_dir):
            if file.startswith('log_') and file.endswith('.txt'):
                log_files.append(file)
    
    # Sort by date (newest first)
    log_files.sort(reverse=True)
    return log_files


def clear_today_log():
    """Clear today's log file and keep only the header."""
    log_filepath = get_today_log_file()
    
    try:
        # Write header to file
        with open(log_filepath, 'w', encoding='utf-8') as f:
            f.write(f"=== Log cleared at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        return True
    except Exception as e:
        print(f"Error clearing log file: {str(e)}")
        return False


def setup_logger(debug=False):
    """
    Setup logging configuration with one log file per day.
    
    Args:
        debug (bool): If True, enables DEBUG level logging. If False, uses INFO level.
    
    Returns:
        logger: Configured logger instance
    """
    # Get today's log file path
    log_filepath = get_today_log_file()
    
    # Set logging level based on debug flag
    log_level = logging.DEBUG if debug else logging.INFO
    
    # Create logger
    logger = logging.getLogger('cc_ai_summarizer')
    logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    # Create file handler
    file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
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
DEBUG = True  # Set to True to enable debug logging
logger = setup_logger(debug=DEBUG)
