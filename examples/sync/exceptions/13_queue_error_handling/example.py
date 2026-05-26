"""Queue exceptions (QueueError) demonstration.

Shows how to handle errors in queue operations like
push, pop, and peek using QueueError.
"""

from wredis._exceptions import QueueError


class RedisQueue:
    """Simulates a Redis-based queue with validations."""

    def __init__(self, name, max_size=5):
        self.name = name
        self.max_size = max_size
        self._elements = []

    def push(self, element):
        """Adds an element to the queue.

        Args:
            element: The element to add.

        Raises:
            QueueError: If queue is full or element is invalid.
        """
        if element is None:
            raise QueueError(f"Cannot add None to queue '{self.name}'")
        if len(self._elements) >= self.max_size:
            raise QueueError(
                f"Queue '{self.name}' is full ({self.max_size} elements max)"
            )
        self._elements.append(element)
        return len(self._elements)

    def pop(self):
        """Extracts the first element from the queue.

        Returns:
            The first element.

        Raises:
            QueueError: If queue is empty.
        """
        if not self._elements:
            raise QueueError(f"Cannot pop from empty queue '{self.name}'")
        return self._elements.pop(0)

    def peek(self):
        """Gets the first element without removing it.

        Returns:
            The first element.

        Raises:
            QueueError: If queue is empty.
        """
        if not self._elements:
            raise QueueError(f"Cannot peek empty queue '{self.name}'")
        return self._elements[0]

    @property
    def size(self):
        return len(self._elements)


# Case 1: Normal operations
print("=== Normal queue operations ===")
queue = RedisQueue("tasks", max_size=3)

queue.push("task_1")
queue.push("task_2")
print(f"Elements in queue: {queue.size}")
print(f"First element (peek): {queue.peek()}")

element = queue.pop()
print(f"Extracted element (pop): {element}")
print(f"Remaining elements: {queue.size}")

# Case 2: Queue full
print("\n=== Error: queue full ===")
queue.push("task_3")
queue.push("task_4")
try:
    queue.push("task_5")
except QueueError as exc:
    print(f"QueueError: {exc}")

# Case 3: Queue empty
print("\n=== Error: queue empty ===")
empty_queue = RedisQueue("empty")
try:
    empty_queue.pop()
except QueueError as exc:
    print(f"QueueError: {exc}")

try:
    empty_queue.peek()
except QueueError as exc:
    print(f"QueueError: {exc}")

# Case 4: Invalid element
print("\n=== Error: invalid element ===")
try:
    queue.push(None)
except QueueError as exc:
    print(f"QueueError: {exc}")

# Case 5: Safe queue processing
print("\n=== Safe processing with QueueError handling ===")


def process_queue(queue):
    """Processes all elements safely.

    Args:
        queue: RedisQueue instance.
    """
    processed = 0
    while True:
        try:
            element = queue.pop()
            print(f"  Processing: {element}")
            processed += 1
        except QueueError:
            break
    print(f"  Total processed: {processed}")


full_queue = RedisQueue("batches", max_size=10)
for i in range(4):
    full_queue.push(f"batch_{i}")

process_queue(full_queue)

# Case 6: Push with retry
print("\n=== Push with retry on QueueError ===")
limited_queue = RedisQueue("limited", max_size=2)
limited_queue.push("msg_1")
limited_queue.push("msg_2")

attempts = 0
max_attempts = 3

while attempts < max_attempts:
    attempts += 1
    try:
        limited_queue.push("msg_3")
        print(f"  Message sent on attempt {attempts}")
        break
    except QueueError as exc:
        # Consume a message to make space
        try:
            old = limited_queue.pop()
            print(f"  Old message discarded: {old}")
        except QueueError:
            print(f"  Attempt {attempts}: {exc}")
else:
    print("  Could not send message after all attempts")
