"""Async Redis Pub/Sub Manager."""

import contextlib
import json
from threading import Thread

import redis.asyncio as redis
from loguru import logger


class AsyncRedisPubSubManager:
    """Manages Redis Pub/Sub functionality asynchronously.

    Attributes:
        redis_client: Async Redis client instance.
        pubsub: Redis Pub/Sub instance.
        subscribers: Dictionary of channels and their callbacks.
        threads: List of threads listening to channels.
        verbose: Enables detailed logging if True.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        verbose: bool = True,
    ):
        """Initialize the AsyncRedisPubSubManager."""
        self.redis_client = redis.Redis(host=host, port=port, db=db)
        self.pubsub = self.redis_client.pubsub()
        self.subscribers: dict[str, callable] = {}
        self.threads: list[Thread] = []
        self.verbose = verbose

    async def log(self, message: str, level: str = "info") -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            getattr(logger, level)(message)

    async def publish_message(self, channel: str, message: str | dict) -> None:
        """Publish a message to a Redis channel."""
        try:
            if isinstance(message, dict):
                message = json.dumps(message)
            elif not isinstance(message, str):
                raise ValueError("Message must be a string or a JSON dictionary.")

            await self.redis_client.publish(channel, message)
            await self.log(f"Message published to channel '{channel}': {message}")
        except Exception as e:
            logger.error(f"Error publishing message to channel '{channel}': {e}")

    def on_message(self, channel: str):
        """Decorator to register a callback function for a specific channel."""

        def decorator(callback):
            if channel not in self.subscribers:
                self.subscribers[channel] = callback
                self._start_listener(channel)
                self.log(f"Subscribed to channel '{channel}' with handler '{callback.__name__}'")
            else:
                self.log(
                    f"Handler already registered for channel '{channel}'",
                    level="warning",
                )
            return callback

        return decorator

    def _start_listener(self, channel: str) -> None:
        """Start a thread to listen for messages on a specific channel."""

        def listener():
            local_pubsub = self.redis_client.pubsub()
            local_pubsub.subscribe(channel)
            self.log(f"Listening for messages on channel '{channel}'")

            for message in local_pubsub.listen():
                if message["type"] == "message" and channel in self.subscribers:
                    callback = self.subscribers[channel]
                    data = message["data"].decode()
                    with contextlib.suppress(json.JSONDecodeError):
                        data = json.loads(data)
                    callback(data)

        thread = Thread(target=listener)
        thread.daemon = True
        thread.start()
        self.threads.append(thread)

    async def stop_listeners(self) -> None:
        """Stop all listener threads."""
        for thread in self.threads:
            if thread.is_alive():
                self.log("Stopping listener thread...")
        self.threads.clear()
