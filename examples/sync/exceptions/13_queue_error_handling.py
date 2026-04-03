"""Demostración de excepciones para colas (QueueError).

Muestra cómo manejar errores en operaciones de cola como
push, pop y peek usando QueueError.
"""

from wredis._exceptions import QueueError


class ColaRedis:
    """Simula una cola basada en Redis con validaciones."""

    def __init__(self, nombre, max_tamano=5):
        self.nombre = nombre
        self.max_tamano = max_tamano
        self._elementos = []

    def push(self, elemento):
        """Agrega un elemento a la cola.

        Args:
            elemento: El elemento a agregar.

        Raises:
            QueueError: Si la cola está llena o el elemento es inválido.
        """
        if elemento is None:
            raise QueueError(f"No se puede agregar None a la cola '{self.nombre}'")
        if len(self._elementos) >= self.max_tamano:
            raise QueueError(f"Cola '{self.nombre}' llena ({self.max_tamano} elementos máximo)")
        self._elementos.append(elemento)
        return len(self._elementos)

    def pop(self):
        """Extrae el primer elemento de la cola.

        Returns:
            El primer elemento.

        Raises:
            QueueError: Si la cola está vacía.
        """
        if not self._elementos:
            raise QueueError(f"No se puede hacer pop de la cola vacía '{self.nombre}'")
        return self._elementos.pop(0)

    def peek(self):
        """Obtiene el primer elemento sin extraerlo.

        Returns:
            El primer elemento.

        Raises:
            QueueError: Si la cola está vacía.
        """
        if not self._elementos:
            raise QueueError(f"No se puede hacer peek de la cola vacía '{self.nombre}'")
        return self._elementos[0]

    @property
    def tamano(self):
        return len(self._elementos)


# Caso 1: Operaciones normales
print("=== Operaciones normales de cola ===")
cola = ColaRedis("tareas", max_tamano=3)

cola.push("tarea_1")
cola.push("tarea_2")
print(f"Elementos en cola: {cola.tamano}")
print(f"Primer elemento (peek): {cola.peek()}")

elemento = cola.pop()
print(f"Elemento extraído (pop): {elemento}")
print(f"Elementos restantes: {cola.tamano}")

# Caso 2: Cola llena
print("\n=== Error: cola llena ===")
cola.push("tarea_3")
cola.push("tarea_4")
try:
    cola.push("tarea_5")
except QueueError as exc:
    print(f"QueueError: {exc}")

# Caso 3: Cola vacía
print("\n=== Error: cola vacía ===")
cola_vacia = ColaRedis("vacia")
try:
    cola_vacia.pop()
except QueueError as exc:
    print(f"QueueError: {exc}")

try:
    cola_vacia.peek()
except QueueError as exc:
    print(f"QueueError: {exc}")

# Caso 4: Elemento inválido
print("\n=== Error: elemento inválido ===")
try:
    cola.push(None)
except QueueError as exc:
    print(f"QueueError: {exc}")

# Caso 5: Procesamiento seguro de cola
print("\n=== Procesamiento seguro con manejo de QueueError ===")


def procesar_cola(cola):
    """Procesa todos los elementos de forma segura.

    Args:
        cola: Instancia de ColaRedis.
    """
    procesados = 0
    while True:
        try:
            elemento = cola.pop()
            print(f"  Procesando: {elemento}")
            procesados += 1
        except QueueError:
            break
    print(f"  Total procesados: {procesados}")


cola_llena = ColaRedis("lotes", max_tamano=10)
for i in range(4):
    cola_llena.push(f"lote_{i}")

procesar_cola(cola_llena)

# Caso 6: Push con reintento
print("\n=== Push con reintento ante QueueError ===")
cola_limitada = ColaRedis("limitada", max_tamano=2)
cola_limitada.push("msg_1")
cola_limitada.push("msg_2")

intentos = 0
max_intentos = 3

while intentos < max_intentos:
    intentos += 1
    try:
        cola_limitada.push("msg_3")
        print(f"  Mensaje enviado en intento {intentos}")
        break
    except QueueError as exc:
        # Consumir un mensaje para hacer espacio
        try:
            antiguo = cola_limitada.pop()
            print(f"  Mensaje antiguo descartado: {antiguo}")
        except QueueError:
            print(f"  Intento {intentos}: {exc}")
else:
    print("  No se pudo enviar el mensaje tras todos los intentos")
