"""Demostración de excepciones para streams (StreamError) y pub/sub (PubSubError).

Muestra cómo manejar errores en operaciones de Redis Streams
y Pub/Sub usando las excepciones correspondientes.
"""

from wredis._exceptions import PubSubError, StreamError


class StreamRedis:
    """Simula operaciones de Redis Streams."""

    def __init__(self, nombre_stream):
        self.nombre = nombre_stream
        self._entradas = []
        self._corrupto = False

    def agregar(self, datos):
        """Agrega una entrada al stream.

        Args:
            datos: Diccionario con los datos de la entrada.

        Returns:
            str: ID de la entrada.

        Raises:
            StreamError: Si los datos son inválidos o el stream está corrupto.
        """
        if self._corrupto:
            raise StreamError(f"Stream '{self.nombre}' está corrupto")
        if not datos:
            raise StreamError("Los datos del stream no pueden estar vacíos")
        if not isinstance(datos, dict):
            raise StreamError(f"Los datos del stream deben ser un dict, no {type(datos).__name__}")
        id_entrada = f"{len(self._entradas)}-0"
        self._entradas.append((id_entrada, datos))
        return id_entrada

    def leer(self, desde_id="0", cantidad=10):
        """Lee entradas del stream.

        Args:
            desde_id: ID desde el cual leer.
            cantidad: Máximo número de entradas.

        Returns:
            Lista de tuplas (id, datos).

        Raises:
            StreamError: Si el stream está corrupto.
        """
        if self._corrupto:
            raise StreamError(f"No se puede leer del stream corrupto '{self.nombre}'")
        inicio = int(desde_id.split("-")[0]) if desde_id != "0" else 0
        return self._entradas[inicio : inicio + cantidad]

    def marcar_corrupto(self):
        self._corrupto = True


class PubSubRedis:
    """Simula operaciones de Redis Pub/Sub."""

    def __init__(self):
        self._suscripciones = {}
        self._conectado = True

    def suscribir(self, canal, callback):
        """Suscribe un callback a un canal.

        Args:
            canal: Nombre del canal.
            callback: Función a llamar cuando llegue un mensaje.

        Raises:
            PubSubError: Si no está conectado o el canal es inválido.
        """
        if not self._conectado:
            raise PubSubError("No se puede suscribir: conexión cerrada")
        if not canal or not isinstance(canal, str):
            raise PubSubError(f"Nombre de canal inválido: '{canal}'")
        self._suscripciones[canal] = callback
        print(f"  Suscrito al canal: {canal}")

    def publicar(self, canal, mensaje):
        """Publica un mensaje en un canal.

        Args:
            canal: Nombre del canal.
            mensaje: El mensaje a publicar.

        Raises:
            PubSubError: Si el canal no existe o no está conectado.
        """
        if not self._conectado:
            raise PubSubError("No se puede publicar: conexión cerrada")
        if canal not in self._suscripciones:
            raise PubSubError(f"Canal '{canal}' no tiene suscriptores")
        self._suscripciones[canal](mensaje)

    def desconectar(self):
        self._conectado = False
        self._suscripciones.clear()


# === StreamError ===
print("=== StreamError: operaciones normales ===")
stream = StreamRedis("eventos:usuario")

id1 = stream.agregar({"accion": "login", "user": "ana"})
id2 = stream.agregar({"accion": "compra", "user": "ana", "monto": 50})
print(f"Entradas agregadas: {id1}, {id2}")

entradas = stream.leer()
for entrada_id, datos in entradas:
    print(f"  [{entrada_id}] {datos}")

print("\n=== StreamError: stream corrupto ===")
stream.marcar_corrupto()
try:
    stream.agregar({"accion": "logout"})
except StreamError as exc:
    print(f"StreamError al agregar: {exc}")

try:
    stream.leer()
except StreamError as exc:
    print(f"StreamError al leer: {exc}")

print("\n=== StreamError: datos inválidos ===")
stream_valido = StreamRedis("logs")
try:
    stream_valido.agregar({})
except StreamError as exc:
    print(f"StreamError: {exc}")

try:
    stream_valido.agregar("no es un dict")
except StreamError as exc:
    print(f"StreamError: {exc}")

# === PubSubError ===
print("\n=== PubSubError: operaciones normales ===")
pubsub = PubSubRedis()


def procesar_mensaje(msg):
    print(f"  [notificaciones] Mensaje recibido: {msg}")


pubsub.suscribir("notificaciones", procesar_mensaje)
pubsub.publicar("notificaciones", "¡Nuevo pedido!")

print("\n=== PubSubError: canal sin suscriptores ===")
try:
    pubsub.publicar("alertas", "Algo pasó")
except PubSubError as exc:
    print(f"PubSubError: {exc}")

print("\n=== PubSubError: conexión cerrada ===")
pubsub.desconectar()
try:
    pubsub.suscribir("otro_canal", lambda x: None)
except PubSubError as exc:
    print(f"PubSubError: {exc}")

try:
    pubsub.publicar("notificaciones", "mensaje perdido")
except PubSubError as exc:
    print(f"PubSubError: {exc}")

print("\n=== PubSubError: canal inválido ===")
pubsub2 = PubSubRedis()
try:
    pubsub2.suscribir("", lambda x: None)
except PubSubError as exc:
    print(f"PubSubError: {exc}")

# Manejo combinado de StreamError y PubSubError
print("\n=== Manejo combinado de StreamError y PubSubError ===")


def procesar_evento(tipo, datos):
    """Procesa un evento que puede usar streams o pub/sub."""
    if tipo == "stream":
        s = StreamRedis("eventos")
        s.marcar_corrupto()
        s.agregar(datos)
    elif tipo == "pubsub":
        p = PubSubRedis()
        p.desconectar()
        p.publicar("canal", datos)


for tipo in ["stream", "pubsub"]:
    try:
        procesar_evento(tipo, {"dato": "test"})
    except StreamError as exc:
        print(f"  [{tipo}] Error de stream: {exc}")
    except PubSubError as exc:
        print(f"  [{tipo}] Error de pub/sub: {exc}")
