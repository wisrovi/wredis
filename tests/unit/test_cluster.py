"""Tests for wredis.ha.ClusterRedisManager."""

from unittest.mock import MagicMock, patch

import pytest
import redis

from wredis._exceptions import ClusterError
from wredis.ha.cluster import ClusterRedisManager

CLUSTER_NODES = [("127.0.0.1", 7000), ("127.0.0.1", 7001), ("127.0.0.1", 7002)]


class TestClusterRedisManagerInit:
    """Test ClusterRedisManager initialization."""

    @patch("wredis.ha.cluster.redis.cluster.RedisCluster")
    def test_init_success(self, mock_cluster_cls):
        """Test successful initialization."""
        mock_cluster = MagicMock()
        mock_cluster_cls.return_value = mock_cluster

        manager = ClusterRedisManager(startup_nodes=CLUSTER_NODES)

        mock_cluster_cls.assert_called_once_with(
            start_nodes=CLUSTER_NODES,
            decode_responses=True,
            password=None,
            ssl=False,
            socket_timeout=5.0,
            socket_connect_timeout=5.0,
            max_redirects=3,
            skip_full_coverage_check=True,
        )
        assert manager.startup_nodes == CLUSTER_NODES
        assert manager.verbose is True
        assert manager.password is None
        assert manager.ssl is False
        assert manager.cluster is mock_cluster

    @patch("wredis.ha.cluster.redis.cluster.RedisCluster")
    def test_init_with_password(self, mock_cluster_cls):
        """Test initialization with password."""
        mock_cluster = MagicMock()
        mock_cluster_cls.return_value = mock_cluster

        manager = ClusterRedisManager(
            startup_nodes=CLUSTER_NODES,
            password="secret",
        )

        mock_cluster_cls.assert_called_once()
        call_kwargs = mock_cluster_cls.call_args[1]
        assert call_kwargs["password"] == "secret"
        assert manager.password == "secret"

    @patch("wredis.ha.cluster.redis.cluster.RedisCluster")
    def test_init_with_ssl(self, mock_cluster_cls):
        """Test initialization with SSL enabled."""
        mock_cluster = MagicMock()
        mock_cluster_cls.return_value = mock_cluster

        manager = ClusterRedisManager(
            startup_nodes=CLUSTER_NODES,
            ssl=True,
        )

        call_kwargs = mock_cluster_cls.call_args[1]
        assert call_kwargs["ssl"] is True
        assert manager.ssl is True

    @patch("wredis.ha.cluster.redis.cluster.RedisCluster")
    def test_init_custom_timeouts(self, mock_cluster_cls):
        """Test initialization with custom timeouts."""
        mock_cluster = MagicMock()
        mock_cluster_cls.return_value = mock_cluster

        ClusterRedisManager(
            startup_nodes=CLUSTER_NODES,
            socket_timeout=10.0,
            socket_connect_timeout=15.0,
            max_redirects=5,
        )

        call_kwargs = mock_cluster_cls.call_args[1]
        assert call_kwargs["socket_timeout"] == 10.0
        assert call_kwargs["socket_connect_timeout"] == 15.0
        assert call_kwargs["max_redirects"] == 5

    @patch("wredis.ha.cluster.redis.cluster.RedisCluster")
    def test_init_verbose_false(self, mock_cluster_cls):
        """Test initialization with verbose disabled."""
        mock_cluster = MagicMock()
        mock_cluster_cls.return_value = mock_cluster

        manager = ClusterRedisManager(
            startup_nodes=CLUSTER_NODES,
            verbose=False,
        )

        assert manager.verbose is False

    @patch("wredis.ha.cluster.redis.cluster.RedisCluster")
    def test_init_cluster_error(self, mock_cluster_cls):
        """Test initialization raises ClusterError on cluster failure."""
        mock_cluster_cls.side_effect = redis.exceptions.ClusterError("Cluster down")

        with pytest.raises(ClusterError, match="Failed to connect to Redis Cluster"):
            ClusterRedisManager(startup_nodes=CLUSTER_NODES)

    @patch("wredis.ha.cluster.redis.cluster.RedisCluster")
    def test_init_unexpected_error(self, mock_cluster_cls):
        """Test initialization raises ClusterError on unexpected error."""
        mock_cluster_cls.side_effect = RuntimeError("Something went wrong")

        with pytest.raises(ClusterError, match="Unexpected error with Redis Cluster"):
            ClusterRedisManager(startup_nodes=CLUSTER_NODES)


class TestClusterRedisManagerLog:
    """Test ClusterRedisManager logging."""

    @patch("wredis.ha.cluster.redis.cluster.RedisCluster")
    @patch("wredis.ha.cluster.logger")
    def test_log_verbose_on(self, mock_logger, mock_cluster_cls):
        """Test log outputs when verbose is True."""
        mock_cluster = MagicMock()
        mock_cluster_cls.return_value = mock_cluster

        manager = ClusterRedisManager(startup_nodes=CLUSTER_NODES, verbose=True)
        manager.log("test message", level="info")

        mock_logger.info.assert_called_with("test message")

    @patch("wredis.ha.cluster.redis.cluster.RedisCluster")
    @patch("wredis.ha.cluster.logger")
    def test_log_verbose_off(self, mock_logger, mock_cluster_cls):
        """Test log does not output when verbose is False."""
        mock_cluster = MagicMock()
        mock_cluster_cls.return_value = mock_cluster

        manager = ClusterRedisManager(startup_nodes=CLUSTER_NODES, verbose=False)
        manager.log("test message", level="warning")

        mock_logger.warning.assert_not_called()

    @patch("wredis.ha.cluster.redis.cluster.RedisCluster")
    @patch("wredis.ha.cluster.logger")
    def test_log_error_level(self, mock_logger, mock_cluster_cls):
        """Test log with error level."""
        mock_cluster = MagicMock()
        mock_cluster_cls.return_value = mock_cluster

        manager = ClusterRedisManager(startup_nodes=CLUSTER_NODES, verbose=True)
        manager.log("error message", level="error")

        mock_logger.error.assert_called_with("error message")


class TestClusterRedisManagerGetClusterInfo:
    """Test get_cluster_info method."""

    @patch("wredis.ha.cluster.redis.cluster.RedisCluster")
    def test_get_cluster_info_success(self, mock_cluster_cls):
        """Test get_cluster_info returns cluster info."""
        mock_cluster = MagicMock()
        mock_cluster.info.return_value = {"cluster_enabled": 1, "cluster_state": "ok"}
        mock_cluster_cls.return_value = mock_cluster

        manager = ClusterRedisManager(startup_nodes=CLUSTER_NODES)

        result = manager.get_cluster_info()

        mock_cluster.info.assert_called_once_with("cluster")
        assert result == {"cluster_enabled": 1, "cluster_state": "ok"}

    @patch("wredis.ha.cluster.redis.cluster.RedisCluster")
    def test_get_cluster_info_error(self, mock_cluster_cls):
        """Test get_cluster_info raises ClusterError on failure."""
        mock_cluster = MagicMock()
        mock_cluster.info.side_effect = Exception("Info unavailable")
        mock_cluster_cls.return_value = mock_cluster

        manager = ClusterRedisManager(startup_nodes=CLUSTER_NODES)

        with pytest.raises(ClusterError, match="Failed to get cluster info"):
            manager.get_cluster_info()


class TestClusterRedisManagerGetNodes:
    """Test get_nodes method."""

    @patch("wredis.ha.cluster.redis.cluster.RedisCluster")
    def test_get_nodes_success(self, mock_cluster_cls):
        """Test get_nodes returns cluster nodes."""
        mock_cluster = MagicMock()
        nodes = [
            {"id": "node1", "host": "127.0.0.1", "port": 7000},
            {"id": "node2", "host": "127.0.0.1", "port": 7001},
        ]
        mock_cluster.cluster_nodes.return_value = nodes
        mock_cluster_cls.return_value = mock_cluster

        manager = ClusterRedisManager(startup_nodes=CLUSTER_NODES)

        result = manager.get_nodes()

        mock_cluster.cluster_nodes.assert_called_once()
        assert result == nodes

    @patch("wredis.ha.cluster.redis.cluster.RedisCluster")
    def test_get_nodes_error(self, mock_cluster_cls):
        """Test get_nodes raises ClusterError on failure."""
        mock_cluster = MagicMock()
        mock_cluster.cluster_nodes.side_effect = Exception("Nodes unavailable")
        mock_cluster_cls.return_value = mock_cluster

        manager = ClusterRedisManager(startup_nodes=CLUSTER_NODES)

        with pytest.raises(ClusterError, match="Failed to get cluster nodes"):
            manager.get_nodes()


class TestClusterRedisManagerGetSlots:
    """Test get_slots method."""

    @patch("wredis.ha.cluster.redis.cluster.RedisCluster")
    def test_get_slots_success(self, mock_cluster_cls):
        """Test get_slots returns slot assignments."""
        mock_cluster = MagicMock()
        slots = {0: {"master": "node1"}, 5461: {"master": "node2"}}
        mock_cluster.cluster_slots.return_value = slots
        mock_cluster_cls.return_value = mock_cluster

        manager = ClusterRedisManager(startup_nodes=CLUSTER_NODES)

        result = manager.get_slots()

        mock_cluster.cluster_slots.assert_called_once()
        assert result == slots

    @patch("wredis.ha.cluster.redis.cluster.RedisCluster")
    def test_get_slots_error(self, mock_cluster_cls):
        """Test get_slots raises ClusterError on failure."""
        mock_cluster = MagicMock()
        mock_cluster.cluster_slots.side_effect = Exception("Slots unavailable")
        mock_cluster_cls.return_value = mock_cluster

        manager = ClusterRedisManager(startup_nodes=CLUSTER_NODES)

        with pytest.raises(ClusterError, match="Failed to get cluster slots"):
            manager.get_slots()


class TestClusterRedisManagerGetClusterState:
    """Test get_cluster_state method."""

    @patch("wredis.ha.cluster.redis.cluster.RedisCluster")
    def test_get_cluster_state_ok(self, mock_cluster_cls):
        """Test get_cluster_state returns 'ok'."""
        mock_cluster = MagicMock()
        mock_cluster.cluster_info.return_value = {"cluster_state": "ok"}
        mock_cluster_cls.return_value = mock_cluster

        manager = ClusterRedisManager(startup_nodes=CLUSTER_NODES)

        result = manager.get_cluster_state()

        mock_cluster.cluster_info.assert_called_once()
        assert result == "ok"

    @patch("wredis.ha.cluster.redis.cluster.RedisCluster")
    def test_get_cluster_state_fail(self, mock_cluster_cls):
        """Test get_cluster_state returns 'fail'."""
        mock_cluster = MagicMock()
        mock_cluster.cluster_info.return_value = {"cluster_state": "fail"}
        mock_cluster_cls.return_value = mock_cluster

        manager = ClusterRedisManager(startup_nodes=CLUSTER_NODES)

        result = manager.get_cluster_state()

        assert result == "fail"

    @patch("wredis.ha.cluster.redis.cluster.RedisCluster")
    def test_get_cluster_state_missing_key(self, mock_cluster_cls):
        """Test get_cluster_state defaults to 'fail' when key is missing."""
        mock_cluster = MagicMock()
        mock_cluster.cluster_info.return_value = {}
        mock_cluster_cls.return_value = mock_cluster

        manager = ClusterRedisManager(startup_nodes=CLUSTER_NODES)

        result = manager.get_cluster_state()

        assert result == "fail"

    @patch("wredis.ha.cluster.redis.cluster.RedisCluster")
    def test_get_cluster_state_error(self, mock_cluster_cls):
        """Test get_cluster_state raises ClusterError on failure."""
        mock_cluster = MagicMock()
        mock_cluster.cluster_info.side_effect = Exception("State unavailable")
        mock_cluster_cls.return_value = mock_cluster

        manager = ClusterRedisManager(startup_nodes=CLUSTER_NODES)

        with pytest.raises(ClusterError, match="Failed to get cluster state"):
            manager.get_cluster_state()


class TestClusterRedisManagerSetReplicas:
    """Test set_replicas method."""

    @patch("wredis.ha.cluster.redis.cluster.RedisCluster")
    def test_set_replicas_returns_false(self, mock_cluster_cls):
        """Test set_replicas always returns False."""
        mock_cluster = MagicMock()
        mock_cluster_cls.return_value = mock_cluster

        manager = ClusterRedisManager(startup_nodes=CLUSTER_NODES)

        result = manager.set_replicas(num_replicas=2)

        assert result is False


class TestClusterRedisManagerWaitForReplicas:
    """Test wait_for_replicas method."""

    @patch("wredis.ha.cluster.redis.cluster.RedisCluster")
    @patch("time.time")
    def test_wait_for_replicas_success(self, mock_time, mock_cluster_cls):
        """Test wait_for_replicas returns True when state is ok."""
        mock_cluster = MagicMock()
        mock_cluster.cluster_info.return_value = {"cluster_state": "ok"}
        mock_cluster_cls.return_value = mock_cluster

        mock_time.side_effect = [0.0, 0.5]

        manager = ClusterRedisManager(startup_nodes=CLUSTER_NODES)

        result = manager.wait_for_replicas(timeout=10.0)

        assert result is True

    @patch("wredis.ha.cluster.redis.cluster.RedisCluster")
    @patch("time.time")
    def test_wait_for_replicas_timeout(self, mock_time, mock_cluster_cls):
        """Test wait_for_replicas returns False on timeout."""
        mock_cluster = MagicMock()
        mock_cluster.cluster_info.return_value = {"cluster_state": "fail"}
        mock_cluster_cls.return_value = mock_cluster

        mock_time.side_effect = [0.0, 5.0, 11.0]

        manager = ClusterRedisManager(startup_nodes=CLUSTER_NODES)

        result = manager.wait_for_replicas(timeout=10.0)

        assert result is False

    @patch("wredis.ha.cluster.redis.cluster.RedisCluster")
    @patch("time.time")
    def test_wait_for_replicas_exception_then_ok(self, mock_time, mock_cluster_cls):
        """Test wait_for_replicas handles exceptions and retries."""
        mock_cluster = MagicMock()
        mock_cluster.cluster_info.side_effect = [
            Exception("Temporary error"),
            {"cluster_state": "ok"},
        ]
        mock_cluster_cls.return_value = mock_cluster

        mock_time.side_effect = [0.0, 1.0, 2.0]

        manager = ClusterRedisManager(startup_nodes=CLUSTER_NODES)

        result = manager.wait_for_replicas(timeout=10.0)

        assert result is True
