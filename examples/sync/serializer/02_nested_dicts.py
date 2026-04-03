"""Serialización de diccionarios anidados.

Este ejemplo muestra cómo serializar estructuras de datos complejas
con diccionarios anidados, comúnmente usadas para almacenar
configuraciones o registros en Redis.
"""

from wredis._serializer import serialize, deserialize

# Diccionario anidado con configuración de usuario
usuario = {
    "id": 1001,
    "nombre": "Ana García",
    "email": "ana@ejemplo.com",
    "preferencias": {
        "tema": "oscuro",
        "idioma": "es",
        "notificaciones": {
            "email": True,
            "push": False,
            "sms": True,
        },
    },
    "roles": ["admin", "editor"],
}

# Serializar el diccionario completo
serialized = serialize(usuario)
print("Diccionario original:")
print(f"  {usuario}")
print(f"\nSerializado ({len(serialized)} caracteres):")
print(f"  {serialized}")

# Deserializar y verificar integridad
restored = deserialize(serialized)
print(f"\nDeserializado:")
print(f"  {restored}")
print(f"\n¿Los datos son iguales? {usuario == restored}")
