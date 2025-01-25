import redis
import json
import threading
import signal
from loguru import logger


class RedisQueueManager:
    """
    Manages Redis queue operations, including publishing messages, consuming queues,
    and managing TTL (Time-to-Live) for queue keys.

    Attributes:
        poll_interval (int): Interval (in seconds) to poll queues for messages.
        redis_client (redis.StrictRedis): Redis client instance.
        callbacks (dict): Mapping of queue names to their respective callback functions.
        threads (list): List of threads handling queue consumption.
        running (bool): Indicates whether queue consumption is active.
        max_retries (int): Maximum number of retries in case of errors.
        verbose (bool): Enables detailed logging if True.
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
        """
        Initializes the RedisQueueManager with connection details.

        Args:
            poll_interval (int): Interval (in seconds) to poll queues.
            host (str): Hostname of the Redis server.
            port (int): Port number of the Redis server.
            db (int): Redis database index.
            max_retries (int): Maximum number of retries in case of errors.
            verbose (bool): Enable detailed logging if True.
        """
        self.poll_interval = poll_interval
        self.redis_client = redis.StrictRedis(host=host, port=port, db=db)
        self.callbacks = {}
        self.threads = []
        self.running = False
        self.max_retries = max_retries
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

    def on_message(self, queue_name: str):
        """
        Decorator to register a callback function for a specific Redis queue.

        Args:
            queue_name (str): The name of the Redis queue.

        Returns:
            Callable: The decorated callback function.
        """

        def decorator(func):
            if queue_name not in self.callbacks:
                self.callbacks[queue_name] = func
            else:
                raise ValueError(
                    f"A callback is already registered for the queue '{queue_name}'"
                )
            return func

        return decorator

    def _consume_queue(self, queue_name: str, callback) -> None:
        """
        Consumes elements from a specific Redis queue and executes its callback.

        Args:
            queue_name (str): The name of the Redis queue.
            callback (Callable): The callback function to process queue messages.
        """
        self.log(f"Starting consumer for queue '{queue_name}'...")
        retries = 0

        while self.running:
            try:
                item = self.redis_client.brpop(queue_name, timeout=self.poll_interval)
                if item:
                    data = json.loads(item[1])
                    self.log(f"Consumed from '{queue_name}': {data}")
                    callback(data)
                else:
                    pass  # Queue is empty
            except json.JSONDecodeError as e:
                self.log(
                    f"Error decoding JSON from queue '{queue_name}': {e}",
                    level="error",
                )
            except Exception as e:
                self.log(
                    f"Error consuming from queue '{queue_name}': {e}", level="error"
                )
                retries += 1
                if retries >= self.max_retries:
                    self.log(
                        f"Maximum retry attempts reached for queue '{queue_name}'.",
                        level="error",
                    )
                    break

    def start(self) -> None:
        """
        Starts parallel consumption for all registered queues.
        """
        if self.running:
            self.log("Consumption is already running.", level="warning")
            return

        self.running = True
        self.threads = []

        for queue_name, callback in self.callbacks.items():
            thread = threading.Thread(
                target=self._consume_queue, args=(queue_name, callback)
            )
            thread.daemon = True
            self.threads.append(thread)
            thread.start()
            self.log(f"Thread started for queue '{queue_name}'.")

    def stop(self) -> None:
        """
        Stops consumption for all queues and their threads.
        """
        if not self.running:
            self.log("Consumption is already stopped.", level="warning")
            return

        self.running = False
        for thread in self.threads:
            if thread.is_alive():
                thread.join()
        self.log("All threads have been stopped.")

    def publish(self, queue_name: str, data: dict, ttl: int = -1) -> None:
        """
        Publishes a message to a Redis queue with an optional TTL.

        Args:
            queue_name (str): The name of the Redis queue.
            data (dict): The message to publish, serialized to JSON.
            ttl (int): Time-to-live for the message in seconds. If -1, no TTL is set.
        """
        try:
            json_data = json.dumps(data)
            self.redis_client.rpush(queue_name, json_data)
            self.log(f"Published to queue '{queue_name}': {data}")

            if ttl > 0:
                self.redis_client.expire(queue_name, ttl)
                self.log(f"Set TTL of {ttl} seconds for queue '{queue_name}'")
        except Exception as e:
            self.log(f"Error publishing to queue '{queue_name}': {e}", level="error")

    def get_queue_length(self, queue_name: str) -> int:
        """
        Retrieves the length of a Redis queue.

        Args:
            queue_name (str): The name of the Redis queue.

        Returns:
            int: The number of elements in the queue.
        """
        try:
            length = self.redis_client.llen(queue_name)
            self.log(f"Length of queue '{queue_name}': {length}")
            return length
        except Exception as e:
            self.log(
                f"Error retrieving length of queue '{queue_name}': {e}", level="error"
            )
            return 0

    def wait(self) -> None:
        """
        Keeps the program running while consumption is active without using while True.
        """

        def signal_handler(sig, frame):
            self.log("\nStopping consumption due to user interruption...")
            self.stop()

        signal.signal(signal.SIGINT, signal_handler)
        signal.pause()
