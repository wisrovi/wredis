import redis
import json
from typing import Any, Dict, Optional
from loguru import logger


class RedisTokenManager:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        verbose: bool = True,
    ):
        """
        Initializes the connection to the Redis server.

        Args:
            host (str): Redis server host. Defaults to "localhost".
            port (int): Redis server port. Defaults to 6379.
            db (int): Redis database to use. Defaults to 0.
            verbose (bool): If True, enables detailed logging. Defaults to True.
        """
        self.verbose = verbose

        # Configure loguru
        logger.remove()
        logger.add(
            sink=lambda msg: print(msg) if self.verbose else None,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            level="INFO" if self.verbose else "WARNING",
        )

        try:
            self.redis_client = redis.StrictRedis(
                host=host, port=port, db=db, decode_responses=True
            )
            self.redis_client.ping()  # Test the connection
            logger.info(f"Connected to Redis at {host}:{port}, DB: {db}.")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def write_token(self, token: str, data: Dict[str, Any], ttl: int = -1) -> bool:
        """
        Writes a JSON object to a token in Redis.

        Args:
            token (str): The token (key) name in Redis.
            data (Dict[str, Any]): The dictionary to store as JSON.
            ttl (int): Time-to-live for the token in seconds. Defaults to -1 (no expiration).

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        try:
            if not isinstance(data, dict):
                logger.error("Data must be a dictionary.")
                return False

            json_data = json.dumps(data)  # Convert dictionary to JSON
            self.redis_client.set(token, json_data)  # Store the JSON in Redis
            logger.info(f"Data written to Redis under token '{token}': {data}")

            if ttl > 0:
                self.redis_client.expire(token, ttl)  # Set expiration time
                logger.info(f"Token '{token}' set to expire in {ttl} seconds.")

            return True
        except Exception as e:
            logger.error(f"Error writing to Redis: {e}")
            return False

    def read_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Reads a JSON object from a token in Redis.

        Args:
            token (str): The token (key) name in Redis.

        Returns:
            Optional[Dict[str, Any]]: A dictionary with the stored data, or None if the token does not exist or an error occurs.
        """
        try:
            json_data = self.redis_client.get(token)  # Get the JSON from Redis
            if json_data:
                data = json.loads(json_data)  # Convert JSON back to dictionary
                logger.info(f"Data read from Redis for token '{token}': {data}")
                return data
            else:
                logger.warning(f"Token '{token}' does not exist or is empty.")
                return None
        except Exception as e:
            logger.error(f"Error reading from Redis: {e}")
            return None
