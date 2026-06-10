High Availability
================================================================================

WRedis provides built-in support for Redis Sentinel and Redis Cluster, ensuring your application remains resilient to failures.

Redis Sentinel
--------------------------------------------------------------------------------

Sentinel is used for automatic failover in a master-replica setup.

.. code-block:: python

   from wredis.ha.sentinel import RedisSentinelManager

   sentinels = [("localhost", 26379), ("localhost", 26380)]
   manager = RedisSentinelManager(sentinels=sentinels, service_name="mymaster")

   # The manager automatically discovers the current master
   manager.set("key", "value")

Redis Cluster
--------------------------------------------------------------------------------

Cluster provides horizontal scaling through data partitioning.

.. code-block:: python

   from wredis.ha.cluster import RedisClusterManager

   startup_nodes = [{"host": "127.0.0.1", "port": "7000"}]
   manager = RedisClusterManager(startup_nodes=startup_nodes)

   manager.set("clustered_key", "data")
