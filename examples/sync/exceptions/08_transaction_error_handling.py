"""Demostración de manejo de TransactionError.

Muestra cómo manejar errores de transacciones, como conflictos
de WATCH, y cómo implementar reintentos optimistas.
"""

from wredis._exceptions import TransactionError


class TransaccionRedis:
    """Simula transacciones de Redis con posibilidad de conflicto."""

    def __init__(self):
        self._datos = {"contador": 100}
        self._version = 1
        self._forzar_conflicto = True

    def ejecutar_transaccion(self, operacion):
        """Ejecuta una transacción simulada con control de versión.

        Args:
            operacion: Función que recibe los datos y retorna nuevos datos.

        Raises:
            TransactionError: Si hay conflicto de versión (simula WATCH).
        """
        version_lectura = self._version

        # Simular que otro proceso modifica los datos
        if self._forzar_conflicto:
            self._version += 1
            self._forzar_conflicto = False

        # Verificar si la versión cambió (conflicto WATCH)
        if version_lectura != self._version:
            raise TransactionError(
                f"Conflicto de transacción: la clave fue modificada "
                f"(versión esperada: {version_lectura}, actual: {self._version})"
            )

        nuevos_datos = operacion(self._datos.copy())
        self._datos.update(nuevos_datos)
        return self._datos


def transaccion_con_reintento(cliente, operacion, max_intentos=5):
    """Ejecuta una transacción con reintentos optimistas.

    Args:
        cliente: Instancia de TransaccionRedis.
        operacion: Función con la lógica de la transacción.
        max_intentos: Máximo número de reintentos.

    Returns:
        Resultado de la transacción.
    """
    for intento in range(1, max_intentos + 1):
        try:
            resultado = cliente.ejecutar_transaccion(operacion)
            print(f"  Transacción exitosa en intento {intento}")
            return resultado
        except TransactionError as exc:
            print(f"  Intento {intento}: {exc}")
            if intento == max_intentos:
                raise
    return None


# Caso 1: Transacción con conflicto que se resuelve
print("=== Transacción con conflicto optimista ===")

cliente = TransaccionRedis()


def incrementar_contador(datos):
    datos["contador"] += 1
    return datos


resultado = transaccion_con_reintento(cliente, incrementar_contador)
print(f"Estado final: {resultado}")

# Caso 2: Múltiples transacciones secuenciales
print("\n=== Múltiples transacciones secuenciales ===")

cliente2 = TransaccionRedis()
cliente2._forzar_conflicto = False  # Sin conflictos

for i in range(3):
    try:

        def sumar_diez(datos):
            datos["contador"] += 10
            return datos

        resultado = cliente2.ejecutar_transaccion(sumar_diez)
        print(f"  Transacción {i + 1}: contador = {resultado['contador']}")
    except TransactionError as exc:
        print(f"  Transacción {i + 1} fallida: {exc}")

# Caso 3: Rollback simulado ante error
print("\n=== Rollback ante TransactionError ===")

cliente3 = TransaccionRedis()
estado_original = cliente3._datos.copy()

try:

    def operacion_compleja(datos):
        datos["contador"] -= 50
        datos["temporal"] = True
        return datos

    cliente3.ejecutar_transaccion(operacion_compleja)
except TransactionError as exc:
    print(f"  Transacción fallida, haciendo rollback: {exc}")
    cliente3._datos = estado_original
    print(f"  Estado restaurado: {cliente3._datos}")
