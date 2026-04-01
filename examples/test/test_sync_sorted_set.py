"""Tests for sync/basic/sorted_set examples."""


def test_example_01_create():
    """Test sorted set creation."""
    from wredis.sortedset import RedisSortedSetManager

    m = RedisSortedSetManager(host="localhost", verbose=False)
    m.add_to_sorted_set("test:sorted", 1, "member1")
    m.add_to_sorted_set("test:sorted", 2, "member2")
    items = m.get_sorted_set("test:sorted")
    assert len(items) >= 2
    m.redis_client.delete("test:sorted")


def test_example_02_read():
    """Test sorted set read."""
    from wredis.sortedset import RedisSortedSetManager

    m = RedisSortedSetManager(host="localhost", verbose=False)
    m.add_to_sorted_set("test:sorted", 1, "member1")
    items = m.get_sorted_set("test:sorted", with_scores=True)
    assert len(items) >= 1
    m.redis_client.delete("test:sorted")


def test_get_rank():
    """Test get rank example."""
    from wredis.sortedset import RedisSortedSetManager

    m = RedisSortedSetManager(host="localhost", verbose=False)
    m.add_to_sorted_set("test:sorted", 1, "member1")
    m.add_to_sorted_set("test:sorted", 2, "member2")
    rank = m.get_rank("test:sorted", "member1")
    assert rank is not None
    m.redis_client.delete("test:sorted")


def test_get_score():
    """Test get score example."""
    from wredis.sortedset import RedisSortedSetManager

    m = RedisSortedSetManager(host="localhost", verbose=False)
    m.add_to_sorted_set("test:sorted", 5.5, "member1")
    score = m.get_score("test:sorted", "member1")
    assert score == 5.5
    m.redis_client.delete("test:sorted")


def test_reverse_order():
    """Test reverse order example."""
    from wredis.sortedset import RedisSortedSetManager

    m = RedisSortedSetManager(host="localhost", verbose=False)
    m.add_to_sorted_set("test:sorted", 1, "member1")
    m.add_to_sorted_set("test:sorted", 2, "member2")
    items = m.get_sorted_set_reverse("test:sorted")
    assert len(items) >= 2
    m.redis_client.delete("test:sorted")


def test_increment_score():
    """Test increment score example."""
    from wredis.sortedset import RedisSortedSetManager

    m = RedisSortedSetManager(host="localhost", verbose=False)
    m.add_to_sorted_set("test:sorted", 1, "member1")
    m.increment_score("test:sorted", 5, "member1")
    score = m.get_score("test:sorted", "member1")
    assert score == 6
    m.redis_client.delete("test:sorted")


def test_delete_sorted_set():
    """Test delete sorted set example."""
    from wredis.sortedset import RedisSortedSetManager

    m = RedisSortedSetManager(host="localhost", verbose=False)
    m.add_to_sorted_set("test:sorted", 1, "member1")
    m.delete_sorted_set("test:sorted")
    items = m.get_sorted_set("test:sorted")
    assert len(items) == 0
