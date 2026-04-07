"""TransactionError handling demonstration.

Shows how to handle transaction errors, such as WATCH
conflicts, and how to implement optimistic retries.
"""

from wredis._exceptions import TransactionError


class RedisTransaction:
    """Simulates Redis transactions with conflict possibility."""

    def __init__(self):
        self._data = {"counter": 100}
        self._version = 1
        self._force_conflict = True

    def execute_transaction(self, operation):
        """Executes a simulated transaction with version control.

        Args:
            operation: Function that receives data and returns new data.

        Raises:
            TransactionError: If there is a version conflict (simulates WATCH).
        """
        read_version = self._version

        # Simulate another process modifying the data
        if self._force_conflict:
            self._version += 1
            self._force_conflict = False

        # Check if version changed (WATCH conflict)
        if read_version != self._version:
            raise TransactionError(
                f"Transaction conflict: key was modified (expected version: {read_version}, current: {self._version})"
            )

        new_data = operation(self._data.copy())
        self._data.update(new_data)
        return self._data


def transaction_with_retry(client, operation, max_attempts=5):
    """Executes a transaction with optimistic retries.

    Args:
        client: RedisTransaction instance.
        operation: Function with transaction logic.
        max_attempts: Maximum number of retries.

    Returns:
        Transaction result.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            result = client.execute_transaction(operation)
            print(f"  Transaction successful on attempt {attempt}")
            return result
        except TransactionError as exc:
            print(f"  Attempt {attempt}: {exc}")
            if attempt == max_attempts:
                raise
    return None


# Case 1: Transaction with conflict that resolves
print("=== Transaction with optimistic conflict ===")

client = RedisTransaction()


def increment_counter(data):
    data["counter"] += 1
    return data


result = transaction_with_retry(client, increment_counter)
print(f"Final state: {result}")

# Case 2: Multiple sequential transactions
print("\n=== Multiple sequential transactions ===")

client2 = RedisTransaction()
client2._force_conflict = False  # No conflicts

for i in range(3):
    try:

        def add_ten(data):
            data["counter"] += 10
            return data

        result = client2.execute_transaction(add_ten)
        print(f"  Transaction {i + 1}: counter = {result['counter']}")
    except TransactionError as exc:
        print(f"  Transaction {i + 1} failed: {exc}")

# Case 3: Simulated rollback on error
print("\n=== Rollback on TransactionError ===")

client3 = RedisTransaction()
original_state = client3._data.copy()

try:

    def complex_operation(data):
        data["counter"] -= 50
        data["temporary"] = True
        return data

    client3.execute_transaction(complex_operation)
except TransactionError as exc:
    print(f"  Transaction failed, rolling back: {exc}")
    client3._data = original_state
    print(f"  State restored: {client3._data}")
