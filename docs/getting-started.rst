Getting Started
===============

Overview
--------

WRedis is a production-ready Python library that provides a clean, intuitive interface for interacting with Redis. It offers both synchronous and asynchronous APIs, cache decorators, high-availability support through Sentinel and Cluster, and comprehensive type hints.

Key Features
~~~~~~~~~~~~

- **Synchronous & Asynchronous APIs** - Full support for both traditional and async/await patterns
- **Cache Decorators** - Drop-in ``@cache`` and ``@async_cache`` decorators for function result caching
- **High Availability** - Built-in Sentinel and Cluster support for production deployments
- **Comprehensive Data Structures** - Bitmap, Hash, Set, Sorted Set, Stream, Queue, Pub/Sub, Geo, HyperLogLog, Pipeline, and Transaction managers
- **Type Safety** - Full type hints for IDE autocomplete and static analysis
- **Zero Breaking Changes** - LTS v1.0.0 designed for long-term stability

Installation
------------

Install WRedis using pip:

.. code-block:: bash

   pip install wredis

Or install with development dependencies:

.. code-block:: bash

   pip install wredis[dev]

Requirements
~~~~~~~~~~~~

- Python 3.10 or higher
- Redis server (local or remote)
- ``redis`` Python package (automatically installed)
- ``loguru`` for logging (automatically installed)

Quick Start
-----------

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from wredis.hash import RedisHashManager

   # Initialize the manager
   manager = RedisHashManager(host="localhost", port=6379, db=0)

   # Store data
   manager.create_hash("user:1001", "profile", {"name": "Alice", "role": "admin"})

   # Retrieve data
   profile = manager.read_hash("user:1001", "profile")
   print(profile)  # {'name': 'Alice', 'role': 'admin'}

Async Usage
~~~~~~~~~~~

.. code-block:: python

   import asyncio
   from wredis.async_api.hash import AsyncRedisHashManager

   async def main():
       manager = AsyncRedisHashManager(host="localhost", port=6379, db=0)

       await manager.create_hash("user:1002", "profile", {"name": "Bob", "role": "user"})
       profile = await manager.read_hash("user:1002", "profile")
       print(profile)

   asyncio.run(main())

Cache Decorator
~~~~~~~~~~~~~~~

.. code-block:: python

   from wredis.decorators import cache

   @cache(ttl=300, prefix="api:users")
   def get_user(user_id: int) -> dict:
       # Expensive database query
       return {"id": user_id, "name": "Alice"}

   # First call executes the function
   user = get_user(1001)

   # Subsequent calls return cached result for 5 minutes

Project Structure
-----------------

.. code-block:: text

   wredis/
   ├── bitmap/          # Bitmap operations
   ├── geo/             # Geographic queries
   ├── hash/            # Hash data structure
   ├── hyperloglog/     # Probabilistic counting
   ├── pipeline/        # Batch command execution
   ├── pubsub/          # Publish/Subscribe
   ├── queue/           # Message queue
   ├── sets/            # Set operations
   ├── sortedset/       # Sorted set operations
   ├── streams/         # Stream processing
   ├── transaction/     # Atomic operations
   ├── ha/              # High Availability (Sentinel/Cluster)
   ├── async_api/       # Async versions of all managers
   ├── decorators.py    # Cache decorators
   ├── _connection.py   # Connection factories
   ├── _exceptions.py   # Custom exceptions
   └── _types.py        # Type aliases

Next Steps
----------

- Read the :doc:`tutorials/index` for detailed usage examples
- Explore the :doc:`api/index` for complete API reference
- Check the :doc:`faq` for common questions and troubleshooting
