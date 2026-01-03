"""
Centralized logging configuration for Astronomy RAG Corpus.

Provides consistent logging format across all modules. Call setup_logging()
once at application entry point, then use logging.getLogger(__name__) in modules.
"""

import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    """
    Configure root logger with consistent format.
    
    Args:
        level: Logging level as string ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    
    This function should be called once at application entry point.
    Modules should then use logging.getLogger(__name__) to get loggers.
    """
    # AI NOTE: Call once at entry point only. Multiple calls are safe (handlers
    # are cleared below) but wasteful. If logging seems broken, check that this
    # was called before any getLogger() usage.
    
    # Defensive handling: ensure level is a valid string before processing.
    # Protects against None being passed explicitly or invalid level names.
    if not level or not isinstance(level, str):
        level = "INFO"
    
    log_level = getattr(logging, level.upper(), None)
    if log_level is None:
        # Invalid level string (e.g., "VERBOSE") - fall back to INFO
        log_level = logging.INFO
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers to ensure idempotent behavior. Without this,
    # repeated calls (e.g., in tests) would duplicate log output.
    root_logger.handlers.clear()
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Format: timestamp | level (padded) | module path | message
    # The module path uses %(name)s which reflects the logger name from
    # getLogger(__name__), giving us the full dotted module path.
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    
    root_logger.addHandler(console_handler)
