"""Validación básica de claves de Redis con casos válidos."""

from wredis._validation import validate_key
from wredis._exceptions import ValidationError

# Clave simple y corta
validate_key("usuario:123")
print("Clave 'usuario:123': válida")

# Clave con prefijo jerárquico
validate_key("app:sessions:token_abc")
print("Clave 'app:sessions:token_abc': válida")

# Clave con caracteres especiales permitidos
validate_key("cache:datos_v2.0")
print("Clave 'cache:datos_v2.0': válida")

# Clave de un solo carácter (mínimo válido)
validate_key("x")
print("Clave 'x': válida")

# Clave con exactamente 512 caracteres (límite máximo)
clave_larga = "k" * 512
validate_key(clave_larga)
print(f"Clave de 512 caracteres: válida")

print("\nTodas las claves válidas fueron aceptadas correctamente.")
