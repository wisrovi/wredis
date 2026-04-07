"""Simple Pub/Sub Subscriber Example"""

import signal

from wredis import subscribe


def my_handler(message):
    print(f"Received: {message}")


if __name__ == "__main__":
    manager = subscribe("my_channel", my_handler)
    print("Listening... Press Ctrl+C to exit")
    manager.wait()
