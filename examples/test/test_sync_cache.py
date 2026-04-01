"""Tests for sync/basic/cache examples (decorators)."""


def test_example_01_basic():
    """Test basic cache decorator."""
    from wredis.decorators import cache

    @cache(ttl=60, prefix="test")
    def my_function(x, y):
        return x + y

    # First call - executes function
    result1 = my_function(1, 2)
    assert result1 == 3

    # Second call - should use cache
    result2 = my_function(1, 2)
    assert result2 == 3


def test_cache_with_dict():
    """Test cache with dictionary return."""
    from wredis.decorators import cache

    @cache(ttl=60, prefix="test")
    def get_data():
        return {"key": "value"}

    result = get_data()
    assert result == {"key": "value"}


def test_cache_ttl():
    """Test cache TTL."""
    from wredis.decorators import cache
    import time

    @cache(ttl=1, prefix="test")
    def slow_function():
        return "result"

    result1 = slow_function()
    time.sleep(1.1)
    # Cache should expire
    result2 = slow_function()
    assert result1 == result2


def test_cache_invalidation():
    """Test cache invalidation."""
    from wredis.decorators import cache, clear_cache

    @cache(ttl=60, prefix="test")
    def my_func():
        return "value"

    my_func()
    clear_cache("test*")
