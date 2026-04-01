"""Custom exceptions for WRedis."""


class WRedisError(Exception):
    """Base exception for all WRedis errors."""

    pass


class RedisConnectionError(WRedisError):
    """Raised when connection to Redis fails."""

    pass


class SerializationError(WRedisError):
    """Raised when serialization/deserialization fails."""

    pass


class CacheError(WRedisError):
    """Raised when cache operations fail."""

    pass


class SentinelError(WRedisError):
    """Raised when Sentinel operations fail."""

    pass


class ClusterError(WRedisError):
    """Raised when Cluster operations fail."""

    pass
