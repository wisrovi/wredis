"""Tests for base manager classes."""

import pytest
import redis

from wredis._base import BaseManager
from wredis._exceptions import OperationError


class TestBaseManager:
    """Tests for BaseManager."""

    def test_init(self):
        """Test initialization."""
        manager = BaseManager(host="localhost", port=6379, db=0, verbose=False)
        assert manager.redis_client is not None
        assert manager.verbose is False
        manager.close()

    def test_init_with_defaults(self):
        """Test initialization with defaults."""
        manager = BaseManager()
        assert manager.verbose is True
        manager.close()

    def test_log_verbose(self):
        """Test logging when verbose is True."""
        manager = BaseManager(verbose=True)
        manager.log("test message")
        manager.close()

    def test_log_not_verbose(self):
        """Test logging when verbose is False."""
        manager = BaseManager(verbose=False)
        manager.log("test message")
        manager.close()

    def test_health_check_success(self, redis_client):
        """Test health check with working connection."""
        manager = BaseManager(verbose=False)
        manager.redis_client = redis_client
        assert manager.health_check() is True

    def test_health_check_failure(self):
        """Test health check with broken connection."""
        manager = BaseManager(verbose=False)
        manager.redis_client = redis.StrictRedis(
            host="invalid", port=9999, socket_timeout=0.1
        )
        with pytest.raises(OperationError):
            manager.health_check()

    def test_context_manager(self, redis_client):
        """Test context manager support."""
        with BaseManager(verbose=False) as manager:
            manager.redis_client = redis_client
            assert manager.health_check()

    def test_execute_success(self, redis_client):
        """Test execute with successful operation."""
        manager = BaseManager(verbose=False)
        manager.redis_client = redis_client
        redis_client.set("test_key", "test_value")
        result = manager._execute("get", "test_key")
        assert result == b"test_value"

    def test_execute_failure(self):
        """Test execute with failing operation."""
        manager = BaseManager(verbose=False)
        manager.redis_client = redis.StrictRedis(
            host="invalid", port=9999, socket_timeout=0.1
        )
        with pytest.raises(OperationError):
            manager._execute("get", "key")

    def test_close(self):
        """Test closing connection pool."""
        manager = BaseManager(verbose=False)
        manager.close()
