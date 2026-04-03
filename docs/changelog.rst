Changelog
=========

v1.0.0 (2026-04-01)
-------------------

**LTS Release**

New Features
~~~~~~~~~~~~

- Full async/await support for all managers
- Cache decorators (``@cache``, ``@async_cache``, ``@invalidate_cache``)
- High Availability support (Sentinel and Cluster)
- New modules: Geo, HyperLogLog, Pipeline, Transaction
- Custom exceptions hierarchy
- Type aliases for improved type hints
- Connection factory functions

Improvements
~~~~~~~~~~~~

- Comprehensive test coverage (95%+)
- Full type hints across all modules
- Improved error handling
- Better logging with loguru

v0.1.2 (Previous)
-----------------

Initial release with core managers:

- Bitmap Manager
- Hash Manager
- Pub/Sub Manager
- Queue Manager
- Set Manager
- Sorted Set Manager
- Stream Manager
