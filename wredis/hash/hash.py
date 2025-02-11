import json
import redis
from loguru import logger


class RedisHashManager:
    """
    Manages Redis hash operations, including creation, reading, updating,
    deleting fields, and managing TTL (Time-to-Live).

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
        Initializes the RedisHashManager with connection details.

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

    def create_hash(
        self, key: str, hash_name: str, value: dict | str, ttl: int = -1
    ) -> None:
        """
        Writes a key-value pair into a Redis hash and optionally sets a TTL.

        Args:
            hash_name (str): Name of the hash in Redis.
            key (str): Key within the hash.
            value (dict | str): Value to store, serialized to JSON if it is a dictionary.
            ttl (int): Time-to-live for the hash in seconds. If -1, no TTL is set.
        """
        try:
            json_value = json.dumps(value) if isinstance(value, dict) else value
            self.redis_client.hset(key, hash_name, json_value)
            self.log(f"Written to hash '{key}' -> {hash_name}: {value}")

            if ttl > 0:
                self.redis_client.expire(key, ttl)
                self.log(f"Set TTL of {ttl} seconds for hash '{key}'")
        except Exception as e:
            logger.error(f"Error writing to hash '{key}': {e}")

    def read_hash(self, key: str, hash_name: str) -> dict | str | None:
        """
        Reads a key-value pair from a Redis hash.

        Args:
            hash_name (str): Name of the hash in Redis.
            key (str): Key within the hash.

        Returns:
            dict | str | None: The value stored, deserialized from JSON if applicable, or None if not found.
        """
        try:
            json_value = self.redis_client.hget(key, hash_name)
            if json_value:
                json_value = json_value.decode()
                try:
                    return json.loads(json_value)
                except json.JSONDecodeError:
                    return json_value
            else:
                self.log(
                    f"Field '{hash_name}' does not exist in hash '{key}'.",
                    level="warning",
                )
                return None
        except Exception as e:
            logger.error(f"Error reading from hash '{key}': {e}")
            return None

    def update_hash(self, key: str, hash_name: str, new_data: dict) -> None:
        """
        Updates a key-value pair in a Redis hash. If the field does not exist, it adds it.

        Args:
            hash_name (str): Name of the hash in Redis.
            key (str): Key within the hash.
            new_data (dict): New data to update the field.
        """
        try:
            current_value = self.read_hash(key, hash_name)

            if isinstance(current_value, dict):
                current_value.update(new_data)
                self.create_hash(key, hash_name, current_value)
                self.log(
                    f"Updated field '{hash_name}' in hash '{key}': {current_value}"
                )
            else:
                self.create_hash(key, hash_name, new_data)
                self.log(f"Added new field '{hash_name}' to hash '{key}': {new_data}")
        except Exception as e:
            logger.error(f"Error updating field '{hash_name}' in hash '{key}': {e}")

    def delete_hash_field(self, hash_name: str, key: str) -> None:
        """
        Deletes a specific field from a Redis hash.

        Args:
            hash_name (str): Name of the hash in Redis.
            key (str): Key within the hash to delete.
        """
        try:
            result = self.redis_client.hdel(hash_name, key)
            if result:
                self.log(f"Deleted field '{key}' from hash '{hash_name}'.")
            else:
                self.log(
                    f"Field '{key}' does not exist in hash '{hash_name}'.",
                    level="warning",
                )
        except Exception as e:
            logger.error(f"Error deleting field '{key}' from hash '{hash_name}': {e}")

    def read_all_hash(self, hash_name: str) -> dict | None:
        """
        Reads all fields and values from a Redis hash.

        Args:
            hash_name (str): Name of the hash in Redis.

        Returns:
            dict | None: A dictionary of all fields and values, or None if the hash does not exist.
        """
        try:
            hash_data = self.redis_client.hgetall(hash_name)
            if hash_data:
                items = {}
                for key, value in hash_data.items():
                    value = value.decode()
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        pass
                    items[key.decode()] = value

                self.log(f"Read all fields from hash '{hash_name}': {items}")
                return items
            else:
                self.log(
                    f"Hash '{hash_name}' is empty or does not exist.", level="warning"
                )
                return None
        except Exception as e:
            logger.error(f"Error reading all fields from hash '{hash_name}': {e}")
            return None

    def get_ttl(self, hash_name: str) -> int | None:
        """
        Retrieves the remaining time-to-live (TTL) for a Redis hash.

        Args:
            hash_name (str): Name of the hash in Redis.

        Returns:
            int | None: The remaining TTL in seconds, or None if the hash does not exist or has no TTL.
        """
        try:
            ttl = self.redis_client.ttl(hash_name)
            if ttl == -1:
                self.log(f"Hash '{hash_name}' has no TTL set.", level="warning")
            elif ttl == -2:
                self.log(f"Hash '{hash_name}' does not exist.", level="warning")
            else:
                self.log(f"TTL for hash '{hash_name}' is {ttl} seconds.")
            return ttl
        except Exception as e:
            logger.error(f"Error retrieving TTL for hash '{hash_name}': {e}")
            return None

    def extend_ttl(self, hash_name: str, ttl: int) -> None:
        """
        Extends or sets a new TTL for a Redis hash.

        Args:
            hash_name (str): Name of the hash in Redis.
            ttl (int): New TTL in seconds.
        """
        try:
            if self.redis_client.exists(hash_name):
                self.redis_client.expire(hash_name, ttl)
                self.log(f"Extended TTL for hash '{hash_name}' to {ttl} seconds.")
            else:
                self.log(
                    f"Cannot set TTL because hash '{hash_name}' does not exist.",
                    level="warning",
                )
        except Exception as e:
            logger.error(f"Error extending TTL for hash '{hash_name}': {e}")

    def delete_all_hash(self, hash_name):
        """
        Elimina todos los campos y valores de un hash.
        :param hash_name: Nombre del hash en Redis.
        """
        try:
            result = self.redis_client.delete(hash_name)  # Elimina todo el hash
            if result:
                print(f"Hash '{hash_name}' eliminado completamente.")
            else:
                print(f"El hash '{hash_name}' no existe o ya está vacío.")
        except Exception as e:
            print(f"Error al eliminar el hash '{hash_name}': {e}")

    def exist(self, hash_name: str) -> bool:
        """
        Verifica si un hash existe en Redis.
        :param hash_name: Nombre del hash en Redis.
        :return: True si el hash existe, False si no.
        """
        return self.redis_client.exists(hash_name) == 1
