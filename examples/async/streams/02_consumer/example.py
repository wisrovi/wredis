import asyncio
import signal
import sys

from wredis.aio import RedisStreamManager

manager = RedisStreamManager(host="localhost", verbose=False)


@manager.on_message(stream_name="my_stream", group_name="my_group", consumer_name="consumer_1")
async def process_message(data):
    print(f"[Consumer 1] Processing: {data}")


def signal_handler(sig, frame):
    print("\nStopping consumer...")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

print("Listening... Press Ctrl+C to exit")
asyncio.get_event_loop().run_until_complete(manager.start())
signal.pause()
