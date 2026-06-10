WRedis Documentation
================================================================================

.. image:: https://img.shields.io/badge/LTS-v1.0.0-orange.svg
   :target: https://pypi.org/project/wredis/
   :alt: LTS Version

**WRedis** is a production-ready Python library designed to simplify Redis operations. It provides a clean, unified API for both synchronous and asynchronous operations, built-in validation, retry logic, and advanced features like high availability (Sentinel/Cluster) and cache metrics.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started
   :hidden:

   getting_started/installation
   getting_started/quickstart

.. toctree::
   :maxdepth: 2
   :caption: API Reference
   :hidden:

   api/sync_api
   api/async_api
   api/exceptions

.. toctree::
   :maxdepth: 2
   :caption: Tutorials
   :hidden:

   tutorials/cache_usage
   tutorials/high_availability
   tutorials/advanced_patterns
   tutorials/examples_index

.. toctree::
   :maxdepth: 1
   :caption: Project Info
   :hidden:

   faq
   resources
   changelog

Key Features
--------------------------------------------------------------------------------

* **Unified API**: Consistent method names across different Redis data structures.
* **Full Async Support**: Native ``asyncio`` implementation for high-performance applications.
* **Type Safety**: Extensively type-hinted for better developer experience and IDE support.
* **Resilience**: Built-in retry mechanisms with exponential backoff.
* **Observability**: Detailed logging and cache performance metrics.
* **High Availability**: Out-of-the-box support for Redis Cluster and Sentinel.

Basic Usage
--------------------------------------------------------------------------------

.. code-block:: python

   from wredis.sync import RedisHashManager

   # Initialize manager
   manager = RedisHashManager(host="localhost")

   # Create a hash with TTL
   manager.create_hash("user:100", "profile", {"name": "Alice", "role": "admin"}, ttl=3600)

   # Check existence
   if manager.exist("user:100"):
       print("User exists!")

Indices and tables
================================================================================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
