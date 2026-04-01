"""Simple Pub/Sub Publisher Example"""

from wredis import publish

if __name__ == "__main__":
    publish("my_channel", {"message": "Hello from WRedis!"})
    publish("my_channel", "Simple string message")
    print("Messages published")
