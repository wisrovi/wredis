"""Uso del serializador como simulación de almacenamiento en Redis.

Este ejemplo muestra un patrón común donde se serializan datos
antes de "almacenarlos" (simulado) y se deserializan al
"recuperarlos", imitando el flujo real con Redis.
"""

from wredis._serializer import serialize, deserialize

# Simulación de una base de datos Redis en memoria
base_datos_simulada = {}


def guardar_en_redis(clave: str, valor: dict) -> None:
    """Simula guardar un valor en Redis serializándolo primero."""
    datos_serializados = serialize(valor)
    base_datos_simulada[clave] = datos_serializados
    print(f"  Guardado '{clave}': {len(datos_serializados)} bytes")


def obtener_de_redis(clave: str) -> dict:
    """Simula obtener un valor de Redis deserializándolo."""
    datos_serializados = base_datos_simulada[clave]
    return deserialize(datos_serializados)


# Guardar varios registros
print("Guardando registros:")
guardar_en_redis(
    "usuario:1",
    {
        "nombre": "María López",
        "email": "maria@ejemplo.com",
        "edad": 30,
        "activo": True,
    },
)
guardar_en_redis(
    "usuario:2",
    {
        "nombre": "Juan Pérez",
        "email": "juan@ejemplo.com",
        "edad": 25,
        "activo": False,
    },
)
guardar_en_redis(
    "config:app",
    {
        "version": "2.1.0",
        "debug": False,
        "max_conexiones": 100,
    },
)

# Recuperar registros
print("\nRecuperando registros:")
usuario1 = obtener_de_redis("usuario:1")
print(f"  Usuario 1: {usuario1}")

usuario2 = obtener_de_redis("usuario:2")
print(f"  Usuario 2: {usuario2}")

config = obtener_de_redis("config:app")
print(f"  Configuración: {config}")

print(f"\nTotal de claves almacenadas: {len(base_datos_simulada)}")
