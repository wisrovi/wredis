#!/usr/bin/env python3
"""
Benchmarks para la biblioteca wredis.

Este script compara el rendimiento de todos los tipos de manager,
operaciones síncronas vs asíncronas, decoradores de caché,
operaciones individuales vs por lotes, y el impacto del pool de conexiones.

Uso:
    python benchmarks/run_benchmarks.py
    python benchmarks/run_benchmarks.py --iterations 5000

Requiere: fakeredis (instalado con pip install -e ".[dev]")
"""

from __future__ import annotations

import asyncio
import os
import sys
import time
from dataclasses import dataclass
from typing import Any

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

ITERATIONS = int(os.environ.get("WREDIS_BENCH_ITERATIONS", 1000))
USE_REAL_REDIS = os.environ.get("WREDIS_BENCH_REAL_REDIS", "0") == "1"
REDIS_HOST = os.environ.get("WREDIS_BENCH_HOST", "localhost")
REDIS_PORT = int(os.environ.get("WREDIS_BENCH_PORT", "6379"))

# ---------------------------------------------------------------------------
# Utilidades de medición
# ---------------------------------------------------------------------------


@dataclass
class BenchResult:
    """Almacena el resultado de un benchmark individual."""

    name: str
    operations: int
    total_ms: float
    avg_us: float
    ops_per_sec: float


def measure(func, *args: Any, **kwargs: Any) -> BenchResult:
    """Ejecuta una función N veces y devuelve métricas de rendimiento."""
    iterations = kwargs.pop("_iterations", ITERATIONS)
    name = kwargs.pop("_name", func.__name__ if callable(func) else "unknown")

    # Calentamiento: una iteración sin medir
    if callable(func):
        func(*args, **kwargs)

    start = time.perf_counter()
    for _ in range(iterations):
        if callable(func):
            func(*args, **kwargs)
    elapsed = time.perf_counter() - start

    total_ms = elapsed * 1000
    avg_us = (elapsed / iterations) * 1_000_000
    ops_per_sec = iterations / elapsed if elapsed > 0 else float("inf")

    return BenchResult(
        name=name,
        operations=iterations,
        total_ms=round(total_ms, 2),
        avg_us=round(avg_us, 2),
        ops_per_sec=round(ops_per_sec, 0),
    )


async def measure_async(coro_func, *args: Any, **kwargs: Any) -> BenchResult:
    """Ejecuta una corrutina N veces y devuelve métricas de rendimiento."""
    iterations = kwargs.pop("_iterations", ITERATIONS)
    name = kwargs.pop("_name", coro_func.__name__ if callable(coro_func) else "unknown")

    # Calentamiento
    if callable(coro_func):
        await coro_func(*args, **kwargs)

    start = time.perf_counter()
    for _ in range(iterations):
        if callable(coro_func):
            await coro_func(*args, **kwargs)
    elapsed = time.perf_counter() - start

    total_ms = elapsed * 1000
    avg_us = (elapsed / iterations) * 1_000_000
    ops_per_sec = iterations / elapsed if elapsed > 0 else float("inf")

    return BenchResult(
        name=name,
        operations=iterations,
        total_ms=round(total_ms, 2),
        avg_us=round(avg_us, 2),
        ops_per_sec=round(ops_per_sec, 0),
    )


# ---------------------------------------------------------------------------
# Fábrica de clientes Redis (fakeredis o real)
# ---------------------------------------------------------------------------


def _make_redis():
    """Crea un cliente Redis (fakeredis o real según configuración)."""
    if USE_REAL_REDIS:
        import redis

        return redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=False)
    else:
        import fakeredis

        return fakeredis.FakeStrictRedis(decode_responses=False)


def _make_async_redis():
    """Crea un cliente Redis asíncrono (fakeredis o real)."""
    if USE_REAL_REDIS:
        import redis.asyncio as aredis

        return aredis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=False)
    else:
        import fakeredis

        return fakeredis.FakeAsyncRedis(decode_responses=False)


def _flush(r):
    """Limpia todas las claves antes/después de cada benchmark."""
    try:
        r.flushdb()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# 1. Bitmap Manager
# ---------------------------------------------------------------------------


def bench_bitmap_sync() -> list[BenchResult]:
    """Benchmark del RedisBitmapManager en modo síncrono."""
    from wredis.bitmap import RedisBitmapManager

    r = _make_redis()
    _flush(r)
    bm = RedisBitmapManager(verbose=False)
    bm.redis_client = r  # Usar fakeredis directamente

    results = []

    def op_set_bit():
        bm.set_bit("bench:bitmap", 42, 1)

    results.append(measure(op_set_bit, _name="Bitmap: set_bit", _iterations=ITERATIONS))

    def op_get_bit():
        bm.get_bit("bench:bitmap", 42)

    results.append(measure(op_get_bit, _name="Bitmap: get_bit", _iterations=ITERATIONS))

    def op_count_bits():
        bm.count_bits("bench:bitmap")

    results.append(measure(op_count_bits, _name="Bitmap: count_bits", _iterations=ITERATIONS))

    _flush(r)
    return results


# ---------------------------------------------------------------------------
# 2. Hash Manager — Sync vs Async
# ---------------------------------------------------------------------------


def bench_hash_sync() -> list[BenchResult]:
    """Benchmark del RedisHashManager en modo síncrono."""
    from wredis.hash import RedisHashManager

    r = _make_redis()
    _flush(r)
    hm = RedisHashManager(verbose=False)
    hm.redis_client = r

    results = []

    def op_create():
        hm.create_hash("bench:hash", "field_1", {"data": "value"})

    results.append(measure(op_create, _name="Hash sync: create_hash", _iterations=ITERATIONS))

    def op_read():
        hm.read_hash("bench:hash", "field_1")

    results.append(measure(op_read, _name="Hash sync: read_hash", _iterations=ITERATIONS))

    def op_read_all():
        hm.read_all_hash("bench:hash")

    results.append(measure(op_read_all, _name="Hash sync: read_all_hash", _iterations=ITERATIONS // 5))

    _flush(r)
    return results


async def bench_hash_async() -> list[BenchResult]:
    """Benchmark del RedisHashManager en modo asíncrono (directo con redis.asyncio)."""
    r = _make_async_redis()
    _flush(r)

    results = []

    async def op_create():
        await r.hset("bench:async_hash", "field_1", '{"data": "value"}')

    results.append(await measure_async(op_create, _name="Hash async: hset", _iterations=ITERATIONS))

    async def op_read():
        await r.hget("bench:async_hash", "field_1")

    results.append(await measure_async(op_read, _name="Hash async: hget", _iterations=ITERATIONS))

    async def op_getall():
        await r.hgetall("bench:async_hash")

    results.append(await measure_async(op_getall, _name="Hash async: hgetall", _iterations=ITERATIONS // 5))

    _flush(r)
    return results


# ---------------------------------------------------------------------------
# 3. Set Manager
# ---------------------------------------------------------------------------


def bench_sets_sync() -> list[BenchResult]:
    """Benchmark del RedisSetManager en modo síncrono."""
    from wredis.sets import RedisSetManager

    r = _make_redis()
    _flush(r)
    sm = RedisSetManager(verbose=False)
    sm.redis_client = r

    results = []

    def op_add():
        sm.add_to_set("bench:set", "member_1")

    results.append(measure(op_add, _name="Set sync: add_to_set", _iterations=ITERATIONS))

    def op_is_member():
        sm.is_member("bench:set", "member_1")

    results.append(measure(op_is_member, _name="Set sync: is_member", _iterations=ITERATIONS))

    def op_members():
        sm.get_set_members("bench:set")

    results.append(measure(op_members, _name="Set sync: get_members", _iterations=ITERATIONS // 5))

    _flush(r)
    return results


# ---------------------------------------------------------------------------
# 4. SortedSet Manager
# ---------------------------------------------------------------------------


def bench_sortedset_sync() -> list[BenchResult]:
    """Benchmark del RedisSortedSetManager en modo síncrono."""
    from wredis.sortedset import RedisSortedSetManager

    r = _make_redis()
    _flush(r)
    ssm = RedisSortedSetManager(verbose=False)
    ssm.redis_client = r

    results = []

    def op_add():
        ssm.add_to_sorted_set("bench:zset", 1.0, "member_1")

    results.append(measure(op_add, _name="SortedSet sync: add", _iterations=ITERATIONS))

    def op_get():
        ssm.get_sorted_set("bench:zset")

    results.append(measure(op_get, _name="SortedSet sync: get", _iterations=ITERATIONS // 5))

    def op_score():
        ssm.get_score("bench:zset", "member_1")

    results.append(measure(op_score, _name="SortedSet sync: get_score", _iterations=ITERATIONS))

    _flush(r)
    return results


# ---------------------------------------------------------------------------
# 5. Pipeline Manager — Single vs Batch
# ---------------------------------------------------------------------------


def bench_pipeline() -> list[BenchResult]:
    """Benchmark del RedisPipelineManager comparando operaciones individuales vs por lotes."""
    from wredis.pipeline import RedisPipelineManager

    r = _make_redis()
    _flush(r)
    pm = RedisPipelineManager(verbose=False)
    pm.redis_client = r

    results = []

    # Operaciones individuales (sin pipeline)
    def op_single_set():
        r.set("bench:pipe:single:1", "value")

    results.append(measure(op_single_set, _name="Pipeline: single SET x1", _iterations=ITERATIONS))

    # Operaciones por lote con pipeline (100 claves)
    batch_size = 100

    def op_batch_mset():
        mapping = {f"bench:pipe:batch:{i}": f"value_{i}" for i in range(batch_size)}
        pm.mset_pipeline(mapping)

    results.append(measure(op_batch_mset, _name=f"Pipeline: mset_pipeline x{batch_size}", _iterations=ITERATIONS // 10))

    # Pipeline de GETs múltiples
    def op_batch_mget():
        # Primero llenar claves
        pipe = r.pipeline()
        for i in range(batch_size):
            pipe.set(f"bench:pipe:batch:{i}", f"value_{i}")
        pipe.execute()
        pm.mget_pipeline(*[f"bench:pipe:batch:{i}" for i in range(batch_size)])

    results.append(measure(op_batch_mget, _name=f"Pipeline: mget_pipeline x{batch_size}", _iterations=ITERATIONS // 10))

    _flush(r)
    return results


# ---------------------------------------------------------------------------
# 6. Transaction Manager
# ---------------------------------------------------------------------------


def bench_transaction() -> list[BenchResult]:
    """Benchmark del RedisTransactionManager."""
    from wredis.transaction import RedisTransactionManager

    r = _make_redis()
    _flush(r)
    tm = RedisTransactionManager(verbose=False)
    tm.redis_client = r

    results = []

    def op_execute():
        tm.execute_transaction([("set", ["bench:txn:key", "value"])])

    results.append(measure(op_execute, _name="Transaction: execute_transaction", _iterations=ITERATIONS))

    def op_set_nx():
        tm.set_if_not_exists("bench:txn:nx", "value")

    results.append(measure(op_set_nx, _name="Transaction: set_if_not_exists", _iterations=ITERATIONS))

    def op_incr():
        tm.increment_atomic("bench:txn:counter")

    results.append(measure(op_incr, _name="Transaction: increment_atomic", _iterations=ITERATIONS))

    _flush(r)
    return results


# ---------------------------------------------------------------------------
# 7. Geo Manager
# ---------------------------------------------------------------------------


def bench_geo() -> list[BenchResult]:
    """Benchmark del RedisGeoManager."""
    from wredis.geo import RedisGeoManager

    r = _make_redis()
    _flush(r)
    gm = RedisGeoManager(verbose=False)
    gm.redis_client = r

    results = []

    def op_add_location():
        gm.add_location("bench:geo", "Palermo", 13.361389, 38.115556)

    results.append(measure(op_add_location, _name="Geo: add_location", _iterations=ITERATIONS // 2))

    def op_distance():
        gm.get_distance("bench:geo", "Palermo", "Palermo")

    results.append(measure(op_distance, _name="Geo: get_distance", _iterations=ITERATIONS // 2))

    _flush(r)
    return results


# ---------------------------------------------------------------------------
# 8. HyperLogLog Manager
# ---------------------------------------------------------------------------


def bench_hyperloglog() -> list[BenchResult]:
    """Benchmark del RedisHyperLogLogManager."""
    from wredis.hyperloglog import RedisHyperLogLogManager

    r = _make_redis()
    _flush(r)
    hll = RedisHyperLogLogManager(verbose=False)
    hll.redis_client = r

    results = []

    def op_add():
        hll.add("bench:hll", f"user_{time.monotonic_ns()}")

    results.append(measure(op_add, _name="HyperLogLog: add", _iterations=ITERATIONS))

    def op_count():
        hll.count("bench:hll")

    results.append(measure(op_count, _name="HyperLogLog: count", _iterations=ITERATIONS))

    _flush(r)
    return results


# ---------------------------------------------------------------------------
# 9. PubSub Manager
# ---------------------------------------------------------------------------


def bench_pubsub() -> list[BenchResult]:
    """Benchmark del RedisPubSubManager (solo publish, sin listeners)."""
    from wredis.pubsub import RedisPubSubManager

    r = _make_redis()
    _flush(r)
    ps = RedisPubSubManager(verbose=False)
    ps.redis_client = r

    results = []

    def op_publish():
        ps.publish_message("bench:pubsub", {"msg": "hello"})

    results.append(measure(op_publish, _name="PubSub: publish_message", _iterations=ITERATIONS))

    _flush(r)
    return results


# ---------------------------------------------------------------------------
# 10. Queue Manager
# ---------------------------------------------------------------------------


def bench_queue() -> list[BenchResult]:
    """Benchmark del RedisQueueManager (solo publish)."""
    from wredis.queue import RedisQueueManager

    r = _make_redis()
    _flush(r)
    qm = RedisQueueManager(verbose=False)
    qm.redis_client = r

    results = []

    def op_publish():
        qm.publish("bench:queue", {"data": "test"})

    results.append(measure(op_publish, _name="Queue: publish", _iterations=ITERATIONS))

    def op_length():
        qm.get_queue_length("bench:queue")

    results.append(measure(op_length, _name="Queue: get_queue_length", _iterations=ITERATIONS))

    _flush(r)
    return results


# ---------------------------------------------------------------------------
# 11. Stream Manager
# ---------------------------------------------------------------------------


def bench_streams() -> list[BenchResult]:
    """Benchmark del RedisStreamManager (solo add)."""
    from wredis.streams import RedisStreamManager

    r = _make_redis()
    _flush(r)
    stm = RedisStreamManager(verbose=False)
    stm.redis_client = r

    results = []

    def op_add():
        stm.add_to_stream("bench:stream", {"field": "value"})

    results.append(measure(op_add, _name="Stream: add_to_stream", _iterations=ITERATIONS // 2))

    _flush(r)
    return results


# ---------------------------------------------------------------------------
# 12. Cache Decorator Overhead
# ---------------------------------------------------------------------------


def bench_cache_decorator() -> list[BenchResult]:
    """Benchmark del decorador @cache comparando miss vs hit."""
    import redis

    from wredis.decorators import CacheMetrics, cache

    r = _make_redis()
    _flush(r)
    metrics = CacheMetrics()

    results = []

    # Función base sin decorador
    def raw_function(x):
        return x * 2

    results.append(measure(lambda: raw_function(42), _name="Cache: raw function call", _iterations=ITERATIONS * 10))

    # Función con decorador @cache — siempre miss (clave nueva cada vez)
    miss_counter = {"i": 0}

    @cache(ttl=60, prefix="bench:cache:miss", redis_client=r, metrics=metrics)
    def cached_miss():
        miss_counter["i"] += 1
        return miss_counter["i"]

    def op_cache_miss():
        cached_miss()

    results.append(measure(op_cache_miss, _name="Cache: @cache MISS", _iterations=ITERATIONS))

    # Función con decorador @cache — siempre hit (misma clave)
    hit_counter = {"i": 0}

    @cache(ttl=60, prefix="bench:cache:hit", redis_client=r, metrics=metrics)
    def cached_hit():
        hit_counter["i"] += 1
        return hit_counter["i"]

    # Primera llamada (miss) para poblar el caché
    cached_hit()
    metrics.reset()

    def op_cache_hit():
        cached_hit()

    results.append(measure(op_cache_hit, _name="Cache: @cache HIT", _iterations=ITERATIONS))

    _flush(r)
    return results


# ---------------------------------------------------------------------------
# 13. Connection Pool Impact
# ---------------------------------------------------------------------------


def bench_connection_pool() -> list[BenchResult]:
    """Benchmark del impacto del tamaño del pool de conexiones."""
    import redis

    from wredis.hash import RedisHashManager

    r_base = _make_redis()
    _flush(r_base)

    results = []

    for pool_size in [1, 5, 10, 50]:
        # Crear manager con pool específico
        hm = RedisHashManager(verbose=False)
        hm.redis_client = redis.StrictRedis(
            connection_pool=redis.ConnectionPool(
                max_connections=pool_size,
                decode_responses=False,
            )
        )
        # Redirigir al fakeredis
        hm.redis_client = r_base

        def op_create():
            hm.create_hash("bench:pool", "f", {"v": "x"})

        res = measure(op_create, _name=f"Pool size={pool_size}: create_hash", _iterations=ITERATIONS)
        results.append(res)

    _flush(r_base)
    return results


# ---------------------------------------------------------------------------
# 14. Direct redis-py vs wredis wrapper
# ---------------------------------------------------------------------------


def bench_direct_vs_wrapper() -> list[BenchResult]:
    """Comparación directa entre redis-py puro y los wrappers de wredis."""
    from wredis.hash import RedisHashManager
    from wredis.sets import RedisSetManager

    r = _make_redis()
    _flush(r)

    results = []

    # Directo vs wrapper — SET
    def direct_set():
        r.set("bench:direct:set", "value")

    results.append(measure(direct_set, _name="Direct redis-py: SET", _iterations=ITERATIONS))

    hm = RedisHashManager(verbose=False)
    hm.redis_client = r

    def wrapper_hset():
        hm.create_hash("bench:wrapper:hash", "key", {"data": "value"})

    results.append(measure(wrapper_hset, _name="wredis wrapper: create_hash", _iterations=ITERATIONS))

    # Directo vs wrapper — SADD
    def direct_sadd():
        r.sadd("bench:direct:sadd", "member")

    results.append(measure(direct_sadd, _name="Direct redis-py: SADD", _iterations=ITERATIONS))

    sm = RedisSetManager(verbose=False)
    sm.redis_client = r

    def wrapper_sadd():
        sm.add_to_set("bench:wrapper:set", "member")

    results.append(measure(wrapper_sadd, _name="wredis wrapper: add_to_set", _iterations=ITERATIONS))

    _flush(r)
    return results


# ---------------------------------------------------------------------------
# Formateo de resultados
# ---------------------------------------------------------------------------


def print_table(title: str, results: list[BenchResult]) -> None:
    """Imprime una tabla formateada con los resultados del benchmark."""
    width = 90
    print(f"\n{'=' * width}")
    print(f"  {title}")
    print(f"{'=' * width}")

    header = f"{'Benchmark':<45} {'Ops':>8} {'Total (ms)':>12} {'Avg (µs)':>12} {'Ops/s':>12}"
    print(header)
    print(f"{'-' * width}")

    for r in results:
        ops_str = f"{r.operations:,}"
        total_str = f"{r.total_ms:,.1f}"
        avg_str = f"{r.avg_us:,.1f}"
        ops_sec = f"{r.ops_per_sec:,.0f}"
        print(f"{r.name:<45} {ops_str:>8} {total_str:>12} {avg_str:>12} {ops_sec:>12}")

    print(f"{'=' * width}")


def print_summary(all_results: dict[str, list[BenchResult]]) -> None:
    """Imprime un resumen general de todos los benchmarks."""
    width = 90
    print(f"\n{'=' * width}")
    print("  RESUMEN GENERAL — WREDIS BENCHMARKS")
    print(f"{'=' * width}")
    print(f"  Iteraciones por operación: {ITERATIONS:,}")
    print(f"  Backend: {'Redis real' if USE_REAL_REDIS else 'fakeredis (in-memory)'}")
    print(f"  Host: {REDIS_HOST}:{REDIS_PORT}")
    print(f"{'=' * width}")

    for title, results in all_results.items():
        print_table(title, results)


# ---------------------------------------------------------------------------
# Ejecución principal
# ---------------------------------------------------------------------------


def main() -> None:
    """Ejecuta todos los benchmarks e imprime los resultados."""
    import argparse

    global ITERATIONS

    parser = argparse.ArgumentParser(description="Benchmarks para wredis")
    parser.add_argument(
        "--iterations",
        type=int,
        default=ITERATIONS,
        help=f"Número de iteraciones por benchmark (default: {ITERATIONS})",
    )
    args = parser.parse_args()

    ITERATIONS = args.iterations

    all_results: dict[str, list[BenchResult]] = {}

    print(f"\n  Iniciando benchmarks con {ITERATIONS:,} iteraciones...")
    print(f"  Backend: {'Redis real' if USE_REAL_REDIS else 'fakeredis'}")

    # 1. Bitmap
    print("  [1/14] Bitmap Manager...")
    all_results["Bitmap Manager (sync)"] = bench_bitmap_sync()

    # 2. Hash Sync
    print("  [2/14] Hash Manager (sync)...")
    all_results["Hash Manager (sync)"] = bench_hash_sync()

    # 3. Hash Async
    print("  [3/14] Hash Manager (async)...")
    all_results["Hash Manager (async)"] = asyncio.run(bench_hash_async())

    # 4. Set Manager
    print("  [4/14] Set Manager...")
    all_results["Set Manager (sync)"] = bench_sets_sync()

    # 5. SortedSet Manager
    print("  [5/14] SortedSet Manager...")
    all_results["SortedSet Manager (sync)"] = bench_sortedset_sync()

    # 6. Pipeline — Single vs Batch
    print("  [6/14] Pipeline (single vs batch)...")
    all_results["Pipeline (single vs batch)"] = bench_pipeline()

    # 7. Transaction Manager
    print("  [7/14] Transaction Manager...")
    all_results["Transaction Manager"] = bench_transaction()

    # 8. Geo Manager
    print("  [8/14] Geo Manager...")
    all_results["Geo Manager"] = bench_geo()

    # 9. HyperLogLog Manager
    print("  [9/14] HyperLogLog Manager...")
    all_results["HyperLogLog Manager"] = bench_hyperloglog()

    # 10. PubSub Manager
    print("  [10/14] PubSub Manager...")
    all_results["PubSub Manager"] = bench_pubsub()

    # 11. Queue Manager
    print("  [11/14] Queue Manager...")
    all_results["Queue Manager"] = bench_queue()

    # 12. Stream Manager
    print("  [12/14] Stream Manager...")
    all_results["Stream Manager"] = bench_streams()

    # 13. Cache Decorator
    print("  [13/14] Cache Decorator overhead...")
    all_results["Cache Decorator"] = bench_cache_decorator()

    # 14. Connection Pool Impact
    print("  [14/14] Connection Pool impact...")
    all_results["Connection Pool Impact"] = bench_connection_pool()

    # Extra: Direct vs Wrapper
    print("  [EXTRA] Direct redis-py vs wredis wrapper...")
    all_results["Direct redis-py vs wredis wrapper"] = bench_direct_vs_wrapper()

    # Imprimir resumen
    print_summary(all_results)

    print(f"\n  Benchmarks completados.")


if __name__ == "__main__":
    main()
