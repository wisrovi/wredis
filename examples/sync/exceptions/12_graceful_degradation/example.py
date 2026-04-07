"""Graceful degradation demonstration on Redis failures.

Shows how to continue operating with reduced functionality
when Redis is unavailable, instead of failing completely.
"""

from wredis._exceptions import CacheError, RedisConnectionError, WRedisError


class CacheWithDegradation:
    """Cache that gracefully degrades when Redis fails.

    When Redis is unavailable, uses an in-memory dictionary
    as fallback to maintain basic functionality.
    """

    def __init__(self):
        self._redis_available = False
        self._memory_cache = {}
        self._degraded_mode = False

    def simulate_redis_failure(self, available):
        """Changes Redis availability state.

        Args:
            available: True if Redis is operational.
        """
        self._redis_available = available

    def _simulate_redis_operation(self, operation, *args):
        """Simulates a Redis operation.

        Raises:
            RedisConnectionError: If Redis is not available.
        """
        if not self._redis_available:
            raise RedisConnectionError("Redis is not available")
        return operation(*args)

    def get(self, key):
        """Gets a value from cache with graceful degradation.

        Args:
            key: The key to look up.

        Returns:
            The stored value or None if not found.
        """
        try:
            return self._simulate_redis_operation(self._get_redis, key)
        except RedisConnectionError:
            self._activate_degraded_mode()
            return self._memory_cache.get(key)

    def set(self, key, value):
        """Stores a value in cache with graceful degradation.

        Args:
            key: The key.
            value: The value to store.

        Returns:
            True if stored in Redis, False if in memory.
        """
        try:
            self._simulate_redis_operation(self._set_redis, key, value)
            return True
        except RedisConnectionError:
            self._activate_degraded_mode()
            self._memory_cache[key] = value
            return False

    def _get_redis(self, key):
        return None

    def _set_redis(self, key, value):
        pass

    def _activate_degraded_mode(self):
        if not self._degraded_mode:
            self._degraded_mode = True
            print("  [WARNING] Degraded mode activated: using in-memory cache")


# Demonstration
cache = CacheWithDegradation()

# Scenario 1: Redis available
print("=== Scenario 1: Redis available ===")
cache.simulate_redis_failure(True)
success = cache.set("user:1", {"name": "Ana"})
print(f"Saved to Redis: {success}")
value = cache.get("user:1")
print(f"Value retrieved: {value}")

# Scenario 2: Redis fails, automatic degradation
print("\n=== Scenario 2: Redis fails, graceful degradation ===")
cache.simulate_redis_failure(False)
success = cache.set("user:2", {"name": "Bob"})
print(f"Saved (memory fallback): {success}")
value = cache.get("user:2")
print(f"Value retrieved from memory: {value}")

# Scenario 3: Multiple operations in degraded mode
print("\n=== Scenario 3: Continuous operations in degraded mode ===")
for i in range(3):
    cache.set(f"temp:{i}", f"value_{i}")

for i in range(3):
    value = cache.get(f"temp:{i}")
    print(f"  temp:{i} = {value}")

# Scenario 4: Base class for services with degradation
print("\n=== Scenario 4: Service with graceful degradation ===")


class ServiceWithFallback:
    """Generic pattern for services with fallback."""

    def __init__(self, name):
        self.name = name

    def execute(self, operation, fallback=None):
        """Executes an operation with fallback on Redis failures.

        Args:
            operation: Function that executes the main operation.
            fallback: Alternative function if Redis fails.

        Returns:
            Result of main operation or fallback.
        """
        try:
            return operation()
        except (RedisConnectionError, CacheError) as exc:
            print(f"  [{self.name}] Redis failed: {exc}")
            if fallback:
                print(f"  [{self.name}] Using fallback")
                return fallback()
            return None


def get_from_redis():
    raise RedisConnectionError("Connection refused")


def get_from_db():
    return {"source": "database", "data": "alternative response"}


service = ServiceWithFallback("Users")
result = service.execute(get_from_redis, fallback=get_from_db)
print(f"  Result: {result}")
