"""Example 07: Retry on external API calls.

Demonstrates using @retry for HTTP API calls that may
fail due to timeouts or connection errors.
"""

import redis

from wredis._exceptions import OperationError
from wredis._retry import retry


class APIMock:
    """Mock API client for demonstration."""

    def __init__(self) -> None:
        self._attempts = 0
        self._data = {"temperature": 25.5, "humidity": 60}

    def get_weather_data(self, city: str) -> dict:
        """Simulates weather API call with intermittent failures."""
        self._attempts += 1
        if self._attempts <= 2:
            raise redis.TimeoutError("Timeout connecting to external API")
        return {"city": city, **self._data}

    def send_notification(self, message: str) -> bool:
        """Simulates notification sending with failures."""
        self._attempts += 1
        if self._attempts <= 3:
            raise redis.ConnectionError("Connection error with notification service")
        return True


api = APIMock()


@retry(max_attempts=3, delay=0.1, backoff=2.0)
def query_weather(city: str) -> dict:
    """Queries weather data with automatic retry."""
    return api.get_weather_data(city)


@retry(max_attempts=5, delay=0.05, backoff=1.5)
def send_alert(message: str) -> bool:
    """Sends alert with more attempts for greater resilience."""
    return api.send_notification(message)


if __name__ == "__main__":
    print("=== Example 07: External API Calls ===")

    # Weather query with retries
    weather = query_weather("Buenos Aires")
    print(
        f"Weather in {weather['city']}: {weather['temperature']}C, {weather['humidity']}% humidity"
    )

    # Send notification
    sent = send_alert("System alert")
    print(f"Notification sent: {sent}")
    print(f"Total API attempts: {api._attempts}")
