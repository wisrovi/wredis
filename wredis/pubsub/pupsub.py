import redis
from threading import Thread
import signal
import json
from loguru import logger


class RedisPubSubManager:
    """
    Manages Redis Pub/Sub functionality, including publishing messages and subscribing to channels.

    Attributes:
        redis_client (redis.StrictRedis): Redis client instance.
        pubsub (redis.client.PubSub): Redis Pub/Sub instance.
        subscribers (dict): Dictionary of channels and their associated callbacks.
        threads (list): List of threads listening to channels.
        verbose (bool): Enables detailed logging if True.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        verbose: bool = True,
    ):
        """
        Initializes the RedisPubSubManager with connection details.

        Args:
            host (str): Hostname of the Redis server.
            port (int): Port number of the Redis server.
            db (int): Redis database index.
            verbose (bool): Enable detailed logging if True.
        """
        self.redis_client = redis.StrictRedis(host=host, port=port, db=db)
        self.pubsub = self.redis_client.pubsub()
        self.subscribers = {}
        self.threads = []
        self.verbose = verbose

    def log(self, message: str, level: str = "info") -> None:
        """
        Logs a message if verbose mode is enabled.

        Args:
            message (str): The message to log.
            level (str): The log level (e.g., "info", "warning", "error").
        """
        if self.verbose:
            getattr(logger, level)(message)

    def publish_message(self, channel: str, message: str | dict) -> None:
        """
        Publishes a message to a Redis channel. Supports both strings and JSON.

        Args:
            channel (str): The channel to publish the message to.
            message (str | dict): The message to publish. JSON messages are serialized automatically.

        Raises:
            ValueError: If the message is neither a string nor a dictionary.
        """
        try:
            if isinstance(message, dict):
                message = json.dumps(message)
            elif not isinstance(message, str):
                raise ValueError("Message must be a string or a JSON dictionary.")

            self.redis_client.publish(channel, message)
            self.log(f"Message published to channel '{channel}': {message}")
        except Exception as e:
            logger.error(f"Error publishing message to channel '{channel}': {e}")

    def on_message(self, channel: str):
        """
        Decorator to register a callback function for a specific Redis channel.

        Args:
            channel (str): The channel to subscribe to.

        Returns:
            Callable: The decorated callback function.
        """

        def decorator(callback):
            if channel not in self.subscribers:
                self.subscribers[channel] = callback
                self._start_listener(channel)
                self.log(
                    f"Subscribed to channel '{channel}' with handler '{callback.__name__}'"
                )
            else:
                self.log(
                    f"Handler already registered for channel '{channel}'",
                    level="warning",
                )
            return callback

        return decorator

    def _start_listener(self, channel: str) -> None:
        """
        Starts a thread to listen for messages on a specific channel and execute the associated callback.

        Args:
            channel (str): The channel to listen to.
        """

        def listener():
            local_pubsub = self.redis_client.pubsub()
            local_pubsub.subscribe(channel)
            self.log(f"Listening for messages on channel '{channel}'")

            for message in local_pubsub.listen():
                if message["type"] == "message" and channel in self.subscribers:
                    callback = self.subscribers[channel]
                    data = message["data"].decode()
                    try:
                        data = json.loads(data)
                    except json.JSONDecodeError:
                        pass
                    callback(data)

        thread = Thread(target=listener)
        thread.daemon = True
        thread.start()
        self.threads.append(thread)

    def stop_listeners(self) -> None:
        """
        Stops all listener threads.
        """
        for thread in self.threads:
            if thread.is_alive():
                self.log("Stopping listener thread...")
        self.threads.clear()


# Example usage
if __name__ == "__main__":
    # Create an instance of RedisPubSubManager
    pubsub_manager = RedisPubSubManager(host="localhost", verbose=True)

    # Subscribe a function to "channel_1"
    @pubsub_manager.on_message("channel_1")
    def handle_channel_1(message):
        if isinstance(message, dict):
            logger.info(f"[channel_1] Received message (JSON): {message}")
        else:
            logger.info(f"[channel_1] Received message (String): {message}")

    # Subscribe a function to "channel_2"
    @pubsub_manager.on_message("channel_2")
    def handle_channel_2(message):
        if isinstance(message, dict):
            logger.info(f"[channel_2] Received message (JSON): {message}")
        else:
            logger.info(f"[channel_2] Received message (String): {message}")

    # Publish test messages
    pubsub_manager.publish_message("channel_1", "Hello from channel_1!")
    pubsub_manager.publish_message("channel_2", {"greeting": "Hello from channel_2!"})

    # Handle Ctrl+C to exit cleanly
    def signal_handler(sig, frame):
        logger.info("\nStopping program...")
        pubsub_manager.stop_listeners()
        logger.info("Program stopped.")
        exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Keep the program running without while True
    signal.pause()
