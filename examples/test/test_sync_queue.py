"""Tests for sync/basic/queue examples."""


def test_example_01_producer():
    """Test queue producer example."""
    from wredis.queue import RedisQueueManager

    m = RedisQueueManager(host="localhost", verbose=False)
    m.publish("test:queue", {"id": 1, "data": "test"})
    length = m.get_queue_length("test:queue")
    assert length >= 1
    m.redis_client.delete("test:queue")


def test_example_02_consumer():
    """Test queue consumer example."""
    from wredis.queue import RedisQueueManager

    m = RedisQueueManager(host="localhost", verbose=False)
    m.publish("test:queue", {"id": 1})
    m.publish("test:queue", {"id": 2})
    m.publish("test:queue", {"id": 3})
    length = m.get_queue_length("test:queue")
    assert length >= 3
    m.redis_client.delete("test:queue")


def test_queue_length():
    """Test get queue length."""
    from wredis.queue import RedisQueueManager

    m = RedisQueueManager(host="localhost", verbose=False)
    m.publish("test:queue", {"id": 1})
    length = m.get_queue_length("test:queue")
    assert length >= 1
    m.redis_client.delete("test:queue")


def test_queue_ttl():
    """Test queue TTL example."""
    from wredis.queue import RedisQueueManager

    m = RedisQueueManager(host="localhost", verbose=False)
    m.publish("test:queue", {"id": 1}, ttl=10)
    length = m.get_queue_length("test:queue")
    assert length >= 1
    m.redis_client.delete("test:queue")
