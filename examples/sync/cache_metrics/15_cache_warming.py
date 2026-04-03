"""Estrategia avanzada de precalentamiento de caché.

Este ejemplo implementa una estrategia completa de cache warming
con métricas detalladas y análisis de efectividad.
"""

import fakeredis
from wredis.decorators import cache, CacheMetrics

redis_client = fakeredis.FakeStrictRedis()
metrics = CacheMetrics()


@cache(ttl=600, prefix="catalogo", redis_client=redis_client, metrics=metrics)
def obtener_categoria(categoria_id: int) -> dict:
    """Obtiene datos de una categoría del catálogo."""
    return {"categoria_id": categoria_id, "nombre": f"Categoria_{categoria_id}", "productos": categoria_id * 10}


def precalentar_categorias(categorias_ids: list[int]) -> None:
    """Precalienta la caché con las categorías especificadas."""
    print("=== Iniciando precalentamiento ===")
    for cat_id in categorias_ids:
        obtener_categoria(cat_id)
        print(f"  Precalentada categoría {cat_id}")
    print(f"Métricas post-precalentamiento: {metrics}")


def simular_trafico(categoria_ids: list[int]) -> None:
    """Simula tráfico real de usuarios accediendo a categorías."""
    print("\n=== Simulando tráfico ===")
    for cat_id in categoria_ids:
        resultado = obtener_categoria(cat_id)
        print(f"  Acceso a categoría {cat_id}: {resultado['nombre']}")


def analizar_efectividad(metrics: CacheMetrics) -> None:
    """Analiza la efectividad del precalentamiento."""
    print("\n=== Análisis de efectividad ===")
    total = metrics.hits + metrics.misses
    if total == 0:
        print("  Sin datos para analizar")
        return

    print(f"  Total solicitudes: {total}")
    print(f"  Hits (servidas desde caché): {metrics.hits}")
    print(f"  Misses (requirieron DB): {metrics.misses}")
    print(f"  Hit rate: {metrics.hit_rate:.1f}%")

    if metrics.hit_rate >= 80:
        print("  Evaluación: EXCELENTE - El precalentamiento fue muy efectivo")
    elif metrics.hit_rate >= 50:
        print("  Evaluación: BUENO - El precalentamiento fue moderadamente efectivo")
    else:
        print("  Evaluación: REGULAR - Considerar ajustar la estrategia de precalentamiento")


# Ejecutar estrategia completa
print("=== Estrategia de Cache Warming ===\n")

# Paso 1: Precalentar con categorías principales
categorias_principales = [1, 2, 3, 4, 5]
precalentar_categorias(categorias_principales)

# Paso 2: Simular tráfico que coincide con categorías precalentadas
trafico_simulado = [1, 2, 1, 3, 1, 2, 4, 5, 1, 3]
simular_trafico(trafico_simulado)

# Paso 3: Analizar resultados
analizar_efectividad(metrics)
