"""Async Redis Stream Manager - real asyncio, no threads."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any

import redis.asyncio as aredis

from wredis._async_base import AsyncBaseManager
from wredis._exceptions import StreamError, ValidationError
from wredis._serializer import deserialize, serialize
from wredis._validation import validate_key


class AsyncRedisStreamManager(AsyncBaseManager):
    """Manages Redis streams asynchronously with real asyncio tasks.

    Uses asyncio.create_task() instead of threads for consumers.

    Attributes:
        consumers: Dictionary of registered stream consumers.
        _tasks: Dict of stream names to asyncio tasks.
        running: Whether the manager is actively consuming.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        verbose: bool = True,
    ):
        """Initialize the AsyncRedisStreamManager.

        Args:
            host: Redis hostname.
            port: Redis port.
            db: Redis database number.
            verbose: Enable logging.
        """
        super().__init__(host=host, port=port, db=db, verbose=verbose)
        self.consumers: dict[str, dict[str, Any]] = {}
        self._tasks: dict[str, asyncio.Task[None]] = {}
        self.running = False

    async def add_to_stream(self, key: str, data: dict[str, str], ttl: int | None = None) -> str | None:
        """Add a message to the stream.

        Args:
            key: Stream name.
            data: Message data.
            ttl: Optional TTL in seconds.

        Returns:
            Message ID, or None on error.

        Raises:
            ValidationError: If key is invalid.
            StreamError: If the operation fails.
        """
        validate_key(key)

        try:
            message_id = await self.redis_client.xadd(key, data)
            await self.log(f"Added to stream '{key}' with ID {message_id}")

            if ttl:
                await self.redis_client.expire(key, ttl)
                await self.log(f"Set TTL of {ttl}s for stream '{key}'")

            return message_id
        except (ValidationError, StreamError):
            raise
        except aredis.RedisError as e:
            raise StreamError(f"Failed to add to stream '{key}': {e}") from e

    def on_message(self, stream_name: str, group_name: str, consumer_name: str) -> Callable:
        """Decorator to register an async consumer for a stream.

        Args:
            stream_name: Name of the Redis stream.
            group_name: Name of the consumer group.
            consumer_name: Name of the consumer.

        Returns:
            Decorated callback function.

        Raises:
            ValidationError: If stream_name is invalid.
            StreamError: If consumer already registered.
        """
        validate_key(stream_name)

        def decorator(func: Callable) -> Callable:
            if stream_name in self.consumers:
                raise StreamError(f"Consumer already registered for stream '{stream_name}'")

            self.consumers[stream_name] = {
                "group_name": group_name,
                "consumer_name": consumer_name,
                "callback": func,
            }
            if self.running:
                self._tasks[stream_name] = asyncio.create_task(self._listen_stream(stream_name))
            # self.log(
            #     f"Registered consumer for stream '{stream_name}' "
            #     f"with group '{group_name}' and consumer '{consumer_name}'"
            # )
            return func

        return decorator

    async def start_listening(self) -> None:
        """Start listening on all registered streams."""
        self.running = True
        for stream_name in self.consumers:
            consumer_info = self.consumers[stream_name]
            group_name = consumer_info["group_name"]

            try:
                await self.redis_client.xgroup_create(stream_name, group_name, id="0", mkstream=True)
            except aredis.exceptions.ResponseError:
                await self.log(
                    f"Group '{group_name}' already exists for stream '{stream_name}'",
                    level="warning",
                )

            self._tasks[stream_name] = asyncio.create_task(self._listen_stream(stream_name))
        await self.log(f"Started listening on {len(self._tasks)} streams")

    async def _listen_stream(self, stream_name: str) -> None:
        """Listen to a single stream and process messages.

        Args:
            stream_name: Name of the stream.
        """
        consumer_info = self.consumers[stream_name]
        group_name = consumer_info["group_name"]
        consumer_name = consumer_info["consumer_name"]
        callback = consumer_info["callback"]

        await self.log(f"Listening for messages on stream '{stream_name}'")

        try:
            while self.running:
                try:
                    messages = await self.redis_client.xreadgroup(
                        group_name,
                        consumer_name,
                        streams={stream_name: ">"},
                        count=1,
                        block=1000,
                    )
                    if messages:
                        for stream, entries in messages:
                            for message_id, data in entries:
                                decoded_data = {
                                    k.decode(): (v.decode() if isinstance(v, bytes) else v) for k, v in data.items()
                                }
                                await self.log(f"Message from stream '{stream}': {decoded_data}")
                                if asyncio.iscoroutinefunction(callback):
                                    await callback(decoded_data)
                                else:
                                    callback(decoded_data)
                                await self.redis_client.xack(stream_name, group_name, message_id)
                except aredis.RedisError as e:
                    await self.log(f"Redis error on stream '{stream_name}': {e}", level="error")
                    await asyncio.sleep(1)
        except asyncio.CancelledError:
            await self.log(f"Listener for stream '{stream_name}' cancelled")
        except Exception as e:
            await self.log(f"Unexpected error on stream '{stream_name}': {e}", level="error")

    async def read_from_stream(self, key: str, count: int = 1, block: int | None = None) -> list:
        """Read messages from a stream without a registered consumer.

        Args:
            key: Stream name.
            count: Number of messages to read.
            block: Time in milliseconds to block.

        Returns:
            List of decoded messages.

        Raises:
            ValidationError: If key is invalid.
            StreamError: If reading fails.
        """
        validate_key(key)

        try:
            messages = await self.redis_client.xread({key: "$"}, count=count, block=block)
            decoded_messages = (
                [
                    {
                        "stream": (stream.decode() if isinstance(stream, bytes) else stream),
                        "entries": [
                            {
                                "id": (entry_id.decode() if isinstance(entry_id, bytes) else entry_id),
                                "data": {
                                    k.decode() if isinstance(k, bytes) else k: (
                                        v.decode() if isinstance(v, bytes) else v
                                    )
                                    for k, v in data.items()
                                },
                            }
                            for entry_id, data in entries
                        ],
                    }
                    for stream, entries in messages
                ]
                if messages
                else []
            )
            await self.log(f"Read {len(decoded_messages)} messages from stream '{key}'")
            return decoded_messages
        except (ValidationError, StreamError):
            raise
        except aredis.RedisError as e:
            raise StreamError(f"Failed to read from stream '{key}': {e}") from e

    async def stop_listening(self) -> None:
        """Stop all stream consumers."""
        self.running = False
        for stream_name, task in self._tasks.items():
            task.cancel()
            await self.log(f"Cancelling listener for stream '{stream_name}'")

        if self._tasks:
            await asyncio.gather(*self._tasks.values(), return_exceptions=True)

        self._tasks.clear()
        self.consumers.clear()
        await self.log("All stream consumers stopped")

    async def close(self) -> None:
        """Stop consumers and close connection pool."""
        await self.stop_listening()
        await super().close()
