import functools

def cache_result(ttl=60):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = f'{func.__name__}:{args}:{kwargs}'
            result = cache.get(key)
            if result is None:
                result = func(*args, **kwargs)
                cache.set(key, result, ttl)
            return result
        return wrapper
    return decorator
