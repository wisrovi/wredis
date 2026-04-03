"""Serialización de valores booleanos y sus variantes.

Este ejemplo muestra cómo se manejan los valores booleanos
True y False, tanto de forma individual como dentro de
estructuras de datos más complejas.
"""

from wredis._serializer import serialize, deserialize

# Booleanos individuales
verdadero = True
falso = False

serialized_true = serialize(verdadero)
serialized_false = serialize(falso)

print(f"True serializado: {serialized_true!r}")
print(f"False serializado: {serialized_false!r}")
print(f"True deserializado: {deserialize(serialized_true)}")
print(f"False deserializado: {deserialize(serialized_false)}")
print()

# Booleanos en un diccionario de configuración
config = {
    "debug": True,
    "produccion": False,
    "log_enabled": True,
    "cache_disabled": False,
    "max_retries": 3,
}
serialized = serialize(config)
print(f"Configuración: {config}")
print(f"Serializado: {serialized}")
restored = deserialize(serialized)
print(f"Deserializado: {restored}")
print(f"Tipo de 'debug': {type(restored['debug']).__name__}")
print()

# Lista de resultados booleanos
resultados = [True, False, True, True, False]
serialized = serialize(resultados)
print(f"Resultados: {resultados}")
print(f"Serializado: {serialized}")
print(f"Deserializado: {deserialize(serialized)}")
