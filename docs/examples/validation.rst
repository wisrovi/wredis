Validation Examples
===================

Examples demonstrating input validation for Redis operations.

.. code-block:: python

   from wredis import WRedis

   client = WRedis()
   # Validation is automatic on all operations
   client.set("my_key", "value", ttl=3600)

Examples
--------

.. list-table::
   :header-rows: 1

   * - Example
     - Description
   * - `01 TTL Validation <https://github.com/wisrovi/wredis/tree/main/examples/sync/validation/01_ttl_validation.py>`_
     - Validating TTL values for cache entries
   * - `02 Invalid TTL <https://github.com/wisrovi/wredis/tree/main/examples/sync/validation/02_invalid_ttl.py>`_
     - Handling invalid TTL configurations
   * - `03 Key Validation <https://github.com/wisrovi/wredis/tree/main/examples/sync/validation/03_key_validation.py>`_
     - Validating Redis key formats
   * - `04 Invalid Key <https://github.com/wisrovi/wredis/tree/main/examples/sync/validation/04_invalid_key.py>`_
     - Handling invalid key patterns
   * - `05 Offset Validation <https://github.com/wisrovi/wredis/tree/main/examples/sync/validation/05_offset_validation.py>`_
     - Validating bit offset values
   * - `06 Bit Value Validation <https://github.com/wisrovi/wredis/tree/main/examples/sync/validation/06_bit_value_validation.py>`_
     - Validating bit values for bitmap operations
   * - `07 Score Validation <https://github.com/wisrovi/wredis/tree/main/examples/sync/validation/07_score_validation.py>`_
     - Validating sorted set scores
   * - `08 Batch Validation <https://github.com/wisrovi/wredis/tree/main/examples/sync/validation/08_batch_validation.py>`_
     - Validating batch operation inputs
   * - `09 Edge Cases <https://github.com/wisrovi/wredis/tree/main/examples/sync/validation/09_edge_cases.py>`_
     - Testing edge cases in validation
   * - `10 Key Patterns <https://github.com/wisrovi/wredis/tree/main/examples/sync/validation/10_key_patterns.py>`_
     - Working with key pattern validation
   * - `11 Score Types <https://github.com/wisrovi/wredis/tree/main/examples/sync/validation/11_score_types.py>`_
     - Handling different score types in sorted sets
   * - `12 Validation Decorator <https://github.com/wisrovi/wredis/tree/main/examples/sync/validation/12_validation_decorator.py>`_
     - Using validation decorators
   * - `13 Config Manager <https://github.com/wisrovi/wredis/tree/main/examples/sync/validation/13_config_manager.py>`_
     - Configuration-based validation
   * - `14 Bitmap Operations <https://github.com/wisrovi/wredis/tree/main/examples/sync/validation/14_bitmap_operations.py>`_
     - Validating bitmap operation parameters
   * - `15 Sorted Set Scores <https://github.com/wisrovi/wredis/tree/main/examples/sync/validation/15_sorted_set_scores.py>`_
     - Advanced sorted set score validation

See `all examples on GitHub <https://github.com/wisrovi/wredis/tree/main/examples/sync/validation>`_.
