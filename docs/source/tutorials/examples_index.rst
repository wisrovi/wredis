Examples Index
================================================================================

WRedis includes over 100 functional examples covering every module. You can find them in the ``examples/`` directory of the source code.

Browse by Category
--------------------------------------------------------------------------------

Synchronous Examples
^^^^^^^^^^^^^^^^----------------------------------------------------------------

* **Basic**: Initialization and health checks.
* **Hash**: Working with Redis Hashes.
* **Queue**: Producer-Consumer patterns.
* **Pub/Sub**: Real-time messaging.
* **Sets & Sorted Sets**: Collection management.
* **Geo**: Location-based operations.
* **HyperLogLog**: Cardinality estimation.
* **Pipeline & Transaction**: Batch and atomic operations.

Asynchronous Examples
^^^^^^^^^^^^^^^^----------------------------------------------------------------

Every synchronous manager has a corresponding asynchronous version in the ``examples/async/`` directory.

Running Examples
--------------------------------------------------------------------------------

To run an example, navigate to its directory and execute it with Python:

.. code-block:: bash

   cd examples/sync/hash/01_read
   python3 example.py
