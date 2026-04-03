"""15 - Integración completa con FastAPI (avanzado)

Este ejemplo muestra una integración más completa con FastAPI,
incluyendo middleware de rate limiting, caché de respuestas y
gestión de sesiones, todo gestionado por AsyncBaseManager.
"""

import asyncio
import json
import time
from contextlib import asynccontextmanager
from typing import Any, Dict

import fakeredis.aioredis
from wredis._async_base import AsyncBaseManager

# Instancia global del manager
redis_manager: AsyncBaseManager | None = None
_fake_redis: Any = None


# --- Componentes simulados de FastAPI ---


class SimulatedRequest:
    """Simula una petición HTTP."""

    def __init__(self, method: str, path: str, client_ip: str):
        self.method = method
        self.path = path
        self.client_ip = client_ip


async def rate_limit_middleware(request: SimulatedRequest) -> dict | None:
    """Middleware de rate limiting."""
    global redis_manager
    if redis_manager is None:
        return None

    key = f"ratelimit:{request.client_ip}"
    ahora = time.time()
    ventana = 60
    max_req = 10

    await redis_manager._execute("zremrangebyscore", key, 0, ahora - ventana)
    contador = await redis_manager._execute("zcard", key)

    if contador >= max_req:
        return {"status": 429, "body": {"error": "Demasiadas peticiones"}}

    await redis_manager._execute("zadd", key, {str(ahora): ahora})
    await redis_manager._execute("expire", key, ventana)
    return None


async def cache_middleware(request: SimulatedRequest) -> dict | None:
    """Middleware de caché para peticiones GET."""
    global redis_manager
    if redis_manager is None or request.method != "GET":
        return None

    cache_key = f"cache:{request.method}:{request.path}"
    cached = await redis_manager._execute("get", cache_key)
    if cached:
        return {"status": 200, "body": json.loads(cached), "cached": True}
    return None


async def store_cache(request: SimulatedRequest, response: dict):
    """Almacena respuesta en caché."""
    global redis_manager
    if redis_manager is None or request.method != "GET":
        return

    cache_key = f"cache:{request.method}:{request.path}"
    await redis_manager._execute("set", cache_key, json.dumps(response), ex=120)


async def handle_request(request: SimulatedRequest) -> dict:
    """Simula el handler de FastAPI con middleware."""
    # 1. Rate limiting
    rate_limit_response = await rate_limit_middleware(request)
    if rate_limit_response:
        return rate_limit_response

    # 2. Cache check
    cached_response = await cache_middleware(request)
    if cached_response:
        return cached_response

    # 3. Procesamiento real (simulado)
    response_data = {
        "path": request.path,
        "timestamp": time.time(),
        "data": f"Contenido de {request.path}",
    }

    # 4. Almacenar en caché
    await store_cache(request, response_data)

    return {"status": 200, "body": response_data, "cached": False}


@asynccontextmanager
async def app_lifespan():
    """Gestiona el ciclo de vida de la aplicación."""
    global redis_manager, _fake_redis
    _fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    redis_manager = AsyncBaseManager(verbose=False)
    redis_manager.redis_client = _fake_redis
    conectado = await redis_manager.health_check()
    print(f"App startup - Redis: {'conectado' if conectado else 'fallo'}")
    yield
    if redis_manager:
        await redis_manager.close()
        await _fake_redis.aclose()
        print("App shutdown - Redis desconectado")


async def main():
    """Simula el flujo completo de FastAPI con middleware."""
    async with app_lifespan():
        # Simulamos varias peticiones
        peticiones = [
            SimulatedRequest("GET", "/api/usuarios", "192.168.1.100"),
            SimulatedRequest("GET", "/api/usuarios", "192.168.1.100"),  # Debe venir de cache
            SimulatedRequest("POST", "/api/usuarios", "192.168.1.100"),  # POST no se cachea
            SimulatedRequest("GET", "/api/productos", "192.168.1.200"),  # Otro cliente
            SimulatedRequest("GET", "/api/productos", "192.168.1.200"),  # Debe venir de cache
        ]

        for i, req in enumerate(peticiones, 1):
            print(f"\n=== Petición {i}: {req.method} {req.path} ({req.client_ip}) ===")
            respuesta = await handle_request(req)

            if respuesta.get("cached"):
                print(f"  [CACHE] Respuesta cacheada")
            else:
                print(f"  [NUEVA] Respuesta generada")

            print(f"  Status: {respuesta['status']}")
            body = respuesta.get("body", {})
            if "error" in body:
                print(f"  Error: {body['error']}")
            elif "data" in body:
                print(f"  Data: {body['data']}")

        # Resumen de estado en Redis
        print("\n=== Estado de Redis ===")
        claves = await redis_manager._execute("keys", "*")  # type: ignore[union-attr]
        print(f"  Claves activas: {len(claves)}")
        for clave in sorted(claves):
            ttl = await redis_manager._execute("ttl", clave)  # type: ignore[union-attr]
            print(f"    {clave} (TTL: {ttl}s)")

    print("\nIntegración FastAPI avanzada completada")


if __name__ == "__main__":
    asyncio.run(main())
