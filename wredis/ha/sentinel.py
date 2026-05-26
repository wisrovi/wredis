"""Redis Sentinel Manager for high availability."""
from __future__ import annotations

import redis
from loguru import logger

from wredis._exceptions import SentinelError as WRedisSentinelError


class SentinelRedisManager:
    """Manages Redis connections via Sentinel for automatic failover.

    This manager connects to Redis through Sentinel, providing automatic
    failover when the master node fails.

    Attributes:
        sentinel_manager: Redis Sentinel client.
        service_name: Name of the service to monitor.
        redis_client: Redis client connected to the master.
        verbose: Enables detailed logging if True.
    """

    def __init__(
        self,
        sentinel_nodes: list[tuple[str, int]],
        service_name: str = "mymaster",
        socket_timeout: float = 5.0,
        sentinel_kwargs: dict | None = None,
        verbose: bool = True,
    ):
        """Initialize the SentinelRedisManager.

        Args:
            sentinel_nodes: List of (host, port) tuples for Sentinel nodes.
            service_name: Name of the service to monitor.
            socket_timeout: Socket timeout in seconds.
            sentinel_kwargs: Additional kwargs for Sentinel.
            verbose: Enable detailed logging if True.
        """
        self.sentinel_nodes = sentinel_nodes
        self.service_name = service_name
        self.verbose = verbose
        self.sentinel_kwargs = sentinel_kwargs or {}

        try:
            self.sentinel = redis.Sentinel(
                sentinel_nodes,
                socket_timeout=socket_timeout,
                **self.sentinel_kwargs,
            )
            self.redis_client = self.sentinel.master_for(service_name)
            self.log(f"Connected to Redis master via Sentinel: {service_name}")
        except redis.exceptions.ConnectionError as e:
            raise WRedisSentinelError(f"Failed to connect to Sentinel: {e}") from e
        except Exception as e:
            raise WRedisSentinelError(f"Unexpected error with Sentinel: {e}") from e

    def log(self, message: str, level: str = "info") -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            getattr(logger, level)(message)

    def get_master(self) -> redis.StrictRedis:
        """Get the current master Redis client."""
        try:
            return self.sentinel.master_for(self.service_name)
        except Exception as e:
            raise WRedisSentinelError(f"Failed to get master: {e}") from e

    def get_slave(self) -> redis.StrictRedis | None:
        """Get a slave Redis client (for read operations)."""
        try:
            return self.sentinel.slave_for(self.service_name)
        except Exception as e:
            self.log(f"Failed to get slave: {e}", level="warning")
            return None

    def is_master(self, host: str, port: int) -> bool:
        """Check if a node is the current master."""
        try:
            master = self.sentinel.master_for(self.service_name)
            info = master.info("replication")
            return info.get("role") == "master"
        except Exception:
            return False

    def discover_master(self) -> tuple[str, int]:
        """Discover the current master node."""
        try:
            master_address = self.sentinel.discover_master(self.service_name)
            self.log(f"Discovered master: {master_address}")
            return master_address
        except Exception as e:
            raise WRedisSentinelError(f"Failed to discover master: {e}") from e

    def discover_slaves(self) -> list[tuple[str, int]]:
        """Discover all slave nodes."""
        try:
            slaves = self.sentinel.discover_slaves(self.service_name)
            self.log(f"Discovered {len(slaves)} slaves")
            return slaves
        except Exception as e:
            self.log(f"Failed to discover slaves: {e}", level="warning")
            return []
