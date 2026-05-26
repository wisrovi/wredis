# WRedis

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/badge/style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![PyPI](https://img.shields.io/badge/pypi-v0.9.6-blue.svg)](https://pypi.org/project/wredis/)
[![Coverage](https://img.shields.io/badge/coverage-95%25%2B-brightgreen.svg)]()
[![LTS](https://img.shields.io/badge/LTS-v0.9.6-orange.svg)]()

**WRedis** — Production-ready Python library for Redis with sync/async APIs, cache decorators, high availability, and comprehensive type safety.

---

## Installation

```bash
pip install wredis
```

Requires Python 3.9+ and a running Redis server (local or remote).

---

## Features

| Feature | Description |
|---------|-------------|
| **Sync & Async** | Full support for both synchronous and asynchronous (`asyncio`) APIs |
| **Cache Decorators** | `@cache` / `@async_cache` with hit/miss metrics and TTL management |
| **High Availability** | Redis Sentinel and Cluster support |
| **12 Data Structures** | Bitmap, Hash, Set, SortedSet, Stream, Queue, Pub/Sub, Geo, HyperLogLog, Pipeline, Transaction |
| **Error Handling** | Proper exception hierarchy, no silent failures |
| **Type Safety** | Fully type-hinted, mypy clean |
| **Compression** | Optional gzip compression for queue messages |
| **Validation** | Built-in key, TTL, and value validation |

---

## Quick Start

```python
from wredis.cache import RedisCacheManager

cache = RedisCacheManager(host="localhost")

@cache("my_cache", ttl=60)
def expensive_function(param: str) -> dict:
    return {"result": f"processed {param}"}

data = expensive_function("hello")  # cached for 60s
```

---

## Modules

### Bitmap

```python
from wredis.bitmap import RedisBitmapManager

bm = RedisBitmapManager(host="localhost")
bm.set_bit("my_bitmap", offset=5, value=1)
print(bm.get_bit("my_bitmap", 0))   # 0
print(bm.count_bits("my_bitmap"))    # 1
```

**Methods:** `set_bit`, `get_bit`, `count_bits`, `get_ttl`, `extend_ttl`

---

### Hash

```python
from wredis.hash import RedisHashManager

hm = RedisHashManager(host="localhost")
hm.create_hash("users", "user:1", {"name": "Alice", "age": 30}, ttl=60)
user = hm.read_hash("users", "user:1")
all_users = hm.read_all_hash("users")
hm.update_hash("users", "user:1", {"age": 31})
hm.delete_hash_field("users", "user:2")
```

**Methods:** `create_hash`, `read_hash`, `update_hash`, `delete_hash_field`, `read_all_hash`, `get_ttl`, `extend_ttl`

---

### Queue

```python
from wredis.queue import RedisQueueManager

# Producer
qm = RedisQueueManager(host="localhost")
qm.publish("tasks", {"id": 1, "task": "process_image"}, ttl=30)

# Consumer
@qm.on_message("tasks")
def worker(record):
    print(f"Processing: {record}")

qm.start()
qm.wait()
```

**Methods:** `publish`, `on_message`, `start`, `stop`, `wait`, `get_queue_length`

---

### Pub/Sub

```python
from wredis.pubsub import RedisPubSubManager

pbm = RedisPubSubManager(host="localhost")

# Producer
pbm.publish_message("notifications", "Hello, Redis!")
pbm.publish_message("alerts", {"severity": "high", "message": "Disk full"})

# Consumer
@pbm.on_message("notifications")
def handle(msg):
    print(f"Received: {msg}")

pbm.stop_listeners()
```

**Methods:** `publish_message`, `on_message`, `stop_listeners`

---

### Streams

```python
from wredis.streams import RedisStreamManager

sm = RedisStreamManager(host="localhost")

# Producer
sm.add_to_stream("events", {"action": "login", "user": "alice"})

# Consumer
@sm.on_message("events", group_name="my_group", consumer_name="worker_1")
def process(data):
    print(f"Processing: {data}")

sm.wait()
```

**Methods:** `add_to_stream`, `on_message`, `read_from_stream`, `wait`

---

### Sets

```python
from wredis.sets import RedisSetManager

sm = RedisSetManager(host="localhost")
sm.add_to_set("tags", "python", "redis", "wredis")
members = sm.get_set_members("tags")
print(sm.is_member("tags", "python"))  # True
sm.remove_from_set("tags", "redis")
```

**Methods:** `add_to_set`, `get_set_members`, `is_member`, `remove_from_set`, `get_ttl`, `extend_ttl`

---

### Sorted Sets

```python
from wredis.sortedset import RedisSortedSetManager

ssm = RedisSortedSetManager(host="localhost")
ssm.add_to_sorted_set("leaderboard", 100, "player1")
ssm.add_to_sorted_set("leaderboard", 200, "player2")
ssm.add_to_sorted_set("leaderboard", 150, "player3")

top = ssm.get_sorted_set_reverse("leaderboard", with_scores=True)
rank = ssm.get_rank("leaderboard", "player2")
score = ssm.get_score("leaderboard", "player3")
ssm.increment_score("leaderboard", 50, "player3")
```

**Methods:** `add_to_sorted_set`, `get_sorted_set`, `get_sorted_set_reverse`, `remove_from_sorted_set`, `get_rank`, `get_score`, `delete_sorted_set`, `set_ttl`, `get_ttl`, `increment_score`, `get_sorted_set_by_score`

---

### Geo

```python
from wredis.geo import RedisGeoManager

gm = RedisGeoManager(host="localhost")
gm.add_location("places", "Central Park", 40.785091, -73.968285)
dist = gm.distance("places", "Central Park", "Times Square")
```

**Methods:** `add_location`, `distance`, `geo_radius`, `get_location`

---

### HyperLogLog

```python
from wredis.hyperloglog import RedisHyperLogLogManager

hll = RedisHyperLogLogManager(host="localhost")
hll.add("visitors", "user1", "user2", "user3")
count = hll.count("visitors")
hll.merge("all_visitors", "visitors")
```

**Methods:** `add`, `count`, `merge`, `get_all`

---

### Pipeline

```python
from wredis.pipeline import RedisPipelineManager

pm = RedisPipelineManager(host="localhost")
pm.set_get("key1", "value1")
results = pm.mget_pipeline("key1", "key2", "key3")
```

**Methods:** `set_get`, `mget_pipeline`

---

### Transaction

```python
from wredis.transaction import RedisTransactionManager

tm = RedisTransactionManager(host="localhost")
result = tm.get_and_set("counter", "1")
```

**Methods:** `get_and_set`

---

### Cache Decorator

```python
from wredis.cache import RedisCacheManager

cache = RedisCacheManager(host="localhost")

@cache(ttl=60)
def get_user(user_id: str) -> dict:
    return {"id": user_id, "name": "Alice"}

# Call decorated function — results are cached
user = get_user("42")
```

**Methods:** `@cache` (sync), `@async_cache` (async), `invalidate`, `clear`, `get_stats`

---

## High Availability

### Sentinel

```python
from wredis.ha.sentinel import RedisSentinelManager

sm = RedisSentinelManager(
    sentinel_hosts=[("sentinel1", 26379), ("sentinel2", 26379)],
    service_name="mymaster",
    password="optional",
)
```

### Cluster

```python
from wredis.ha.cluster import RedisClusterManager

cm = RedisClusterManager(
    startup_nodes=[{"host": "node1", "port": 6379}],
    password="optional",
)
```

---

## Configuration

All managers accept common connection parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `host` | `"localhost"` | Redis server hostname |
| `port` | `6379` | Redis server port |
| `db` | `0` | Redis database number |
| `password` | `None` | Redis password |
| `verbose` | `True` | Enable logging |
| `decode_responses` | `False` | Decode responses to strings |

Queue-specific:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `poll_interval` | `1` | Seconds between polls for empty queues |
| `max_retries` | `3` | Maximum retry attempts on error |
| `compress` | `False` | Enable gzip compression for messages |

---

## Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=wredis tests/

# Run specific module tests
pytest tests/unit/test_queue.py
pytest tests/integration/test_all_modules_integration.py
```

---

## License

MIT — see [LICENSE](LICENSE) for details.
