"""Redis Pub/Sub management implementation."""

from __future__ import annotations

import contextlib
import json
import signal
import sys
from collections.abc import Callable
from threading import Thread
from typing import Any

import redis
from loguru import logger

from wredis._base import BaseManager
from wredis._exceptions import PubSubError, ValidationError
from wredis._serializer import deserialize, serialize
from wredis._validation import validate_key


class RedisPubSubManager(BaseManager):
    """Manages Redis Pub/Sub functionality.

    Includes publishing messages and subscribing to channels.

    Attributes:
        redis_client: Redis client instance.
        pubsub: Redis Pub/Sub instance.
        subscribers: Dictionary of channels and their associated callbacks.
        verbose: Enables detailed logging if True.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        verbose: bool = True,
    ):
        """Initialize the RedisPubSubManager with connection details.

        Args:
            host: Hostname of the Redis server.
            port: Port number of the Redis server.
            db: Redis database index.
            verbose: Enable detailed logging if True.
        """
        super().__init__(
            host=host,
            port=port,
            db=db,
            decode_responses=False,
            verbose=verbose,
        )
        self.pubsub = self.redis_client.pubsub()
        self.subscribers: dict[str, Callable[..., Any]] = {}

    def publish_message(self, channel: str, message: str | dict) -> None:
        """Publish a message to a Redis channel.

        Args:
            channel: The channel to publish the message to.
            message: The message to publish (string or dict for JSON).

        Raises:
            ValidationError: If the channel name is invalid.
            PubSubError: If publishing fails.
        """
        validate_key(channel)

        try:
            if isinstance(message, dict):
                payload = serialize(message)
            elif isinstance(message, str):
                payload = message
            else:
                raise ValidationError("Message must be a string or a JSON-serializable dictionary.")

            self._execute("publish", channel, payload)
            self.log(f"Message published to channel '{channel}': {payload}")
        except (ValidationError, PubSubError):
            raise
        except Exception as e:
            raise PubSubError(f"Error publishing message to channel '{channel}': {e}") from e

    def on_message(self, channel: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to register a callback function for a specific Redis channel.

        Args:
            channel: The channel to subscribe to.

        Returns:
            The decorated callback function.

        Raises:
            ValidationError: If the channel name is invalid.
            PubSubError: If the channel is already subscribed.
        """
        validate_key(channel)

        def decorator(callback: Callable[..., Any]) -> Callable[..., Any]:
            if channel in self.subscribers:
                raise PubSubError(f"Handler already registered for channel '{channel}'")

            self.subscribers[channel] = callback
            self._start_listener(channel)
            self.log(f"Subscribed to channel '{channel}' with handler '{callback.__name__}'")
            return callback

        return decorator

    def _start_listener(self, channel: str) -> None:
        """Start a thread to listen for messages on a specific channel.

        Args:
            channel: The channel to listen to.

        Raises:
            PubSubError: If the listener thread fails to start.
        """

        def listener() -> None:
            local_pubsub = self.redis_client.pubsub()
            try:
                local_pubsub.subscribe(channel)
                self.log(f"Listening for messages on channel '{channel}'")

                for message in local_pubsub.listen():
                    if message["type"] == "message" and channel in self.subscribers:
                        callback = self.subscribers[channel]
                        try:
                            data = message["data"].decode()
                        except (AttributeError, UnicodeDecodeError) as e:
                            self.log(
                                f"Failed to decode message on channel '{channel}': {e}",
                                level="error",
                            )
                            continue

                        with contextlib.suppress(Exception):
                            data = deserialize(data)

                        try:
                            callback(data)
                        except Exception as e:
                            self.log(
                                f"Callback error on channel '{channel}': {e}",
                                level="error",
                            )
            except redis.RedisError as e:
                self.log(
                    f"Redis error on channel '{channel}': {e}",
                    level="error",
                )
            finally:
                with contextlib.suppress(redis.RedisError):
                    local_pubsub.unsubscribe(channel)
                    local_pubsub.close()

        thread = Thread(target=listener, daemon=True)
        try:
            thread.start()
        except RuntimeError as e:
            raise PubSubError(f"Failed to start listener for channel '{channel}': {e}") from e

    def stop_listeners(self) -> None:
        """Stop all listener threads and unsubscribe from all channels."""
        for channel in list(self.subscribers.keys()):
            self.log(f"Unsubscribing from channel '{channel}'")
        self.subscribers.clear()
        with contextlib.suppress(redis.RedisError):
            self.pubsub.unsubscribe()
            self.pubsub.close()
        self.log("All listeners stopped")


if __name__ == "__main__":
    pubsub_manager = RedisPubSubManager(host="localhost", verbose=True)

    @pubsub_manager.on_message("channel_1")
    def handle_channel_1(message: Any) -> None:
        """Handle messages from channel_1."""
        if isinstance(message, dict):
            logger.info(f"[channel_1] Received message (JSON): {message}")
        else:
            logger.info(f"[channel_1] Received message (String): {message}")

    @pubsub_manager.on_message("channel_2")
    def handle_channel_2(message: Any) -> None:
        """Handle messages from channel_2."""
        if isinstance(message, dict):
            logger.info(f"[channel_2] Received message (JSON): {message}")
        else:
            logger.info(f"[channel_2] Received message (String): {message}")

    pubsub_manager.publish_message("channel_1", "Hello from channel_1!")
    pubsub_manager.publish_message("channel_2", {"greeting": "Hello from channel_2!"})

    def signal_handler(sig: int, frame: Any) -> None:
        """Handle SIGINT signal."""
        logger.info("\nStopping program...")
        pubsub_manager.stop_listeners()
        logger.info("Program stopped.")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()
