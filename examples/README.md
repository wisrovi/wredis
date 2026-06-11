# WRedis Examples

Practical examples demonstrating how to use `wredis` library for Redis operations in Python.

## Quick Start

```bash
# Install dependencies
pip install wredis redis

# Make sure Redis is running
redis-server

# Run all examples
pytest examples/test/test_all_examples.py -v

# Run a specific example
python examples/sync/base/01_basic_init/example.py
```

## Clean Import API

All examples use consistent imports from `wredis.sync` or `wredis.aio`:

```python
# Sync operations
from wredis.sync import (
    BaseManager,
    RedisHashManager,
    RedisBitmapManager,
    RedisQueueManager,
    cache,
    CacheMetrics,
)

# Async operations
from wredis.aio import (
    AsyncBaseManager,
    AsyncRedisHashManager,
    AsyncRedisQueueManager,
    async_cache,
    CacheMetrics,
)
```

## Structure

```
examples/
├── async/                      # Async examples
│   ├── base/                   # AsyncBaseManager examples (15)
│   ├── bitmap/                 # Bitmap operations (2)
│   ├── cache/                  # Cache decorators (1)
│   ├── cluster/                # Redis Cluster (1)
│   ├── geo/                    # Geographic operations (2)
│   ├── hash/                   # Hash operations (2)
│   ├── hyperloglog/            # HyperLogLog (2)
│   ├── pipeline/               # Pipeline operations (2)
│   ├── pubsub/                 # Pub/Sub (2)
│   ├── queue/                  # Queue operations (2)
│   ├── sentinel/               # Redis Sentinel (1)
│   ├── sets/                   # Set operations (2)
│   ├── sorted_set/             # Sorted set operations (2)
│   ├── streams/                # Redis Streams (2)
│   └── transaction/            # Transactions (2)
│
├── sync/                       # Sync examples
│   ├── base/                   # BaseManager examples (15)
│   ├── bitmap/                 # Bitmap operations (3)
│   ├── cache/                  # Cache metrics examples (15)
│   ├── cluster/                # Redis Cluster (1)
│   ├── exceptions/             # Error handling (15)
│   ├── geo/                    # Geographic operations (2)
│   ├── hash/                   # Hash operations (6)
│   ├── hyperloglog/            # HyperLogLog (2)
│   ├── pipeline/               # Pipeline operations (2)
│   ├── pubsub/                 # Pub/Sub (4)
│   ├── queue/                  # Queue operations (2)
│   ├── retry/                  # Retry patterns (15)
│   ├── sentinel/               # Redis Sentinel (1)
│   ├── serializer/             # Serialization (15)
│   ├── sets/                   # Set operations (3)
│   ├── sorted_set/             # Sorted set operations (3)
│   ├── streams/                # Redis Streams (2)
│   ├── transaction/            # Transactions (2)
│   └── validation/             # Input validation (15)
│
└── test/                      # Test suite
    ├── conftest.py            # Pytest fixtures
    └── test_all_examples.py   # Auto-discovers and runs all examples
```

## Examples by Category

### Async Operations

| Category | Examples | Description |
|----------|----------|-------------|
| [base/](async/base/) | 15 | AsyncBaseManager with async/await |
| [bitmap/](async/bitmap/) | 2 | Bitmap operations |
| [cache/](async/cache/) | 1 | Async cache decorators |
| [cluster/](async/cluster/) | 1 | Redis Cluster support |
| [geo/](async/geo/) | 2 | Geographic queries |
| [hash/](async/hash/) | 2 | Hash operations |
| [hyperloglog/](async/hyperloglog/) | 2 | HyperLogLog |
| [pipeline/](async/pipeline/) | 2 | Pipeline operations |
| [pubsub/](async/pubsub/) | 2 | Pub/Sub messaging |
| [queue/](async/queue/) | 2 | Message queues |
| [sentinel/](async/sentinel/) | 1 | Sentinel HA |
| [sets/](async/sets/) | 2 | Set operations |
| [sorted_set/](async/sorted_set/) | 2 | Sorted sets |
| [streams/](async/streams/) | 2 | Redis Streams |
| [transaction/](async/transaction/) | 2 | Transactions |

### Sync Operations

| Category | Examples | Description |
|----------|----------|-------------|
| [base/](sync/base/) | 15 | BaseManager basics |
| [bitmap/](sync/bitmap/) | 3 | Bitmap operations |
| [cache/](sync/cache/) | 15 | Cache metrics & decorators |
| [cluster/](sync/cluster/) | 1 | Redis Cluster |
| [exceptions/](sync/exceptions/) | 15 | Error handling |
| [geo/](sync/geo/) | 2 | Geographic queries |
| [hash/](sync/hash/) | 6 | Hash CRUD operations |
| [hyperloglog/](sync/hyperloglog/) | 2 | HyperLogLog |
| [pipeline/](sync/pipeline/) | 2 | Pipeline operations |
| [pubsub/](sync/pubsub/) | 4 | Pub/Sub messaging |
| [queue/](sync/queue/) | 2 | Message queues |
| [retry/](sync/retry/) | 15 | Retry patterns |
| [sentinel/](sync/sentinel/) | 1 | Sentinel HA |
| [serializer/](sync/serializer/) | 15 | Data serialization |
| [sets/](sync/sets/) | 3 | Set operations |
| [sorted_set/](sync/sorted_set/) | 3 | Sorted sets |
| [streams/](sync/streams/) | 2 | Redis Streams |
| [transaction/](sync/transaction/) | 2 | Transactions |
| [validation/](sync/validation/) | 15 | Input validation |

## Running Tests

### Run all examples as tests
```bash
pytest examples/test/test_all_examples.py -v
```

### Run specific category
```bash
pytest examples/test/test_all_examples.py -v -k "sync/base"
pytest examples/test/test_all_examples.py -v -k "async/base"
```

### Run single example manually
```bash
python examples/sync/base/01_basic_init/example.py
```

## Each Example Contains

- **README.md** - Description, Mermaid diagram, when to use, code, run instructions
- **example.py** - Ready-to-run code that you can copy and adapt

## Requirements

```bash
pip install wredis redis
```

Make sure Redis is running:
```bash
redis-server
```
