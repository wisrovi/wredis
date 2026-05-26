"""Redis Cluster Manager for high availability."""
from __future__ import annotations

import ssl

import redis
from loguru import logger

from wredis._exceptions import ClusterError as WRedisClusterError


class ClusterRedisManager:
    """Manages Redis Cluster connections with automatic hash slot routing.

    This manager provides automatic failover and distributed operations
    across multiple Redis nodes.

    Attributes:
        cluster: Redis Cluster client.
        verbose: Enables detailed logging if True.
    """

    def __init__(
        self,
        startup_nodes: list[tuple[str, int]],
        password: str | None = None,
        ssl: bool | ssl.SSLContext = False,
        socket_timeout: float = 5.0,
        socket_connect_timeout: float = 5.0,
        max_redirects: int = 3,
        decode_responses: bool = True,
        verbose: bool = True,
    ):
        """Initialize the ClusterRedisManager.

        Args:
            startup_nodes: List of (host, port) tuples for cluster nodes.
            password: Redis password (optional).
            ssl: Enable SSL or provide SSL context.
            socket_timeout: Socket timeout in seconds.
            socket_connect_timeout: Socket connect timeout in seconds.
            max_redirects: Maximum redirects to follow.
            decode_responses: Decode responses to strings.
            verbose: Enable detailed logging if True.
        """
        self.startup_nodes = startup_nodes
        self.verbose = verbose
        self.password = password
        self.ssl = ssl

        try:
            self.cluster = redis.cluster.RedisCluster(
                start_nodes=startup_nodes,
                decode_responses=decode_responses,
                password=password,
                ssl=ssl,
                socket_timeout=socket_timeout,
                socket_connect_timeout=socket_connect_timeout,
                max_redirects=max_redirects,
                skip_full_coverage_check=True,
            )
            self.log(f"Connected to Redis Cluster with {len(startup_nodes)} nodes")
        except redis.exceptions.ClusterError as e:
            raise WRedisClusterError(f"Failed to connect to Redis Cluster: {e}") from e
        except Exception as e:
            raise WRedisClusterError(f"Unexpected error with Redis Cluster: {e}") from e

    def log(self, message: str, level: str = "info") -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            getattr(logger, level)(message)

    def get_cluster_info(self) -> dict:
        """Get cluster information."""
        try:
            return self.cluster.info("cluster")
        except Exception as e:
            raise WRedisClusterError(f"Failed to get cluster info: {e}") from e

    def get_nodes(self) -> list[dict]:
        """Get all nodes in the cluster."""
        try:
            return self.cluster.cluster_nodes()
        except Exception as e:
            raise WRedisClusterError(f"Failed to get cluster nodes: {e}") from e

    def get_slots(self) -> dict:
        """Get slot assignments."""
        try:
            return self.cluster.cluster_slots()
        except Exception as e:
            raise WRedisClusterError(f"Failed to get cluster slots: {e}") from e

    def get_cluster_state(self) -> str:
        """Get the cluster state (ok or fail)."""
        try:
            return self.cluster.cluster_info().get("cluster_state", "fail")
        except Exception as e:
            raise WRedisClusterError(f"Failed to get cluster state: {e}") from e

    def set_replicas(self, num_replicas: int = 1) -> bool:
        """Set the number of replicas for each master.

        Note: This requires cluster rebalancing and is typically done
        via redis-cli or a management tool.
        """
        self.log(
            "Setting replicas is not supported via API. Use redis-cli --cluster for this operation.",
            level="warning",
        )
        return False

    def wait_for_replicas(self, timeout: float = 10.0) -> bool:
        """Wait for all replicas to be in ready state."""
        import time

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                state = self.get_cluster_state()
                if state == "ok":
                    return True
            except Exception:
                pass
        return False
