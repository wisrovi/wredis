"""Stream (StreamError) and Pub/Sub (PubSubError) exceptions demonstration.

Shows how to handle errors in Redis Streams and Pub/Sub
operations using the corresponding exceptions.
"""

from wredis._exceptions import PubSubError, StreamError


class RedisStream:
    """Simulates Redis Streams operations."""

    def __init__(self, stream_name):
        self.name = stream_name
        self._entries = []
        self._corrupted = False

    def add(self, data):
        """Adds an entry to the stream.

        Args:
            data: Dictionary with entry data.

        Returns:
            str: Entry ID.

        Raises:
            StreamError: If data is invalid or stream is corrupted.
        """
        if self._corrupted:
            raise StreamError(f"Stream '{self.name}' is corrupted")
        if not data:
            raise StreamError("Stream data cannot be empty")
        if not isinstance(data, dict):
            raise StreamError(f"Stream data must be a dict, not {type(data).__name__}")
        entry_id = f"{len(self._entries)}-0"
        self._entries.append((entry_id, data))
        return entry_id

    def read(self, from_id="0", count=10):
        """Reads entries from the stream.

        Args:
            from_id: ID to read from.
            count: Maximum number of entries.

        Returns:
            List of tuples (id, data).

        Raises:
            StreamError: If stream is corrupted.
        """
        if self._corrupted:
            raise StreamError(f"Cannot read from corrupted stream '{self.name}'")
        start = int(from_id.split("-")[0]) if from_id != "0" else 0
        return self._entries[start : start + count]

    def mark_corrupted(self):
        self._corrupted = True


class RedisPubSub:
    """Simulates Redis Pub/Sub operations."""

    def __init__(self):
        self._subscriptions = {}
        self._connected = True

    def subscribe(self, channel, callback):
        """Subscribes a callback to a channel.

        Args:
            channel: Channel name.
            callback: Function to call when message arrives.

        Raises:
            PubSubError: If not connected or channel is invalid.
        """
        if not self._connected:
            raise PubSubError("Cannot subscribe: connection closed")
        if not channel or not isinstance(channel, str):
            raise PubSubError(f"Invalid channel name: '{channel}'")
        self._subscriptions[channel] = callback
        print(f"  Subscribed to channel: {channel}")

    def publish(self, channel, message):
        """Publishes a message to a channel.

        Args:
            channel: Channel name.
            message: Message to publish.

        Raises:
            PubSubError: If channel has no subscribers or not connected.
        """
        if not self._connected:
            raise PubSubError("Cannot publish: connection closed")
        if channel not in self._subscriptions:
            raise PubSubError(f"Channel '{channel}' has no subscribers")
        self._subscriptions[channel](message)

    def disconnect(self):
        self._connected = False
        self._subscriptions.clear()


# === StreamError ===
print("=== StreamError: normal operations ===")
stream = RedisStream("user:events")

id1 = stream.add({"action": "login", "user": "ana"})
id2 = stream.add({"action": "purchase", "user": "ana", "amount": 50})
print(f"Entries added: {id1}, {id2}")

entries = stream.read()
for entry_id, data in entries:
    print(f"  [{entry_id}] {data}")

print("\n=== StreamError: corrupted stream ===")
stream.mark_corrupted()
try:
    stream.add({"action": "logout"})
except StreamError as exc:
    print(f"StreamError on add: {exc}")

try:
    stream.read()
except StreamError as exc:
    print(f"StreamError on read: {exc}")

print("\n=== StreamError: invalid data ===")
valid_stream = RedisStream("logs")
try:
    valid_stream.add({})
except StreamError as exc:
    print(f"StreamError: {exc}")

try:
    valid_stream.add("not a dict")
except StreamError as exc:
    print(f"StreamError: {exc}")

# === PubSubError ===
print("\n=== PubSubError: normal operations ===")
pubsub = RedisPubSub()


def process_message(msg):
    print(f"  [notifications] Message received: {msg}")


pubsub.subscribe("notifications", process_message)
pubsub.publish("notifications", "New order!")

print("\n=== PubSubError: channel without subscribers ===")
try:
    pubsub.publish("alerts", "Something happened")
except PubSubError as exc:
    print(f"PubSubError: {exc}")

print("\n=== PubSubError: connection closed ===")
pubsub.disconnect()
try:
    pubsub.subscribe("other_channel", lambda x: None)
except PubSubError as exc:
    print(f"PubSubError: {exc}")

try:
    pubsub.publish("notifications", "message lost")
except PubSubError as exc:
    print(f"PubSubError: {exc}")

print("\n=== PubSubError: invalid channel ===")
pubsub2 = RedisPubSub()
try:
    pubsub2.subscribe("", lambda x: None)
except PubSubError as exc:
    print(f"PubSubError: {exc}")

# Combined handling of StreamError and PubSubError
print("\n=== Combined StreamError and PubSubError handling ===")


def process_event(event_type, data):
    """Processes an event that may use streams or pub/sub."""
    if event_type == "stream":
        s = RedisStream("events")
        s.mark_corrupted()
        s.add(data)
    elif event_type == "pubsub":
        p = RedisPubSub()
        p.disconnect()
        p.publish("channel", data)


for event_type in ["stream", "pubsub"]:
    try:
        process_event(event_type, {"data": "test"})
    except StreamError as exc:
        print(f"  [{event_type}] Stream error: {exc}")
    except PubSubError as exc:
        print(f"  [{event_type}] Pub/Sub error: {exc}")
