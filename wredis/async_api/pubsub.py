"""Async Redis Pub/Sub Manager - real asyncio, no threads."""

import asyncio
import contextlib
from collections.abc import Callable
from typing import Any

import redis.asyncio as aredis
from loguru import logger

from wredis._async_base import AsyncBaseManager
from wredis._exceptions import PubSubError, ValidationError
from wredis._serializer import deserialize, serialize
from wredis._validation import validate_key


class AsyncRedisPubSubManager(AsyncBaseManager):
    """Manages Redis Pub/Sub functionality with real asyncio.

    Uses asyncio tasks instead of threads for message listening.

    Attributes:
        redis_client: Async Redis client instance.
        subscribers: Dictionary of channels and their callbacks.
        _tasks: Dictionary of channel names to asyncio tasks.
        verbose: Enables detailed logging if True.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        verbose: bool = True,
    ):
        """Initialize the AsyncRedisPubSubManager.

        Args:
            host: Redis server hostname.
            port: Redis server port.
            db: Redis database number.
            verbose: Enable detailed logging.
        """
        super().__init__(
            host=host,
            port=port,
            db=db,
            decode_responses=False,
            verbose=verbose,
        )
        self.subscribers: dict[str, Callable[[Any], None]] = {}
        self._tasks: dict[str, asyncio.Task[None]] = {}
        self._running = False

    async def publish_message(self, channel: str, message: str | dict) -> None:
        """Publish a message to a Redis channel.

        Args:
            channel: The channel to publish to.
            message: String or dict (auto-serialized to JSON).

        Raises:
            ValidationError: If channel name is invalid.
            PubSubError: If publishing fails.
        """
        validate_key(channel)

        try:
            if isinstance(message, dict):
                payload = serialize(message)
            elif isinstance(message, str):
                payload = message
            else:
                raise ValidationError(
                    "Message must be a string or a JSON-serializable dictionary."
                )

            await self.redis_client.publish(channel, payload)
            self.log(f"Message published to channel '{channel}': {payload}")
        except (ValidationError, PubSubError):
            raise
        except aredis.RedisError as e:
            raise PubSubError(f"Failed to publish to channel '{channel}': {e}") from e

    def on_message(self, channel: str) -> Callable[[Callable], Callable]:
        """Decorator to register an async callback for a specific channel.

        Args:
            channel: The channel to subscribe to.

        Returns:
            Decorated callback function.

        Raises:
            ValidationError: If channel name is invalid.
            PubSubError: If channel is already subscribed.
        """
        validate_key(channel)

        def decorator(callback: Callable) -> Callable:
            if channel in self.subscribers:
                raise PubSubError(f"Handler already registered for channel '{channel}'")

            self.subscribers[channel] = callback
            if self._running:
                self._tasks[channel] = asyncio.create_task(
                    self._listen_channel(channel, callback)
                )
            self.log(
                f"Subscribed to channel '{channel}' with handler '{callback.__name__}'"
            )
            return callback

        return decorator

    async def start_listening(self) -> None:
        """Start listening on all registered channels.

        Creates asyncio tasks for each subscribed channel.
        """
        self._running = True
        for channel, callback in self.subscribers.items():
            self._tasks[channel] = asyncio.create_task(
                self._listen_channel(channel, callback)
            )
        self.log(f"Started listening on {len(self._tasks)} channels")

    async def _listen_channel(self, channel: str, callback: Callable) -> None:
        """Listen to a single channel and invoke callback on messages.

        Args:
            channel: Channel name.
            callback: Function to call with received messages.
        """
        pubsub = self.redis_client.pubsub()
        try:
            await pubsub.subscribe(channel)
            self.log(f"Listening for messages on channel '{channel}'")

            async for message in pubsub.listen():
                if message["type"] == "message" and channel in self.subscribers:
                    try:
                        data = message["data"]
                        if isinstance(data, bytes):
                            data = data.decode()
                        with contextlib.suppress(Exception):
                            data = deserialize(data)
                        if asyncio.iscoroutinefunction(callback):
                            await callback(data)
                        else:
                            callback(data)
                    except Exception as e:
                        self.log(
                            f"Error processing message on '{channel}': {e}",
                            level="error",
                        )
        except asyncio.CancelledError:
            self.log(f"Listener for channel '{channel}' cancelled")
        except aredis.RedisError as e:
            self.log(f"Redis error on channel '{channel}': {e}", level="error")
        finally:
            with contextlib.suppress(Exception):
                await pubsub.unsubscribe(channel)
                await pubsub.close()

    async def stop_listening(self) -> None:
        """Stop all listening tasks and clear subscribers."""
        self._running = False
        for channel, task in self._tasks.items():
            task.cancel()
            self.log(f"Cancelling listener for channel '{channel}'")

        if self._tasks:
            await asyncio.gather(*self._tasks.values(), return_exceptions=True)

        self._tasks.clear()
        self.subscribers.clear()
        self.log("All listeners stopped")

    async def close(self) -> None:
        """Stop listeners and close connection pool."""
        await self.stop_listening()
        await super().close()
