High Availability
=================

WRedis provides built-in support for Redis Sentinel and Redis Cluster, enabling automatic failover and horizontal scaling for production deployments.

Sentinel Setup
--------------

Redis Sentinel provides automatic failover when the master node becomes unavailable.

Configuration
~~~~~~~~~~~~~

.. code-block:: python

   from wredis.ha import SentinelRedisManager

   # Connect to Sentinel
   sentinel = SentinelRedisManager(
       sentinel_nodes=[
           ("sentinel-1.example.com", 26379),
           ("sentinel-2.example.com", 26379),
           ("sentinel-3.example.com", 26379),
       ],
       service_name="mymaster",
       socket_timeout=5.0,
   )

   # Get master for write operations
   master = sentinel.get_master()
   master.set("key", "value")

   # Get slave for read operations
   slave = sentinel.get_slave()
   if slave:
       value = slave.get("key")

Discovery
~~~~~~~~~

.. code-block:: python

   # Discover current master
   host, port = sentinel.discover_master()
   print(f"Master: {host}:{port}")

   # Discover all slaves
   slaves = sentinel.discover_slaves()
   for host, port in slaves:
       print(f"Slave: {host}:{port}")

   # Check if a node is master
   is_master = sentinel.is_master("192.168.1.100", 6379)

Cluster Setup
-------------

Redis Cluster provides horizontal scaling through data sharding across multiple nodes.

Configuration
~~~~~~~~~~~~~

.. code-block:: python

   from wredis.ha import ClusterRedisManager

   # Connect to Cluster
   cluster = ClusterRedisManager(
       startup_nodes=[
           ("cluster-1.example.com", 7000),
           ("cluster-2.example.com", 7001),
           ("cluster-3.example.com", 7002),
       ],
       password="your-cluster-password",
       ssl=True,
       socket_timeout=5.0,
   )

   # Use the cluster client
   client = cluster.redis_client
   client.set("key", "value")

Cluster Monitoring
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Get cluster information
   info = cluster.get_cluster_info()
   print(f"Cluster state: {info.get('cluster_state')}")

   # Get all nodes
   nodes = cluster.get_nodes()
   for node in nodes:
       print(f"Node: {node['host']}:{node['port']} - {node['flags']}")

   # Get slot assignments
   slots = cluster.get_slots()

   # Check cluster health
   state = cluster.get_cluster_state()
   if state == "ok":
       print("Cluster is healthy")

   # Wait for replicas to be ready
   ready = cluster.wait_for_replicas(timeout=10.0)
   if ready:
       print("All replicas are ready")

Read/Write Splitting
--------------------

For optimal performance, split read and write operations:

.. code-block:: python

   from wredis.ha import SentinelRedisManager

   sentinel = SentinelRedisManager(
       sentinel_nodes=[("sentinel.example.com", 26379)],
       service_name="mymaster",
   )

   # Write to master
   master = sentinel.get_master()
   master.set("user:1:profile", '{"name": "Alice"}')

   # Read from slave
   slave = sentinel.get_slave()
   if slave:
       profile = slave.get("user:1:profile")
   else:
       # Fallback to master if no slaves available
       profile = master.get("user:1:profile")

Best Practices
--------------

1. **Deploy at least 3 Sentinel nodes** - Ensures quorum for failover decisions
2. **Monitor cluster state regularly** - Use ``get_cluster_state()`` in health checks
3. **Configure appropriate timeouts** - Balance between responsiveness and false positives
4. **Use SSL for cluster connections** - Encrypt inter-node communication
5. **Test failover scenarios** - Regularly validate automatic failover works correctly
6. **Plan capacity** - Monitor memory usage across all cluster nodes
