"""Async Redis Queue Manager."""

import asyncio
import json
import signal
import threading

import redis.asyncio as redis
from loguru import logger


class AsyncRedisQueueManager:
    """Manages Redis queue operations asynchronously.

    Attributes:
        poll_interval: Interval in seconds to poll queues.
        redis_client: Async Redis client instance.
        callbacks: Mapping of queue names to callback functions.
        threads: List of threads handling queue consumption.
        running: Indicates whether queue consumption is active.
        max_retries: Maximum number of retries in case of errors.
        verbose: Enables detailed logging if True.
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
        """Initialize the AsyncRedisQueueManager."""
        self.poll_interval = poll_interval
        self.redis_client = redis.Redis(host=host, port=port, db=db)
        self.callbacks: dict[str, callable] = {}
        self.threads: list[threading.Thread] = []
        self.running = False
        self.max_retries = max_retries
        self.verbose = verbose

    async def log(self, message: str, level: str = "info") -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            getattr(logger, level)(message)

    def on_message(self, queue_name: str):
        """Decorator to register a callback for a specific queue."""

        def decorator(func):
            if queue_name not in self.callbacks:
                self.callbacks[queue_name] = func
            else:
                raise ValueError(f"A callback is already registered for the queue '{queue_name}'")
            return func

        return decorator

    async def _consume_queue(self, queue_name: str, callback) -> None:
        """Consume elements from a specific Redis queue."""
        self.log(f"Starting consumer for queue '{queue_name}'...")
        retries = 0

        while self.running:
            try:
                item = await self.redis_client.brpop(queue_name, timeout=self.poll_interval)
                if item:
                    data = json.loads(item[1])
                    await self.log(f"Consumed from '{queue_name}': {data}")
                    callback(data)
            except json.JSONDecodeError as e:
                await self.log(
                    f"Error decoding JSON from queue '{queue_name}': {e}",
                    level="error",
                )
            except Exception as e:
                await self.log(f"Error consuming from queue '{queue_name}': {e}", level="error")
                retries += 1
                if retries >= self.max_retries:
                    await self.log(
                        f"Maximum retry attempts reached for queue '{queue_name}'.",
                        level="error",
                    )
                    break

    async def start(self) -> None:
        """Start parallel consumption for all registered queues."""
        if self.running:
            await self.log("Consumption is already running.", level="warning")
            return

        self.running = True
        self.threads = []

        for queue_name, callback in self.callbacks.items():
            thread = threading.Thread(
                target=lambda q=queue_name, c=callback: asyncio.create_task(self._consume_queue(q, c))
            )
            thread.daemon = True
            self.threads.append(thread)
            thread.start()
            await self.log(f"Thread started for queue '{queue_name}'.")

    async def stop(self) -> None:
        """Stop consumption for all queues."""
        if not self.running:
            await self.log("Consumption is already stopped.", level="warning")
            return

        self.running = False
        for thread in self.threads:
            if thread.is_alive():
                thread.join()
        await self.log("All threads have been stopped.")

    async def publish(self, queue_name: str, data: dict, ttl: int = -1) -> None:
        """Publish a message to a Redis queue."""
        try:
            json_data = json.dumps(data)
            await self.redis_client.rpush(queue_name, json_data)
            await self.log(f"Published to queue '{queue_name}': {data}")

            if ttl > 0:
                await self.redis_client.expire(queue_name, ttl)
                await self.log(f"Set TTL of {ttl} seconds for queue '{queue_name}'")
        except Exception as e:
            await self.log(f"Error publishing to queue '{queue_name}': {e}", level="error")

    async def get_queue_length(self, queue_name: str) -> int:
        """Retrieve the length of a Redis queue."""
        try:
            length = await self.redis_client.llen(queue_name)
            await self.log(f"Length of queue '{queue_name}': {length}")
            return length
        except Exception as e:
            await self.log(f"Error retrieving length of queue '{queue_name}': {e}", level="error")
            return 0

    async def wait(self) -> None:
        """Keep the program running."""

        def signal_handler(sig, frame):
            self.log("\nStopping consumption due to user interruption...")
            asyncio.create_task(self.stop())

        signal.signal(signal.SIGINT, signal_handler)
        signal.pause()
