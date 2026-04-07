"""Redis Queue Manager with proper error handling and validation."""

import json
import signal
import sys
import threading
from collections.abc import Callable
from typing import Any

import redis

from wredis._base import BaseManager
from wredis._exceptions import QueueError, ValidationError
from wredis._serializer import serialize
from wredis._validation import validate_key, validate_ttl


class RedisQueueManager(BaseManager):
    """Manages Redis queue operations with thread-based consumers.

    Attributes:
        poll_interval: Interval in seconds to poll queues.
        callbacks: Mapping of queue names to callback functions.
        _threads: List of consumer threads.
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
    ) -> None:
        """Initialize the RedisQueueManager.

        Args:
            poll_interval: Seconds between polls for empty queues.
            host: Redis hostname.
            port: Redis port.
            db: Redis database number.
            max_retries: Maximum retries on error.
            verbose: Enable logging.
        """
        super().__init__(host=host, port=port, db=db, verbose=verbose)
        self.poll_interval = poll_interval
        self.callbacks: dict[str, Callable[..., Any]] = {}
        self._threads: list[threading.Thread] = []
        self.running = False
        self.max_retries = max_retries

    def on_message(self, queue_name: str):
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

        def decorator(func):
            if queue_name in self.callbacks:
                raise QueueError(
                    f"Callback already registered for queue '{queue_name}'"
                )
            self.callbacks[queue_name] = func
            return func

        return decorator

    def _consume_queue(self, queue_name: str, callback) -> None:
        """Consume elements from a queue and execute callback.

        Args:
            queue_name: Name of the queue.
            callback: Function to process messages.
        """
        self.log(f"Starting consumer for queue '{queue_name}'")
        retries = 0

        while self.running:
            try:
                item = self.redis_client.brpop(queue_name, timeout=self.poll_interval)
                if item:
                    data = json.loads(item[1])
                    self.log(f"Consumed from '{queue_name}': {data}")
                    callback(data)
                    retries = 0
            except json.JSONDecodeError as e:
                self.log(f"Invalid JSON in queue '{queue_name}': {e}", level="error")
                retries += 1
                if retries >= self.max_retries:
                    self.log(
                        f"Max retries reached for queue '{queue_name}'", level="error"
                    )
                    break
            except redis.RedisError as e:
                self.log(f"Redis error on queue '{queue_name}': {e}", level="error")
                retries += 1
                if retries >= self.max_retries:
                    self.log(
                        f"Max retries reached for queue '{queue_name}'", level="error"
                    )
                    break

    def start(self) -> None:
        """Start parallel consumption for all registered queues.

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
        self._threads = []

        for queue_name, callback in self.callbacks.items():
            thread = threading.Thread(
                target=self._consume_queue, args=(queue_name, callback), daemon=True
            )
            self._threads.append(thread)
            thread.start()
            self.log(f"Thread started for queue '{queue_name}'")

    def stop(self) -> None:
        """Stop consumption and join all threads."""
        if not self.running:
            self.log("Consumption already stopped", level="warning")
            return

        self.running = False
        for thread in self._threads:
            if thread.is_alive():
                thread.join(timeout=5)
        self._threads.clear()
        self.log("All queue consumers stopped")

    def publish(self, queue_name: str, data: dict, ttl: int = -1) -> None:
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
            self.redis_client.rpush(queue_name, json_data)
            self.log(f"Published to queue '{queue_name}': {data}")

            if ttl > 0:
                self.redis_client.expire(queue_name, ttl)
                self.log(f"Set TTL of {ttl}s for queue '{queue_name}'")
        except (ValidationError, QueueError):
            raise
        except Exception as e:
            raise QueueError(f"Failed to publish to queue '{queue_name}': {e}") from e

    def get_queue_length(self, queue_name: str) -> int:
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
            length = self.redis_client.llen(queue_name)
            self.log(f"Queue '{queue_name}' length: {length}")
            return length
        except redis.RedisError as e:
            raise QueueError(
                f"Failed to get length of queue '{queue_name}': {e}"
            ) from e

    def wait(self) -> None:
        """Keep the program running until SIGINT."""

        def signal_handler(sig, frame):
            self.log("Stopping due to user interruption")
            self.stop()

        signal.signal(signal.SIGINT, signal_handler)
        signal.pause()
