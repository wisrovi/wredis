"""Connection factories for WRedis."""

from __future__ import annotations

import ssl
from typing import Any

import redis
from redis import Sentinel
from redis.cluster import RedisCluster

from wredis._exceptions import (
    ClusterError as WRedisClusterError,
    RedisConnectionError,
    SentinelError as WRedisSentinelError,
)


def create_sync_client(
    host: str = "localhost",
    port: int = 6379,
    db: int = 0,
    password: str | None = None,
    ssl: bool | ssl.SSLContext = False,
    socket_timeout: float = 5.0,
    socket_connect_timeout: float = 5.0,
    retry_on_timeout: bool = True,
    max_connections: int = 10,
    decode_responses: bool = True,
) -> redis.StrictRedis:
    """Create a synchronous Redis client.

    Args:
        host: Redis server hostname.
        port: Redis server port.
        db: Redis database number.
        password: Redis password (optional).
        ssl: Enable SSL or provide SSL context.
        socket_timeout: Socket timeout in seconds.
        socket_connect_timeout: Socket connect timeout in seconds.
        retry_on_timeout: Retry on timeout errors.
        max_connections: Maximum connections in pool.
        decode_responses: Decode responses to strings.

    Returns:
        Redis client instance.
    """
    try:
        return redis.StrictRedis(
            host=host,
            port=port,
            db=db,
            password=password,
            ssl=ssl,
            socket_timeout=socket_timeout,
            socket_connect_timeout=socket_connect_timeout,
            retry_on_timeout=retry_on_timeout,
            decode_responses=decode_responses,
            connection_pool=redis.ConnectionPool(
                max_connections=max_connections,
                host=host,
                port=port,
                db=db,
                password=password,
                ssl=ssl if isinstance(ssl, ssl.SSLContext) else None,
                socket_timeout=socket_timeout,
                socket_connect_timeout=socket_connect_timeout,
                retry_on_timeout=retry_on_timeout,
                decode_responses=decode_responses,
            ),
        )
    except redis.exceptions.ConnectionError as e:
        raise RedisConnectionError(f"Failed to connect to Redis: {e}") from e
    except Exception as e:
        raise RedisConnectionError(f"Unexpected error connecting to Redis: {e}") from e


def create_async_client(
    host: str = "localhost",
    port: int = 6379,
    db: int = 0,
    password: str | None = None,
    ssl: bool | ssl.SSLContext = False,
    socket_timeout: float = 5.0,
    socket_connect_timeout: float = 5.0,
    retry_on_timeout: bool = True,
    max_connections: int = 10,
    decode_responses: bool = True,
) -> redis.asyncio.Redis:
    """Create an asynchronous Redis client.

    Args:
        host: Redis server hostname.
        port: Redis server port.
        db: Redis database number.
        password: Redis password (optional).
        ssl: Enable SSL or provide SSL context.
        socket_timeout: Socket timeout in seconds.
        socket_connect_timeout: Socket connect timeout in seconds.
        retry_on_timeout: Retry on timeout errors.
        max_connections: Maximum connections in pool.
        decode_responses: Decode responses to strings.

    Returns:
        Async Redis client instance.
    """
    try:
        return redis.asyncio.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            ssl=ssl,
            socket_timeout=socket_timeout,
            socket_connect_timeout=socket_connect_timeout,
            retry_on_timeout=retry_on_timeout,
            decode_responses=decode_responses,
            connection_pool=redis.asyncio.ConnectionPool(
                max_connections=max_connections,
                host=host,
                port=port,
                db=db,
                password=password,
                ssl=ssl if isinstance(ssl, ssl.SSLContext) else None,
                socket_timeout=socket_timeout,
                socket_connect_timeout=socket_connect_timeout,
                retry_on_timeout=retry_on_timeout,
                decode_responses=decode_responses,
            ),
        )
    except redis.asyncio.ConnectionError as e:
        raise RedisConnectionError(f"Failed to connect to Redis: {e}") from e
    except Exception as e:
        raise RedisConnectionError(f"Unexpected error connecting to Redis: {e}") from e


def create_sentinel_client(
    sentinel_nodes: list[tuple[str, int]],
    service_name: str = "mymaster",
    socket_timeout: float = 5.0,
    sentinel_kwargs: dict[str, Any] | None = None,
    **kwargs: Any,
) -> redis.StrictRedis:
    """Create a Redis client through Sentinel.

    Args:
        sentinel_nodes: List of (host, port) tuples for Sentinel nodes.
        service_name: Name of the service to monitor.
        socket_timeout: Socket timeout in seconds.
        sentinel_kwargs: Additional kwargs for Sentinel.
        **kwargs: Additional kwargs for Redis client.

    Returns:
        Redis client connected via Sentinel.
    """
    try:
        sentinel_kwargs = sentinel_kwargs or {}
        sentinel = Sentinel(
            sentinel_nodes,
            socket_timeout=socket_timeout,
            **sentinel_kwargs,
        )
        return sentinel.master_for(
            service_name,
            redis_class=redis.StrictRedis,
            **kwargs,
        )
    except redis.exceptions.ConnectionError as e:
        raise WRedisSentinelError(f"Failed to connect to Sentinel: {e}") from e
    except Exception as e:
        raise WRedisSentinelError(f"Unexpected error with Sentinel: {e}") from e


def create_cluster_client(
    startup_nodes: list[tuple[str, int]],
    password: str | None = None,
    ssl: bool | ssl.SSLContext = False,
    socket_timeout: float = 5.0,
    socket_connect_timeout: float = 5.0,
    max_redirects: int = 3,
    decode_responses: bool = True,
) -> RedisCluster:
    """Create a Redis Cluster client.

    Args:
        startup_nodes: List of (host, port) tuples for cluster nodes.
        password: Redis password (optional).
        ssl: Enable SSL or provide SSL context.
        socket_timeout: Socket timeout in seconds.
        socket_connect_timeout: Socket connect timeout in seconds.
        max_redirects: Maximum redirects to follow.
        decode_responses: Decode responses to strings.

    Returns:
        Redis Cluster client instance.
    """
    try:
        return RedisCluster(
            start_nodes=startup_nodes,
            decode_responses=decode_responses,
            password=password,
            ssl=ssl,
            socket_timeout=socket_timeout,
            socket_connect_timeout=socket_connect_timeout,
            max_redirects=max_redirects,
            skip_full_coverage_check=True,
        )
    except redis.exceptions.ClusterError as e:
        raise WRedisClusterError(f"Failed to connect to Redis Cluster: {e}") from e
    except Exception as e:
        raise WRedisClusterError(f"Unexpected error with Redis Cluster: {e}") from e
