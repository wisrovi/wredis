"""Demostración de manejo de SerializationError.

Muestra cómo detectar y manejar errores de serialización y
deserialización de datos al interactuar con Redis.
"""

import json

from wredis._exceptions import SerializationError


def serializar(datos):
    """Serializa datos a JSON para almacenar en Redis.

    Args:
        datos: El objeto a serializar.

    Returns:
        str: Datos serializados en JSON.

    Raises:
        SerializationError: Si no se puede serializar.
    """
    try:
        return json.dumps(datos)
    except (TypeError, ValueError) as exc:
        raise SerializationError(f"No se pudo serializar datos de tipo {type(datos).__name__}: {exc}") from exc


def deserializar(texto):
    """Deserializa datos JSON obtenidos de Redis.

    Args:
        texto: El string JSON a deserializar.

    Returns:
        El objeto deserializado.

    Raises:
        SerializationError: Si no se puede deserializar.
    """
    try:
        return json.loads(texto)
    except (json.JSONDecodeError, TypeError) as exc:
        raise SerializationError(f"No se pudo deserializar: {exc}") from exc


# Caso 1: Serialización exitosa
print("=== Serialización exitosa ===")
datos = {"nombre": "Ana", "edad": 30, "roles": ["admin", "user"]}
try:
    resultado = serializar(datos)
    print(f"Serializado: {resultado}")
except SerializationError as exc:
    print(f"Error: {exc}")

# Caso 2: Objeto no serializable
print("\n=== Objeto no serializable ===")


class Configuracion:
    def __init__(self):
        self.debug = True


config = Configuracion()
try:
    serializar(config)
except SerializationError as exc:
    print(f"Error de serialización: {exc}")
    print(f"  Causa original: {exc.__cause__}")

# Caso 3: Deserialización de JSON corrupto
print("\n=== JSON corrupto ===")
json_corrupto = '{nombre: "Ana", edad: }'
try:
    deserializar(json_corrupto)
except SerializationError as exc:
    print(f"Error de deserialización: {exc}")

# Caso 4: Fallback a valor por defecto
print("\n=== Fallback ante error de deserialización ===")
datos_cache = ["no es json", '{"valido": true}', "tampoco es json"]

for dato in datos_cache:
    try:
        resultado = deserializar(dato)
        print(f"Deserializado: {resultado}")
    except SerializationError:
        resultado = None
        print(f"No se pudo deserializar '{dato}', usando None")

# Caso 5: Serializador personalizado con manejo de errores
print("\n=== Serializador personalizado ===")


def serializar_seguro(datos, fallback=None):
    """Intenta serializar y retorna fallback si falla.

    Args:
        datos: Objeto a serializar.
        fallback: Valor a retornar si falla.

    Returns:
        Datos serializados o fallback.
    """
    try:
        return serializar(datos)
    except SerializationError:
        # Intentar convertir a string como último recurso
        try:
            return json.dumps(str(datos))
        except Exception:
            return fallback


resultado = serializar_seguro(Configuracion(), fallback='{"error": true}')
print(f"Serialización segura: {resultado}")
