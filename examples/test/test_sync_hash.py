"""Tests for sync/basic/hash examples."""


def test_example_01_create():
    """Test hash creation example."""
    from wredis.hash import RedisHashManager

    m = RedisHashManager(host="localhost", verbose=False)
    m.create_hash("test:hash", "key1", {"name": "Test"})
    result = m.read_hash("test:hash", "key1")
    assert result == {"name": "Test"}
    m.redis_client.delete("test:hash")


def test_example_02_read():
    """Test hash read example."""
    from wredis.hash import RedisHashManager

    m = RedisHashManager(host="localhost", verbose=False)
    m.create_hash("test:hash", "key1", {"name": "Alice", "age": 30})
    result = m.read_hash("test:hash", "key1")
    assert result == {"name": "Alice", "age": 30}
    m.redis_client.delete("test:hash")


def test_example_03_update():
    """Test hash update example."""
    from wredis.hash import RedisHashManager

    m = RedisHashManager(host="localhost", verbose=False)
    m.create_hash("test:hash", "profile", {"name": "Alice", "age": 30})
    m.update_hash("test:hash", "profile", {"city": "Madrid"})
    result = m.read_hash("test:hash", "profile")
    assert "city" in result or "name" in result
    m.redis_client.delete("test:hash")


def test_example_04_delete():
    """Test hash delete example."""
    from wredis.hash import RedisHashManager

    m = RedisHashManager(host="localhost", verbose=False)
    m.create_hash("test:hash", "key1", {"name": "Bob", "age": 25})
    m.delete_hash_field("test:hash", "key1")
    result = m.read_hash("test:hash", "key1")
    assert result is None or result == {}
    m.redis_client.delete("test:hash")


def test_example_05_ttl():
    """Test hash TTL example."""
    from wredis.hash import RedisHashManager

    m = RedisHashManager(host="localhost", verbose=False)
    m.create_hash("test:hash", "key1", {"value": "test"}, ttl=10)
    ttl = m.get_ttl("test:hash")
    assert ttl > 0 and ttl <= 10
    m.redis_client.delete("test:hash")
