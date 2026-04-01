"""Tests for sync/basic/sets examples."""


def test_example_01_read():
    """Test set read example."""
    from wredis.sets import RedisSetManager

    m = RedisSetManager(host="localhost", verbose=False)
    m.add_to_set("test:set", "value1", "value2")
    members = m.get_set_members("test:set")
    assert "value1" in members
    assert "value2" in members
    m.redis_client.delete("test:set")


def test_example_02_create():
    """Test set create example."""
    from wredis.sets import RedisSetManager

    m = RedisSetManager(host="localhost", verbose=False)
    m.add_to_set("test:set", "value1", "value2", "value3")
    members = m.get_set_members("test:set")
    assert len(members) >= 3
    m.redis_client.delete("test:set")


def test_is_member():
    """Test is_member example."""
    from wredis.sets import RedisSetManager

    m = RedisSetManager(host="localhost", verbose=False)
    m.add_to_set("test:set", "value1")
    is_member = m.is_member("test:set", "value1")
    assert is_member
    m.redis_client.delete("test:set")


def test_remove_from_set():
    """Test remove from set example."""
    from wredis.sets import RedisSetManager

    m = RedisSetManager(host="localhost", verbose=False)
    m.add_to_set("test:set", "value1", "value2")
    m.remove_from_set("test:set", "value1")
    members = m.get_set_members("test:set")
    assert "value1" not in members
    m.redis_client.delete("test:set")


def test_set_ttl():
    """Test set TTL example."""
    from wredis.sets import RedisSetManager

    m = RedisSetManager(host="localhost", verbose=False)
    m.add_to_set("test:set", "value1", ttl=10)
    ttl = m.get_ttl("test:set")
    assert ttl > 0 and ttl <= 10
    m.redis_client.delete("test:set")
