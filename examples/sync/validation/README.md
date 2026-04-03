# Validation Examples

Ejemplos que demuestran el uso de las funciones de validación de `wredis._validation`.

## Tabla de contenidos

| # | Archivo | Descripción |
|---|---------|-------------|
| 01 | [`01_ttl_validation.py`](01_ttl_validation.py) | Validación básica de TTL con valores aceptables (positivos, 0 y -1). |
| 02 | [`02_invalid_ttl.py`](02_invalid_ttl.py) | Validación de TTL con valores inválidos menores a -1 que lanzan `ValidationError`. |
| 03 | [`03_key_validation.py`](03_key_validation.py) | Validación de claves de Redis con casos válidos: simples, jerárquicas y de 512 caracteres. |
| 04 | [`04_invalid_key.py`](04_invalid_key.py) | Validación de claves inválidas: vacías y mayores a 512 caracteres. |
| 05 | [`05_offset_validation.py`](05_offset_validation.py) | Validación de offset para operaciones con bitmaps (valores válidos e inválidos). |
| 06 | [`06_bit_value_validation.py`](06_bit_value_validation.py) | Validación de valores de bit (0 y 1) para operaciones SETBIT/GETBIT. |
| 07 | [`07_score_validation.py`](07_score_validation.py) | Validación de scores para conjuntos ordenados: enteros, floats, NaN e infinito. |
| 08 | [`08_batch_validation.py`](08_batch_validation.py) | Validación de múltiples parámetros en una sola operación (validación por lotes). |
| 09 | [`09_edge_cases.py`](09_edge_cases.py) | Casos límite para todas las funciones de validación: límites exactos y valores justo fuera del rango. |
| 10 | [`10_key_patterns.py`](10_key_patterns.py) | Validación de claves con patrones de nomenclatura comunes en Redis (entity:id, jerárquicos, etc.). |
| 11 | [`11_score_types.py`](11_score_types.py) | Validación de scores con diferentes tipos numéricos de Python: int, float, bool y tipos inválidos. |
| 12 | [`12_validation_decorator.py`](12_validation_decorator.py) | Decorador reutilizable para validar parámetros automáticamente antes de ejecutar operaciones. |
| 13 | [`13_config_manager.py`](13_config_manager.py) | Integración de validación con un gestor de configuración simulado. |
| 14 | [`14_bitmap_operations.py`](14_bitmap_operations.py) | Validación completa de parámetros para operaciones con bitmaps (key, offset, bit value). |
| 15 | [`15_sorted_set_scores.py`](15_sorted_set_scores.py) | Validación de scores en un gestor de conjuntos ordenados con leaderboard simulado. |

## API de validación

Las funciones disponibles en `wredis._validation` son:

| Función | Parámetro | Válidos | Inválidos |
|---------|-----------|---------|-----------|
| `validate_ttl(ttl)` | `int` | `>= 0` y `-1` | `< -1` |
| `validate_key(key)` | `str` | 1 a 512 caracteres | vacío o `> 512` |
| `validate_offset(offset)` | `int` | `>= 0` | `< 0` |
| `validate_bit_value(value)` | `int` | `0` o `1` | cualquier otro |
| `validate_score(score)` | `float` | números finitos | `NaN`, `inf`, no-números |

Todas las funciones lanzan `ValidationError` (de `wredis._exceptions`) cuando la validación falla.

## Cómo ejecutar

Cada ejemplo se puede ejecutar de forma independiente:

```bash
python examples/sync/validation/01_ttl_validation.py
python examples/sync/validation/07_score_validation.py
python examples/sync/validation/15_sorted_set_scores.py
```
