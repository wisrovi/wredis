"""Async Redis Queue Manager - real asyncio, no threads."""

import asyncio
import json
from collections.abc import Callable
from typing import Any

import redis.asyncio as aredis

from wredis._async_base import AsyncBaseManager
from wredis._exceptions import QueueError, ValidationError
from wredis._serializer import serialize
from wredis._validation import validate_key, validate_ttl


class AsyncRedisQueueManager(AsyncBaseManager):
    """Manages Redis queue operations with real asyncio tasks.

    Uses asyncio.create_task() instead of threads for consumers.

    Attributes:
        poll_interval: Seconds between polls for empty queues.
        callbacks: Mapping of queue names to callback functions.
        _tasks: Dict of queue names to asyncio tasks.
        running: Whether consumption is active.
        max_retries: Maximum retries on error.
    """

    def __init__(
        self,
        poll_interval: int = 1,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        max_retries: int = 3,
        verbose: bool = True,
    ):
        """Initialize the AsyncRedisQueueManager.

        Args:
            poll_interval: Seconds between polls.
            host: Redis hostname.
            port: Redis port.
            db: Redis database number.
            max_retries: Maximum retries on error.
            verbose: Enable logging.
        """
        super().__init__(host=host, port=port, db=db, verbose=verbose)
        self.poll_interval = poll_interval
        self.callbacks: dict[str, Callable[[Any], None]] = {}
        self._tasks: dict[str, asyncio.Task[None]] = {}
        self.running = False
        self.max_retries = max_retries

    def on_message(self, queue_name: str) -> Callable[[Callable], Callable]:
        """Decorator to register a callback for a queue.

        Args:
            queue_name: Name of the Redis queue.

        Returns:
            Decorated callback function.

        Raises:
            ValidationError: If queue name is invalid.
            QueueError: If callback already registered.
        """
        validate_key(queue_name)

        def decorator(func: Callable) -> Callable:
            if queue_name in self.callbacks:
                raise QueueError(
                    f"Callback already registered for queue '{queue_name}'"
                )
            self.callbacks[queue_name] = func
            return func

        return decorator

    async def _consume_queue(self, queue_name: str, callback: Callable) -> None:
        """Consume elements from a queue using asyncio.

        Args:
            queue_name: Name of the queue.
            callback: Function to process messages.
        """
        self.log(f"Starting async consumer for queue '{queue_name}'")
        retries = 0

        while self.running:
            try:
                item = await self.redis_client.brpop(
                    queue_name, timeout=self.poll_interval
                )
                if item:
                    data = json.loads(item[1])
                    self.log(f"Consumed from '{queue_name}': {data}")
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data)
                    else:
                        callback(data)
                    retries = 0
            except json.JSONDecodeError as e:
                self.log(f"Invalid JSON in queue '{queue_name}': {e}", level="error")
                retries += 1
                if retries >= self.max_retries:
                    self.log(f"Max retries for queue '{queue_name}'", level="error")
                    break
            except aredis.RedisError as e:
                self.log(f"Redis error on queue '{queue_name}': {e}", level="error")
                retries += 1
                if retries >= self.max_retries:
                    self.log(f"Max retries for queue '{queue_name}'", level="error")
                    break
            except asyncio.CancelledError:
                self.log(f"Consumer for queue '{queue_name}' cancelled")
                break

    async def start(self) -> None:
        """Start parallel async consumption for all registered queues.

        Raises:
            QueueError: If no callbacks registered.
        """
        if self.running:
            self.log("Consumption already running", level="warning")
            return

        if not self.callbacks:
            raise QueueError(
                "No callbacks registered. Use @on_message decorator first."
            )

        self.running = True
        self._tasks = {}

        for queue_name, callback in self.callbacks.items():
            self._tasks[queue_name] = asyncio.create_task(
                self._consume_queue(queue_name, callback)
            )
            self.log(f"Task started for queue '{queue_name}'")

    async def stop(self) -> None:
        """Stop all consumption tasks."""
        if not self.running:
            self.log("Consumption already stopped", level="warning")
            return

        self.running = False
        for queue_name, task in self._tasks.items():
            task.cancel()
            self.log(f"Cancelling consumer for queue '{queue_name}'")

        if self._tasks:
            await asyncio.gather(*self._tasks.values(), return_exceptions=True)

        self._tasks.clear()
        self.log("All queue consumers stopped")

    async def publish(self, queue_name: str, data: dict, ttl: int = -1) -> None:
        """Publish a message to a Redis queue.

        Args:
            queue_name: Name of the queue.
            data: Message data (dict, serialized to JSON).
            ttl: Optional TTL in seconds.

        Raises:
            ValidationError: If queue_name or ttl is invalid.
            QueueError: If publishing fails.
        """
        validate_key(queue_name)
        validate_ttl(ttl)

        try:
            json_data = serialize(data)
            await self.redis_client.rpush(queue_name, json_data)
            self.log(f"Published to queue '{queue_name}': {data}")

            if ttl > 0:
                await self.redis_client.expire(queue_name, ttl)
                self.log(f"Set TTL of {ttl}s for queue '{queue_name}'")
        except (ValidationError, QueueError):
            raise
        except aredis.RedisError as e:
            raise QueueError(f"Failed to publish to queue '{queue_name}': {e}") from e

    async def get_queue_length(self, queue_name: str) -> int:
        """Get the length of a queue.

        Args:
            queue_name: Name of the queue.

        Returns:
            Number of elements in the queue.

        Raises:
            ValidationError: If queue_name is invalid.
            QueueError: If the operation fails.
        """
        validate_key(queue_name)

        try:
            length = await self.redis_client.llen(queue_name)
            self.log(f"Queue '{queue_name}' length: {length}")
            return length
        except aredis.RedisError as e:
            raise QueueError(
                f"Failed to get length of queue '{queue_name}': {e}"
            ) from e

    async def close(self) -> None:
        """Stop consumers and close connection pool."""
        await self.stop()
        await super().close()
