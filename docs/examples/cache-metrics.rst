Cache Metrics Examples
======================

Examples demonstrating cache metrics collection, monitoring, and analysis.

.. code-block:: python

   from wredis import WRedis

   client = WRedis(enable_metrics=True)
   client.set("key", "value")
   metrics = client.get_metrics()
   print(metrics.hit_rate)

Examples
--------

.. list-table::
   :header-rows: 1

   * - Example
     - Description
   * - `01 Basic Metrics <https://github.com/wisrovi/wredis/tree/main/examples/sync/cache_metrics/01_basic_metrics.py>`_
     - Basic metrics collection
   * - `02 Hit Rate Monitoring <https://github.com/wisrovi/wredis/tree/main/examples/sync/cache_metrics/02_hit_rate_monitoring.py>`_
     - Monitoring cache hit rates
   * - `03 Multiple Cache Zones <https://github.com/wisrovi/wredis/tree/main/examples/sync/cache_metrics/03_multiple_cache_zones.py>`_
     - Metrics across multiple cache zones
   * - `04 TTL Impact <https://github.com/wisrovi/wredis/tree/main/examples/sync/cache_metrics/04_ttl_impact.py>`_
     - Analyzing TTL impact on hit rates
   * - `05 Cache Warming <https://github.com/wisrovi/wredis/tree/main/examples/sync/cache_metrics/05_cache_warming.py>`_
     - Metrics during cache warming
   * - `06 Invalidation Impact <https://github.com/wisrovi/wredis/tree/main/examples/sync/cache_metrics/06_invalidation_impact.py>`_
     - Measuring invalidation impact
   * - `07 Dashboard Pattern <https://github.com/wisrovi/wredis/tree/main/examples/sync/cache_metrics/07_dashboard_pattern.py>`_
     - Building a metrics dashboard
   * - `08 Alerting Low Hit Rate <https://github.com/wisrovi/wredis/tree/main/examples/sync/cache_metrics/08_alerting_low_hitrate.py>`_
     - Alerting on low hit rates
   * - `09 Manual Recording <https://github.com/wisrovi/wredis/tree/main/examples/sync/cache_metrics/09_manual_recording.py>`_
     - Manual metrics recording
   * - `10 Async Cache Metrics <https://github.com/wisrovi/wredis/tree/main/examples/sync/cache_metrics/10_async_cache_metrics.py>`_
     - Async metrics collection
   * - `11 Performance Comparison <https://github.com/wisrovi/wredis/tree/main/examples/sync/cache_metrics/11_performance_comparison.py>`_
     - Comparing cache performance
   * - `12 Custom Key Builder <https://github.com/wisrovi/wredis/tree/main/examples/sync/cache_metrics/12_custom_key_builder.py>`_
     - Custom key building for metrics
   * - `13 Error Handling Metrics <https://github.com/wisrovi/wredis/tree/main/examples/sync/cache_metrics/13_error_handling_metrics.py>`_
     - Tracking errors in metrics
   * - `14 Invalidation Decorator <https://github.com/wisrovi/wredis/tree/main/examples/sync/cache_metrics/14_invalidation_decorator.py>`_
     - Decorator-based invalidation metrics
   * - `15 Cache Warming <https://github.com/wisrovi/wredis/tree/main/examples/sync/cache_metrics/15_cache_warming.py>`_
     - Advanced cache warming strategies

See `all examples on GitHub <https://github.com/wisrovi/wredis/tree/main/examples/sync/cache_metrics>`_.
