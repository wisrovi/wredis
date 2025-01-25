from wredis.streams import RedisStreamManager


stream_manager = RedisStreamManager(host="localhost", verbose=False)


# Registrar un consumidor para un stream
@stream_manager.on_message(
    stream_name="my_stream", group_name="my_group", consumer_name="consumer_1"
)
def process_message(data):
    print(f"[Consumer 1] Procesando mensaje: {data}")


# Registrar el segundo consumidor
@stream_manager.on_message(
    stream_name="my_stream_2", group_name="my_group", consumer_name="consumer_2"
)
def process_message_consumer_2(data):
    print(f"[Consumer 2] Procesando mensaje: {data}")


# Mantener el programa activo para consumir mensajes
stream_manager.wait()
