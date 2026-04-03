"""Prueba de ida y vuelta (round-trip) de datos.

Este ejemplo verifica que los datos serializados y luego
deserializados son idénticos a los originales, garantizando
la integridad del proceso de serialización.
"""

from wredis._serializer import serialize, deserialize

# Casos de prueba para round-trip
casos = [
    ("entero", 42),
    ("flotante", 3.14159),
    ("cadena", "hola mundo"),
    ("booleano_true", True),
    ("booleano_false", False),
    ("none", None),
    ("lista_vacia", []),
    ("dict_vacio", {}),
    ("lista_anidada", [[1, 2], [3, 4], [5, 6]]),
    ("dict_anidado", {"a": {"b": {"c": "profundo"}}}),
    ("mixto", [1, "dos", 3.0, True, None, {"seis": 6}]),
]

print("Pruebas de ida y vuelta (round-trip):")
print("=" * 60)

todos_ok = True
for nombre, valor in casos:
    serialized = serialize(valor)
    restored = deserialize(serialized)
    es_igual = valor == restored
    estado = "OK" if es_igual else "FALLO"
    if not es_igual:
        todos_ok = False
    print(f"  {nombre:20s} | {estado:5s} | {valor!r:40s}")

print("=" * 60)
print(f"Resultado: {'TODAS LAS PRUEBAS PASARON' if todos_ok else 'ALGUNAS PRUEBAS FALLARON'}")
