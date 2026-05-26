"""Cache Decorator Example - Basic"""

import time

from wredis.decorators import cache


@cache(ttl=60, prefix="myapp")
def expensive_operation(x, y):
    """This function only runs if result is not cached."""
    time.sleep(2)  # Simulate expensive computation
    return x + y


if __name__ == "__main__":
    # First call - will be slow (2 seconds)
    start = time.time()
    result1 = expensive_operation(10, 20)
    print(f"First call: {result1} (took {time.time() - start:.2f}s)")

    # Second call - will be fast (from cache)
    start = time.time()
    result2 = expensive_operation(10, 20)
    print(f"Second call: {result2} (took {time.time() - start:.2f}s)")
