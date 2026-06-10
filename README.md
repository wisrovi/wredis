

# WRedis

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Coverage: 95%+](https://img.shields.io/badge/coverage-95%25%2B-brightgreen.svg)]()
[![Ruff](https://img.shields.io/badge/style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![PyPI](https://img.shields.io/badge/pypi-v1.0.0-blue.svg)](https://pypi.org/project/wredis/)
[![LTS](https://img.shields.io/badge/LTS-v1.0.0-orange.svg)]()

**WRedis v1.0.0 LTS** — Production-ready Python library for Redis with real async/await, cache decorators, high availability, and comprehensive type safety.

<img width="1452" height="826" alt="image" src="https://github.com/user-attachments/assets/ec5277c7-ec3d-4df2-88a3-37937a318133" />



## Description

WRedis simplifies interacting with Redis by providing:

- **Sync & Async APIs** — Real asyncio, zero threads
- **Cache Decorators** — `@cache`, `@async_cache` with hit/miss metrics
- **High Availability** — Sentinel & Cluster support
- **Error Handling** — Proper exceptions, no silent failures
- **Type Safety** — Full type hints, mypy clean
- **12 Data Structures** — Bitmap, Hash, Set, SortedSet, Stream, Queue, Pub/Sub, Geo, HyperLogLog, Pipeline, Transaction
- **95%+ Test Coverage** — 800+ unit tests, 38 integration tests (Redis real), 19 stress tests

## Installation

To install the library, use `pip`:

```bash
pip install wredis
```

Make sure you have Redis installed on your system or that you can access a remote Redis server. You can install Redis locally by following the [official instructions](https://redis.io/download) or use a `docker-compose.yaml` like the following:

```yaml
version: "3.3"
services:
  redis:
    image: redislabs/redismod
    ports:
      - "6379:6379"
    environment:
      - SO=docker
    volumes:
      - ./cache_redis:/data
    command: --dir /data --loadmodule /usr/lib/redis/modules/redistimeseries.so

  redis-commander:
    image: rediscommander/redis-commander:latest
    environment:
      - REDIS_HOSTS=local:redis:6379
      - HTTP_USER=root
      - HTTP_PASSWORD=qwerty
    ports:
      - "8081:8081"
    depends_on:
      - redis
```

## Modules

The **WRedis** library offers a series of modules that facilitate interaction with Redis. The available modules are described below:

---

## Bitmaps

**Class:** `RedisBitmapManager`

This module allows you to interact with bitmaps in Redis.

### Constructor

```python
RedisBitmapManager(host="localhost", port=6379, db=0, verbose=True)
```

### Methods

| Method | Description |
|--------|-------------|
| `set_bit(key, offset, value, ttl=-1)` | Sets a bit at a specific position. Optionally sets TTL. |
| `get_bit(key, offset)` | Retrieves the value of a bit at a specific position (0 or 1). |
| `count_bits(key)` | Counts the number of bits set to 1 in a bitmap. |
| `get_ttl(key)` | Retrieves the TTL for a bitmap key. Returns -1 (no TTL), -2 (key doesn't exist), or seconds remaining. |
| `extend_ttl(key, ttl)` | Extends or sets a new TTL for a bitmap key. |

### Example

```python
from wredis.bitmap import RedisBitmapManager

bitmap_manager = RedisBitmapManager(host="localhost")

# Write
bitmap_manager.set_bit(key="my_bitmap", offset=5, value=1)

# Read
print(bitmap_manager.get_bit("my_bitmap", 0))
print(bitmap_manager.count_bits("my_bitmap"))

# TTL
bitmap_manager.set_bit(key="my_bitmap", offset=10, value=1, ttl=300)
print(bitmap_manager.get_ttl("my_bitmap"))
bitmap_manager.extend_ttl("my_bitmap", 600)
```

---

## Hash

**Class:** `RedisHashManager`

This module allows you to interact with hashes in Redis. Supports automatic JSON serialization for dict values.

### Constructor

```python
RedisHashManager(host="localhost", port=6379, db=0, verbose=True)
```

### Methods

| Method | Description |
|--------|-------------|
| `create_hash(hash_name, key, value, ttl=-1)` | Writes a key-value pair into a Redis hash. Dict values are auto-serialized to JSON. |
| `read_hash(hash_name, key)` | Reads a value from a hash. Auto-deserializes JSON if applicable. Returns `None` if not found. |
| `update_hash(hash_name, key, new_data)` | Updates a key-value pair. If the field exists and is a dict, merges the data. Otherwise, replaces it. |
| `delete_hash_field(hash_name, key)` | Deletes a specific field from a hash. |
| `read_all_hash(hash_name)` | Reads all fields and values from a hash. Returns a dict or `None`. |
| `get_ttl(hash_name)` | Retrieves the TTL for a hash. Returns -1 (no TTL), -2 (key doesn't exist), or seconds remaining. |
| `extend_ttl(hash_name, ttl)` | Extends or sets a new TTL for a hash. |

### Example

```python
from wredis.hash import RedisHashManager

redis_manager = RedisHashManager(host="localhost")

# Create
redis_manager.create_hash("my_hash", "user:1", {"name": "Alice", "age": 30}, ttl=60)
redis_manager.create_hash("my_hash", "user:2", {"name": "Bob", "age": 25})

# Read
user1 = redis_manager.read_hash("my_hash", "user:1")
print(f"User 1: {user1}")

all_users = redis_manager.read_all_hash("my_hash")
print(f"All users: {all_users}")

# Update
redis_manager.update_hash("my_hash", "user:3", {"name": "William", "age": 35, "gender": "male"})

# Delete
redis_manager.delete_hash_field("my_hash", "user:2")

# TTL
print(redis_manager.get_ttl("my_hash"))
redis_manager.extend_ttl("my_hash", 120)
```

---

## Pub/Sub

**Class:** `RedisPubSubManager`

This module allows you to interact with the Redis publish/subscribe system using a decorator-based API.

### Constructor

```python
RedisPubSubManager(host="localhost", port=6379, db=0, verbose=True)
```

### Methods

| Method | Description |
|--------|-------------|
| `publish_message(channel, message)` | Publishes a message to a channel. Supports strings and dicts (auto-serialized to JSON). |
| `on_message(channel)` | Decorator to register a callback function for a specific channel. Starts a listener thread automatically. |
| `stop_listeners()` | Stops all listener threads. |

### Example

**Producer:**

```python
from wredis.pubsub import RedisPubSubManager

pubsub_manager = RedisPubSubManager(host="localhost")

pubsub_manager.publish_message("channel_1", "Hello, Redis!")
pubsub_manager.publish_message("channel_2", {"saludo": "Hola desde channel_2!"})
```

**Consumer:**

```python
from wredis.pubsub import RedisPubSubManager
import signal

pubsub_manager = RedisPubSubManager(host="localhost", verbose=False)

@pubsub_manager.on_message("channel_1")
def handle_message(message):
    print(f"[channel_1] Received: {message}")

@pubsub_manager.on_message("channel_2")
def handle_channel_2(message):
    print(f"[channel_2] Received: {message}")

def signal_handler(sig, frame):
    print("\nStopping...")
    pubsub_manager.stop_listeners()
    exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.pause()
```

---

## Queue

**Class:** `RedisQueueManager`

This module allows you to interact with queues in Redis using lists (`RPUSH`/`BRPOP`).

### Constructor

```python
RedisQueueManager(poll_interval=1, host="localhost", port=6379, db=0, max_retries=3, verbose=True)
```

### Methods

| Method | Description |
|--------|-------------|
| `publish(queue_name, data, ttl=-1)` | Publishes a message (dict) to a queue. Auto-serialized to JSON. Optionally sets TTL on the queue key. |
| `on_message(queue_name)` | Decorator to register a callback function for a specific queue. |
| `start()` | Starts parallel consumption threads for all registered queues. |
| `stop()` | Stops consumption for all queues and joins threads. |
| `wait()` | Keeps the program running and handles SIGINT for clean shutdown. |
| `get_queue_length(queue_name)` | Returns the number of elements in a queue. |

### Example

**Producer:**

```python
from wredis.queue import RedisQueueManager

queue_manager = RedisQueueManager(host="localhost")

queue_manager.publish("tasks", {"id": 1, "task": "process_image", "status": "pending"})
queue_manager.publish("tasks", {"id": 2, "task": "generate_report", "priority": "high"}, ttl=30)
```

**Consumer:**

```python
from wredis.queue import RedisQueueManager

queue_manager = RedisQueueManager(poll_interval=2, host="localhost", verbose=False)

@queue_manager.on_message("tasks")
def worker(record):
    print(f"Processing: {record}")

queue_manager.start()
queue_manager.wait()
```

> **Note:** Setting a TTL on a queue modifies the TTL of the entire queue key, not individual messages. TTL is measured in seconds.

---

## Sets

**Class:** `RedisSetManager`

This module allows you to interact with sets in Redis.

### Constructor

```python
RedisSetManager(host="localhost", port=6379, db=0, verbose=True)
```

### Methods

| Method | Description |
|--------|-------------|
| `add_to_set(key, *values, ttl=-1)` | Adds one or more elements to a set. Optionally sets TTL. |
| `get_set_members(key)` | Retrieves all members of a set as a decoded `set`. |
| `is_member(key, value)` | Checks if an element is a member of the set. Returns `True` or `False`. |
| `remove_from_set(key, *values)` | Removes one or more elements from a set. |
| `get_ttl(key)` | Retrieves the TTL for a set. Returns -1 (no TTL), -2 (key doesn't exist), or seconds remaining. |
| `extend_ttl(key, ttl)` | Extends or sets a new TTL for a set. |

### Example

```python
from wredis.sets import RedisSetManager

set_manager = RedisSetManager(host="localhost")

# Add
set_manager.add_to_set("my_set", "value1", "value2")
set_manager.add_to_set("my_set", "value5", ttl=300)

# Read
print(set_manager.get_set_members("my_set"))
print(set_manager.is_member("my_set", "value1"))

# Remove
set_manager.remove_from_set("my_set", "value2")

# TTL
print(set_manager.get_ttl("my_set"))
set_manager.extend_ttl("my_set", 600)
```

---

## Sorted Sets

**Class:** `RedisSortedSetManager`

This module allows you to interact with sorted sets in Redis.

### Constructor

```python
RedisSortedSetManager(host="localhost", port=6379, db=0, verbose=True)
```

### Methods

| Method | Description |
|--------|-------------|
| `add_to_sorted_set(key, score, member, ttl=-1)` | Adds a member with a score. Optionally sets TTL. |
| `get_sorted_set(key, start=0, stop=-1, with_scores=False)` | Retrieves elements in ascending order. Returns list of members or `(member, score)` tuples. |
| `get_sorted_set_reverse(key, start=0, stop=-1, with_scores=False)` | Retrieves elements in descending order. |
| `remove_from_sorted_set(key, member)` | Removes a member from the sorted set. |
| `get_rank(key, member)` | Retrieves the rank (0-based index) of a member. |
| `get_score(key, member)` | Retrieves the score of a member. |
| `delete_sorted_set(key)` | Deletes the entire sorted set. |
| `set_ttl(key, ttl)` | Sets a TTL for an existing sorted set. |
| `get_ttl(key)` | Retrieves the TTL for a sorted set. |
| `increment_score(key, increment, member)` | Increments the score of a member by a given amount. |
| `get_sorted_set_by_score(key, min_score, max_score, with_scores=False)` | Retrieves members within a specific score range. |

### Example

```python
from wredis.sortedset import RedisSortedSetManager

sorted_set_manager = RedisSortedSetManager(host="localhost")

# Add
sorted_set_manager.add_to_sorted_set("my_sorted_set", 1, "item1")
sorted_set_manager.add_to_sorted_set("my_sorted_set", 3, "item3")
sorted_set_manager.add_to_sorted_set("my_sorted_set", 2, "item2")

# Read
items = sorted_set_manager.get_sorted_set("my_sorted_set", with_scores=True)
items_reverse = sorted_set_manager.get_sorted_set_reverse("my_sorted_set")

# Rank and score
rank = sorted_set_manager.get_rank("my_sorted_set", "item1")
score = sorted_set_manager.get_score("my_sorted_set", "item2")

# Increment score
sorted_set_manager.increment_score("my_sorted_set", 5, "item1")

# Range by score
by_score = sorted_set_manager.get_sorted_set_by_score("my_sorted_set", 1, 3, with_scores=True)

# Remove
sorted_set_manager.remove_from_sorted_set("my_sorted_set", "item1")

# Delete entire sorted set
# sorted_set_manager.delete_sorted_set("my_sorted_set")

# TTL
sorted_set_manager.set_ttl("my_sorted_set", 300)
print(sorted_set_manager.get_ttl("my_sorted_set"))
```

---

## Streams

**Class:** `RedisStreamManager`

This module allows you to interact with Redis Streams using consumer groups.

### Constructor

```python
RedisStreamManager(host="localhost", port=6379, db=0, verbose=True)
```

### Methods

| Method | Description |
|--------|-------------|
| `add_to_stream(key, data, ttl=None)` | Adds a message to a stream. Returns the message ID. Optionally sets TTL. |
| `on_message(stream_name, group_name, consumer_name)` | Decorator to register a consumer for a stream. Creates the consumer group if it doesn't exist. Starts a listener thread. |
| `read_from_stream(key, count=1, block=None)` | Reads messages from a stream without a registered consumer. |
| `wait()` | Keeps the program running and handles SIGINT for clean shutdown. |

### Example

**Producer:**

```python
from wredis.streams import RedisStreamManager

stream_manager = RedisStreamManager(host="localhost")

stream_manager.add_to_stream("my_stream", {"field1": "value1"})
stream_manager.add_to_stream("my_stream", {"field2": "value3", "field4": "value4"})
stream_manager.add_to_stream("my_stream_2", {"field1": "value1"})
```

**Consumer:**

```python
from wredis.streams import RedisStreamManager

stream_manager = RedisStreamManager(host="localhost", verbose=False)

@stream_manager.on_message(
    stream_name="my_stream", group_name="my_group", consumer_name="consumer_1"
)
def process_message(data):
    print(f"[Consumer 1] Processing: {data}")

@stream_manager.on_message(
    stream_name="my_stream_2", group_name="my_group", consumer_name="consumer_2"
)
def process_message_consumer_2(data):
    print(f"[Consumer 2] Processing: {data}")

stream_manager.wait()
```

---

## License

MIT

This project is licensed under the MIT license. See the `LICENSE` file for more details.

## Examples

This directory contains a collection of examples that demonstrate the usage of various modules and functionalities. Each subfolder corresponds to a specific module and includes example scripts to help you understand how to use that module.

### Directory Structure

```
examples/
    bitmap/
        read.py
        write.py
    hash/
        read.py
        write.py
    pub_sub/
        consumer.py
        producer.py
    queue/
        consumer.py
        producer.py
    sets/
        read.py
        write.py
    sorted_set.py/
        read.py
        write.py
    streams/
        consume.py
        producer.py
```

### How to Use

1. Navigate to the module folder of interest, e.g., `examples/bitmap/`.
2. Run the scripts directly using:
   ```bash
   python read.py
   python write.py
   ```
