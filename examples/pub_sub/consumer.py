from wredis.pubsub import RedisPubSubManager
import signal

pubsub_manager = RedisPubSubManager(host="localhost", verbose=False)


@pubsub_manager.on_message("channel_1")
def handle_message(message):
    print(f"[channel_1] Mensaje recibido: {message}")


@pubsub_manager.on_message("channel_2")
def handle_channel_2(message):
    print(f"[channel_2] Mensaje recibido: {message}")


# Manejar la señal de interrupción (Ctrl+C) para salir limpiamente
def signal_handler(sig, frame):
    print("\nDeteniendo programa...")
    pubsub_manager.stop_listeners()
    print("Programa detenido.")
    exit(0)


signal.signal(signal.SIGINT, signal_handler)

signal.pause()
