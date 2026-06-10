Exceptions
================================================================================

WRedis uses a custom exception hierarchy to provide granular error handling.

Hierarchy
--------------------------------------------------------------------------------

.. code-block:: text

   WRedisError (Base)
   ├── ValidationError
   ├── OperationError
   ├── TransactionError
   ├── QueueError
   ├── StreamError
   └── PubSubError

Detailed Reference
--------------------------------------------------------------------------------

.. automodule:: wredis._exceptions
   :members:
   :undoc-members:
   :show-inheritance:
