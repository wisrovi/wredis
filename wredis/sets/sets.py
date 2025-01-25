import redis
from loguru import logger


class RedisSetManager:
    """
    Manages Redis set operations, including adding elements, checking membership,
    removing elements, and managing TTL (Time-to-Live) for set keys.

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
        Initializes the RedisSetManager with connection details.

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

    def add_to_set(self, key: str, *values: str, ttl: int = -1) -> None:
        """
        Adds one or more elements to a set and optionally sets a TTL.

        Args:
            key (str): Name of the set in Redis.
            values (str): Elements to add to the set.
            ttl (int): Time-to-live for the set in seconds. If -1, no TTL is set.
        """
        try:
            self.redis_client.sadd(key, *values)
            self.log(f"Added to set '{key}': {values}")

            if ttl > 0:
                self.redis_client.expire(key, ttl)
                self.log(f"Set TTL of {ttl} seconds for set '{key}'")
        except Exception as e:
            logger.error(f"Error adding to set '{key}': {e}")

    def get_set_members(self, key: str) -> set:
        """
        Retrieves all members of a set.

        Args:
            key (str): Name of the set in Redis.

        Returns:
            set: A set of decoded members.
        """
        try:
            members = {member.decode() for member in self.redis_client.smembers(key)}
            self.log(f"Members of set '{key}': {members}")
            return members
        except Exception as e:
            logger.error(f"Error retrieving members of set '{key}': {e}")
            return set()

    def is_member(self, key: str, value: str) -> bool:
        """
        Checks if an element is a member of the set.

        Args:
            key (str): Name of the set in Redis.
            value (str): Element to check.

        Returns:
            bool: True if the element is in the set, False otherwise.
        """
        try:
            result = self.redis_client.sismember(key, value)
            self.log(
                f"Element '{value}' {'is' if result else 'is not'} a member of set '{key}'"
            )
            return result
        except Exception as e:
            logger.error(f"Error checking membership in set '{key}': {e}")
            return False

    def remove_from_set(self, key: str, *values: str) -> None:
        """
        Removes one or more elements from a set.

        Args:
            key (str): Name of the set in Redis.
            values (str): Elements to remove.
        """
        try:
            self.redis_client.srem(key, *values)
            self.log(f"Removed from set '{key}': {values}")
        except Exception as e:
            logger.error(f"Error removing from set '{key}': {e}")

    def get_ttl(self, key: str) -> int | None:
        """
        Retrieves the remaining TTL (Time-to-Live) of a set.

        Args:
            key (str): Name of the set in Redis.

        Returns:
            int | None: Remaining TTL in seconds, or None if no TTL or the set does not exist.
        """
        try:
            ttl = self.redis_client.ttl(key)
            if ttl == -1:
                self.log(f"Set '{key}' has no TTL set.", level="warning")
            elif ttl == -2:
                self.log(f"Set '{key}' does not exist.", level="warning")
            else:
                self.log(f"TTL for set '{key}' is {ttl} seconds.")
            return ttl
        except Exception as e:
            logger.error(f"Error retrieving TTL for set '{key}': {e}")
            return None

    def extend_ttl(self, key: str, ttl: int) -> None:
        """
        Extends or sets a new TTL for the set.

        Args:
            key (str): Name of the set in Redis.
            ttl (int): New TTL in seconds.
        """
        try:
            if self.redis_client.exists(key):
                self.redis_client.expire(key, ttl)
                self.log(f"Extended TTL for set '{key}' to {ttl} seconds.")
            else:
                self.log(
                    f"Cannot set TTL because set '{key}' does not exist.",
                    level="warning",
                )
        except Exception as e:
            logger.error(f"Error extending TTL for set '{key}': {e}")
