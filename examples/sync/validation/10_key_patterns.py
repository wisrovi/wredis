"""Validación de claves con diferentes patrones de nomenclatura usados en Redis."""

from wredis._validation import validate_key
from wredis._exceptions import ValidationError

# Patrones comunes de nomenclatura en Redis
patrones = [
    "user:1000",  # Patrón entidad:id
    "session:abc123:token",  # Patrón jerárquico con 3 niveles
    "cache:api:github:users",  # Patrón de caché con fuente
    "rate_limit:192.168.1.1",  # Patrón con dirección IP
    "queue:emails:pending",  # Patrón de cola
    "counter:page:home:visits",  # Patrón de contador
    "lock:resource:database",  # Patrón de lock distribuido
    "config:app:database:url",  # Patrón de configuración
    "index:user:email:juan@ejemplo.com",  # Patrón con email (caracteres especiales)
    "temp:data_2024-01-15",  # Patrón temporal con fecha
]

print("Validando patrones comunes de nomenclatura de claves Redis:\n")

for patron in patrones:
    try:
        validate_key(patron)
        print(f"  [OK] '{patron}'")
    except ValidationError as e:
        print(f"  [ERR] '{patron}' -> {e}")

print(f"\n{len(patrones)} patrones de nomenclatura validados.")
