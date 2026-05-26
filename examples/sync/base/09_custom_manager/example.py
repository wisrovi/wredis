"""Example 09: Creating a custom manager by extending BaseManager.

Demonstrates how to create a custom class that inherits from BaseManager
to add application-specific functionality.
"""

from wredis.sync import BaseManager


class MyCacheManager(BaseManager):
    """Custom cache manager that extends BaseManager.

    Adds convenience methods for common cache operations
    with expiration times and key prefixes.
    """

    def __init__(self, prefix: str = "cache", ttl: int = 300, **kwargs):
        """Initialize the cache manager.

        Args:
            prefix: Prefix for all cache keys.
            ttl: Default time-to-live in seconds.
            **kwargs: Additional arguments for BaseManager.
        """
        super().__init__(**kwargs)
        self.prefix = prefix
        self.ttl = ttl

    def _full_key(self, key: str) -> str:
        """Generate the full key with the prefix."""
        return f"{self.prefix}:{key}"

    def store(self, key: str, value: str) -> bool:
        """Store a value in cache with TTL.

        Args:
            key: Key of the value.
            value: Value to store.

        Returns:
            True if stored successfully.
        """
        full_key = self._full_key(key)
        return self._execute("setex", full_key, self.ttl, value)

    def get(self, key: str) -> str | None:
        """Get a value from the cache.

        Args:
            key: Key of the value.

        Returns:
            The stored value or None if it doesn't exist.
        """
        full_key = self._full_key(key)
        return self._execute("get", full_key)

    def delete(self, key: str) -> bool:
        """Delete a value from the cache.

        Args:
            key: Key to delete.

        Returns:
            True if deleted successfully.
        """
        full_key = self._full_key(key)
        return bool(self._execute("delete", full_key))

    def stats(self) -> dict:
        """Get cache manager statistics.

        Returns:
            Dictionary with manager information.
        """
        return {
            "prefix": self.prefix,
            "ttl": self.ttl,
            "verbose": self.verbose,
            "pool_type": type(self._pool).__name__,
        }


# Custom manager demonstration
print("=== Custom Manager Extending BaseManager ===\n")

with MyCacheManager(prefix="myapp", ttl=600, verbose=False) as cache:
    # Display manager statistics
    stats = cache.stats()
    print("Manager statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Store values in cache
    print("\nStoring values in cache:")
    cache.store("user:1", '{"name": "Ana", "role": "admin"}')
    print("  User 1 stored")

    cache.store("user:2", '{"name": "Carlos", "role": "user"}')
    print("  User 2 stored")

    # Retrieve values
    print("\nRetrieving values from cache:")
    user1 = cache.get("user:1")
    print(f"  User 1: {user1}")

    user2 = cache.get("user:2")
    print(f"  User 2: {user2}")

    # Delete a value
    print("\nDeleting value:")
    cache.delete("user:1")
    user1_deleted = cache.get("user:1")
    print(f"  User 1 after deletion: {user1_deleted}")

print("\nCustom manager closed successfully")
