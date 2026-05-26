"""Retry logic for WRedis operations."""

import time
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

import redis

from wredis._exceptions import OperationError

T = TypeVar("T")


def retry(
    max_attempts: int = 3,
    delay: float = 0.1,
    backoff: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (
        redis.ConnectionError,
        redis.TimeoutError,
    ),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Retry decorator with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts.
        delay: Initial delay between retries in seconds.
        backoff: Multiplier for delay after each retry.
        exceptions: Tuple of exception types to retry on.

    Returns:
        Decorated function with retry logic.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            current_delay = delay
            last_exception: Exception | None = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(current_delay)
                        current_delay *= backoff

            raise OperationError(
                f"Operation {func.__name__} failed after {max_attempts} attempts: {last_exception}"
            ) from last_exception

        return wrapper

    return decorator


def async_retry(
    max_attempts: int = 3,
    delay: float = 0.1,
    backoff: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (
        redis.ConnectionError,
        redis.TimeoutError,
    ),
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Async retry decorator with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts.
        delay: Initial delay between retries in seconds.
        backoff: Multiplier for delay after each retry.
        exceptions: Tuple of exception types to retry on.

    Returns:
        Decorated async function with retry logic.
    """
    import asyncio

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            last_exception: Exception | None = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff

            raise OperationError(
                f"Operation {func.__name__} failed after {max_attempts} attempts: {last_exception}"
            ) from last_exception

        return wrapper

    return decorator
