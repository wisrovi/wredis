"""Example 15: Async retry integrated with FastAPI.

Demonstrates using async_retry in FastAPI endpoints to
create resilient APIs against Redis failures.
"""

import asyncio

import redis

from wredis._exceptions import OperationError
from wredis._retry import async_retry


# Simulating FastAPI without needing to install it
class FastAPIMock:
    """Minimalist FastAPI mock for demonstration."""

    def __init__(self) -> None:
        self.routes: dict[str, callable] = {}

    def get(self, path: str):
        """Decorator to register GET routes."""

        def decorator(func):
            self.routes[path] = func
            return func

        return decorator

    async def execute(self, path: str, **kwargs) -> dict:
        """Executes a route simulating an HTTP request."""
        # Find matching route (supports {param} type parameters)
        found_route = None
        for registered_route, func in self.routes.items():
            registered_parts = registered_route.split("/")
            path_parts = path.split("/")
            if len(registered_parts) == len(path_parts):
                matches = True
                params = {}
                for i, reg_part in enumerate(registered_parts):
                    if reg_part.startswith("{") and reg_part.endswith("}"):
                        # It's a parameter, extract name and value
                        param_name = reg_part[1:-1]
                        params[param_name] = path_parts[i]
                    elif reg_part != path_parts[i]:
                        matches = False
                        break
                if matches:
                    found_route = (func, params)
                    break

        if found_route is None:
            return {"error": "404 Not Found"}

        func, params = found_route
        try:
            result = await func(**params, **kwargs)
            return {"status": 200, "data": result}
        except OperationError as e:
            return {"status": 503, "error": str(e)}


app = FastAPIMock()


class MockRedisClient:
    """Mock Redis client for FastAPI."""

    def __init__(self) -> None:
        self._data = {"user:1": {"name": "Ana", "role": "admin"}}
        self._attempts = 0

    async def get_user(self, user_id: str) -> dict | None:
        self._attempts += 1
        if self._attempts <= 1:
            raise redis.ConnectionError("Redis disconnected")
        return self._data.get(f"user:{user_id}")

    async def save_metric(self, metric: str, value: float) -> bool:
        self._attempts += 1
        if self._attempts <= 2:
            raise redis.TimeoutError("Timeout saving metric")
        return True


redis_client = MockRedisClient()


@app.get("/users/{user_id}")
@async_retry(max_attempts=3, delay=0.1, backoff=2.0)
async def get_user(user_id: str) -> dict:
    """Endpoint to get user with automatic retry."""
    user = await redis_client.get_user(user_id)
    if user is None:
        return {"error": "User not found"}
    return user


@app.get("/metrics")
@async_retry(max_attempts=4, delay=0.05, backoff=1.5)
async def register_metric() -> bool:
    """Endpoint to register metric with retry."""
    return await redis_client.save_metric("requests", 1.0)


async def main() -> None:
    """Simulates HTTP requests to the API."""
    print("=== Example 15: Async Retry with FastAPI ===")

    # Request to get user
    print("\nGET /users/1")
    response = await app.execute("/users/1")
    print(f"  Status: {response['status']}")
    if "data" in response:
        print(f"  Data: {response['data']}")
    else:
        print(f"  Error: {response.get('error')}")

    # Request to register metric
    print("\nGET /metrics")
    metric_response = await app.execute("/metrics")
    print(f"  Status: {metric_response['status']}")
    print(f"  Data: {metric_response.get('data')}")

    print(f"\nTotal Redis attempts: {redis_client._attempts}")


if __name__ == "__main__":
    asyncio.run(main())
