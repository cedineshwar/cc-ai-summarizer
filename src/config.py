"""
Configuration management module for loading settings from .env file.

This module handles loading environment variables and providing default values
for application configuration.
"""

import os
from dotenv import load_dotenv
from src.logger import logger

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class to manage application settings."""
    
    # Vector Store Configuration
    RETRIEVER_K = int(os.getenv('RETRIEVER_K', '100'))
    SUMMARIES_FILE = os.getenv('SUMMARIES_FILE', 'output_data/bulk_summaries.json')
    VECTOR_STORE_PATH = os.getenv('VECTOR_STORE_PATH', 'output_data/vector_store')
    
    # LLM Configuration
    MODEL_NAME = os.getenv('MODEL_NAME', 'gpt-4.1-mini-2025-04-14')
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.0'))
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '600'))
    
    # Application Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    DEBUG = os.getenv('DEBUG', 'FALSE').upper() == 'TRUE'
    
    @classmethod
    def log_config(cls):
        """Log current configuration values (excluding sensitive data)."""
        logger.info("=" * 70)
        logger.info("📋 APPLICATION CONFIGURATION LOADED")
        logger.info("=" * 70)
        logger.info(f"🔍 RETRIEVER_K: {cls.RETRIEVER_K} (max documents to retrieve)")
        logger.info(f"📊 Summaries File: {cls.SUMMARIES_FILE}")
        logger.info(f"🗂️  Vector Store Path: {cls.VECTOR_STORE_PATH}")
        logger.info(f"🤖 Model: {cls.MODEL_NAME}")
        logger.info(f"🌡️  Temperature: {cls.TEMPERATURE}")
        logger.info(f"📝 Max Tokens: {cls.MAX_TOKENS}")
        logger.info(f"📍 Log Level: {cls.LOG_LEVEL}")
        logger.info(f"🐛 Debug Mode: {'ON' if cls.DEBUG else 'OFF'}")
        logger.info("=" * 70)


def get_retriever_k() -> int:
    """
    Get the RETRIEVER_K value from configuration.
    
    Returns:
        int: Maximum number of documents to retrieve (k parameter)
    """
    return Config.RETRIEVER_K


def get_model_config() -> dict:
    """
    Get LLM model configuration.
    
    Returns:
        dict: Configuration dictionary with model settings
    """
    return {
        'model': Config.MODEL_NAME,
        'temperature': Config.TEMPERATURE,
        'max_tokens': Config.MAX_TOKENS
    }


def get_vector_store_config() -> dict:
    """
    Get vector store configuration.
    
    Returns:
        dict: Configuration dictionary with vector store paths and settings
    """
    return {
        'summaries_file': Config.SUMMARIES_FILE,
        'vector_store_path': Config.VECTOR_STORE_PATH,
        'retriever_k': Config.RETRIEVER_K
    }
