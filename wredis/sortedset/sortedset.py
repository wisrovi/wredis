import redis
from loguru import logger
from typing import List, Optional, Union, Tuple


class RedisSortedSetManager:
    """
    Manages Redis sorted sets, allowing operations such as adding, removing, retrieving, and managing TTL for sorted sets.

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
        Initializes the RedisSortedSetManager with connection details.

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

    def add_to_sorted_set(
        self, key: str, score: float, member: str, ttl: int = -1
    ) -> None:
        """
        Adds an element to the sorted set with its score and optionally sets a TTL.

        Args:
            key (str): Name of the sorted set in Redis.
            score (float): Score associated with the member.
            member (str): Member to add to the sorted set.
            ttl (int): Time-to-live in seconds for the sorted set. If -1, no TTL is set.
        """
        try:
            self.redis_client.zadd(key, {member: score})
            self.log(f"Added to sorted set '{key}': {member} with score {score}")

            if ttl > 0:
                self.redis_client.expire(key, ttl)
                self.log(f"Set TTL of {ttl} seconds for sorted set '{key}'")
        except Exception as e:
            logger.error(f"Error adding to sorted set '{key}': {e}")

    def get_sorted_set(
        self, key: str, start: int = 0, stop: int = -1, with_scores: bool = False
    ) -> Union[List[str], List[Tuple[str, float]]]:
        """
        Retrieves elements from the sorted set in a given range.

        Args:
            key (str): Name of the sorted set in Redis.
            start (int): Starting index of the range.
            stop (int): Ending index of the range.
            with_scores (bool): Whether to include scores in the result.

        Returns:
            Union[List[str], List[Tuple[str, float]]]: List of members or tuples of (member, score) if with_scores is True.
        """
        try:
            result = self.redis_client.zrange(key, start, stop, withscores=with_scores)

            if with_scores:
                result = [(member.decode(), score) for member, score in result]
            else:
                result = [member.decode() for member in result]

            self.log(f"Retrieved elements from sorted set '{key}': {result}")
            return result
        except Exception as e:
            logger.error(f"Error retrieving elements from sorted set '{key}': {e}")
            return []

    def get_sorted_set_reverse(
        self, key: str, start: int = 0, stop: int = -1, with_scores: bool = False
    ) -> Union[List[str], List[Tuple[str, float]]]:
        """
        Retrieves elements from the sorted set in reverse order within a given range.

        Args:
            key (str): Name of the sorted set in Redis.
            start (int): Starting index of the range.
            stop (int): Ending index of the range.
            with_scores (bool): Whether to include scores in the result.

        Returns:
            Union[List[str], List[Tuple[str, float]]]: List of members or tuples of (member, score) if with_scores is True.
        """
        try:
            result = self.redis_client.zrevrange(
                key, start, stop, withscores=with_scores
            )
            if with_scores:
                result = [(member.decode(), score) for member, score in result]
            else:
                result = [member.decode() for member in result]

            self.log(
                f"Retrieved elements in reverse order from sorted set '{key}': {result}"
            )
            return result
        except Exception as e:
            logger.error(
                f"Error retrieving elements in reverse from sorted set '{key}': {e}"
            )
            return []

    def remove_from_sorted_set(self, key: str, member: str) -> None:
        """
        Removes a member from the sorted set.

        Args:
            key (str): Name of the sorted set in Redis.
            member (str): Member to remove.
        """
        try:
            self.redis_client.zrem(key, member)
            self.log(f"Removed from sorted set '{key}': {member}")
        except Exception as e:
            logger.error(f"Error removing from sorted set '{key}': {e}")

    def get_rank(self, key: str, member: str) -> Optional[int]:
        """
        Retrieves the rank of a member in the sorted set.

        Args:
            key (str): Name of the sorted set in Redis.
            member (str): Member whose rank to retrieve.

        Returns:
            Optional[int]: The rank of the member, or None if an error occurs.
        """
        try:
            rank = self.redis_client.zrank(key, member)
            self.log(f"Rank of '{member}' in sorted set '{key}': {rank}")
            return rank
        except Exception as e:
            logger.error(
                f"Error retrieving rank of '{member}' in sorted set '{key}': {e}"
            )
            return None

    def get_score(self, key: str, member: str) -> Optional[float]:
        """
        Retrieves the score of a member in the sorted set.

        Args:
            key (str): Name of the sorted set in Redis.
            member (str): Member whose score to retrieve.

        Returns:
            Optional[float]: The score of the member, or None if an error occurs.
        """
        try:
            score = self.redis_client.zscore(key, member)
            self.log(f"Score of '{member}' in sorted set '{key}': {score}")
            return score
        except Exception as e:
            logger.error(
                f"Error retrieving score of '{member}' in sorted set '{key}': {e}"
            )
            return None

    def delete_sorted_set(self, key: str) -> None:
        """
        Deletes the entire sorted set.

        Args:
            key (str): Name of the sorted set in Redis.
        """
        try:
            self.redis_client.delete(key)
            self.log(f"Deleted entire sorted set '{key}'")
        except Exception as e:
            logger.error(f"Error deleting sorted set '{key}': {e}")

    def set_ttl(self, key: str, ttl: int) -> None:
        """
        Sets a TTL for an existing sorted set.

        Args:
            key (str): Name of the sorted set in Redis.
            ttl (int): Time-to-live in seconds.
        """
        try:
            if self.redis_client.exists(key):
                self.redis_client.expire(key, ttl)
                self.log(f"Set TTL of {ttl} seconds for sorted set '{key}'")
            else:
                logger.warning(f"Sorted set '{key}' does not exist to set TTL.")
        except Exception as e:
            logger.error(f"Error setting TTL for sorted set '{key}': {e}")

    def get_ttl(self, key: str) -> Optional[int]:
        """
        Retrieves the remaining TTL of a sorted set.

        Args:
            key (str): Name of the sorted set in Redis.

        Returns:
            Optional[int]: Remaining TTL in seconds, or None if the sorted set does not exist or has no TTL.
        """
        try:
            ttl = self.redis_client.ttl(key)
            if ttl == -1:
                self.log(f"Sorted set '{key}' has no TTL set.", level="warning")
            elif ttl == -2:
                self.log(f"Sorted set '{key}' does not exist.", level="warning")
            else:
                self.log(f"TTL for sorted set '{key}' is {ttl} seconds.")
            return ttl
        except Exception as e:
            logger.error(f"Error retrieving TTL for sorted set '{key}': {e}")
            return None

    def increment_score(self, key: str, increment: float, member: str) -> None:
        """
        Increments the score of a member in the sorted set.

        Args:
            key (str): Name of the sorted set in Redis.
            increment (float): Amount to increment the score.
            member (str): Member whose score will be incremented.
        """
        try:
            self.redis_client.zincrby(key, increment, member)
            self.log(
                f"Incremented score of '{member}' by {increment} in sorted set '{key}'"
            )
        except Exception as e:
            logger.error(
                f"Error incrementing score of '{member}' in sorted set '{key}': {e}"
            )

    def get_sorted_set_by_score(
        self, key: str, min_score: float, max_score: float, with_scores: bool = False
    ) -> Union[List[str], List[Tuple[str, float]]]:
        """
        Retrieves members of the sorted set within a specific score range.

        Args:
            key (str): Name of the sorted set in Redis.
            min_score (float): Minimum score (inclusive).
            max_score (float): Maximum score (inclusive).
            with_scores (bool): Whether to include scores in the result.

        Returns:
            Union[List[str], List[Tuple[str, float]]]: List of members or tuples of (member, score) if with_scores is True.
        """
        try:
            result = self.redis_client.zrangebyscore(
                key, min_score, max_score, withscores=with_scores
            )
            if with_scores:
                result = [(member.decode(), score) for member, score in result]
            else:
                result = [member.decode() for member in result]
            self.log(f"Retrieved elements by score from sorted set '{key}': {result}")
            return result
        except Exception as e:
            logger.error(
                f"Error retrieving elements by score from sorted set '{key}': {e}"
            )
            return []
