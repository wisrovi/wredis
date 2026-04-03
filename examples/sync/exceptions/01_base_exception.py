"""Demostración de la excepción base WRedisError.

Muestra cómo WRedisError es la clase base de todas las excepciones
en wredis y cómo puede usarse como punto de captura genérico.
"""

from wredis._exceptions import WRedisError


# Lanzar la excepción base directamente
try:
    raise WRedisError("Error genérico de WRedis")
except WRedisError as exc:
    print(f"Tipo de excepción: {type(exc).__name__}")
    print(f"Mensaje: {exc}")
    print(f"¿Es instancia de Exception? {isinstance(exc, Exception)}")


# Crear subclases personalizadas que heredan de WRedisError
class MiErrorPersonalizado(WRedisError):
    """Excepción personalizada para mi aplicación."""


try:
    raise MiErrorPersonalizado("Algo salió mal en mi app")
except WRedisError as exc:
    print(f"\nCapturada como WRedisError: {exc}")
    print(f"Tipo real: {type(exc).__name__}")

# Verificar que WRedisError hereda directamente de Exception
print(f"\nWRedisError.__bases__: {WRedisError.__bases__}")
print("La excepción base funciona correctamente.")
