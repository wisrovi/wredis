"""Validación de claves con casos inválidos: vacías y demasiado largas."""

from wredis._validation import validate_key
from wredis._exceptions import ValidationError

# Clave vacía (string vacío)
try:
    validate_key("")
    print("Clave vacía: válida (inesperado)")
except ValidationError as e:
    print(f"Clave vacía: inválida -> {e}")

# Clave con más de 512 caracteres
clave_muy_larga = "a" * 513
try:
    validate_key(clave_muy_larga)
    print("Clave de 513 caracteres: válida (inesperado)")
except ValidationError as e:
    print(f"Clave de 513 caracteres: inválida -> {e}")

# Clave extremadamente larga
clave_gigante = "b" * 10000
try:
    validate_key(clave_gigante)
    print("Clave de 10000 caracteres: válida (inesperado)")
except ValidationError as e:
    print(f"Clave de 10000 caracteres: inválida -> {e}")

print("\nSe demostró que las claves vacías o mayores a 512 caracteres generan ValidationError.")
