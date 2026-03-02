"""Logging utility module"""
from loguru import logger as loguru_logger
import sys
from src.config import settings


def get_logger(name: str = None):
    """Get a configured logger instance"""
    logger = loguru_logger.bind(name=name or "ci_cd_agent")
    
    # Remove default handler
    logger.remove()
    
    # Add console handler with format
    logger.add(
        sys.stderr,
        format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
    )
    
    # Add file handler
    logger.add(
        f"{settings.logs_dir}/app.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation="500 MB",
    )
    
    return logger
