"""
Logging utilities for Jarvis Voice Assistant.

This module provides structured logging setup with configurable output,
log levels, and formatting for consistent logging throughout the application.
"""

import logging
import logging.handlers
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from ..config import LoggingConfig


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log levels."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        """Format log record with colors."""
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}{record.levelname}"
                f"{self.COLORS['RESET']}"
            )
        
        return super().format(record)


class StructuredFormatter(logging.Formatter):
    """Formatter that outputs structured log data."""
    
    def format(self, record):
        """Format log record as structured data."""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created',
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'getMessage', 'exc_info',
                          'exc_text', 'stack_info']:
                log_data[key] = value
        
        return str(log_data)


def setup_logging(config: LoggingConfig,
                 enable_colors: bool = True,
                 structured: bool = False,
                 console_level: str = "ERROR",
                 clean_console: bool = True) -> None:
    """
    Set up logging configuration for the application.

    Args:
        config: Logging configuration
        enable_colors: Whether to enable colored output for console
        structured: Whether to use structured logging format
        console_level: Log level for console output (default: ERROR to keep console clean)
        clean_console: Whether to use clean console mode (minimal logging to terminal)
    """
    # Get root logger
    root_logger = logging.getLogger()

    # Clear existing handlers
    root_logger.handlers.clear()

    # Set log level (file gets full logging)
    log_level = getattr(logging, config.level.upper(), logging.INFO)
    root_logger.setLevel(log_level)

    # Set console level (higher threshold for clean UI)
    console_log_level = getattr(logging, console_level.upper(), logging.ERROR)

    # Create formatters
    if structured:
        formatter = StructuredFormatter()
        console_formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            fmt=config.format,
            datefmt=config.date_format
        )

        if enable_colors and sys.stdout.isatty():
            console_formatter = ColoredFormatter(
                fmt=config.format,
                datefmt=config.date_format
            )
        else:
            console_formatter = formatter

    # Console handler - minimal logging for clean UI
    if clean_console:
        # Only show CRITICAL errors in console for clean UI
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.CRITICAL)  # Only critical errors in console
        root_logger.addHandler(console_handler)
    else:
        # Traditional console logging
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(console_log_level)
        root_logger.addHandler(console_handler)
    
    # File handler if specified
    if config.file:
        try:
            log_file = Path(config.file)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Use rotating file handler to prevent huge log files
            file_handler = logging.handlers.RotatingFileHandler(
                filename=log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(log_level)
            root_logger.addHandler(file_handler)
            
            root_logger.info(f"Logging to file: {log_file}")
            
        except Exception as e:
            root_logger.error(f"Failed to setup file logging: {str(e)}")
    
    # Set specific logger levels for noisy libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('langchain').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)

    # Suppress noisy audio libraries in console (but keep in file)
    logging.getLogger('faster_whisper').setLevel(logging.ERROR)  # Console only shows errors
    logging.getLogger('jarvis.audio').setLevel(logging.ERROR)    # Console only shows errors

    root_logger.info("Logging system initialized")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LogContext:
    """Context manager for adding context to log messages."""
    
    def __init__(self, logger: logging.Logger, **context):
        """
        Initialize log context.
        
        Args:
            logger: Logger instance
            **context: Context key-value pairs
        """
        self.logger = logger
        self.context = context
        self.old_factory = None
    
    def __enter__(self):
        """Enter context and modify log record factory."""
        self.old_factory = logging.getLogRecordFactory()
        
        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record
        
        logging.setLogRecordFactory(record_factory)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and restore original log record factory."""
        if self.old_factory:
            logging.setLogRecordFactory(self.old_factory)


class PerformanceLogger:
    """Logger for performance metrics and timing."""
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize performance logger.
        
        Args:
            logger: Base logger instance
        """
        self.logger = logger
        self.timings: Dict[str, float] = {}
    
    def start_timer(self, name: str) -> None:
        """
        Start a named timer.
        
        Args:
            name: Timer name
        """
        import time
        self.timings[name] = time.time()
        self.logger.debug(f"Started timer: {name}")
    
    def end_timer(self, name: str) -> float:
        """
        End a named timer and log the duration.
        
        Args:
            name: Timer name
            
        Returns:
            Duration in seconds
        """
        import time
        if name not in self.timings:
            self.logger.warning(f"Timer '{name}' was not started")
            return 0.0
        
        duration = time.time() - self.timings[name]
        del self.timings[name]
        
        self.logger.info(f"Timer '{name}' completed in {duration:.3f}s")
        return duration
    
    def log_memory_usage(self) -> None:
        """Log current memory usage."""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            self.logger.info(
                f"Memory usage: RSS={memory_info.rss / 1024 / 1024:.1f}MB, "
                f"VMS={memory_info.vms / 1024 / 1024:.1f}MB"
            )
        except ImportError:
            self.logger.debug("psutil not available for memory logging")
        except Exception as e:
            self.logger.error(f"Failed to log memory usage: {str(e)}")
    
    def log_system_info(self) -> None:
        """Log system information."""
        try:
            import platform
            import psutil
            
            self.logger.info(f"System: {platform.system()} {platform.release()}")
            self.logger.info(f"Python: {platform.python_version()}")
            self.logger.info(f"CPU cores: {psutil.cpu_count()}")
            self.logger.info(f"Memory: {psutil.virtual_memory().total / 1024 / 1024 / 1024:.1f}GB")
            
        except ImportError:
            self.logger.debug("System info logging requires psutil")
        except Exception as e:
            self.logger.error(f"Failed to log system info: {str(e)}")


def configure_library_logging() -> None:
    """Configure logging for third-party libraries."""
    # Reduce noise from common libraries
    library_levels = {
        'urllib3.connectionpool': logging.WARNING,
        'requests.packages.urllib3': logging.WARNING,
        'langchain.llms.base': logging.WARNING,
        'langchain.schema': logging.WARNING,
        'httpx': logging.WARNING,
        'httpcore': logging.WARNING,
        'asyncio': logging.WARNING,
        'matplotlib': logging.WARNING,
        'PIL': logging.WARNING,
    }
    
    for library, level in library_levels.items():
        logging.getLogger(library).setLevel(level)


def log_function_call(logger: logging.Logger, func_name: str, args: tuple, kwargs: dict) -> None:
    """
    Log function call details.
    
    Args:
        logger: Logger instance
        func_name: Function name
        args: Function arguments
        kwargs: Function keyword arguments
    """
    # Sanitize arguments for logging (avoid logging sensitive data)
    safe_args = []
    for arg in args:
        if isinstance(arg, str) and len(arg) > 100:
            safe_args.append(f"{arg[:100]}...")
        else:
            safe_args.append(repr(arg))
    
    safe_kwargs = {}
    for key, value in kwargs.items():
        if isinstance(value, str) and len(value) > 100:
            safe_kwargs[key] = f"{value[:100]}..."
        else:
            safe_kwargs[key] = repr(value)
    
    logger.debug(f"Calling {func_name}(args={safe_args}, kwargs={safe_kwargs})")


def setup_exception_logging() -> None:
    """Set up global exception logging."""
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions."""
        if issubclass(exc_type, KeyboardInterrupt):
            # Don't log keyboard interrupts
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logger = get_logger(__name__)
        logger.critical(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
    
    sys.excepthook = handle_exception
