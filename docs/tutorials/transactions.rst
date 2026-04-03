Transactions
============

Redis transactions provide atomic execution of multiple commands. WRedis simplifies transaction management with a clean API.

Basic Transactions
------------------

Execute multiple commands atomically:

.. code-block:: python

   from wredis.transaction import RedisTransactionManager

   manager = RedisTransactionManager()

   # Execute commands in a single transaction
   results = manager.execute_transaction([
       ("set", ["user:1001:name", "Alice"]),
       ("set", ["user:1001:email", "alice@example.com"]),
       ("set", ["user:1001:role", "admin"]),
       ("incr", ["user:count"]),
   ])

   print(f"Transaction results: {results}")

WATCH/MULTI/EXEC
----------------

Optimistic locking with WATCH ensures data consistency:

.. code-block:: python

   from wredis.transaction import RedisTransactionManager

   manager = RedisTransactionManager()

   # Watch a key and execute transaction
   # If the key is modified by another client, the transaction fails
   result = manager.watch_and_execute(
       keys=["account:balance"],
       commands=[
           ("get", ["account:balance"]),
           ("set", ["account:balance", "new_value"]),
       ],
   )

   if result is None:
       print("Transaction aborted - key was modified by another client")
   else:
       print(f"Transaction succeeded: {result}")

Atomic Operations
-----------------

SET NX (Set If Not Exists)
~~~~~~~~~~~~~~~~~~~~~~~~~~

Perfect for distributed locks:

.. code-block:: python

   from wredis.transaction import RedisTransactionManager

   manager = RedisTransactionManager()

   # Attempt to acquire a lock
   acquired = manager.set_if_not_exists("lock:resource", "locked", ttl=30)

   if acquired:
       try:
           # Critical section
           print("Lock acquired, performing operation...")
       finally:
           # Release lock
           manager.redis_client.delete("lock:resource")
   else:
       print("Lock already held by another process")

Atomic Counter
~~~~~~~~~~~~~~

.. code-block:: python

   from wredis.transaction import RedisTransactionManager

   manager = RedisTransactionManager()

   # Initialize counter
   manager.redis_client.set("page:views", "0")

   # Increment atomically
   new_value = manager.increment_atomic("page:views", 1)
   print(f"Page views: {new_value}")

   # Decrement
   new_value = manager.increment_atomic("page:views", -1)
   print(f"Page views after decrement: {new_value}")

   # Increment by arbitrary amount
   new_value = manager.increment_atomic("page:views", 10)
   print(f"Page views after +10: {new_value}")

Atomic Get-And-Set
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from wredis.transaction import RedisTransactionManager

   manager = RedisTransactionManager()

   # Set initial value
   manager.redis_client.set("config:version", "1.0")

   # Atomically get old value and set new value
   old_version = manager.get_and_set("config:version", "2.0")
   print(f"Upgraded from {old_version} to 2.0")

Banking Example
---------------

Demonstrating atomic money transfer:

.. code-block:: python

   from wredis.transaction import RedisTransactionManager

   manager = RedisTransactionManager()

   # Initialize accounts
   manager.execute_transaction([
       ("set", ["account:A", "1000"]),
       ("set", ["account:B", "500"]),
   ])

   def transfer_money(from_account: str, to_account: str, amount: int) -> bool:
       """Transfer money between accounts atomically."""
       results = manager.execute_transaction([
           ("get", [from_account]),
           ("get", [to_account]),
       ])

       from_balance = int(results[0])
       to_balance = int(results[1])

       if from_balance < amount:
           return False

       # Execute transfer
       transfer_results = manager.execute_transaction([
           ("decrby", [from_account, amount]),
           ("incrby", [to_account, amount]),
       ])

       return True

   # Transfer $100 from A to B
   success = transfer_money("account:A", "account:B", 100)
   print(f"Transfer {'succeeded' if success else 'failed'}")

Distributed Lock Pattern
------------------------

.. code-block:: python

   import time
   from wredis.transaction import RedisTransactionManager

   class DistributedLock:
       def __init__(self, resource: str, ttl: int = 30):
           self.manager = RedisTransactionManager()
           self.resource = resource
           self.ttl = ttl
           self.lock_key = f"lock:{resource}"

       def acquire(self) -> bool:
           """Attempt to acquire the lock."""
           return self.manager.set_if_not_exists(
               self.lock_key, "locked", ttl=self.ttl
           )

       def release(self) -> None:
           """Release the lock."""
           self.manager.redis_client.delete(self.lock_key)

       def __enter__(self):
           if not self.acquire():
               raise RuntimeError(f"Could not acquire lock: {self.resource}")
           return self

       def __exit__(self, exc_type, exc_val, exc_tb):
           self.release()

   # Usage
   with DistributedLock("database_migration"):
       print("Performing database migration...")
       time.sleep(1)
       print("Migration complete")

Best Practices
--------------

1. **Keep transactions short** - Minimize the time keys are locked
2. **Handle WATCH failures** - Implement retry logic for optimistic locking
3. **Use SET NX for locks** - Always set a TTL to prevent deadlocks
4. **Monitor transaction failures** - Track WATCH failures for contention issues
5. **Avoid nested transactions** - Redis does not support nested transactions
6. **Test under load** - Validate transaction behavior under concurrent access
