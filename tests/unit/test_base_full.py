"""Full coverage tests for BaseManager and AsyncBaseManager."""
from unittest.mock import AsyncMock, patch

import fakeredis
import fakeredis.aioredis
import pytest
import redis
import redis.asyncio as aredis

from wredis._async_base import AsyncBaseManager
from wredis._base import BaseManager
from wredis._exceptions import OperationError


class TestBaseManagerFull:
    """Extra tests for BaseManager - all uncovered lines."""

    def test_log_verbose_enabled(self):
        """Test log method when verbose=True calls logger (line 70)."""
        manager = BaseManager(verbose=True)
        with patch("wredis._base.logger") as mock_logger:
            manager.log("test message", "info")
            mock_logger.info.assert_called_once_with("test message")
        manager.close()

    def test_health_check_redis_error(self):
        """Test health_check raises OperationError on RedisError (lines 83-84)."""
        manager = BaseManager(verbose=False)
        with patch.object(
            manager.redis_client, "ping", side_effect=redis.RedisError("fail")
        ), pytest.raises(OperationError, match="Redis health check failed"):
            manager.health_check()
        manager.close()

    def test_exist_success(self, redis_client_binary):
        """Test exist returns True/False for existing/missing keys (lines 95-99)."""
        manager = BaseManager(verbose=False)
        manager.redis_client = redis_client_binary
        redis_client_binary.set("mykey", "value")
        assert manager.exist("mykey") is True
        assert manager.exist("nonexistent") is False
        manager.close()

    def test_exist_redis_error(self):
        """Test exist raises OperationError on RedisError (lines 100-101)."""
        manager = BaseManager(verbose=False)
        with patch.object(
            manager.redis_client, "exists", side_effect=redis.RedisError("fail")
        ), pytest.raises(OperationError, match="Redis exists failed"):
            manager.exist("key")
        manager.close()

    def test_execute_push_alias(self, redis_client_binary):
        """Test _execute maps 'push' to 'rpush' (line 121)."""
        manager = BaseManager(verbose=False)
        manager.redis_client = redis_client_binary
        result = manager._execute("push", "mylist", "value")
        assert result == 1
        assert redis_client_binary.lrange("mylist", 0, -1) == [b"value"]
        manager.close()

    def test_execute_bytes_decode_success(self, redis_client_binary):
        """Test _execute decodes bytes to string (line 128)."""
        manager = BaseManager(verbose=False)
        manager.redis_client = redis_client_binary
        redis_client_binary.set("strkey", "hello")
        result = manager._execute("get", "strkey")
        assert result == "hello"
        manager.close()

    def test_execute_bytes_decode_failure(self, redis_client_binary):
        """Test _execute returns raw bytes when decode fails (lines 129-130)."""
        manager = BaseManager(verbose=False)
        manager.redis_client = redis_client_binary
        redis_client_binary.set("binkey", b"\x80\x81\x82")
        result = manager._execute("get", "binkey")
        assert result == b"\x80\x81\x82"
        manager.close()

    def test_execute_list_decode(self, redis_client_binary):
        """Test _execute decodes list of bytes (lines 132-141)."""
        manager = BaseManager(verbose=False)
        manager.redis_client = redis_client_binary
        redis_client_binary.rpush("mylist", "a", "b", "c")
        result = manager._execute("lrange", "mylist", 0, -1)
        assert result == ["a", "b", "c"]
        manager.close()

    def test_execute_list_with_binary(self, redis_client_binary):
        """Test _execute handles list with non-decodable bytes (lines 132-141)."""
        manager = BaseManager(verbose=False)
        manager.redis_client = redis_client_binary
        redis_client_binary.set("k1", "hello")
        redis_client_binary.set("k2", b"\x80\x81")
        result = manager._execute("mget", "k1", "k2")
        assert result == ["hello", b"\x80\x81"]
        manager.close()

    def test_execute_dict_decode(self, redis_client_binary):
        """Test _execute decodes dict with bytes keys/values (lines 143-153)."""
        manager = BaseManager(verbose=False)
        manager.redis_client = redis_client_binary
        redis_client_binary.hset("myhash", "field1", "value1")
        redis_client_binary.hset("myhash", "field2", "value2")
        result = manager._execute("hgetall", "myhash")
        assert result == {"field1": "value1", "field2": "value2"}
        manager.close()

    def test_execute_list_with_non_bytes_items(self):
        """Test _execute when list item is not bytes (line 140 else branch)."""
        manager = BaseManager(verbose=False)
        fake = fakeredis.FakeRedis(decode_responses=False)
        manager.redis_client = fake
        with patch.object(fake, "smembers", return_value={b"hello", 42}):
            result = manager._execute("smembers", "key")
            assert b"hello" in result or "hello" in result
        manager.close()

    def test_execute_dict_with_non_bytes_values(self):
        """Test _execute when dict value is not bytes (line 147 False branch)."""
        manager = BaseManager(verbose=False)
        fake = fakeredis.FakeRedis(decode_responses=False)
        manager.redis_client = fake
        with patch.object(fake, "hgetall", return_value={b"k1": "str_val"}):
            result = manager._execute("hgetall", "key")
            assert result["k1"] == "str_val"
        manager.close()

    def test_execute_dict_with_non_utf8_bytes(self):
        """Test _execute when dict value bytes can't be decoded (lines 150-151)."""
        manager = BaseManager(verbose=False)
        fake = fakeredis.FakeRedis(decode_responses=False)
        manager.redis_client = fake
        with patch.object(fake, "hgetall", return_value={b"k": b"\xff\xfe"}):
            result = manager._execute("hgetall", "key")
            assert result["k"] == b"\xff\xfe"
        manager.close()

    def test_execute_redis_error(self):
        """Test _execute raises OperationError on RedisError (line 156)."""
        manager = BaseManager(verbose=False)
        with patch.object(
            manager.redis_client, "get", side_effect=redis.RedisError("fail")
        ), pytest.raises(OperationError, match="Redis get failed"):
            manager._execute("get", "key")
        manager.close()

    def test_close_disconnects_and_logs(self):
        """Test close disconnects pool and logs (lines 160-161)."""
        manager = BaseManager(verbose=True)
        with patch("wredis._base.logger") as mock_logger:
            manager.close()
            mock_logger.info.assert_called_once_with("Connection pool closed")

    def test_context_manager_enter_exit(self):
        """Test __enter__ returns self and __exit__ calls close (lines 169, 179)."""
        manager = BaseManager(verbose=False)
        with patch.object(manager, "close") as mock_close:
            with manager as m:
                assert m is manager
            mock_close.assert_called_once()


class TestAsyncBaseManagerFull:
    """Extra tests for AsyncBaseManager - all uncovered lines."""

    @pytest.mark.asyncio
    async def test_aenter_returns_self(self):
        """Test __aenter__ returns self (line 55)."""
        manager = AsyncBaseManager(verbose=False)
        result = await manager.__aenter__()
        assert result is manager
        await manager.close()

    @pytest.mark.asyncio
    async def test_aexit_calls_close(self):
        """Test __aexit__ calls close (line 67)."""
        manager = AsyncBaseManager(verbose=False)
        with patch.object(manager, "close", new_callable=AsyncMock) as mock_close:
            await manager.__aexit__(None, None, None)
            mock_close.assert_awaited_once()
        await manager.close()

    @pytest.mark.asyncio
    async def test_log_verbose_enabled(self):
        """Test log calls logger when verbose=True (line 77)."""
        manager = AsyncBaseManager(verbose=True)
        with patch("wredis._async_base.logger") as mock_logger:
            await manager.log("test message", "info")
            mock_logger.info.assert_called_once_with("test message")
        await manager.close()

    @pytest.mark.asyncio
    async def test_health_check_redis_error(self):
        """Test health_check returns False on RedisError (lines 87-88)."""
        manager = AsyncBaseManager(verbose=False)
        with patch.object(
            manager.redis_client,
            "ping",
            side_effect=aredis.RedisError("fail"),
            new_callable=AsyncMock,
        ):
            result = await manager.health_check()
            assert result is False
        await manager.close()

    @pytest.mark.asyncio
    async def test_health_check_redis_error_logs(self):
        """Test health_check logs error when verbose (lines 85-89)."""
        manager = AsyncBaseManager(verbose=True)
        with patch.object(
            manager.redis_client,
            "ping",
            side_effect=aredis.RedisError("fail"),
            new_callable=AsyncMock,
        ), patch("wredis._async_base.logger") as mock_logger:
            result = await manager.health_check()
            assert result is False
            mock_logger.error.assert_called_once()
        await manager.close()

    @pytest.mark.asyncio
    async def test_exists_success(self, async_redis_client):
        """Test exists with existing and non-existing keys (lines 100-104)."""
        manager = AsyncBaseManager(verbose=False)
        manager.redis_client = async_redis_client
        await async_redis_client.set("mykey", "value")
        assert await manager.exists("mykey") is True
        assert await manager.exists("nonexistent") is False
        await manager.close()

    @pytest.mark.asyncio
    async def test_exists_redis_error(self):
        """Test exists raises OperationError on RedisError (lines 105-106)."""
        manager = AsyncBaseManager(verbose=False)
        with patch.object(
            manager.redis_client,
            "exists",
            side_effect=aredis.RedisError("fail"),
            new_callable=AsyncMock,
        ), pytest.raises(OperationError, match="Redis exists failed"):
            await manager.exists("key")
        await manager.close()

    @pytest.mark.asyncio
    async def test_execute_push_alias(self, async_redis_client):
        """Test _execute maps 'push' to 'rpush' (line 126)."""
        manager = AsyncBaseManager(verbose=False)
        manager.redis_client = async_redis_client
        result = await manager._execute("push", "mylist", "value")
        assert result == 1
        await manager.close()

    @pytest.mark.asyncio
    async def test_execute_bytes_decode_success(self, async_redis_client_binary):
        """Test _execute decodes bytes to string (line 135)."""
        manager = AsyncBaseManager(verbose=False)
        manager.redis_client = async_redis_client_binary
        await async_redis_client_binary.set("strkey", "hello")
        result = await manager._execute("get", "strkey")
        assert result == "hello"
        await manager.close()

    @pytest.mark.asyncio
    async def test_execute_bytes_decode_failure(self, async_redis_client_binary):
        """Test _execute returns raw bytes when decode fails (lines 136-137)."""
        manager = AsyncBaseManager(verbose=False)
        manager.redis_client = async_redis_client_binary
        await async_redis_client_binary.set("binkey", b"\x80\x81\x82")
        result = await manager._execute("get", "binkey")
        assert result == b"\x80\x81\x82"
        await manager.close()

    @pytest.mark.asyncio
    async def test_execute_list_decode(self, async_redis_client_binary):
        """Test _execute decodes list of bytes (lines 138-148)."""
        manager = AsyncBaseManager(verbose=False)
        manager.redis_client = async_redis_client_binary
        await async_redis_client_binary.rpush("mylist", "a", "b", "c")
        result = await manager._execute("lrange", "mylist", 0, -1)
        assert result == ["a", "b", "c"]
        await manager.close()

    @pytest.mark.asyncio
    async def test_execute_list_with_binary(self, async_redis_client_binary):
        """Test _execute handles list with non-decodable bytes (lines 138-148)."""
        manager = AsyncBaseManager(verbose=False)
        manager.redis_client = async_redis_client_binary
        await async_redis_client_binary.set("k1", "hello")
        await async_redis_client_binary.set("k2", b"\x80\x81")
        result = await manager._execute("mget", "k1", "k2")
        assert result == ["hello", b"\x80\x81"]
        await manager.close()

    @pytest.mark.asyncio
    async def test_execute_dict_decode(self, async_redis_client_binary):
        """Test _execute decodes dict with bytes keys/values (lines 149-160)."""
        manager = AsyncBaseManager(verbose=False)
        manager.redis_client = async_redis_client_binary
        await async_redis_client_binary.hset("myhash", "field1", "value1")
        await async_redis_client_binary.hset("myhash", "field2", "value2")
        result = await manager._execute("hgetall", "myhash")
        assert result == {"field1": "value1", "field2": "value2"}
        await manager.close()

    @pytest.mark.asyncio
    async def test_execute_list_non_bytes_items_async(self):
        """Test _execute when list item is not bytes (line 147 else branch)."""
        manager = AsyncBaseManager(verbose=False)
        fake = fakeredis.aioredis.FakeRedis(decode_responses=False)
        manager.redis_client = fake
        with patch.object(fake, "smembers", return_value={b"hello", 42}, new_callable=AsyncMock):
            result = await manager._execute("smembers", "key")
            assert b"hello" in result or "hello" in result
        await manager.close()

    @pytest.mark.asyncio
    async def test_execute_dict_non_bytes_values_async(self):
        """Test _execute when dict value is not bytes (line 154 False)."""
        manager = AsyncBaseManager(verbose=False)
        fake = fakeredis.aioredis.FakeRedis(decode_responses=False)
        manager.redis_client = fake
        with patch.object(fake, "hgetall", return_value={b"k1": "str_val"}, new_callable=AsyncMock):
            result = await manager._execute("hgetall", "key")
            assert result["k1"] == "str_val"
        await manager.close()

    @pytest.mark.asyncio
    async def test_execute_dict_non_utf8_bytes_async(self):
        """Test _execute when dict value bytes can't be decoded (lines 157-158)."""
        manager = AsyncBaseManager(verbose=False)
        fake = fakeredis.aioredis.FakeRedis(decode_responses=False)
        manager.redis_client = fake
        with patch.object(fake, "hgetall", return_value={b"k": b"\xff\xfe"}, new_callable=AsyncMock):
            result = await manager._execute("hgetall", "key")
            assert result["k"] == b"\xff\xfe"
        await manager.close()

    @pytest.mark.asyncio
    async def test_execute_retry_and_fail(self):
        """Test _execute raises OperationError after retries (lines 163-170)."""
        manager = AsyncBaseManager(verbose=False)
        with patch.object(
            manager.redis_client,
            "get",
            side_effect=aredis.RedisError("fail"),
            new_callable=AsyncMock,
        ), pytest.raises(
            OperationError, match="Redis get failed after 3 attempts"
        ):
            await manager._execute("get", "key")
        await manager.close()

    @pytest.mark.asyncio
    async def test_close_calls_redis_close(self):
        """Test close calls redis_client.close and logs (line 174)."""
        manager = AsyncBaseManager(verbose=True)
        with patch.object(
            manager.redis_client, "close", new_callable=AsyncMock
        ) as mock_close, patch("wredis._async_base.logger") as mock_logger:
            await manager.close()
            mock_close.assert_awaited_once()
            mock_logger.info.assert_called_once_with("Connection closed")
        await manager.close()
