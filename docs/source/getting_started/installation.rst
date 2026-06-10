Installation
================================================================================

WRedis requires Python 3.10 or higher and a Redis server (v6.0+ recommended).

Standard Installation
--------------------------------------------------------------------------------

You can install WRedis directly from PyPI using ``pip``:

.. code-block:: bash

   pip install wredis

Development Version
--------------------------------------------------------------------------------

To install the latest development version from the repository:

.. code-block:: bash

   git clone https://github.com/wisrovi/wredis.git
   cd wredis
   pip install -e .

Redis Compatibility
--------------------------------------------------------------------------------

WRedis is compatible with:
* Single node Redis
* Redis Cluster
* Redis Sentinel
* Managed Redis services (AWS ElastiCache, Azure Cache for Redis, GCP Memorystore)
