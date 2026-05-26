# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

- **Clean Import API**: New consistent module structure:
  - `from wredis.sync import ...` - for all sync operations
  - `from wredis.aio import ...` - for all async operations
  - `from wredis import cache` - for cache decorator

- **Examples Reorganization**: All 164 examples restructured to a consistent format:
  - Each example now has its own folder (e.g., `examples/sync/base/01_basic_init/`)
  - Each folder contains `example.py` and `README.md`
  - READMEs include Mermaid diagrams, descriptions, and run instructions
  - Tests can now run all examples: `pytest examples/test/test_all_examples.py`

- **Examples Categories** (new structure):
  - `async/base/` - 15 AsyncBaseManager examples
  - `sync/base/` - 15 BaseManager examples  
  - `sync/cache/` - 15 Cache metrics examples
  - `sync/exceptions/` - 15 Error handling examples
  - `sync/retry/` - 15 Retry pattern examples
  - `sync/serializer/` - 15 Serialization examples
  - `sync/validation/` - 15 Validation examples
  - Plus: bitmap, geo, hash, hyperloglog, pipeline, pubsub, queue, sets, sorted_set, streams, transaction, cluster, sentinel

### Changed

- Removed `fakeredis` from all examples (now use real Redis)
- Examples README files updated to English with Mermaid diagrams
- Examples now use `from wredis.sync import ...` or `from wredis.aio import ...`
- Simplified async examples - no manual redis client creation needed

### Fixed

- Example tests now properly skip long-running processes (pubsub subscribers, queue consumers)
- AsyncBaseManager now creates connections correctly without manual injection


## [1.0.0] - 2026-04-03

### LTS Release

This is the first Long-Term Support (LTS) release of WRedis, supported for 3+ years.

### Breaking Changes

- **Error Handling**: Operations now raise specific exceptions instead of silently logging errors and returning defaults. All managers propagate `ValidationError`, `OperationError`, etc.
- **Async API Rewritten**: All async managers now use real `asyncio` tasks instead of threads. `AsyncRedisPubSubManager`, `AsyncRedisQueueManager`, and `AsyncRedisStreamManager` use `asyncio.create_task()` for consumers.
- **Connection Pooling**: Managers now use explicit connection pools via `BaseManager` and `AsyncBaseManager`.
- **Python 3.10+ Required**: Dropped support for Python 3.8 and 3.9.

### Added

- **Foundation Modules**:
  - `BaseManager` / `AsyncBaseManager` — Connection pooling, health checks, context managers, retry logic
  - `_serializer` — Centralized JSON serialization with proper error handling
  - `_validation` — Input validation for keys, TTL, offsets, scores, bit values
  - `_retry` — Retry decorators with exponential backoff (`@retry`, `@async_retry`)

- **Exception Hierarchy** (8 new exceptions):
  - `ValidationError`, `OperationError`, `TransactionError`
  - `QueueError`, `StreamError`, `PubSubError`

- **Cache Metrics**: `CacheMetrics` class tracking hits, misses, errors, and hit rate percentage

- **New Data Structures**: Geo, HyperLogLog, Pipeline, Transaction managers

- **High Availability**: Sentinel and Cluster support

- **CI/CD**: 10 GitHub Actions jobs (lint, mypy, test matrix, integration, stress, security, docs, release)

- **Documentation**: Sphinx docs with migration guide, deprecation policy, API stability guarantee, 105 example scripts

- **Testing**: 800+ unit tests, 38 integration tests (Redis real), 19 stress tests, 95%+ coverage

### Deprecated

- Silent error returns (now raise exceptions)
- Thread-based async consumers (now use asyncio tasks)
- Implicit connections (now use BaseManager with connection pooling)
  - `ClusterRedisManager` - Redis Cluster with hash slot routing

- **Convenience Functions** - Simplified top-level API:
  - `publish(channel, message, host="localhost")` - Pub/Sub without boilerplate
  - `subscribe(channel, callback, host="localhost")` - Subscribe simplified
  - `enqueue(queue_name, data, host="localhost")` - Queue without boilerplate
  - `xadd(stream_name, data, host="localhost")` - Stream without boilerplate

- **Auto-Serialization** - All managers now include:
  - `set_json(key, value, ttl=-1)` - Store dict/list as JSON
  - `get_json(key)` - Retrieve and deserialize JSON
  - `delete_key(key)` - Delete any key

- **Infrastructure** - New core modules:
  - `wredis/_types.py` - Type aliases
  - `wredis/_exceptions.py` - Custom exceptions
  - `wredis/_connection.py` - Connection factories

- **CI/CD** - GitHub Actions workflows:
  - `test.yml` - Lint (ruff), type check (mypy), test (pytest with 95% coverage)
  - `publish.yml` - Auto-publish to PyPI on release
  - `pages.yml` - Deploy marketing site to GitHub Pages

- **Docker Compose** - Environment setups:
  - `docker-compose.yml` - Single Redis instance
  - `docker-compose.cluster.yml` - 6-node cluster (3 masters + 3 replicas)
  - `docker-compose.sentinel.yml` - Sentinel setup (1 master + 2 replicas + 3 sentinels)

### Changed

- **Python Version** - Minimum Python version is now 3.10 (3.8/3.9 are EOL)
- **Build System** - Using hatchling only (removed setup.py)
- **Project Structure** - Cleaned up all `__init__.py` files with explicit re-exports
- **Code Quality** - Zero ruff linting errors, type hints added throughout

### Fixed

- Queue consumer example: Fixed duplicate function names (`worker` → `worker_4090`, `worker_queue_4060`, `worker_4060`)
- Directory naming: `sorted_set.py/` → `sorted_set/`
- All `__init__.py` files: Proper explicit re-exports instead of `from . import *`

### Removed

- `setup.py` - Replaced by hatchling in pyproject.toml
- `requirements.txt` - Dependencies now in pyproject.toml

---

## [0.1.2] - 2024-01-01

### Added

- Initial release with 7 modules:
  - RedisBitmapManager
  - RedisHashManager
  - RedisPubSubManager
  - RedisQueueManager
  - RedisSetManager
  - RedisSortedSetManager
  - RedisStreamManager
