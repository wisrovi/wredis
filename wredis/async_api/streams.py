"""Async Redis Stream Manager."""

import asyncio
import signal
import threading
from collections.abc import Callable

import redis.asyncio as redis
from loguru import logger


class AsyncRedisStreamManager:
    """Manages Redis streams asynchronously with consumer groups.

    Attributes:
        redis_client: Async Redis client instance.
        verbose: Enables detailed logging if True.
        consumers: Dictionary of registered consumers.
        running: Indicates whether the manager is actively consuming.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        verbose: bool = True,
    ):
        """Initialize the AsyncRedisStreamManager."""
        self.redis_client = redis.Redis(host=host, port=port, db=db)
        self.verbose = verbose
        self.consumers: dict[str, dict[str, str | Callable]] = {}
        self.running = False

    async def log(self, message: str, level: str = "info") -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            getattr(logger, level)(message)

    async def add_to_stream(self, key: str, data: dict[str, str], ttl: int | None = None) -> str | None:
        """Add a message to the stream."""
        try:
            message_id = await self.redis_client.xadd(key, data)
            await self.log(f"Added to stream '{key}' with ID {message_id}")

            if ttl:
                await self.redis_client.expire(key, ttl)
                await self.log(f"Set TTL of {ttl} seconds for stream '{key}'")

            return message_id
        except Exception as e:
            logger.error(f"Error adding to stream '{key}': {e}")
            return None

    def on_message(self, stream_name: str, group_name: str, consumer_name: str) -> Callable:
        """Decorator to register a consumer for a stream."""

        def decorator(func: Callable) -> Callable:
            if stream_name not in self.consumers:
                self.consumers[stream_name] = {
                    "group_name": group_name,
                    "consumer_name": consumer_name,
                    "callback": func,
                }
                self._start_listener(stream_name)
                logger.info(
                    f"Registered consumer for stream '{stream_name}' "
                    f"with group '{group_name}' and consumer '{consumer_name}'"
                )
            else:
                logger.warning(f"A consumer is already registered for the stream '{stream_name}'")
            return func

        return decorator

    async def _decode_message(self, data: dict[bytes, bytes]) -> dict[str, str]:
        """Decode the keys and values of a received message."""
        return {key.decode(): value.decode() if isinstance(value, bytes) else value for key, value in data.items()}

    def _start_listener(self, stream_name: str) -> None:
        """Start a thread to listen for messages on a specific stream."""

        def listener() -> None:
            consumer_info = self.consumers[stream_name]
            group_name = consumer_info["group_name"]
            consumer_name = consumer_info["consumer_name"]
            callback = consumer_info["callback"]

            # Create consumer group if it does not exist
            try:
                asyncio.get_event_loop().run_until_complete(
                    self.redis_client.xgroup_create(stream_name, group_name, id="0", mkstream=True)
                )
            except redis.exceptions.ResponseError:
                self.log(
                    f"Group '{group_name}' already exists for stream '{stream_name}'",
                    level="warning",
                )

            self.log(f"Listening for messages on stream '{stream_name}'...")
            self.running = True
            while self.running:
                try:
                    messages = asyncio.get_event_loop().run_until_complete(
                        self.redis_client.xreadgroup(
                            group_name,
                            consumer_name,
                            streams={stream_name: ">"},
                            count=1,
                            block=1000,
                        )
                    )
                    for stream, entries in messages:
                        for message_id, data in entries:
                            decoded_data = asyncio.get_event_loop().run_until_complete(self._decode_message(data))
                            logger.info(f"Message received from stream '{stream}': {decoded_data}")
                            callback(decoded_data)
                            asyncio.get_event_loop().run_until_complete(
                                self.redis_client.xack(stream_name, group_name, message_id)
                            )
                except Exception as e:
                    logger.error(f"Error reading from stream '{stream_name}': {e}")

        thread = threading.Thread(target=listener)
        thread.daemon = True
        thread.start()

    async def read_from_stream(self, key: str, count: int = 1, block: int | None = None) -> list:
        """Read messages from the stream without a registered consumer."""
        try:
            messages = await self.redis_client.xread({key: "$"}, count=count, block=block)
            decoded_messages = [
                {
                    "stream": stream.decode(),
                    "entries": [
                        {
                            "id": entry_id.decode(),
                            "data": await self._decode_message(data),
                        }
                        for entry_id, data in entries
                    ],
                }
                for stream, entries in messages
            ]
            await self.log(f"Messages read from stream '{key}': {decoded_messages}")
            return decoded_messages
        except Exception as e:
            logger.error(f"Error reading messages from stream '{key}': {e}")
            return []

    async def wait(self) -> None:
        """Keep the program active and handle interrupt signals."""

        def signal_handler(sig: int, frame) -> None:
            logger.info("Stopping consumers...")
            self.running = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.pause()

    async def set_json(self, key: str, value: dict | list, ttl: int = -1) -> None:
        """Set a JSON value in Redis."""
        import json

        try:
            json_value = json.dumps(value)
            await self.redis_client.set(key, json_value)
            await self.log(f"Set JSON value for key '{key}'.")

            if ttl > 0:
                await self.redis_client.expire(key, ttl)
                await self.log(f"Set TTL of {ttl} seconds for '{key}'.")
        except Exception as e:
            logger.error(f"Error setting JSON for key '{key}': {e}")

    async def get_json(self, key: str) -> dict | list | None:
        """Get and deserialize a JSON value from Redis."""
        import json

        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting JSON for key '{key}': {e}")
            return None

    async def delete_key(self, key: str) -> bool:
        """Delete a key from Redis."""
        try:
            result = await self.redis_client.delete(key)
            await self.log(f"Deleted key '{key}': {result > 0}")
            return result > 0
        except Exception as e:
            logger.error(f"Error deleting key '{key}': {e}")
            return False
