from wredis.queue import RedisQueueManager

queue_manager = RedisQueueManager(host="192.168.1.84", compress=True, verbose=False)


@queue_manager.on_message("baches_queue")
def baches_eyesnroad(record):
    print(f"Procesando de 'baches_queue': {record}")


if __name__ == "__main__":
    queue_manager.start()

    sms = {
        "to": "+1234567890",
        "from": "+0987654321",
        "message": "Hello, this is a test message.",
    }
    queue_manager.publish("baches_queue", sms)

    queue_manager.wait()
