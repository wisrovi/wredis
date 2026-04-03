"""Comprehensive unit tests for wredis.decorators."""

import json
from unittest.mock import MagicMock, patch

import fakeredis
import pytest
import redis

from wredis._exceptions import CacheError
from wredis.decorators import (
    CacheMetrics,
    async_cache,
    cache,
    clear_cache,
    default_metrics,
    invalidate_cache,
)

# ─── CacheMetrics ────────────────────────────────────────────────────────────


class TestCacheMetrics:
    """Tests for CacheMetrics class."""

    def test_initial_state(self):
        metrics = CacheMetrics()
        assert metrics.hits == 0
        assert metrics.misses == 0
        assert metrics.errors == 0

    def test_hit_rate_is_zero_when_no_requests(self):
        metrics = CacheMetrics()
        assert metrics.hit_rate == 0.0

    def test_hit_rate_all_hits(self):
        metrics = CacheMetrics()
        metrics.record_hit()
        metrics.record_hit()
        assert metrics.hit_rate == 100.0

    def test_hit_rate_all_misses(self):
        metrics = CacheMetrics()
        metrics.record_miss()
        metrics.record_miss()
        assert metrics.hit_rate == 0.0

    def test_hit_rate_mixed(self):
        metrics = CacheMetrics()
        metrics.record_hit()
        metrics.record_hit()
        metrics.record_miss()
        assert metrics.hit_rate == pytest.approx(66.6666, rel=1e-3)

    def test_hit_rate_single_hit(self):
        metrics = CacheMetrics()
        metrics.record_hit()
        assert metrics.hit_rate == 100.0

    def test_hit_rate_single_miss(self):
        metrics = CacheMetrics()
        metrics.record_miss()
        assert metrics.hit_rate == 0.0

    def test_record_hit(self):
        metrics = CacheMetrics()
        metrics.record_hit()
        assert metrics.hits == 1

    def test_record_miss(self):
        metrics = CacheMetrics()
        metrics.record_miss()
        assert metrics.misses == 1

    def test_record_error(self):
        metrics = CacheMetrics()
        metrics.record_error()
        assert metrics.errors == 1

    def test_multiple_recordings(self):
        metrics = CacheMetrics()
        metrics.record_hit()
        metrics.record_hit()
        metrics.record_miss()
        metrics.record_error()
        assert metrics.hits == 2
        assert metrics.misses == 1
        assert metrics.errors == 1

    def test_reset(self):
        metrics = CacheMetrics()
        metrics.record_hit()
        metrics.record_miss()
        metrics.record_error()
        metrics.reset()
        assert metrics.hits == 0
        assert metrics.misses == 0
        assert metrics.errors == 0
        assert metrics.hit_rate == 0.0

    def test_repr_empty(self):
        metrics = CacheMetrics()
        assert repr(metrics) == "CacheMetrics(hits=0, misses=0, errors=0, hit_rate=0.0%)"

    def test_repr_with_data(self):
        metrics = CacheMetrics()
        metrics.record_hit()
        metrics.record_miss()
        metrics.record_error()
        assert repr(metrics) == "CacheMetrics(hits=1, misses=1, errors=1, hit_rate=50.0%)"

    def test_default_metrics_is_cache_metrics(self):
        assert isinstance(default_metrics, CacheMetrics)


# ─── _default_key_builder ────────────────────────────────────────────────────


class TestDefaultKeyBuilder:
    """Tests for _default_key_builder."""

    def _make_func(self):
        def dummy(a, b):
            return a + b

        return dummy

    def test_with_positional_args(self):
        from wredis.decorators import _default_key_builder

        func = self._make_func()
        key = _default_key_builder(func, (1, 2), {})
        assert isinstance(key, str)
        assert len(key) == 32  # MD5 hex digest

    def test_with_kwargs(self):
        from wredis.decorators import _default_key_builder

        func = self._make_func()
        key = _default_key_builder(func, (), {"a": 1, "b": 2})
        assert isinstance(key, str)
        assert len(key) == 32

    def test_with_mixed_args_kwargs(self):
        from wredis.decorators import _default_key_builder

        func = self._make_func()
        key = _default_key_builder(func, (1,), {"b": 2})
        assert isinstance(key, str)
        assert len(key) == 32

    def test_with_no_args(self):
        from wredis.decorators import _default_key_builder

        def no_args():
            return 42

        key = _default_key_builder(no_args, (), {})
        assert isinstance(key, str)
        assert len(key) == 32

    def test_deterministic(self):
        from wredis.decorators import _default_key_builder

        func = self._make_func()
        key1 = _default_key_builder(func, (1, 2), {"c": 3})
        key2 = _default_key_builder(func, (1, 2), {"c": 3})
        assert key1 == key2

    def test_different_args_different_keys(self):
        from wredis.decorators import _default_key_builder

        func = self._make_func()
        key1 = _default_key_builder(func, (1, 2), {})
        key2 = _default_key_builder(func, (3, 4), {})
        assert key1 != key2

    def test_unserializable_args_fallback_to_str(self):
        from wredis.decorators import _default_key_builder

        func = self._make_func()
        obj = object()
        key = _default_key_builder(func, (obj,), {})
        assert isinstance(key, str)
        assert len(key) == 32

    def test_unserializable_kwargs_fallback_to_str(self):
        from wredis.decorators import _default_key_builder

        func = self._make_func()
        obj = object()
        key = _default_key_builder(func, (), {"x": obj})
        assert isinstance(key, str)
        assert len(key) == 32

    def test_with_complex_serializable_args(self):
        from wredis.decorators import _default_key_builder

        func = self._make_func()
        key = _default_key_builder(func, ([1, 2], {"nested": True}), {})
        assert isinstance(key, str)
        assert len(key) == 32

    def test_kwargs_sorted_order(self):
        from wredis.decorators import _default_key_builder

        func = self._make_func()
        key1 = _default_key_builder(func, (), {"b": 2, "a": 1})
        key2 = _default_key_builder(func, (), {"a": 1, "b": 2})
        assert key1 == key2


# ─── @cache decorator ────────────────────────────────────────────────────────


class TestCacheDecorator:
    """Tests for @cache decorator."""

    def test_cache_miss_first_call(self, redis_client):
        call_count = 0

        @cache(ttl=300, prefix="test", redis_client=redis_client)
        def expensive(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        result = expensive(5)
        assert result == 10
        assert call_count == 1

    def test_cache_hit_second_call(self, redis_client):
        call_count = 0

        @cache(ttl=300, prefix="test", redis_client=redis_client)
        def expensive(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        expensive(5)
        result = expensive(5)
        assert result == 10
        assert call_count == 1  # function not called again

    def test_cache_different_args(self, redis_client):
        call_count = 0

        @cache(ttl=300, prefix="test", redis_client=redis_client)
        def expensive(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        expensive(5)
        expensive(10)
        assert call_count == 2

    def test_cache_with_custom_prefix(self, redis_client):
        @cache(ttl=300, prefix="myapp:v1", redis_client=redis_client)
        def func(x):
            return x

        func(1)
        keys = redis_client.keys("myapp:v1:*")
        assert len(keys) == 1

    def test_cache_with_custom_key_builder(self, redis_client):
        def my_builder(func, args, kwargs):
            return "custom_key"

        @cache(ttl=300, prefix="test", key_builder=my_builder, redis_client=redis_client)
        def func(x):
            return x

        func(1)
        assert redis_client.exists("test:custom_key")

    def test_cache_with_custom_key_builder_uses_args(self, redis_client):
        def my_builder(func, args, kwargs):
            return f"arg_{args[0]}"

        @cache(ttl=300, prefix="test", key_builder=my_builder, redis_client=redis_client)
        def func(x):
            return x

        func(42)
        assert redis_client.exists("test:arg_42")

    def test_cache_metrics_tracking(self, redis_client):
        metrics = CacheMetrics()

        @cache(ttl=300, prefix="test", redis_client=redis_client, metrics=metrics)
        def func(x):
            return x

        func(1)  # miss
        func(1)  # hit
        func(2)  # miss
        func(2)  # hit

        assert metrics.hits == 2
        assert metrics.misses == 2
        assert metrics.errors == 0
        assert metrics.hit_rate == 50.0

    def test_cache_error_on_read(self, redis_client):
        metrics = CacheMetrics()

        @cache(ttl=300, prefix="test", redis_client=redis_client, metrics=metrics)
        def func(x):
            return x

        original_get = redis_client.get
        redis_client.get = lambda key: (_ for _ in ()).throw(redis.RedisError("connection lost"))
        try:
            with pytest.raises(CacheError):
                func(1)
        finally:
            redis_client.get = original_get

        assert metrics.errors >= 1

    def test_cache_error_on_write(self, redis_client):
        metrics = CacheMetrics()

        @cache(ttl=300, prefix="test", redis_client=redis_client, metrics=metrics)
        def func(x):
            return x

        original_get = redis_client.get
        original_setex = redis_client.setex
        redis_client.get = lambda key: None
        redis_client.setex = lambda key, ttl, value: (_ for _ in ()).throw(redis.RedisError("write failed"))
        try:
            with pytest.raises(CacheError):
                func(1)
        finally:
            redis_client.get = original_get
            redis_client.setex = original_setex

        assert metrics.errors >= 1

    def test_cache_bytes_result(self, redis_client):
        @cache(ttl=300, prefix="test", redis_client=redis_client)
        def func():
            return b"binary data"

        result = func()
        assert result == b"binary data"

    def test_cache_string_result(self, redis_client):
        @cache(ttl=300, prefix="test", redis_client=redis_client)
        def func():
            return "hello world"

        result = func()
        assert result == "hello world"

    def test_cache_string_result_hit(self, redis_client):
        @cache(ttl=300, prefix="test", redis_client=redis_client)
        def func():
            return "hello world"

        func()
        result = func()
        redis_client.get(_get_cached_key(redis_client, "test"))
        assert result in {"hello world", b"hello world"}

    def test_cache_dict_result(self, redis_client):
        @cache(ttl=300, prefix="test", redis_client=redis_client)
        def func():
            return {"key": "value", "nested": {"a": 1}}

        result = func()
        assert result == {"key": "value", "nested": {"a": 1}}

    def test_cache_dict_result_hit(self, redis_client):
        @cache(ttl=300, prefix="test", redis_client=redis_client)
        def func():
            return {"key": "value"}

        func()
        result = func()
        assert result == {"key": "value"}

    def test_cache_list_result(self, redis_client):
        @cache(ttl=300, prefix="test", redis_client=redis_client)
        def func():
            return [1, 2, 3]

        result = func()
        assert result == [1, 2, 3]

    def test_cache_list_result_hit(self, redis_client):
        @cache(ttl=300, prefix="test", redis_client=redis_client)
        def func():
            return [1, 2, 3]

        func()
        result = func()
        assert result == [1, 2, 3]

    def test_cache_with_kwargs(self, redis_client):
        call_count = 0

        @cache(ttl=300, prefix="test", redis_client=redis_client)
        def func(a, b=10):
            nonlocal call_count
            call_count += 1
            return a + b

        func(1, b=20)
        func(1, b=20)
        assert call_count == 1

    def test_cache_different_kwargs_different_keys(self, redis_client):
        call_count = 0

        @cache(ttl=300, prefix="test", redis_client=redis_client)
        def func(a, b=10):
            nonlocal call_count
            call_count += 1
            return a + b

        func(1, b=10)
        func(1, b=20)
        assert call_count == 2

    def test_cache_preserves_function_metadata(self, redis_client):
        @cache(ttl=300, prefix="test", redis_client=redis_client)
        def my_special_function(x):
            """My docstring."""
            return x

        assert my_special_function.__name__ == "my_special_function"
        assert my_special_function.__doc__ == "My docstring."

    def test_cache_with_ttl_stores_key(self, redis_client):
        @cache(ttl=60, prefix="test", redis_client=redis_client)
        def func(x):
            return x

        func(1)
        key = _get_cached_key(redis_client, "test")
        assert key != ""
        ttl = redis_client.ttl(key)
        assert ttl > 0


def _get_cached_key(r, prefix):
    keys = r.keys(f"{prefix}:*")
    if keys:
        return keys[0].decode() if isinstance(keys[0], bytes) else keys[0]
    return ""


# ─── @async_cache decorator ──────────────────────────────────────────────────


class TestAsyncCacheDecorator:
    """Tests for @async_cache decorator."""

    @pytest.mark.asyncio
    async def test_cache_miss_first_call(self, async_redis_client):
        call_count = 0

        @async_cache(ttl=300, prefix="atest", redis_client=async_redis_client)
        async def expensive(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        result = await expensive(5)
        assert result == 10
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_cache_hit_second_call(self, async_redis_client):
        call_count = 0

        @async_cache(ttl=300, prefix="atest", redis_client=async_redis_client)
        async def expensive(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        await expensive(5)
        result = await expensive(5)
        assert result == 10
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_cache_different_args(self, async_redis_client):
        call_count = 0

        @async_cache(ttl=300, prefix="atest", redis_client=async_redis_client)
        async def expensive(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        await expensive(5)
        await expensive(10)
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_cache_with_custom_prefix(self, async_redis_client):
        @async_cache(ttl=300, prefix="myapp:async", redis_client=async_redis_client)
        async def func(x):
            return x

        await func(1)
        keys = await async_redis_client.keys("myapp:async:*")
        assert len(keys) == 1

    @pytest.mark.asyncio
    async def test_cache_with_custom_key_builder(self, async_redis_client):
        def my_builder(func, args, kwargs):
            return "async_custom_key"

        @async_cache(ttl=300, prefix="atest", key_builder=my_builder, redis_client=async_redis_client)
        async def func(x):
            return x

        await func(1)
        assert await async_redis_client.exists("atest:async_custom_key")

    @pytest.mark.asyncio
    async def test_cache_metrics_tracking(self, async_redis_client):
        metrics = CacheMetrics()

        @async_cache(ttl=300, prefix="atest", redis_client=async_redis_client, metrics=metrics)
        async def func(x):
            return x

        await func(1)  # miss
        await func(1)  # hit
        await func(2)  # miss
        await func(2)  # hit

        assert metrics.hits == 2
        assert metrics.misses == 2
        assert metrics.errors == 0

    @pytest.mark.asyncio
    async def test_cache_error_on_read(self, async_redis_client):
        import redis.asyncio as aredis

        metrics = CacheMetrics()

        @async_cache(ttl=300, prefix="atest", redis_client=async_redis_client, metrics=metrics)
        async def func(x):
            return x

        original_get = async_redis_client.get

        async def failing_get(key):
            raise aredis.RedisError("connection lost")

        async_redis_client.get = failing_get
        try:
            with pytest.raises(CacheError):
                await func(1)
        finally:
            async_redis_client.get = original_get

        assert metrics.errors >= 1

    @pytest.mark.asyncio
    async def test_cache_error_on_write(self, async_redis_client):
        import redis.asyncio as aredis

        metrics = CacheMetrics()

        @async_cache(ttl=300, prefix="atest", redis_client=async_redis_client, metrics=metrics)
        async def func(x):
            return x

        original_get = async_redis_client.get
        original_setex = async_redis_client.setex

        async def none_get(key):
            return None

        async def failing_setex(key, ttl, value):
            raise aredis.RedisError("write failed")

        async_redis_client.get = none_get
        async_redis_client.setex = failing_setex
        try:
            with pytest.raises(CacheError):
                await func(1)
        finally:
            async_redis_client.get = original_get
            async_redis_client.setex = original_setex

        assert metrics.errors >= 1

    @pytest.mark.asyncio
    async def test_cache_bytes_result(self, async_redis_client):
        @async_cache(ttl=300, prefix="atest", redis_client=async_redis_client)
        async def func():
            return b"async binary"

        result = await func()
        assert result == b"async binary"

    @pytest.mark.asyncio
    async def test_cache_string_result(self, async_redis_client):
        @async_cache(ttl=300, prefix="atest", redis_client=async_redis_client)
        async def func():
            return "async string"

        result = await func()
        assert result == "async string"

    @pytest.mark.asyncio
    async def test_cache_string_result_hit(self, async_redis_client):
        @async_cache(ttl=300, prefix="atest", redis_client=async_redis_client)
        async def func():
            return "async string"

        await func()
        result = await func()
        assert result == "async string"

    @pytest.mark.asyncio
    async def test_cache_dict_result(self, async_redis_client):
        @async_cache(ttl=300, prefix="atest", redis_client=async_redis_client)
        async def func():
            return {"async": True}

        result = await func()
        assert result == {"async": True}

    @pytest.mark.asyncio
    async def test_cache_dict_result_hit(self, async_redis_client):
        @async_cache(ttl=300, prefix="atest", redis_client=async_redis_client)
        async def func():
            return {"async": True}

        await func()
        result = await func()
        assert result == {"async": True}

    @pytest.mark.asyncio
    async def test_cache_with_kwargs(self, async_redis_client):
        call_count = 0

        @async_cache(ttl=300, prefix="atest", redis_client=async_redis_client)
        async def func(a, b=10):
            nonlocal call_count
            call_count += 1
            return a + b

        await func(1, b=20)
        await func(1, b=20)
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_cache_preserves_function_metadata(self, async_redis_client):
        @async_cache(ttl=300, prefix="atest", redis_client=async_redis_client)
        async def my_async_func(x):
            """Async docstring."""
            return x

        assert my_async_func.__name__ == "my_async_func"
        assert my_async_func.__doc__ == "Async docstring."


# ─── @invalidate_cache decorator ─────────────────────────────────────────────


class TestInvalidateCacheDecorator:
    """Tests for @invalidate_cache decorator."""

    def test_invalidation_after_function_call(self, redis_client):
        redis_client.set("test:invalidate:1", "value1")
        redis_client.set("test:invalidate:2", "value2")
        assert redis_client.exists("test:invalidate:1")
        assert redis_client.exists("test:invalidate:2")

        @invalidate_cache(pattern="test:invalidate:*", redis_client=redis_client)
        def update_func():
            return "updated"

        result = update_func()
        assert result == "updated"
        assert not redis_client.exists("test:invalidate:1")
        assert not redis_client.exists("test:invalidate:2")

    def test_invalidation_no_keys_to_delete(self, redis_client):
        @invalidate_cache(pattern="nonexistent:pattern:*", redis_client=redis_client)
        def func():
            return "ok"

        result = func()
        assert result == "ok"

    def test_invalidation_preserves_unmatched_keys(self, redis_client):
        redis_client.set("test:keep:1", "value1")
        redis_client.set("test:delete:1", "value2")

        @invalidate_cache(pattern="test:delete:*", redis_client=redis_client)
        def func():
            return "ok"

        func()
        assert redis_client.exists("test:keep:1")
        assert not redis_client.exists("test:delete:1")

    def test_invalidation_error(self, redis_client):
        @invalidate_cache(pattern="test:*", redis_client=redis_client)
        def func():
            return "ok"

        original_keys = redis_client.keys
        redis_client.keys = lambda pattern: (_ for _ in ()).throw(redis.RedisError("redis error"))
        try:
            with pytest.raises(CacheError):
                func()
        finally:
            redis_client.keys = original_keys

    def test_invalidation_with_function_args(self, redis_client):
        redis_client.set("inv:test", "old")

        @invalidate_cache(pattern="inv:*", redis_client=redis_client)
        def update_value(new_val):
            return new_val

        result = update_value("new")
        assert result == "new"
        assert not redis_client.exists("inv:test")


# ─── clear_cache function ────────────────────────────────────────────────────


class TestClearCache:
    """Tests for clear_cache function."""

    def test_clear_cache_with_keys(self, redis_client):
        redis_client.set("clear:test:1", "v1")
        redis_client.set("clear:test:2", "v2")
        redis_client.set("clear:other:1", "v3")

        deleted = clear_cache("clear:test:*", redis_client=redis_client)
        assert deleted == 2
        assert not redis_client.exists("clear:test:1")
        assert not redis_client.exists("clear:test:2")
        assert redis_client.exists("clear:other:1")

    def test_clear_cache_no_keys(self, redis_client):
        deleted = clear_cache("nonexistent:*", redis_client=redis_client)
        assert deleted == 0

    def test_clear_cache_error(self, redis_client):
        original_keys = redis_client.keys
        redis_client.keys = lambda pattern: (_ for _ in ()).throw(redis.RedisError("redis error"))
        try:
            with pytest.raises(CacheError):
                clear_cache("test:*", redis_client=redis_client)
        finally:
            redis_client.keys = original_keys

    def test_clear_cache_returns_deleted_count(self, redis_client):
        redis_client.set("count:1", "v1")
        redis_client.set("count:2", "v2")
        redis_client.set("count:3", "v3")

        deleted = clear_cache("count:*", redis_client=redis_client)
        assert deleted == 3

    def test_clear_cache_single_key(self, redis_client):
        redis_client.set("single:key", "value")
        deleted = clear_cache("single:key", redis_client=redis_client)
        assert deleted == 1
        assert not redis_client.exists("single:key")
