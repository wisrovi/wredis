# Cache Metrics Examples

Ejemplos prácticos de uso de `CacheMetrics` con los decoradores `@cache` y `@async_cache` de wredis.

## Tabla de Contenidos

| # | Archivo | Descripción |
|---|---------|-------------|
| 01 | [01_basic_metrics.py](01_basic_metrics.py) | Seguimiento básico de métricas de caché con hits y misses |
| 02 | [02_hit_rate_monitoring.py](02_hit_rate_monitoring.py) | Monitoreo de tasa de aciertos usando la propiedad `hit_rate` |
| 03 | [03_multiple_cache_zones.py](03_multiple_cache_zones.py) | Múltiples zonas de caché con métricas independientes |
| 04 | [04_ttl_impact.py](04_ttl_impact.py) | Impacto del TTL en la tasa de aciertos de caché |
| 05 | [05_cache_warming.py](05_cache_warming.py) | Precalentamiento de caché con datos conocidos |
| 06 | [06_invalidation_impact.py](06_invalidation_impact.py) | Impacto de la invalidación en las métricas de caché |
| 07 | [07_dashboard_pattern.py](07_dashboard_pattern.py) | Patrón de dashboard para monitoreo de caché |
| 08 | [08_alerting_low_hitrate.py](08_alerting_low_hitrate.py) | Sistema de alertas por baja tasa de aciertos |
| 09 | [09_manual_recording.py](09_manual_recording.py) | Registro manual de hits, misses y errores |
| 10 | [10_async_cache_metrics.py](10_async_cache_metrics.py) | Métricas con funciones asíncronas usando `@async_cache` |
| 11 | [11_performance_comparison.py](11_performance_comparison.py) | Comparación de rendimiento con y sin caché |
| 12 | [12_custom_key_builder.py](12_custom_key_builder.py) | Métricas con prefijos y key builders personalizados |
| 13 | [13_error_handling_metrics.py](13_error_handling_metrics.py) | Manejo de errores y métricas de error |
| 14 | [14_invalidation_decorator.py](14_invalidation_decorator.py) | Decorador de invalidación combinado con métricas |
| 15 | [15_cache_warming.py](15_cache_warming.py) | Estrategia avanzada de precalentamiento con análisis |

## Requisitos

```bash
pip install wredis fakeredis
```

## Uso

Cada ejemplo es un script independiente que se puede ejecutar directamente:

```bash
python 01_basic_metrics.py
python 02_hit_rate_monitoring.py
# ... etc
```

## API de CacheMetrics

```python
from wredis.decorators import cache, async_cache, CacheMetrics

# Crear instancia de métricas
metrics = CacheMetrics()

# Propiedades
metrics.hits       # Número de aciertos
metrics.misses     # Número de fallos
metrics.errors     # Número de errores
metrics.hit_rate   # Tasa de aciertos en porcentaje (0.0-100.0)

# Métodos
metrics.record_hit()    # Registrar un acierto
metrics.record_miss()   # Registrar un fallo
metrics.record_error()  # Registrar un error
metrics.reset()         # Resetear todos los contadores

# Usar con decoradores
@cache(ttl=300, prefix="mi_app", metrics=metrics)
def mi_funcion(arg):
    return resultado

@async_cache(ttl=300, prefix="mi_app", metrics=metrics)
async def mi_funcion_async(arg):
    return resultado
```
