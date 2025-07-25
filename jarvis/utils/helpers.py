"""
Helper utilities for Jarvis Voice Assistant.

This module provides common utility functions for validation,
file operations, system information, and other general-purpose tasks.
"""

import os
import re
import platform
import subprocess
import urllib.parse
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import logging

logger = logging.getLogger(__name__)


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email format is valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip()) is not None


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL format is valid, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    try:
        result = urllib.parse.urlparse(url.strip())
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 0:
        return "0s"
    
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"
    else:
        hours = int(seconds // 3600)
        remaining_minutes = int((seconds % 3600) // 60)
        remaining_seconds = seconds % 60
        return f"{hours}h {remaining_minutes}m {remaining_seconds:.1f}s"


def safe_filename(filename: str, max_length: int = 255) -> str:
    """
    Convert string to safe filename by removing/replacing invalid characters.
    
    Args:
        filename: Original filename
        max_length: Maximum filename length
        
    Returns:
        Safe filename string
    """
    if not filename:
        return "untitled"
    
    # Remove or replace invalid characters
    safe_chars = re.sub(r'[<>:"/\\|?*]', '_', filename)
    safe_chars = re.sub(r'\s+', '_', safe_chars)  # Replace spaces with underscores
    safe_chars = re.sub(r'_+', '_', safe_chars)   # Replace multiple underscores with single
    safe_chars = safe_chars.strip('._')           # Remove leading/trailing dots and underscores
    
    # Ensure it's not empty
    if not safe_chars:
        safe_chars = "untitled"
    
    # Truncate if too long
    if len(safe_chars) > max_length:
        name, ext = os.path.splitext(safe_chars)
        max_name_length = max_length - len(ext)
        safe_chars = name[:max_name_length] + ext
    
    return safe_chars


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure directory exists, creating it if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        Path object for the directory
        
    Raises:
        OSError: If directory cannot be created
    """
    path_obj = Path(path)
    
    try:
        path_obj.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {path_obj}")
        return path_obj
    except Exception as e:
        logger.error(f"Failed to create directory {path_obj}: {str(e)}")
        raise OSError(f"Cannot create directory {path_obj}: {str(e)}") from e


def get_system_info() -> Dict[str, Any]:
    """
    Get comprehensive system information.
    
    Returns:
        Dictionary containing system information
    """
    info = {
        'platform': platform.platform(),
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
        'python_implementation': platform.python_implementation(),
    }
    
    # Add memory information if available
    try:
        import psutil
        memory = psutil.virtual_memory()
        info.update({
            'total_memory_gb': round(memory.total / (1024**3), 2),
            'available_memory_gb': round(memory.available / (1024**3), 2),
            'memory_percent': memory.percent,
            'cpu_count': psutil.cpu_count(),
            'cpu_count_logical': psutil.cpu_count(logical=True),
        })
    except ImportError:
        logger.debug("psutil not available for detailed system info")
    
    # Add disk information
    try:
        disk_usage = os.statvfs('/')
        total_space = disk_usage.f_frsize * disk_usage.f_blocks
        free_space = disk_usage.f_frsize * disk_usage.f_available
        
        info.update({
            'disk_total_gb': round(total_space / (1024**3), 2),
            'disk_free_gb': round(free_space / (1024**3), 2),
            'disk_used_percent': round((1 - free_space / total_space) * 100, 1)
        })
    except (AttributeError, OSError):
        # statvfs not available on Windows
        logger.debug("Disk usage information not available")
    
    return info


def get_file_size_human(size_bytes: int) -> str:
    """
    Convert file size in bytes to human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable size string
    """
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f}{size_names[i]}"


def find_executable(name: str) -> Optional[str]:
    """
    Find executable in system PATH.
    
    Args:
        name: Executable name
        
    Returns:
        Full path to executable or None if not found
    """
    try:
        # Use 'which' on Unix-like systems, 'where' on Windows
        if platform.system() == 'Windows':
            result = subprocess.run(['where', name], capture_output=True, text=True)
        else:
            result = subprocess.run(['which', name], capture_output=True, text=True)
        
        if result.returncode == 0:
            return result.stdout.strip().split('\n')[0]
    except Exception as e:
        logger.debug(f"Error finding executable {name}: {str(e)}")
    
    return None


def is_port_available(port: int, host: str = 'localhost') -> bool:
    """
    Check if a network port is available.
    
    Args:
        port: Port number to check
        host: Host to check (default: localhost)
        
    Returns:
        True if port is available, False otherwise
    """
    import socket
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result != 0  # Port is available if connection failed
    except Exception:
        return False


def get_available_port(start_port: int = 8000, max_attempts: int = 100) -> Optional[int]:
    """
    Find an available port starting from a given port number.
    
    Args:
        start_port: Starting port number
        max_attempts: Maximum number of ports to try
        
    Returns:
        Available port number or None if none found
    """
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(port):
            return port
    
    return None


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate string to maximum length with optional suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated string
    """
    if not text or len(text) <= max_length:
        return text
    
    if len(suffix) >= max_length:
        return text[:max_length]
    
    return text[:max_length - len(suffix)] + suffix


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def sanitize_for_logging(data: Any, max_length: int = 100) -> str:
    """
    Sanitize data for safe logging (remove sensitive info, limit length).
    
    Args:
        data: Data to sanitize
        max_length: Maximum length of output
        
    Returns:
        Sanitized string representation
    """
    # Convert to string
    text = str(data)
    
    # Remove potential sensitive patterns
    sensitive_patterns = [
        (r'password["\']?\s*[:=]\s*["\']?[^"\'\s,}]+', 'password=***'),
        (r'token["\']?\s*[:=]\s*["\']?[^"\'\s,}]+', 'token=***'),
        (r'key["\']?\s*[:=]\s*["\']?[^"\'\s,}]+', 'key=***'),
        (r'secret["\']?\s*[:=]\s*["\']?[^"\'\s,}]+', 'secret=***'),
    ]
    
    for pattern, replacement in sensitive_patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Truncate if too long
    return truncate_string(text, max_length)


def retry_with_backoff(func, max_retries: int = 3, base_delay: float = 1.0, 
                      max_delay: float = 60.0, backoff_factor: float = 2.0) -> Any:
    """
    Retry function with exponential backoff.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retries
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        backoff_factor: Backoff multiplier
        
    Returns:
        Function result
        
    Raises:
        Last exception if all retries fail
    """
    import time
    import random
    
    delay = base_delay
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            last_exception = e
            
            if attempt == max_retries:
                break
            
            # Add jitter to prevent thundering herd
            jitter = random.uniform(0.1, 0.3) * delay
            sleep_time = min(delay + jitter, max_delay)
            
            logger.debug(f"Retry attempt {attempt + 1} failed, sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
            
            delay *= backoff_factor
    
    raise last_exception


def get_env_list(env_var: str, separator: str = ',', default: Optional[List[str]] = None) -> List[str]:
    """
    Get environment variable as list of strings.
    
    Args:
        env_var: Environment variable name
        separator: Separator character
        default: Default value if env var not set
        
    Returns:
        List of strings
    """
    value = os.getenv(env_var)
    if not value:
        return default or []
    
    return [item.strip() for item in value.split(separator) if item.strip()]


def get_env_bool(env_var: str, default: bool = False) -> bool:
    """
    Get environment variable as boolean.
    
    Args:
        env_var: Environment variable name
        default: Default value if env var not set
        
    Returns:
        Boolean value
    """
    value = os.getenv(env_var)
    if not value:
        return default
    
    return value.lower() in ('true', '1', 'yes', 'on', 'enabled')
