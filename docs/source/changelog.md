# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-06-10

### LTS Release

This is the first Long-Term Support (LTS) release of WRedis, supported for 3+ years.

### Added

- **Unified existence check**: Added `exist()` method to ALL Redis managers (sync and async) for consistent API across Bitmap, Hash, Set, SortedSet, Geo, HyperLogLog, Queue, Pub/Sub, and Streams.
- **Clean Import API**: New consistent module structure:
  - `from wredis.sync import ...` - for all sync operations
  - `from wredis.aio import ...` - for all async operations
  - `from wredis import cache` - for cache decorator
- **Examples Reorganization**: All 164 examples restructured to a consistent format:
  - Each example now has its own folder (e.g., `examples/sync/base/01_basic_init/`)
  - Each folder contains `example.py` and `README.md`
  - READMEs include Mermaid diagrams, descriptions, and run instructions
  - Tests can now run all examples: `pytest examples/test/test_all_examples.py`
- **Foundation Modules**:
  - `BaseManager` / `AsyncBaseManager` — Connection pooling, health checks, context managers, retry logic
  - `_serializer` — Centralized JSON serialization with proper error handling
  - `_validation` — Input validation for keys, TTL, offsets, scores, bit values
  - `_retry` — Retry decorators with exponential backoff (`@retry`, `@async_retry`)
- **Exception Hierarchy**: `ValidationError`, `OperationError`, `TransactionError`, `QueueError`, `StreamError`, `PubSubError`.
- **New Data Structures**: Geo, HyperLogLog, Pipeline, Transaction managers.
- **High Availability**: Sentinel and Cluster support.

### Breaking Changes

- **Error Handling**: Operations now raise specific exceptions instead of silently logging errors and returning defaults.
- **Async API Rewritten**: All async managers now use real `asyncio` tasks instead of threads.
- **Python 3.10+ Required**: Dropped support for Python 3.8 and 3.9.

### Changed

- Removed `fakeredis` from all examples (now use real Redis).
- Examples README files updated to English with Mermaid diagrams.
- Simplified async examples - no manual redis client creation needed.

### Fixed

- Example tests now properly skip long-running processes (pubsub subscribers, queue consumers).
- AsyncBaseManager now creates connections correctly without manual injection.
- Fixed `AttributeError` in Hash examples by implementing missing `exist()` method.

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
