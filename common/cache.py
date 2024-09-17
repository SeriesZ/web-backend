import inspect
from functools import wraps

from cachetools.func import ttl_cache


def ttl_cache_with_signature(*cache_args, **cache_kwargs):
    def decorator(func):
        cached_func = ttl_cache(*cache_args, **cache_kwargs)(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return cached_func(*args, **kwargs)

        # 함수의 원래 시그니처를 유지합니다.
        wrapper.__signature__ = inspect.signature(func)
        # 캐시 제어 메소드를 노출합니다.
        wrapper.cache_clear = cached_func.cache_clear
        return wrapper
    return decorator
