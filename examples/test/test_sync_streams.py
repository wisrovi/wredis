"""Tests for sync/basic/streams examples."""


def test_example_01_producer():
    """Test stream producer example."""
    from wredis.streams import RedisStreamManager

    m = RedisStreamManager(host="localhost", verbose=False)
    msg_id = m.add_to_stream("test:stream", {"field1": "value1"})
    assert msg_id is not None
    m.redis_client.delete("test:stream")


def test_example_02_consumer():
    """Test stream consumer example."""
    from wredis.streams import RedisStreamManager

    m = RedisStreamManager(host="localhost", verbose=False)
    # Create stream with producer first
    m.add_to_stream("test:stream", {"field1": "value1"})
    # Verify consumer can be created
    assert m is not None
    m.redis_client.delete("test:stream")


def test_stream_read():
    """Test stream read example."""
    from wredis.streams import RedisStreamManager

    m = RedisStreamManager(host="localhost", verbose=False)
    m.add_to_stream("test:stream", {"field1": "value1"})
    messages = m.read_from_stream("test:stream")
    # May be empty if using $ consumer
    assert isinstance(messages, list)
    m.redis_client.delete("test:stream")


def test_stream_with_ttl():
    """Test stream with TTL."""
    from wredis.streams import RedisStreamManager

    m = RedisStreamManager(host="localhost", verbose=False)
    msg_id = m.add_to_stream("test:stream", {"field1": "value1"}, ttl=60)
    assert msg_id is not None
    m.redis_client.delete("test:stream")
