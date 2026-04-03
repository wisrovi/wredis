"""Precalentamiento de caché (cache warming).

Este ejemplo muestra cómo precalentar la caché con datos conocidos
antes de que lleguen las solicitudes reales, mejorando la tasa de aciertos.
"""

import fakeredis
from wredis.decorators import cache, CacheMetrics

redis_client = fakeredis.FakeStrictRedis()
metrics = CacheMetrics()


@cache(ttl=600, prefix="config", redis_client=redis_client, metrics=metrics)
def cargar_configuracion(clave: str) -> dict:
    """Simula carga de configuración desde base de datos."""
    print(f"  [DB] Cargando configuración: {clave}")
    return {"clave": clave, "valor": f"valor_para_{clave}"}


# Precalentar caché con las claves más comunes
print("=== Precalentando caché ===")
claves_comunes = ["theme", "language", "timezone", "notifications", "layout"]
for clave in claves_comunes:
    cargar_configuracion(clave)

print(f"Métricas después del precalentamiento: {metrics}")
print(f"Hit rate: {metrics.hit_rate:.1f}%")

# Simular tráfico real que coincide con las claves precalentadas
print("\n=== Tráfico real ===")
solicitudes_reales = ["theme", "language", "theme", "notifications", "theme", "layout"]
for clave in solicitudes_reales:
    resultado = cargar_configuracion(clave)
    print(f"  Solicitud '{clave}' -> {resultado['valor']}")

print(f"\nMétricas finales: {metrics}")
print(f"Hit rate final: {metrics.hit_rate:.1f}%")
print(f"Beneficio del precalentamiento: {metrics.hits} hits de {metrics.hits + metrics.misses} solicitudes")
