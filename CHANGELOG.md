# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-03-31

### Added

- **AsyncRedis Support** - New `wredis.async_api` module with async versions of all 7 managers:
  - `AsyncRedisBitmapManager`
  - `AsyncRedisHashManager`
  - `AsyncRedisPubSubManager`
  - `AsyncRedisQueueManager`
  - `AsyncRedisSetManager`
  - `AsyncRedisSortedSetManager`
  - `AsyncRedisStreamManager`

- **Cache Decorators** - New `wredis.decorators` module with:
  - `@cache(ttl=300, prefix="wredis:cache")` - Cache-Aside pattern decorator
  - `@async_cache(ttl=300, prefix="wredis:cache")` - Async version for FastAPI/AI agents
  - `@invalidate_cache(pattern)` - Cache invalidation decorator
  - `clear_cache(pattern)` - Utility function for cache clearing

- **High Availability** - New `wredis.ha` module with:
  - `SentinelRedisManager` - Sentinel-based failover management
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
