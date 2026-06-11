"""Additional unit tests covering uncovered lines across all sync modules.

Tests `log` with verbose=True, `exist` methods, `pubsub._start_listener`,
and `transaction.watch_and_execute` error paths.
"""

import time
from unittest.mock import MagicMock, patch

import pytest
import redis

from wredis._exceptions import PubSubError
from wredis.bitmap import RedisBitmapManager
from wredis.geo import RedisGeoManager
from wredis.hash import RedisHashManager
from wredis.hyperloglog import RedisHyperLogLogManager
from wredis.pipeline import RedisPipelineManager
from wredis.pubsub import RedisPubSubManager
from wredis.sets import RedisSetManager
from wredis.sortedset import RedisSortedSetManager
from wredis.transaction import RedisTransactionManager


class TestRedisBitmapManagerFull:
    """Covers bitmap log body (verbose=True) and exist method."""

    def test_log_verbose_true(self, redis_client):
        manager = RedisBitmapManager(host="localhost", verbose=True)
        manager.redis_client = redis_client
        manager.log("test info")
        manager.log("test warning", level="warning")
        manager.log("test error", level="error")

    def test_exist_true(self, redis_client):
        manager = RedisBitmapManager(host="localhost", verbose=False)
        manager.redis_client = redis_client
        redis_client.setbit("bmap", 0, 1)
        assert manager.exist("bmap") is True

    def test_exist_false(self, redis_client):
        manager = RedisBitmapManager(host="localhost", verbose=False)
        manager.redis_client = redis_client
        assert manager.exist("nonexistent") is False

    def test_exist_error(self, redis_client):
        manager = RedisBitmapManager(host="localhost", verbose=False)
        manager.redis_client = redis_client
        with patch.object(redis_client, "exists", side_effect=Exception("err")):
            assert manager.exist("bmap") is False


class TestRedisGeoManagerFull:
    """Covers geo log body (verbose=True) and exist method."""

    def test_log_verbose_true(self, redis_client):
        manager = RedisGeoManager(host="localhost", verbose=True)
        manager.redis_client = redis_client
        manager.log("test info")

    def test_exist_true(self, redis_client):
        manager = RedisGeoManager(host="localhost", verbose=False)
        manager.redis_client = redis_client
        redis_client.geoadd("cities", (-74.006, 40.7128, "nyc"))
        assert manager.exist("cities") is True

    def test_exist_false(self, redis_client):
        manager = RedisGeoManager(host="localhost", verbose=False)
        manager.redis_client = redis_client
        assert manager.exist("nonexistent") is False

    def test_exist_error(self, redis_client):
        manager = RedisGeoManager(host="localhost", verbose=False)
        manager.redis_client = redis_client
        with patch.object(redis_client, "exists", side_effect=Exception("err")):
            assert manager.exist("cities") is False


class TestRedisHashManagerFull:
    """Covers hash log body (verbose=True)."""

    def test_log_verbose_true(self, redis_client):
        manager = RedisHashManager(host="localhost", verbose=True)
        manager.redis_client = redis_client
        manager.log("test info")
        manager.log("test warning", level="warning")
        manager.log("test error", level="error")


class TestRedisHyperLogLogManagerFull:
    """Covers hyperloglog log body (verbose=True) and exist method."""

    def test_log_verbose_true(self, redis_client):
        manager = RedisHyperLogLogManager(host="localhost", verbose=True)
        manager.redis_client = redis_client
        manager.log("test info")

    def test_exist_true(self, redis_client):
        manager = RedisHyperLogLogManager(host="localhost", verbose=False)
        manager.redis_client = redis_client
        redis_client.pfadd("hll", "a", "b")
        assert manager.exist("hll") is True

    def test_exist_false(self, redis_client):
        manager = RedisHyperLogLogManager(host="localhost", verbose=False)
        manager.redis_client = redis_client
        assert manager.exist("nonexistent") is False

    def test_exist_error(self, redis_client):
        manager = RedisHyperLogLogManager(host="localhost", verbose=False)
        manager.redis_client = redis_client
        with patch.object(redis_client, "exists", side_effect=Exception("err")):
            assert manager.exist("hll") is False


class TestRedisPipelineManagerFull:
    """Covers pipeline log body (verbose=True)."""

    def test_log_verbose_true(self, redis_client):
        manager = RedisPipelineManager(host="localhost", verbose=True)
        manager.redis_client = redis_client
        manager.log("test info")


class TestRedisPubSubManagerFull:
    """Covers _start_listener lines 143-177."""

    def test_start_listener_receives_message(self, redis_client):
        manager = RedisPubSubManager(host="localhost", verbose=False)
        manager.redis_client = redis_client
        mock_pubsub = MagicMock()
        mock_pubsub.listen.return_value = [{"type": "message", "data": b'{"foo": "bar"}'}]
        manager.redis_client.pubsub = MagicMock(return_value=mock_pubsub)
        received = []
        manager.subscribers["ch"] = lambda msg: received.append(msg)
        manager._start_listener("ch")
        time.sleep(0.15)
        assert len(received) == 1
        assert received[0] == {"foo": "bar"}
        mock_pubsub.subscribe.assert_called_once_with("ch")
        mock_pubsub.unsubscribe.assert_called_once_with("ch")
        mock_pubsub.close.assert_called_once()

    def test_start_listener_decode_error(self, redis_client):
        manager = RedisPubSubManager(host="localhost", verbose=False)
        manager.redis_client = redis_client
        mock_pubsub = MagicMock()
        mock_pubsub.listen.return_value = [{"type": "message", "data": 12345}]
        manager.redis_client.pubsub = MagicMock(return_value=mock_pubsub)
        received = []
        manager.subscribers["ch"] = lambda msg: received.append(msg)
        manager._start_listener("ch")
        time.sleep(0.15)
        assert len(received) == 0

    def test_start_listener_callback_error(self, redis_client):
        manager = RedisPubSubManager(host="localhost", verbose=False)
        manager.redis_client = redis_client
        mock_pubsub = MagicMock()

        def failing(_msg):
            raise Exception("callback error")

        mock_pubsub.listen.return_value = [{"type": "message", "data": b'"hello"'}]
        manager.redis_client.pubsub = MagicMock(return_value=mock_pubsub)
        manager.subscribers["ch"] = failing
        manager._start_listener("ch")
        time.sleep(0.15)

    def test_start_listener_redis_error(self, redis_client):
        manager = RedisPubSubManager(host="localhost", verbose=False)
        manager.redis_client = redis_client
        mock_pubsub = MagicMock()
        mock_pubsub.subscribe.side_effect = redis.RedisError("subscribe failed")
        manager.redis_client.pubsub = MagicMock(return_value=mock_pubsub)
        manager._start_listener("ch")
        time.sleep(0.15)
        mock_pubsub.subscribe.assert_called_once_with("ch")
        mock_pubsub.unsubscribe.assert_called_once_with("ch")
        mock_pubsub.close.assert_called_once()

    def test_start_listener_runtime_error(self):
        manager = RedisPubSubManager(host="localhost", verbose=False)
        with patch("wredis.pubsub.pupsub.Thread") as mock_thread_cls:
            mock_thread_cls.return_value.start.side_effect = RuntimeError("start failed")
            with pytest.raises(PubSubError):
                manager._start_listener("ch")

    def test_log_verbose_true(self, redis_client):
        manager = RedisPubSubManager(host="localhost", verbose=True)
        manager.redis_client = redis_client
        manager.log("test info")


class TestRedisSetManagerFull:
    """Covers sets log body (verbose=True) and exist method."""

    def test_log_verbose_true(self, redis_client):
        manager = RedisSetManager(host="localhost", verbose=True)
        manager.redis_client = redis_client
        manager.log("test info")

    def test_exist_true(self, redis_client):
        manager = RedisSetManager(host="localhost", verbose=False)
        manager.redis_client = redis_client
        redis_client.sadd("my_set", "v1")
        assert manager.exist("my_set") is True

    def test_exist_false(self, redis_client):
        manager = RedisSetManager(host="localhost", verbose=False)
        manager.redis_client = redis_client
        assert manager.exist("nonexistent") is False

    def test_exist_error(self, redis_client):
        manager = RedisSetManager(host="localhost", verbose=False)
        manager.redis_client = redis_client
        with patch.object(redis_client, "exists", side_effect=Exception("err")):
            assert manager.exist("my_set") is False


class TestRedisSortedSetManagerFull:
    """Covers sortedset log body (verbose=True) and exist method."""

    def test_log_verbose_true(self, redis_client):
        manager = RedisSortedSetManager(host="localhost", verbose=True)
        manager.redis_client = redis_client
        manager.log("test info")

    def test_exist_true(self, redis_client):
        manager = RedisSortedSetManager(host="localhost", verbose=False)
        manager.redis_client = redis_client
        redis_client.zadd("my_zset", {"a": 1})
        assert manager.exist("my_zset") is True

    def test_exist_false(self, redis_client):
        manager = RedisSortedSetManager(host="localhost", verbose=False)
        manager.redis_client = redis_client
        assert manager.exist("nonexistent") is False

    def test_exist_error(self, redis_client):
        manager = RedisSortedSetManager(host="localhost", verbose=False)
        manager.redis_client = redis_client
        with patch.object(redis_client, "exists", side_effect=Exception("err")):
            assert manager.exist("my_zset") is False


class TestRedisTransactionManagerFull:
    """Covers watch_and_execute WatchError + generic exception paths and log body."""

    def test_watch_and_execute_watch_error(self, redis_client):
        manager = RedisTransactionManager(host="localhost", verbose=False)
        manager.redis_client = redis_client
        with patch.object(manager.redis_client, "watch", side_effect=redis.WatchError):
            result = manager.watch_and_execute(
                ["key1"],
                [("set", ["key1", "val1"])],
            )
            assert result is None

    def test_watch_and_execute_exception(self, redis_client):
        manager = RedisTransactionManager(host="localhost", verbose=False)
        manager.redis_client = redis_client
        with patch.object(manager.redis_client, "watch", side_effect=Exception("generic")):
            result = manager.watch_and_execute(
                ["key1"],
                [("set", ["key1", "val1"])],
            )
            assert result is None

    def test_log_verbose_true(self, redis_client):
        manager = RedisTransactionManager(host="localhost", verbose=True)
        manager.redis_client = redis_client
        manager.log("test info")
