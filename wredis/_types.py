"""Type aliases for WRedis."""

from collections.abc import Awaitable, Callable
from typing import Any, TypeAlias

RedisValue: TypeAlias = str | bytes | int | float | dict[str, Any] | list[Any] | None
Callback: TypeAlias = Callable[[dict[str, Any]], None]
AsyncCallback: TypeAlias = Callable[[dict[str, Any]], Awaitable[None]]
TTL: TypeAlias = int  # seconds, -1 means no TTL
