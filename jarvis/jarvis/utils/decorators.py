"""
Decorators for Jarvis Voice Assistant.

This module provides common decorators for retry logic, timing,
error handling, and other cross-cutting concerns.
"""

import functools
import time
import logging
from typing import Callable, Any, Optional, Type, Union, Tuple
from threading import Lock

from ..exceptions import JarvisError


logger = logging.getLogger(__name__)


def retry(max_attempts: int = 3, 
         delay: float = 1.0, 
         backoff: float = 2.0,
         exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
         on_retry: Optional[Callable] = None) -> Callable:
    """
    Decorator that retries a function on failure.
    
    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between attempts in seconds
        backoff: Multiplier for delay after each attempt
        exceptions: Exception types to catch and retry on
        on_retry: Optional callback function called on each retry
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        # Last attempt failed, re-raise
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {str(e)}")
                        raise
                    
                    logger.warning(f"Function {func.__name__} failed (attempt {attempt + 1}/{max_attempts}): {str(e)}")
                    
                    # Call retry callback if provided
                    if on_retry:
                        try:
                            on_retry(attempt + 1, e)
                        except Exception as callback_error:
                            logger.error(f"Retry callback failed: {str(callback_error)}")
                    
                    # Wait before retrying
                    if current_delay > 0:
                        time.sleep(current_delay)
                        current_delay *= backoff
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator


def timing(log_level: int = logging.INFO, 
          include_args: bool = False,
          threshold: Optional[float] = None) -> Callable:
    """
    Decorator that logs function execution time.
    
    Args:
        log_level: Logging level for timing messages
        include_args: Whether to include function arguments in log
        threshold: Only log if execution time exceeds this threshold (seconds)
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                success = True
            except Exception as e:
                result = e
                success = False
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Only log if threshold is met
            if threshold is None or duration >= threshold:
                log_msg = f"Function {func.__name__} executed in {duration:.3f}s"
                
                if include_args:
                    # Sanitize arguments for logging
                    safe_args = [str(arg)[:100] for arg in args]
                    safe_kwargs = {k: str(v)[:100] for k, v in kwargs.items()}
                    log_msg += f" with args={safe_args}, kwargs={safe_kwargs}"
                
                if not success:
                    log_msg += f" (failed with {type(result).__name__})"
                
                logger.log(log_level, log_msg)
            
            if success:
                return result
            else:
                raise result
        
        return wrapper
    return decorator


def error_handler(default_return: Any = None,
                 log_level: int = logging.ERROR,
                 reraise: bool = False,
                 exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception) -> Callable:
    """
    Decorator that handles exceptions gracefully.
    
    Args:
        default_return: Value to return on error
        log_level: Logging level for error messages
        reraise: Whether to re-raise the exception after logging
        exceptions: Exception types to catch
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                logger.log(log_level, f"Error in {func.__name__}: {str(e)}", exc_info=True)
                
                if reraise:
                    raise
                
                return default_return
        
        return wrapper
    return decorator


def singleton(cls: Type) -> Type:
    """
    Decorator that makes a class a singleton.
    
    Args:
        cls: Class to make singleton
        
    Returns:
        Singleton class
    """
    instances = {}
    lock = Lock()
    
    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            with lock:
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance


def validate_types(**type_checks) -> Callable:
    """
    Decorator that validates function argument types.
    
    Args:
        **type_checks: Mapping of argument names to expected types
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate types
            for arg_name, expected_type in type_checks.items():
                if arg_name in bound_args.arguments:
                    value = bound_args.arguments[arg_name]
                    if value is not None and not isinstance(value, expected_type):
                        raise TypeError(
                            f"Argument '{arg_name}' must be of type {expected_type.__name__}, "
                            f"got {type(value).__name__}"
                        )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def cache_result(ttl: Optional[float] = None, maxsize: int = 128) -> Callable:
    """
    Decorator that caches function results.
    
    Args:
        ttl: Time-to-live for cached results in seconds (None for no expiration)
        maxsize: Maximum number of cached results
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        cache = {}
        cache_times = {}
        lock = Lock()
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key = str(args) + str(sorted(kwargs.items()))
            current_time = time.time()
            
            with lock:
                # Check if result is cached and still valid
                if key in cache:
                    if ttl is None or (current_time - cache_times[key]) < ttl:
                        logger.debug(f"Cache hit for {func.__name__}")
                        return cache[key]
                    else:
                        # Expired, remove from cache
                        del cache[key]
                        del cache_times[key]
                
                # Limit cache size
                if len(cache) >= maxsize:
                    # Remove oldest entry
                    oldest_key = min(cache_times.keys(), key=lambda k: cache_times[k])
                    del cache[oldest_key]
                    del cache_times[oldest_key]
                
                # Execute function and cache result
                logger.debug(f"Cache miss for {func.__name__}")
                result = func(*args, **kwargs)
                cache[key] = result
                cache_times[key] = current_time
                
                return result
        
        # Add cache management methods
        def clear_cache():
            with lock:
                cache.clear()
                cache_times.clear()
        
        def cache_info():
            with lock:
                return {
                    'size': len(cache),
                    'maxsize': maxsize,
                    'ttl': ttl,
                    'keys': list(cache.keys())
                }
        
        wrapper.clear_cache = clear_cache
        wrapper.cache_info = cache_info
        
        return wrapper
    return decorator


def deprecated(reason: str = "", version: str = "") -> Callable:
    """
    Decorator that marks a function as deprecated.
    
    Args:
        reason: Reason for deprecation
        version: Version when function was deprecated
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warning_msg = f"Function {func.__name__} is deprecated"
            if version:
                warning_msg += f" since version {version}"
            if reason:
                warning_msg += f": {reason}"
            
            logger.warning(warning_msg)
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_initialization(attribute: str) -> Callable:
    """
    Decorator that ensures an object is initialized before method execution.
    
    Args:
        attribute: Attribute name to check for initialization
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if not hasattr(self, attribute) or not getattr(self, attribute):
                raise JarvisError(f"Object must be initialized before calling {func.__name__}")
            
            return func(self, *args, **kwargs)
        
        return wrapper
    return decorator


def log_calls(log_level: int = logging.DEBUG, 
             include_result: bool = False,
             max_arg_length: int = 100) -> Callable:
    """
    Decorator that logs function calls.
    
    Args:
        log_level: Logging level for call messages
        include_result: Whether to include function result in log
        max_arg_length: Maximum length for argument values in log
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Sanitize arguments for logging
            safe_args = []
            for arg in args:
                arg_str = str(arg)
                if len(arg_str) > max_arg_length:
                    arg_str = arg_str[:max_arg_length] + "..."
                safe_args.append(arg_str)
            
            safe_kwargs = {}
            for key, value in kwargs.items():
                value_str = str(value)
                if len(value_str) > max_arg_length:
                    value_str = value_str[:max_arg_length] + "..."
                safe_kwargs[key] = value_str
            
            logger.log(log_level, f"Calling {func.__name__}(args={safe_args}, kwargs={safe_kwargs})")
            
            try:
                result = func(*args, **kwargs)
                
                if include_result:
                    result_str = str(result)
                    if len(result_str) > max_arg_length:
                        result_str = result_str[:max_arg_length] + "..."
                    logger.log(log_level, f"{func.__name__} returned: {result_str}")
                
                return result
                
            except Exception as e:
                logger.log(log_level, f"{func.__name__} raised {type(e).__name__}: {str(e)}")
                raise
        
        return wrapper
    return decorator
