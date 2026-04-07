"""wredis - Simple and powerful Redis library for Python.

Quick Start:
    # Sync
    from wredis.sync import RedisHashManager

    manager = RedisHashManager()
    manager.set("user:1", {"name": "Alice"})
    user = manager.get("user:1")

    # Async
    from wredis.aioredis import AsyncRedisHashManager

    async def main():
        manager = AsyncRedisHashManager()
        await manager.set("user:1", {"name": "Alice"})
        user = await manager.get("user:1")

For more: from wredis.sync import * or from wredis.aioredis import *
"""

from collections.abc import Callable
from typing import Any

from wredis.bitmap import RedisBitmapManager
from wredis.hash import RedisHashManager
from wredis.pubsub import RedisPubSubManager
from wredis.queue import RedisQueueManager
from wredis.sets import RedisSetManager
from wredis.sortedset import RedisSortedSetManager
from wredis.streams import RedisStreamManager

__all__ = [
    "RedisBitmapManager",
    "RedisHashManager",
    "RedisPubSubManager",
    "RedisQueueManager",
    "RedisSetManager",
    "RedisSortedSetManager",
    "RedisStreamManager",
    "enqueue",
    "publish",
    "subscribe",
    "xadd",
]


def publish(
    channel: str,
    message: str | dict[str, Any],
    host: str = "localhost",
    port: int = 6379,
    db: int = 0,
) -> None:
    """Publish a message to a Redis channel.

    Simplified API for Pub/Sub without boilerplate.

    Args:
        channel: The channel to publish to.
        message: Message to publish (str or dict).
        host: Redis host.
        port: Redis port.
        db: Redis database number.
    """
    manager = RedisPubSubManager(host=host, port=port, db=db, verbose=False)
    manager.publish_message(channel, message)


def subscribe(
    channel: str,
    callback: Callable[[Any], None],
    host: str = "localhost",
    port: int = 6379,
    db: int = 0,
) -> RedisPubSubManager:
    """Subscribe to a Redis channel with a callback.

    Simplified API for Pub/Sub without boilerplate.

    Args:
        channel: The channel to subscribe to.
        callback: Callback function to handle messages.
        host: Redis host.
        port: Redis port.
        db: Redis database number.

    Returns:
        RedisPubSubManager instance (for keeping the program running).
    """
    manager = RedisPubSubManager(host=host, port=port, db=db, verbose=False)

    @manager.on_message(channel)
    def handler(message):  # type: ignore[misc]
        callback(message)

    return manager


def enqueue(
    queue_name: str,
    data: dict[str, Any],
    host: str = "localhost",
    port: int = 6379,
    db: int = 0,
    ttl: int = -1,
) -> None:
    """Add a message to a Redis queue.

    Simplified API for queue operations without boilerplate.

    Args:
        queue_name: The queue name.
        data: Message data (dict).
        host: Redis host.
        port: Redis port.
        db: Redis database number.
        ttl: Time-to-live in seconds (optional).
    """
    manager = RedisQueueManager(host=host, port=port, db=db, verbose=False)
    manager.publish(queue_name, data, ttl=ttl)


def xadd(
    stream_name: str,
    data: dict,
    host: str = "localhost",
    port: int = 6379,
    db: int = 0,
    ttl: int | None = None,
) -> str | None:
    """Add a message to a Redis stream.

    Simplified API for stream operations without boilerplate.

    Args:
        stream_name: The stream name.
        data: Message data (dict).
        host: Redis host.
        port: Redis port.
        db: Redis database number.
        ttl: Time-to-live in seconds (optional).

    Returns:
        Message ID or None on error.
    """
    manager = RedisStreamManager(host=host, port=port, db=db, verbose=False)
    return manager.add_to_stream(stream_name, data, ttl=ttl)
