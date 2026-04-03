"""Tests for wredis.ha.SentinelRedisManager."""

from unittest.mock import MagicMock, patch

import pytest
import redis

from wredis._exceptions import SentinelError
from wredis.ha.sentinel import SentinelRedisManager

SENTINEL_NODES = [("127.0.0.1", 26379), ("127.0.0.1", 26380)]


class TestSentinelRedisManagerInit:
    """Test SentinelRedisManager initialization."""

    @patch("wredis.ha.sentinel.redis.Sentinel")
    def test_init_success(self, mock_sentinel_cls):
        """Test successful initialization."""
        mock_sentinel = MagicMock()
        mock_master = MagicMock()
        mock_sentinel.master_for.return_value = mock_master
        mock_sentinel_cls.return_value = mock_sentinel

        manager = SentinelRedisManager(sentinel_nodes=SENTINEL_NODES)

        mock_sentinel_cls.assert_called_once_with(
            SENTINEL_NODES,
            socket_timeout=5.0,
        )
        mock_sentinel.master_for.assert_called_once_with("mymaster")
        assert manager.sentinel_nodes == SENTINEL_NODES
        assert manager.service_name == "mymaster"
        assert manager.verbose is True
        assert manager.sentinel is mock_sentinel
        assert manager.redis_client is mock_master

    @patch("wredis.ha.sentinel.redis.Sentinel")
    def test_init_with_custom_service_name(self, mock_sentinel_cls):
        """Test initialization with custom service name."""
        mock_sentinel = MagicMock()
        mock_sentinel.master_for.return_value = MagicMock()
        mock_sentinel_cls.return_value = mock_sentinel

        manager = SentinelRedisManager(
            sentinel_nodes=SENTINEL_NODES,
            service_name="my-service",
            socket_timeout=10.0,
        )

        mock_sentinel_cls.assert_called_once_with(
            SENTINEL_NODES,
            socket_timeout=10.0,
        )
        mock_sentinel.master_for.assert_called_once_with("my-service")
        assert manager.service_name == "my-service"

    @patch("wredis.ha.sentinel.redis.Sentinel")
    def test_init_with_sentinel_kwargs(self, mock_sentinel_cls):
        """Test initialization with additional sentinel kwargs."""
        mock_sentinel = MagicMock()
        mock_sentinel.master_for.return_value = MagicMock()
        mock_sentinel_cls.return_value = mock_sentinel

        sentinel_kwargs = {"sentinel_kwargs": {"password": "secret"}}
        manager = SentinelRedisManager(
            sentinel_nodes=SENTINEL_NODES,
            sentinel_kwargs=sentinel_kwargs,
        )

        mock_sentinel_cls.assert_called_once_with(
            SENTINEL_NODES,
            socket_timeout=5.0,
            **sentinel_kwargs,
        )
        assert manager.sentinel_kwargs == sentinel_kwargs

    @patch("wredis.ha.sentinel.redis.Sentinel")
    def test_init_connection_error(self, mock_sentinel_cls):
        """Test initialization raises SentinelError on connection failure."""
        mock_sentinel_cls.side_effect = redis.exceptions.ConnectionError("Connection refused")

        with pytest.raises(SentinelError, match="Failed to connect to Sentinel"):
            SentinelRedisManager(sentinel_nodes=SENTINEL_NODES)

    @patch("wredis.ha.sentinel.redis.Sentinel")
    def test_init_unexpected_error(self, mock_sentinel_cls):
        """Test initialization raises SentinelError on unexpected error."""
        mock_sentinel_cls.side_effect = RuntimeError("Something went wrong")

        with pytest.raises(SentinelError, match="Unexpected error with Sentinel"):
            SentinelRedisManager(sentinel_nodes=SENTINEL_NODES)

    @patch("wredis.ha.sentinel.redis.Sentinel")
    def test_init_verbose_false(self, mock_sentinel_cls):
        """Test initialization with verbose disabled."""
        mock_sentinel = MagicMock()
        mock_sentinel.master_for.return_value = MagicMock()
        mock_sentinel_cls.return_value = mock_sentinel

        manager = SentinelRedisManager(sentinel_nodes=SENTINEL_NODES, verbose=False)

        assert manager.verbose is False

    @patch("wredis.ha.sentinel.redis.Sentinel")
    def test_init_default_sentinel_kwargs(self, mock_sentinel_cls):
        """Test that sentinel_kwargs defaults to empty dict."""
        mock_sentinel = MagicMock()
        mock_sentinel.master_for.return_value = MagicMock()
        mock_sentinel_cls.return_value = mock_sentinel

        manager = SentinelRedisManager(sentinel_nodes=SENTINEL_NODES)

        assert manager.sentinel_kwargs == {}


class TestSentinelRedisManagerLog:
    """Test SentinelRedisManager logging."""

    @patch("wredis.ha.sentinel.redis.Sentinel")
    @patch("wredis.ha.sentinel.logger")
    def test_log_verbose_on(self, mock_logger, mock_sentinel_cls):
        """Test log outputs when verbose is True."""
        mock_sentinel = MagicMock()
        mock_sentinel.master_for.return_value = MagicMock()
        mock_sentinel_cls.return_value = mock_sentinel

        manager = SentinelRedisManager(sentinel_nodes=SENTINEL_NODES, verbose=True)
        manager.log("test message", level="info")

        mock_logger.info.assert_called_with("test message")

    @patch("wredis.ha.sentinel.redis.Sentinel")
    @patch("wredis.ha.sentinel.logger")
    def test_log_verbose_off(self, mock_logger, mock_sentinel_cls):
        """Test log does not output when verbose is False."""
        mock_sentinel = MagicMock()
        mock_sentinel.master_for.return_value = MagicMock()
        mock_sentinel_cls.return_value = mock_sentinel

        manager = SentinelRedisManager(sentinel_nodes=SENTINEL_NODES, verbose=False)
        manager.log("test message", level="warning")

        mock_logger.warning.assert_not_called()

    @patch("wredis.ha.sentinel.redis.Sentinel")
    @patch("wredis.ha.sentinel.logger")
    def test_log_different_levels(self, mock_logger, mock_sentinel_cls):
        """Test log with different log levels."""
        mock_sentinel = MagicMock()
        mock_sentinel.master_for.return_value = MagicMock()
        mock_sentinel_cls.return_value = mock_sentinel

        manager = SentinelRedisManager(sentinel_nodes=SENTINEL_NODES, verbose=True)
        manager.log("error message", level="error")

        mock_logger.error.assert_called_with("error message")


class TestSentinelRedisManagerGetMaster:
    """Test get_master method."""

    @patch("wredis.ha.sentinel.redis.Sentinel")
    def test_get_master_success(self, mock_sentinel_cls):
        """Test get_master returns master client."""
        mock_sentinel = MagicMock()
        mock_master = MagicMock()
        mock_sentinel.master_for.return_value = mock_master
        mock_sentinel_cls.return_value = mock_sentinel

        manager = SentinelRedisManager(sentinel_nodes=SENTINEL_NODES)
        mock_sentinel.reset_mock()

        result = manager.get_master()

        mock_sentinel.master_for.assert_called_once_with("mymaster")
        assert result is mock_master

    @patch("wredis.ha.sentinel.redis.Sentinel")
    def test_get_master_error(self, mock_sentinel_cls):
        """Test get_master raises SentinelError on failure."""
        mock_sentinel = MagicMock()
        mock_master = MagicMock()
        mock_sentinel.master_for.side_effect = [mock_master, Exception("Master unavailable")]
        mock_sentinel_cls.return_value = mock_sentinel

        manager = SentinelRedisManager(sentinel_nodes=SENTINEL_NODES)

        with pytest.raises(SentinelError, match="Failed to get master"):
            manager.get_master()


class TestSentinelRedisManagerGetSlave:
    """Test get_slave method."""

    @patch("wredis.ha.sentinel.redis.Sentinel")
    def test_get_slave_success(self, mock_sentinel_cls):
        """Test get_slave returns slave client."""
        mock_sentinel = MagicMock()
        mock_slave = MagicMock()
        mock_sentinel.slave_for.return_value = mock_slave
        mock_sentinel.master_for.return_value = MagicMock()
        mock_sentinel_cls.return_value = mock_sentinel

        manager = SentinelRedisManager(sentinel_nodes=SENTINEL_NODES)

        result = manager.get_slave()

        mock_sentinel.slave_for.assert_called_once_with("mymaster")
        assert result is mock_slave

    @patch("wredis.ha.sentinel.redis.Sentinel")
    def test_get_slave_error_returns_none(self, mock_sentinel_cls):
        """Test get_slave returns None on failure."""
        mock_sentinel = MagicMock()
        mock_sentinel.slave_for.side_effect = Exception("No slaves available")
        mock_sentinel.master_for.return_value = MagicMock()
        mock_sentinel_cls.return_value = mock_sentinel

        manager = SentinelRedisManager(sentinel_nodes=SENTINEL_NODES)

        result = manager.get_slave()

        assert result is None


class TestSentinelRedisManagerIsMaster:
    """Test is_master method."""

    @patch("wredis.ha.sentinel.redis.Sentinel")
    def test_is_master_true(self, mock_sentinel_cls):
        """Test is_master returns True when node is master."""
        mock_sentinel = MagicMock()
        mock_master = MagicMock()
        mock_master.info.return_value = {"role": "master"}
        mock_sentinel.master_for.return_value = mock_master
        mock_sentinel_cls.return_value = mock_sentinel

        manager = SentinelRedisManager(sentinel_nodes=SENTINEL_NODES)

        result = manager.is_master("127.0.0.1", 6379)

        assert result is True

    @patch("wredis.ha.sentinel.redis.Sentinel")
    def test_is_master_false(self, mock_sentinel_cls):
        """Test is_master returns False when node is not master."""
        mock_sentinel = MagicMock()
        mock_master = MagicMock()
        mock_master.info.return_value = {"role": "slave"}
        mock_sentinel.master_for.return_value = mock_master
        mock_sentinel_cls.return_value = mock_sentinel

        manager = SentinelRedisManager(sentinel_nodes=SENTINEL_NODES)

        result = manager.is_master("127.0.0.1", 6380)

        assert result is False

    @patch("wredis.ha.sentinel.redis.Sentinel")
    def test_is_master_exception_returns_false(self, mock_sentinel_cls):
        """Test is_master returns False on exception."""
        mock_sentinel = MagicMock()
        mock_master = MagicMock()
        mock_sentinel.master_for.side_effect = [mock_master, Exception("Connection lost")]
        mock_sentinel_cls.return_value = mock_sentinel

        manager = SentinelRedisManager(sentinel_nodes=SENTINEL_NODES)

        result = manager.is_master("127.0.0.1", 6379)

        assert result is False


class TestSentinelRedisManagerDiscoverMaster:
    """Test discover_master method."""

    @patch("wredis.ha.sentinel.redis.Sentinel")
    def test_discover_master_success(self, mock_sentinel_cls):
        """Test discover_master returns master address."""
        mock_sentinel = MagicMock()
        mock_sentinel.discover_master.return_value = ("127.0.0.1", 6379)
        mock_sentinel.master_for.return_value = MagicMock()
        mock_sentinel_cls.return_value = mock_sentinel

        manager = SentinelRedisManager(sentinel_nodes=SENTINEL_NODES)

        result = manager.discover_master()

        mock_sentinel.discover_master.assert_called_once_with("mymaster")
        assert result == ("127.0.0.1", 6379)

    @patch("wredis.ha.sentinel.redis.Sentinel")
    def test_discover_master_error(self, mock_sentinel_cls):
        """Test discover_master raises SentinelError on failure."""
        mock_sentinel = MagicMock()
        mock_sentinel.discover_master.side_effect = Exception("Discovery failed")
        mock_sentinel.master_for.return_value = MagicMock()
        mock_sentinel_cls.return_value = mock_sentinel

        manager = SentinelRedisManager(sentinel_nodes=SENTINEL_NODES)

        with pytest.raises(SentinelError, match="Failed to discover master"):
            manager.discover_master()


class TestSentinelRedisManagerDiscoverSlaves:
    """Test discover_slaves method."""

    @patch("wredis.ha.sentinel.redis.Sentinel")
    def test_discover_slaves_success(self, mock_sentinel_cls):
        """Test discover_slaves returns list of slaves."""
        mock_sentinel = MagicMock()
        slaves = [("127.0.0.1", 6380), ("127.0.0.1", 6381)]
        mock_sentinel.discover_slaves.return_value = slaves
        mock_sentinel.master_for.return_value = MagicMock()
        mock_sentinel_cls.return_value = mock_sentinel

        manager = SentinelRedisManager(sentinel_nodes=SENTINEL_NODES)

        result = manager.discover_slaves()

        mock_sentinel.discover_slaves.assert_called_once_with("mymaster")
        assert result == slaves

    @patch("wredis.ha.sentinel.redis.Sentinel")
    def test_discover_slaves_error_returns_empty(self, mock_sentinel_cls):
        """Test discover_slaves returns empty list on failure."""
        mock_sentinel = MagicMock()
        mock_sentinel.discover_slaves.side_effect = Exception("Discovery failed")
        mock_sentinel.master_for.return_value = MagicMock()
        mock_sentinel_cls.return_value = mock_sentinel

        manager = SentinelRedisManager(sentinel_nodes=SENTINEL_NODES)

        result = manager.discover_slaves()

        assert result == []
