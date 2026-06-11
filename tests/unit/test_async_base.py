"""Tests for async base manager."""

import pytest
import redis.asyncio as aredis

from wredis._async_base import AsyncBaseManager
from wredis._exceptions import OperationError


class TestAsyncBaseManager:
    """Tests for AsyncBaseManager."""

    def test_init(self):
        """Test initialization."""
        manager = AsyncBaseManager(host="localhost", port=6379, db=0, verbose=False)
        assert manager.redis_client is not None
        assert manager.verbose is False

    def test_init_with_defaults(self):
        """Test initialization with defaults."""
        manager = AsyncBaseManager()
        assert manager.verbose is True

    @pytest.mark.asyncio
    async def test_log_verbose(self):
        """Test logging when verbose is True."""
        manager = AsyncBaseManager(verbose=True)
        await manager.log("test message")

    @pytest.mark.asyncio
    async def test_log_not_verbose(self):
        """Test logging when verbose is False."""
        manager = AsyncBaseManager(verbose=False)
        await manager.log("test message")

    @pytest.mark.asyncio
    async def test_health_check_success(self, async_redis_client):
        """Test health check with working connection."""
        manager = AsyncBaseManager(verbose=False)
        manager.redis_client = async_redis_client
        assert await manager.health_check() is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """Test health check with broken connection."""
        manager = AsyncBaseManager(verbose=False)
        manager.redis_client = aredis.Redis(host="invalid", port=9999, socket_timeout=0.1)
        # health_check now returns False instead of raising OperationError
        assert await manager.health_check() is False

    @pytest.mark.asyncio
    async def test_async_context_manager(self, async_redis_client):
        """Test async context manager support."""
        async with AsyncBaseManager(verbose=False) as manager:
            manager.redis_client = async_redis_client
            assert await manager.health_check()

    @pytest.mark.asyncio
    async def test_execute_success(self, async_redis_client):
        """Test execute with successful operation."""
        manager = AsyncBaseManager(verbose=False)
        manager.redis_client = async_redis_client
        await async_redis_client.set("test_key", "test_value")
        result = await manager._execute("get", "test_key")
        assert result == "test_value"

    @pytest.mark.asyncio
    async def test_execute_failure(self):
        """Test execute with failing operation."""
        manager = AsyncBaseManager(verbose=False)
        manager.redis_client = aredis.Redis(host="invalid", port=9999, socket_timeout=0.1)
        with pytest.raises(OperationError):
            await manager._execute("get", "key")

    @pytest.mark.asyncio
    async def test_close(self):
        """Test closing connection pool."""
        manager = AsyncBaseManager(verbose=False)
        await manager.close()
