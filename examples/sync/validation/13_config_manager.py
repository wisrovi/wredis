"""Validación integrada con un gestor de configuración simulado."""

from wredis._validation import validate_key, validate_ttl
from wredis._exceptions import ValidationError


class ConfigManager:
    """Gestor de configuración que usa validación de wredis."""

    def __init__(self):
        self._store = {}

    def set_config(self, key: str, value, ttl: int = -1) -> bool:
        """Almacena una configuración con validación previa."""
        # Validar parámetros antes de almacenar
        validate_key(key)
        validate_ttl(ttl)

        self._store[key] = {"value": value, "ttl": ttl}
        print(f"  Configuración guardada: {key} = {value}")
        return True

    def get_config(self, key: str):
        """Obtiene una configuración validando la clave."""
        validate_key(key)
        return self._store.get(key)

    def list_configs(self):
        """Lista todas las configuraciones almacenadas."""
        return dict(self._store)


# Crear instancia del gestor
manager = ConfigManager()

print("=== Guardando configuraciones válidas ===")
manager.set_config("app:name", "MiAplicacion")
manager.set_config("app:version", "2.0.0", ttl=86400)
manager.set_config("db:host", "localhost", ttl=-1)

print("\n=== Intentando guardar configuraciones inválidas ===")

try:
    manager.set_config("", "valor_invalido")
except ValidationError as e:
    print(f"  Error: {e}")

try:
    manager.set_config("app:debug", "true", ttl=-10)
except ValidationError as e:
    print(f"  Error: {e}")

print("\n=== Configuraciones almacenadas ===")
for key, data in manager.list_configs().items():
    print(f"  {key}: {data['value']} (TTL: {data['ttl']})")

print("\nSe demostró la integración de validación con un gestor de configuración.")
