Serializer Examples
===================

The serializer module provides centralized JSON serialization with proper error handling.

.. code-block:: python

   from wredis._serializer import serialize, deserialize
   from wredis._exceptions import SerializationError

   # Serialize
   data = serialize({"user": "Alice", "role": "admin"})
   print(data)  # '{"user": "Alice", "role": "admin"}'

   # Deserialize
   original = deserialize(data)
   print(original)  # {'user': 'Alice', 'role': 'admin'}

Examples
--------

.. list-table::
   :header-rows: 1

   * - Example
     - Description
   * - `01 Basic Serialize <https://github.com/wisrovi/wredis/tree/main/examples/sync/serializer/01_basic_serialize.py>`_
     - Basic serialization of common types
   * - `02 Basic Deserialize <https://github.com/wisrovi/wredis/tree/main/examples/sync/serializer/02_basic_deserialize.py>`_
     - Basic deserialization patterns
   * - `03 Nested Dicts <https://github.com/wisrovi/wredis/tree/main/examples/sync/serializer/03_nested_dicts.py>`_
     - Serializing nested dictionaries
   * - `04 Lists <https://github.com/wisrovi/wredis/tree/main/examples/sync/serializer/04_lists.py>`_
     - Working with lists and arrays
   * - `05 Unicode <https://github.com/wisrovi/wredis/tree/main/examples/sync/serializer/05_unicode.py>`_
     - Unicode character handling
   * - `06 None Values <https://github.com/wisrovi/wredis/tree/main/examples/sync/serializer/06_none_values.py>`_
     - Handling None/null values
   * - `07 Booleans <https://github.com/wisrovi/wredis/tree/main/examples/sync/serializer/07_booleans.py>`_
     - Boolean serialization
   * - `08 Numbers <https://github.com/wisrovi/wredis/tree/main/examples/sync/serializer/08_numbers.py>`_
     - Integer and float handling
   * - `09 Datetime <https://github.com/wisrovi/wredis/tree/main/examples/sync/serializer/09_datetime.py>`_
     - Date/time serialization with default=str
   * - `10 Custom Objects <https://github.com/wisrovi/wredis/tree/main/examples/sync/serializer/10_custom_objects.py>`_
     - Serializing custom class instances
   * - `11 Large Data <https://github.com/wisrovi/wredis/tree/main/examples/sync/serializer/11_large_data.py>`_
     - Handling large payloads
   * - `12 Round Trip <https://github.com/wisrovi/wredis/tree/main/examples/sync/serializer/12_round_trip.py>`_
     - Serialize-deserialize round-trip verification
   * - `13 Error Handling <https://github.com/wisrovi/wredis/tree/main/examples/sync/serializer/13_error_handling.py>`_
     - SerializationError handling
   * - `14 Integration <https://github.com/wisrovi/wredis/tree/main/examples/sync/serializer/14_integration.py>`_
     - Integration with Redis managers
   * - `15 Performance <https://github.com/wisrovi/wredis/tree/main/examples/sync/serializer/15_performance.py>`_
     - Performance benchmarks

See `all examples on GitHub <https://github.com/wisrovi/wredis/tree/main/examples/sync/serializer>`_.
