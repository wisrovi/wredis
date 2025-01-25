import redis
from loguru import logger


class RedisBitmapManager:
    """
    Manages Redis bitmap operations, including setting, retrieving, and counting bits,
    as well as managing TTL (Time-to-Live) for bitmap keys.

    Attributes:
        redis_client (redis.StrictRedis): Redis client instance.
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
        Initializes the RedisBitmapManager with connection details.

        Args:
            host (str): Hostname of the Redis server.
            port (int): Port number of the Redis server.
            db (int): Redis database index.
            verbose (bool): Enable detailed logging if True.
        """
        self.redis_client = redis.StrictRedis(host=host, port=port, db=db)
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

    def set_bit(self, key: str, offset: int, value: int, ttl: int = -1) -> None:
        """
        Sets a bit at a specific position in a bitmap and optionally sets a TTL.

        Args:
            key (str): The Redis key for the bitmap.
            offset (int): The position of the bit to set.
            value (int): The value to set the bit to (0 or 1).
            ttl (int): The time-to-live for the key in seconds. If -1, no TTL is set.
        """
        try:
            self.redis_client.setbit(key, offset, value)
            self.log(f"Set bit in '{key}' at position {offset} to value {value}.")

            if ttl > 0:
                self.redis_client.expire(key, ttl)
                self.log(f"Set TTL of {ttl} seconds for '{key}'.")
        except Exception as e:
            logger.error(f"Error setting bit in '{key}': {e}")

    def get_bit(self, key: str, offset: int) -> int:
        """
        Retrieves the value of a bit at a specific position in a bitmap.

        Args:
            key (str): The Redis key for the bitmap.
            offset (int): The position of the bit to retrieve.

        Returns:
            int: The value of the bit (0 or 1).
        """
        try:
            bit_value = self.redis_client.getbit(key, offset)
            self.log(f"Bit value in '{key}' at position {offset}: {bit_value}.")
            return bit_value
        except Exception as e:
            logger.error(f"Error retrieving bit from '{key}': {e}")
            return 0

    def count_bits(self, key: str) -> int:
        """
        Counts the number of bits set to 1 in a bitmap.

        Args:
            key (str): The Redis key for the bitmap.

        Returns:
            int: The number of bits set to 1.
        """
        try:
            bit_count = self.redis_client.bitcount(key)
            self.log(f"Number of bits set to 1 in '{key}': {bit_count}.")
            return bit_count
        except Exception as e:
            logger.error(f"Error counting bits in '{key}': {e}")
            return 0

    def get_ttl(self, key: str) -> int:
        """
        Retrieves the time-to-live (TTL) for a bitmap key.

        Args:
            key (str): The Redis key for the bitmap.

        Returns:
            int: The TTL in seconds. -1 if no TTL is set, -2 if the key does not exist.
        """
        try:
            ttl = self.redis_client.ttl(key)
            if ttl == -1:
                self.log(f"The bitmap '{key}' has no TTL set.", level="warning")
            elif ttl == -2:
                self.log(f"The bitmap '{key}' does not exist.", level="warning")
            else:
                self.log(f"The TTL for bitmap '{key}' is {ttl} seconds.")
            return ttl
        except Exception as e:
            logger.error(f"Error retrieving TTL for '{key}': {e}")
            return -2

    def extend_ttl(self, key: str, ttl: int) -> None:
        """
        Extends or sets a new TTL for a bitmap key.

        Args:
            key (str): The Redis key for the bitmap.
            ttl (int): The new TTL in seconds.
        """
        try:
            if self.redis_client.exists(key):
                self.redis_client.expire(key, ttl)
                self.log(f"Extended TTL for bitmap '{key}' to {ttl} seconds.")
            else:
                self.log(
                    f"Cannot set TTL because the bitmap '{key}' does not exist.",
                    level="warning",
                )
        except Exception as e:
            logger.error(f"Error extending TTL for '{key}': {e}")
