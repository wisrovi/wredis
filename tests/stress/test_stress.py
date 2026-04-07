"""Stress tests for wredis under concurrent load."""

import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import fakeredis
import fakeredis.aioredis
import pytest

from wredis.decorators import CacheMetrics, cache, clear_cache
from wredis.pubsub import RedisPubSubManager
from wredis.queue.queue import RedisQueueManager


@pytest.fixture
def fake_redis():
    """Provide a fakeredis client."""
    client = fakeredis.FakeRedis(decode_responses=True)
    yield client
    client.flushall()


@pytest.fixture
def fake_redis_binary():
    """Provide a fakeredis client with binary mode."""
    client = fakeredis.FakeRedis(decode_responses=False)
    yield client
    client.flushall()


@pytest.fixture
def async_fake_redis():
    """Provide an async fakeredis client."""
    client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    return client


class TestConcurrentOperations:
    """Stress tests for concurrent Redis operations."""

    def test_concurrent_set_get(self, fake_redis):
        """Stress test concurrent set and get operations."""
        num_ops = 500
        errors = []

        def worker(i):
            try:
                key = f"stress:key:{i}"
                fake_redis.set(key, f"value:{i}")
                val = fake_redis.get(key)
                assert val == f"value:{i}"
            except Exception as e:
                errors.append(e)

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(worker, i) for i in range(num_ops)]
            for f in as_completed(futures):
                f.result()

        assert len(errors) == 0, f"Errors during concurrent set/get: {errors}"

    def test_concurrent_incr(self, fake_redis):
        """Stress test concurrent increment on a single key."""
        num_increments = 200
        fake_redis.set("counter", 0)

        def worker():
            for _ in range(10):
                fake_redis.incr("counter")

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(worker) for _ in range(num_increments // 10)]
            for f in as_completed(futures):
                f.result()

        final = int(fake_redis.get("counter"))
        assert final == num_increments

    def test_concurrent_list_push(self, fake_redis):
        """Stress test concurrent list pushes."""
        num_pushes = 300
        errors = []

        def worker(i):
            try:
                fake_redis.rpush("stress:list", f"item:{i}")
            except Exception as e:
                errors.append(e)

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(worker, i) for i in range(num_pushes)]
            for f in as_completed(futures):
                f.result()

        assert len(errors) == 0
        assert fake_redis.llen("stress:list") == num_pushes


class TestConnectionPoolExhaustion:
    """Stress tests for connection pool behavior."""

    def test_pool_exhaustion_recovery(self, fake_redis):
        """Test that operations recover after pool exhaustion."""
        num_threads = 50
        results = {"success": 0, "fail": 0}
        lock = threading.Lock()

        def worker(i):
            try:
                fake_redis.set(f"pool:test:{i}", f"val:{i}")
                fake_redis.get(f"pool:test:{i}")
                with lock:
                    results["success"] += 1
            except Exception:
                with lock:
                    results["fail"] += 1

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker, i) for i in range(200)]
            for f in as_completed(futures):
                f.result()

        assert results["success"] > 0

    def test_rapid_connect_disconnect(self, fake_redis):
        """Stress test rapid connection creation and cleanup."""
        for i in range(100):
            client = fakeredis.FakeRedis(decode_responses=True)
            client.set(f"rapid:{i}", "ok")
            assert client.get(f"rapid:{i}") == "ok"
            client.flushdb()

    def test_concurrent_pipeline(self, fake_redis):
        """Stress test concurrent pipeline execution."""
        num_pipelines = 100
        errors = []

        def worker(i):
            try:
                pipe = fake_redis.pipeline()
                for j in range(10):
                    pipe.set(f"pipe:{i}:{j}", f"val:{j}")
                pipe.execute()
            except Exception as e:
                errors.append(e)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker, i) for i in range(num_pipelines)]
            for f in as_completed(futures):
                f.result()

        assert len(errors) == 0


class TestPubSubHighMessageRate:
    """Stress tests for pub/sub under high message rates."""

    def test_high_rate_publish(self, fake_redis):
        """Stress test high-rate message publishing."""
        manager = RedisPubSubManager(host="localhost", verbose=False)
        manager.redis_client = fake_redis

        num_messages = 500
        for i in range(num_messages):
            manager.publish_message("stress:channel", f"msg:{i}")

    def test_pubsub_concurrent_publish(self, fake_redis):
        """Stress test concurrent publishing to same channel."""
        manager = RedisPubSubManager(host="localhost", verbose=False)
        manager.redis_client = fake_redis
        errors = []

        def publisher(start, end):
            try:
                for i in range(start, end):
                    manager.publish_message("concurrent:ch", f"msg:{i}")
            except Exception as e:
                errors.append(e)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            batch = 50
            for i in range(0, 500, batch):
                futures.append(executor.submit(publisher, i, i + batch))
            for f in as_completed(futures):
                f.result()

        assert len(errors) == 0

    def test_pubsub_multiple_channels(self, fake_redis):
        """Stress test publishing across many channels simultaneously."""
        manager = RedisPubSubManager(host="localhost", verbose=False)
        manager.redis_client = fake_redis

        num_channels = 50
        msgs_per_channel = 20

        def channel_worker(ch):
            for i in range(msgs_per_channel):
                manager.publish_message(f"ch:{ch}", f"msg:{i}")

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(channel_worker, ch) for ch in range(num_channels)
            ]
            for f in as_completed(futures):
                f.result()


class TestQueueHighThroughput:
    """Stress tests for queue under high throughput."""

    def test_high_throughput_publish(self, fake_redis):
        """Stress test high-throughput queue publishing."""
        manager = RedisQueueManager(
            host="localhost",
            port=6379,
            db=0,
            poll_interval=1,
            max_retries=3,
            verbose=False,
        )
        manager.redis_client = fake_redis

        num_messages = 1000
        for i in range(num_messages):
            manager.publish("stress:queue", {"index": i})

        length = manager.get_queue_length("stress:queue")
        assert length == num_messages

    def test_queue_concurrent_publish(self, fake_redis):
        """Stress test concurrent queue publishing."""
        manager = RedisQueueManager(
            host="localhost",
            port=6379,
            db=0,
            poll_interval=1,
            max_retries=3,
            verbose=False,
        )
        manager.redis_client = fake_redis
        errors = []

        def publisher(start, end):
            try:
                for i in range(start, end):
                    manager.publish("concurrent:queue", {"index": i})
            except Exception as e:
                errors.append(e)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            batch = 50
            for i in range(0, 500, batch):
                futures.append(executor.submit(publisher, i, i + batch))
            for f in as_completed(futures):
                f.result()

        assert len(errors) == 0
        assert manager.get_queue_length("concurrent:queue") == 500

    def test_queue_multiple_queues_concurrent(self, fake_redis):
        """Stress test concurrent operations across multiple queues."""
        manager = RedisQueueManager(
            host="localhost",
            port=6379,
            db=0,
            poll_interval=1,
            max_retries=3,
            verbose=False,
        )
        manager.redis_client = fake_redis

        num_queues = 20
        msgs_per_queue = 50

        def queue_worker(q):
            for i in range(msgs_per_queue):
                manager.publish(f"queue:{q}", {"q": q, "i": i})

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(queue_worker, q) for q in range(num_queues)]
            for f in as_completed(futures):
                f.result()

        for q in range(num_queues):
            assert manager.get_queue_length(f"queue:{q}") == msgs_per_queue


class TestCacheDecoratorConcurrent:
    """Stress tests for cache decorator under concurrent access."""

    def test_concurrent_cache_access(self, fake_redis):
        """Stress test concurrent access to cached function."""
        metrics = CacheMetrics()

        @cache(ttl=60, prefix="stress:cache", redis_client=fake_redis, metrics=metrics)
        def slow_func(x):
            time.sleep(0.001)
            return x * 2

        results = []
        errors = []

        def worker(i):
            try:
                r = slow_func(i % 10)
                results.append(r)
            except Exception as e:
                errors.append(e)

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(worker, i) for i in range(200)]
            for f in as_completed(futures):
                f.result()

        assert len(errors) == 0
        assert len(results) == 200

    def test_concurrent_cache_same_key(self, fake_redis):
        """Stress test concurrent access to the same cache key."""
        metrics = CacheMetrics()
        call_count = [0]
        lock = threading.Lock()

        @cache(ttl=60, prefix="same:key", redis_client=fake_redis, metrics=metrics)
        def counted_func(x):
            with lock:
                call_count[0] += 1
            return x + 1

        def worker():
            return counted_func(42)

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(worker) for _ in range(100)]
            for f in as_completed(futures):
                assert f.result() == 43

    def test_concurrent_cache_invalidation(self, fake_redis):
        """Stress test cache invalidation under concurrent access."""
        metrics = CacheMetrics()

        @cache(ttl=60, prefix="inval:cache", redis_client=fake_redis, metrics=metrics)
        def func_to_invalidate(x):
            return x * 3

        for i in range(50):
            func_to_invalidate(i)

        assert metrics.hits == 0
        assert metrics.misses == 50

        clear_cache("inval:cache:*", redis_client=fake_redis)
        metrics.reset()

        for i in range(50):
            func_to_invalidate(i)

        assert metrics.misses == 50


class TestAsyncStress:
    """Async stress tests."""

    @pytest.mark.asyncio
    async def test_async_concurrent_set_get(self, async_fake_redis):
        """Stress test async concurrent set/get operations."""
        num_ops = 200

        async def worker(i):
            key = f"async:stress:{i}"
            await async_fake_redis.set(key, f"val:{i}")
            val = await async_fake_redis.get(key)
            assert val == f"val:{i}"

        tasks = [worker(i) for i in range(num_ops)]
        await asyncio.gather(*tasks)

    @pytest.mark.asyncio
    async def test_async_concurrent_pubsub(self, async_fake_redis):
        """Stress test async concurrent pub/sub operations."""
        num_messages = 100

        async def publisher(i):
            await async_fake_redis.publish("async:ch", f"msg:{i}")

        tasks = [publisher(i) for i in range(num_messages)]
        await asyncio.gather(*tasks)

    @pytest.mark.asyncio
    async def test_async_concurrent_pipeline(self, async_fake_redis):
        """Stress test async concurrent pipeline operations."""
        num_pipelines = 50

        async def pipeline_worker(i):
            async with async_fake_redis.pipeline() as pipe:
                for j in range(10):
                    await pipe.set(f"async:pipe:{i}:{j}", f"val:{j}")
                await pipe.execute()

        tasks = [pipeline_worker(i) for i in range(num_pipelines)]
        await asyncio.gather(*tasks)

    @pytest.mark.asyncio
    async def test_async_high_throughput(self, async_fake_redis):
        """Stress test async high-throughput operations."""
        num_ops = 500

        async def worker(i):
            await async_fake_redis.rpush("async:queue", f"item:{i}")

        tasks = [worker(i) for i in range(num_ops)]
        await asyncio.gather(*tasks)

        length = await async_fake_redis.llen("async:queue")
        assert length == num_ops
