"""Unit tests for RedisPipelineManager."""

from unittest.mock import patch

import pytest

from wredis.pipeline import RedisPipelineManager


class TestRedisPipelineManager:
    """Tests for RedisPipelineManager."""

    def test_execute_commands(self, redis_client):
        """Test executing multiple commands in pipeline."""
        manager = RedisPipelineManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        results = manager.execute_commands(
            [
                ("set", ["key1", "value1"]),
                ("set", ["key2", "value2"]),
                ("get", ["key1"]),
                ("get", ["key2"]),
            ]
        )

        assert len(results) == 4
        assert results[0] is True
        assert results[1] is True
        assert results[2] == b"value1"
        assert results[3] == b"value2"

    def test_execute_commands_empty(self, redis_client):
        """Test executing empty command list."""
        manager = RedisPipelineManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        results = manager.execute_commands([])
        assert results == []

    def test_execute_commands_error(self, redis_client):
        """Test execute_commands with error handling."""
        manager = RedisPipelineManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        with patch.object(manager.redis_client, "pipeline", side_effect=Exception("Redis error")):
            result = manager.execute_commands([("set", ["k", "v"])])
            assert result == []

    def test_set_get(self, redis_client):
        """Test set and get in pipeline."""
        manager = RedisPipelineManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        result = manager.set_get("mykey", "myvalue")

        assert result == b"myvalue"
        assert redis_client.get("mykey") == b"myvalue"

    def test_set_get_error(self, redis_client):
        """Test set_get with error handling."""
        manager = RedisPipelineManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        with patch.object(manager.redis_client, "pipeline", side_effect=Exception("Redis error")):
            result = manager.set_get("key", "value")
            assert result is None

    def test_mget_pipeline(self, redis_client):
        """Test mget in pipeline."""
        manager = RedisPipelineManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.set("key1", "value1")
        redis_client.set("key2", "value2")

        results = manager.mget_pipeline("key1", "key2", "key3")

        assert results[0] == b"value1"
        assert results[1] == b"value2"
        assert results[2] is None

    def test_mget_pipeline_empty(self, redis_client):
        """Test mget with no keys."""
        manager = RedisPipelineManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        results = manager.mget_pipeline()
        assert results == []

    def test_mget_pipeline_error(self, redis_client):
        """Test mget_pipeline with error handling."""
        manager = RedisPipelineManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        with patch.object(manager.redis_client, "pipeline", side_effect=Exception("Redis error")):
            result = manager.mget_pipeline("key")
            assert result == []

    def test_mset_pipeline(self, redis_client):
        """Test mset in pipeline."""
        manager = RedisPipelineManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        mapping = {"key1": "value1", "key2": "value2", "key3": "value3"}
        result = manager.mset_pipeline(mapping)

        assert result is True
        assert redis_client.get("key1") == b"value1"
        assert redis_client.get("key2") == b"value2"
        assert redis_client.get("key3") == b"value3"

    def test_mset_pipeline_empty(self, redis_client):
        """Test mset with empty mapping."""
        manager = RedisPipelineManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        result = manager.mset_pipeline({})
        assert result is True

    def test_mset_pipeline_error(self, redis_client):
        """Test mset_pipeline with error handling."""
        manager = RedisPipelineManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        with patch.object(manager.redis_client, "pipeline", side_effect=Exception("Redis error")):
            result = manager.mset_pipeline({"k": "v"})
            assert result is False

    def test_delete_keys(self, redis_client):
        """Test deleting multiple keys in pipeline."""
        manager = RedisPipelineManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        redis_client.set("key1", "value1")
        redis_client.set("key2", "value2")
        redis_client.set("key3", "value3")

        deleted = manager.delete_keys("key1", "key2", "nonexistent")

        assert deleted == 2
        assert redis_client.get("key1") is None
        assert redis_client.get("key2") is None
        assert redis_client.get("key3") == b"value3"

    def test_delete_keys_edge(self, redis_client):
        """Test deleting keys with edge cases."""
        manager = RedisPipelineManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        deleted = manager.delete_keys("nonexistent1", "nonexistent2")
        assert deleted == 0

    def test_delete_keys_error(self, redis_client):
        """Test delete_keys with error handling."""
        manager = RedisPipelineManager(host="localhost", verbose=False)
        manager.redis_client = redis_client

        with patch.object(manager.redis_client, "pipeline", side_effect=Exception("Redis error")):
            result = manager.delete_keys("key")
            assert result == 0
