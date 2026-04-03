"""Custom exceptions for WRedis."""


class WRedisError(Exception):
    """Base exception for all WRedis errors."""


class RedisConnectionError(WRedisError):
    """Raised when connection to Redis fails."""


class SerializationError(WRedisError):
    """Raised when serialization/deserialization fails."""


class CacheError(WRedisError):
    """Raised when cache operations fail."""


class SentinelError(WRedisError):
    """Raised when Sentinel operations fail."""


class ClusterError(WRedisError):
    """Raised when Cluster operations fail."""


class ValidationError(WRedisError):
    """Raised when input validation fails."""


class OperationError(WRedisError):
    """Raised when a Redis operation fails."""


class TransactionError(WRedisError):
    """Raised when a transaction fails (e.g., WATCH conflict)."""


class QueueError(WRedisError):
    """Raised when queue operations fail."""


class StreamError(WRedisError):
    """Raised when stream operations fail."""


class PubSubError(WRedisError):
    """Raised when pub/sub operations fail."""
