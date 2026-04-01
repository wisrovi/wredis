"""Tests for sync/basic/pubsub examples."""


def test_example_01_publisher():
    """Test pubsub publisher example."""
    from wredis.pubsub import RedisPubSubManager

    m = RedisPubSubManager(host="localhost", verbose=False)
    m.publish_message("test:channel", "Hello")
    m.publish_message("test:channel", {"data": "test"})
    # Verify message was published (no error = success)
    assert True


def test_example_02_subscriber():
    """Test pubsub subscriber example."""
    from wredis.pubsub import RedisPubSubManager

    m = RedisPubSubManager(host="localhost", verbose=False)
    # Verify manager can be created
    assert m is not None


def test_pubsub_message_types():
    """Test pubsub with different message types."""
    from wredis.pubsub import RedisPubSubManager

    m = RedisPubSubManager(host="localhost", verbose=False)
    m.publish_message("test:channel", "string message")
    m.publish_message("test:channel", {"dict": "message"})
    m.publish_message("test:channel", "123")
    assert True
