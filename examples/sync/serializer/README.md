# Ejemplos de Serialización en WRedis

Colección de ejemplos prácticos que demuestran el uso del módulo
`wredis._serializer` para serializar y deserializar datos en formato JSON.

## API

```python
from wredis._serializer import serialize, deserialize
from wredis._exceptions import SerializationError

# Serializar cualquier valor compatible con JSON a cadena
datos_json: str = serialize(valor)

# Deserializar una cadena JSON a objeto Python
valor = deserialize(datos_json)
```

## Tabla de Contenidos

| # | Archivo | Descripción |
|---|---------|-------------|
| 01 | [01_basic_serialize.py](01_basic_serialize.py) | Serialización de tipos primitivos: enteros, flotantes, cadenas y booleanos |
| 02 | [02_nested_dicts.py](02_nested_dicts.py) | Serialización de diccionarios anidados con estructuras complejas |
| 03 | [03_lists_and_collections.py](03_lists_and_collections.py) | Manejo de listas simples, mixtas, anidadas y vacías |
| 04 | [04_unicode_strings.py](04_unicode_strings.py) | Soporte de Unicode: español, japonés, emojis y símbolos especiales |
| 05 | [05_none_values.py](05_none_values.py) | Serialización de valores None en estructuras de datos |
| 06 | [06_booleans.py](06_booleans.py) | Manejo de valores booleanos True y False en diferentes contextos |
| 07 | [07_datetime_serialization.py](07_datetime_serialization.py) | Serialización de fechas y horas usando formato ISO 8601 |
| 08 | [08_custom_objects.py](08_custom_objects.py) | Serialización de objetos personalizados con dataclasses |
| 09 | [09_large_data.py](09_large_data.py) | Rendimiento con conjuntos de datos grandes (miles de elementos) |
| 10 | [10_round_trip.py](10_round_trip.py) | Pruebas de ida y vuelta para verificar integridad de datos |
| 11 | [11_error_handling.py](11_error_handling.py) | Captura y manejo de excepciones SerializationError |
| 12 | [12_tuples_to_lists.py](12_tuples_to_lists.py) | Comportamiento de tuplas al serializar (se convierten a listas) |
| 13 | [13_long_strings.py](13_long_strings.py) | Serialización de cadenas de texto muy largas y con caracteres de escape |
| 14 | [14_redis_storage_pattern.py](14_redis_storage_pattern.py) | Patrón de almacenamiento simulando operaciones de Redis |
| 15 | [15_error_handling.py](15_error_handling.py) | Manejo avanzado de errores con validación previa y valores por defecto |

## Ejecutar ejemplos

Cada ejemplo es un script independiente que se puede ejecutar directamente:

```bash
python examples/sync/serializer/01_basic_serialize.py
python examples/sync/serializer/02_nested_dicts.py
# ... etc
```

## Notas

- El serializador usa `json.dumps` con `ensure_ascii=False` para preservar caracteres Unicode.
- Los objetos `datetime` deben convertirse a cadena ISO 8601 antes de serializar.
- Las tuplas se convierten a listas durante la serialización (limitación de JSON).
- No todos los tipos de Python son serializables (sets, funciones, clases personalizadas sin conversión).
