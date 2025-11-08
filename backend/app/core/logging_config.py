"""
Logging configuration
"""
import logging
import sys
from pathlib import Path
from pythonjsonlogger import jsonlogger

from app.core.config import settings


def setup_logging():
    """Setup application logging"""

    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Define log format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    # Clear existing handlers
    root_logger.handlers = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    if settings.ENVIRONMENT == "production":
        # JSON formatting for production
        json_formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s"
        )
        console_handler.setFormatter(json_formatter)
    else:
        # Human-readable format for development
        formatter = logging.Formatter(log_format)
        console_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)

    # File handler for errors
    error_handler = logging.FileHandler(log_dir / "error.log")
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(log_format)
    error_handler.setFormatter(error_formatter)
    root_logger.addHandler(error_handler)

    # File handler for all logs
    if settings.DEBUG:
        debug_handler = logging.FileHandler(log_dir / "debug.log")
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(error_formatter)
        root_logger.addHandler(debug_handler)

    # Suppress noisy loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("multipart").setLevel(logging.WARNING)

    logging.info(f"Logging configured for {settings.ENVIRONMENT} environment")
