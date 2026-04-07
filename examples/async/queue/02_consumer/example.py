import asyncio
import signal
import sys

from wredis.aio import RedisQueueManager

manager = RedisQueueManager(poll_interval=2, host="localhost", verbose=False)


@manager.on_message("tasks")
async def worker_tasks(record):
    print(f"Processing tasks: {record}")


@manager.on_message("priority")
async def worker_priority(record):
    print(f"Processing priority: {record}")


def signal_handler(sig, frame):
    print("\nStopping consumer...")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

print("Listening... Press Ctrl+C to exit")
asyncio.get_event_loop().run_until_complete(manager.start())
signal.pause()
