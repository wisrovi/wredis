from wredis.queue import RedisQueueManager

queue_manager = RedisQueueManager(host="localhost", compress=True, verbose=True)


@queue_manager.on_message("tasks")
def baches_eyesnroad(record):
    print(f"Procesando de 'tasks': {record}")


if __name__ == "__main__":
    queue_manager.start()

    sms = {
        "to": "+1234567890",
        "from": "+0987654321",
        "message": "Hello, this is a test message.",
    }
    queue_manager.publish("tasks", sms)

    queue_manager.wait()
