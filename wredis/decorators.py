"""Cache decorators for WRedis with metrics tracking."""

import functools
import hashlib
import json
from collections.abc import Callable
from typing import Any, TypeVar

import redis

from wredis._exceptions import CacheError

T = TypeVar("T")


class CacheMetrics:
    """Tracks cache hit/miss statistics.

    Attributes:
        hits: Number of cache hits.
        misses: Number of cache misses.
        errors: Number of cache errors.
    """

    def __init__(self) -> None:
        self.hits = 0
        self.misses = 0
        self.errors = 0

    @property
    def hit_rate(self) -> float:
        """Cache hit rate as a percentage.

        Returns:
            Hit rate percentage (0.0-100.0), or 0.0 if no requests.
        """
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0

    def record_hit(self) -> None:
        """Record a cache hit."""
        self.hits += 1

    def record_miss(self) -> None:
        """Record a cache miss."""
        self.misses += 1

    def record_error(self) -> None:
        """Record a cache error."""
        self.errors += 1

    def reset(self) -> None:
        """Reset all counters."""
        self.hits = 0
        self.misses = 0
        self.errors = 0

    def __repr__(self) -> str:
        return (
            f"CacheMetrics(hits={self.hits}, misses={self.misses}, errors={self.errors}, hit_rate={self.hit_rate:.1f}%)"
        )


default_metrics = CacheMetrics()


def _default_key_builder(func: Callable, args: tuple, kwargs: dict) -> str:
    """Build a cache key from function name and arguments.

    Args:
        func: The decorated function.
        args: Positional arguments.
        kwargs: Keyword arguments.

    Returns:
        A cache key string.
    """
    key_parts = [func.__module__, func.__name__]

    for arg in args:
        try:
            key_parts.append(json.dumps(arg, sort_keys=True))
        except (TypeError, ValueError):
            key_parts.append(str(arg))

    for k, v in sorted(kwargs.items()):
        try:
            key_parts.append(f"{k}:{json.dumps(v, sort_keys=True)}")
        except (TypeError, ValueError):
            key_parts.append(f"{k}:{str(v)}")

    key_string = ":".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def cache(
    ttl: int = 300,
    prefix: str = "wredis:cache",
    key_builder: Callable | None = None,
    redis_client: redis.StrictRedis | None = None,
    metrics: CacheMetrics | None = None,
):
    """Decorator to cache function results in Redis.

    Implements the Cache-Aside pattern:
    1. If result is in cache -> return it
    2. If not -> execute function, save to cache, return result

    Args:
        ttl: Time-to-live in seconds (default: 300).
        prefix: Prefix for cache keys (default: "wredis:cache").
        key_builder: Custom function to build cache keys.
        redis_client: Custom Redis client (creates new if None).
        metrics: Optional CacheMetrics instance for tracking.

    Returns:
        Decorated function.

    Example:
        >>> metrics = CacheMetrics()
        >>> @cache(ttl=300, prefix="myapp", metrics=metrics)
        ... def expensive_function(arg1):
        ...     return compute_result(arg1)
    """
    _redis = redis_client or redis.StrictRedis()
    _key_builder = key_builder or _default_key_builder
    _metrics = metrics or default_metrics

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            cache_key = f"{prefix}:{_key_builder(func, args, kwargs)}"

            try:
                cached = _redis.get(cache_key)
                if cached is not None:
                    _metrics.record_hit()
                    try:
                        return json.loads(cached)
                    except json.JSONDecodeError:
                        return cached
            except redis.RedisError as e:
                _metrics.record_error()
                raise CacheError(f"Error reading from cache: {e}") from e

            _metrics.record_miss()
            result = func(*args, **kwargs)

            try:
                cache_value = json.dumps(result, default=str) if not isinstance(result, (str, bytes)) else result
                _redis.setex(cache_key, ttl, cache_value)
            except redis.RedisError as e:
                _metrics.record_error()
                raise CacheError(f"Error writing to cache: {e}") from e

            return result

        return wrapper  # type: ignore[return-value]

    return decorator


def async_cache(
    ttl: int = 300,
    prefix: str = "wredis:cache",
    key_builder: Callable | None = None,
    redis_client: "redis.asyncio.Redis | None" = None,
    metrics: CacheMetrics | None = None,
):
    """Async version of @cache decorator.

    Args:
        ttl: Time-to-live in seconds (default: 300).
        prefix: Prefix for cache keys (default: "wredis:cache").
        key_builder: Custom function to build cache keys.
        redis_client: Custom async Redis client.
        metrics: Optional CacheMetrics instance for tracking.

    Returns:
        Decorated async function.
    """
    import redis.asyncio as aredis

    _redis = redis_client or aredis.Redis()
    _key_builder = key_builder or _default_key_builder
    _metrics = metrics or default_metrics

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache_key = f"{prefix}:{_key_builder(func, args, kwargs)}"

            try:
                cached = await _redis.get(cache_key)
                if cached is not None:
                    _metrics.record_hit()
                    try:
                        return json.loads(cached)
                    except json.JSONDecodeError:
                        return cached
            except aredis.RedisError as e:
                _metrics.record_error()
                raise CacheError(f"Error reading from cache: {e}") from e

            _metrics.record_miss()
            result = await func(*args, **kwargs)

            try:
                cache_value = json.dumps(result, default=str) if not isinstance(result, (str, bytes)) else result
                await _redis.setex(cache_key, ttl, cache_value)
            except aredis.RedisError as e:
                _metrics.record_error()
                raise CacheError(f"Error writing to cache: {e}") from e

            return result

        return wrapper  # type: ignore[return-value]

    return decorator


def invalidate_cache(
    pattern: str,
    redis_client: redis.StrictRedis | None = None,
):
    """Decorator to invalidate cache after function execution.

    Args:
        pattern: Glob pattern for keys to invalidate.
        redis_client: Custom Redis client.

    Returns:
        Decorated function.
    """
    _redis = redis_client or redis.StrictRedis()

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            result = func(*args, **kwargs)

            try:
                keys = _redis.keys(pattern)
                if keys:
                    _redis.delete(*keys)
            except redis.RedisError as e:
                raise CacheError(f"Error invalidating cache: {e}") from e

            return result

        return wrapper  # type: ignore[return-value]

    return decorator


def clear_cache(
    pattern: str,
    redis_client: redis.StrictRedis | None = None,
) -> int:
    """Utility function to clear cache keys matching a pattern.

    Args:
        pattern: Glob pattern for keys to clear.
        redis_client: Custom Redis client.

    Returns:
        Number of keys deleted.

    Raises:
        CacheError: If the operation fails.
    """
    _redis = redis_client or redis.StrictRedis()
    try:
        keys = _redis.keys(pattern)
        if keys:
            return _redis.delete(*keys)
        return 0
    except redis.RedisError as e:
        raise CacheError(f"Error clearing cache with pattern '{pattern}': {e}") from e
