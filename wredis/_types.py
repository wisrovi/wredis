"""Type aliases for WRedis."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Union

RedisValue = Union[str, bytes, int, float, dict[str, Any], list[Any], None]
Callback = Callable[[dict[str, Any]], None]
AsyncCallback = Callable[[dict[str, Any]], Awaitable[None]]
TTL = int  # seconds, -1 means no TTL
