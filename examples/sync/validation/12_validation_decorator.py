"""Decorador reutilizable para validar parámetros antes de ejecutar operaciones."""

from wredis._validation import validate_ttl, validate_key
from wredis._exceptions import ValidationError
from functools import wraps


def validar_set_params(func):
    """Decorador que valida key y ttl antes de ejecutar una función SET."""

    @wraps(func)
    def wrapper(key: str, value, ttl: int = -1, *args, **kwargs):
        # Validar la clave antes de ejecutar
        validate_key(key)
        # Validar el TTL antes de ejecutar
        validate_ttl(ttl)
        return func(key, value, ttl, *args, **kwargs)

    return wrapper


@validar_set_params
def simular_set(key: str, value, ttl: int = -1):
    """Simula una operación SET de Redis con validación automática."""
    ttl_desc = "sin expiración" if ttl == -1 else f"{ttl}s"
    print(f"  SET {key} = {value} (TTL: {ttl_desc})")
    return True


print("=== Operaciones válidas ===")
simular_set("usuario:1", {"nombre": "Ana"}, ttl=3600)
simular_set("config:app", {"tema": "oscuro"}, ttl=-1)
simular_set("temp:datos", "valor_temporal", ttl=60)

print("\n=== Operaciones inválidas ===")

try:
    simular_set("", "valor", ttl=3600)
except ValidationError as e:
    print(f"  Error con clave vacía: {e}")

try:
    simular_set("usuario:2", "valor", ttl=-5)
except ValidationError as e:
    print(f"  Error con TTL inválido: {e}")

print("\nSe demostró el uso de un decorador para validación automática.")
