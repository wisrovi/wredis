import redis
from loguru import logger
import threading
import signal
from typing import Callable, Dict, Optional


class RedisStreamManager:
    """
    Manages Redis streams, allowing message publishing and consumption with support for message groups and TTL.

    Attributes:
        redis_client (redis.StrictRedis): Redis client instance.
        verbose (bool): Enables detailed logging if True.
        consumers (Dict): Dictionary of registered consumers for streams.
        running (bool): Indicates whether the manager is actively consuming messages.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        verbose: bool = True,
    ):
        """
        Initializes the RedisStreamManager with connection details.

        Args:
            host (str): Hostname of the Redis server.
            port (int): Port number of the Redis server.
            db (int): Redis database index.
            verbose (bool): Enable detailed logging if True.
        """
        self.redis_client = redis.StrictRedis(host=host, port=port, db=db)
        self.verbose = verbose
        self.consumers: Dict[str, Dict[str, str]] = {}
        self.running = False

    def log(self, message: str, level: str = "info") -> None:
        """
        Logs a message if verbose mode is enabled.

        Args:
            message (str): The message to log.
            level (str): The log level (e.g., "info", "warning", "error").
        """
        if self.verbose:
            getattr(logger, level)(message)

    def add_to_stream(
        self, key: str, data: Dict[str, str], ttl: Optional[int] = None
    ) -> Optional[str]:
        """
        Adds a message to the stream and optionally sets a TTL for the stream.

        Args:
            key (str): Name of the stream in Redis.
            data (Dict[str, str]): Message data to add to the stream.
            ttl (Optional[int]): Time-to-live for the stream in seconds. If None, no TTL is set.

        Returns:
            Optional[str]: The ID of the added message, or None if an error occurred.
        """
        try:
            message_id = self.redis_client.xadd(key, data)
            self.log(f"Added to stream '{key}' with ID {message_id}")

            if ttl:
                self.redis_client.expire(key, ttl)
                self.log(f"Set TTL of {ttl} seconds for stream '{key}'")

            return message_id
        except Exception as e:
            logger.error(f"Error adding to stream '{key}': {e}")
            return None

    def on_message(
        self, stream_name: str, group_name: str, consumer_name: str
    ) -> Callable:
        """
        Decorator to register a consumer for a specific stream.

        Args:
            stream_name (str): Name of the Redis stream.
            group_name (str): Name of the consumer group.
            consumer_name (str): Name of the consumer.

        Returns:
            Callable: A decorator that registers the consumer callback function.
        """

        def decorator(func: Callable) -> Callable:
            if stream_name not in self.consumers:
                self.consumers[stream_name] = {
                    "group_name": group_name,
                    "consumer_name": consumer_name,
                    "callback": func,
                }
                self._start_listener(stream_name)
                self.log(
                    f"Registered consumer for stream '{stream_name}' with group '{group_name}' and consumer '{consumer_name}'"
                )
            else:
                logger.warning(
                    f"A consumer is already registered for the stream '{stream_name}'"
                )
            return func

        return decorator

    def _decode_message(self, data: Dict[bytes, bytes]) -> Dict[str, str]:
        """
        Decodes the keys and values of a received message.

        Args:
            data (Dict[bytes, bytes]): Raw message data from Redis.

        Returns:
            Dict[str, str]: Decoded message data.
        """
        return {
            key.decode(): value.decode() if isinstance(value, bytes) else value
            for key, value in data.items()
        }

    def _start_listener(self, stream_name: str) -> None:
        """
        Starts a thread to listen for messages on a specific stream.

        Args:
            stream_name (str): Name of the Redis stream.
        """

        def listener() -> None:
            consumer_info = self.consumers[stream_name]
            group_name = consumer_info["group_name"]
            consumer_name = consumer_info["consumer_name"]
            callback = consumer_info["callback"]

            # Create the consumer group if it does not exist
            try:
                self.redis_client.xgroup_create(
                    stream_name, group_name, id="0", mkstream=True
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
                    messages = self.redis_client.xreadgroup(
                        group_name,
                        consumer_name,
                        streams={stream_name: ">"},
                        count=1,
                        block=1000,
                    )
                    for stream, entries in messages:
                        for message_id, data in entries:
                            decoded_data = self._decode_message(data)
                            self.log(
                                f"Message received from stream '{stream}': {decoded_data}"
                            )
                            callback(decoded_data)
                            self.redis_client.xack(stream_name, group_name, message_id)
                except Exception as e:
                    logger.error(f"Error reading from stream '{stream_name}': {e}")

        thread = threading.Thread(target=listener)
        thread.daemon = True
        thread.start()

    def read_from_stream(
        self, key: str, count: int = 1, block: Optional[int] = None
    ) -> list:
        """
        Reads messages from the stream without a registered consumer.

        Args:
            key (str): Name of the stream in Redis.
            count (int): Number of messages to read.
            block (Optional[int]): Time in milliseconds to block if no messages are available.

        Returns:
            list: List of decoded messages from the stream.
        """
        try:
            messages = self.redis_client.xread({key: "$"}, count=count, block=block)
            decoded_messages = [
                {
                    "stream": stream.decode(),
                    "entries": [
                        {"id": entry_id.decode(), "data": self._decode_message(data)}
                        for entry_id, data in entries
                    ],
                }
                for stream, entries in messages
            ]
            self.log(f"Messages read from stream '{key}': {decoded_messages}")
            return decoded_messages
        except Exception as e:
            logger.error(f"Error reading messages from stream '{key}': {e}")
            return []

    def wait(self) -> None:
        """
        Keeps the program active and handles interrupt signals to stop consumers cleanly.
        """

        def signal_handler(sig: int, frame: Optional[object]) -> None:
            logger.info("Stopping consumers...")
            self.running = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.pause()
