from wredis.queue import RedisQueueManager


# Crear una instancia del consumidor
queue_manager = RedisQueueManager(poll_interval=2, host="localhost", verbose=False)


@queue_manager.on_message("4090")
def worker(record):

    global conteo_global_queso

    """
    Procesa un registro de la cola 'queue_1'.
    """
    print(f"Procesando de 'queue_1': {record}")


@queue_manager.on_message("queue:4060")
def worker(record):

    global conteo_global_queso

    """
    Procesa un registro de la cola 'queue_1'.
    """
    print(f"Procesando de 'queue_1': {record}")


@queue_manager.on_message("4060")
def worker(record):

    global conteo_global_queso

    """
    Procesa un registro de la cola 'queue_1'.
    """
    print(f"Procesando de 'queue_1': {record}")


# Verificar la longitud de la cola
queue_length = queue_manager.get_queue_length("tasks")


queue_manager.start()

# Mantener el programa activo
queue_manager.wait()
