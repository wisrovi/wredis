# 🗺️ WRedis Roadmap → LTS v1.0.0

> **Objetivo:** Convertir WRedis de un wrapper de conexión a un **Gestor de Estado Inteligente** con resiliencia empresarial, manteniendo **cero breaking changes** para los 32,000+ usuarios existentes.

---

## 📊 Estado Actual

| Métrica | Valor | Meta LTS |
|---------|-------|----------|
| Versión | `0.1.2` | `1.0.0` |
| Python | `>=3.8` | `>=3.10` |
| Tests | `0` | `95%+ coverage` |
| Módulos | `7 sync` | `7 sync + 7 async + HA` |
| Ruff errors | `10` | `0` |
| CI/CD | `Ninguno` | `test + publish + pages` |
| Documentación | `README básico` | `Completa + sitio web` |

---

## FASE 0: Calidad de Código — Ruff = 0 Errores

> **Prioridad:** 🔴 Crítica | **Tiempo estimado:** 1 día

### Problemas Actuales

| Error | Archivo | Línea | Fix |
|-------|---------|-------|-----|
| `F811` | `examples/queue/consumer.py` | 9, 20, 31 | Renombrar `worker` duplicados |
| `F403` | `wredis/__init__.py` | 1 | Imports explícitos + `__all__` |
| `F401` | `wredis/bitmap/__init__.py` | 1 | `as RedisBitmapManager` |
| `F401` | `wredis/hash/__init__.py` | 1 | `as RedisHashManager` |
| `F401` | `wredis/pubsub/__init__.py` | 1 | `as RedisPubSubManager` |
| `F401` | `wredis/queue/__init__.py` | 1 | `as RedisQueueManager` |
| `F401` | `wredis/sets/__init__.py` | 1 | `as RedisSetManager` |
| `F401` | `wredis/sortedset/__init__.py` | 1 | `as RedisSortedSetManager` |
| `F401` | `wredis/streams/__init__.py` | 1 | `as RedisStreamManager` |

### Entregables

- [ ] Crear `.ruff.toml` con reglas estrictas
- [ ] Crear `.editorconfig` para consistencia
- [ ] Fix todos los `__init__.py` con re-exports explícitos
- [ ] Fix `examples/queue/consumer.py` — renombrar funciones duplicadas
- [ ] Verificar: `ruff check .` retorna 0 errores
- [ ] Verificar: `ruff format --check .` retorna 0 errores

---

## FASE 1: Restructuración del Proyecto

> **Prioridad:** 🔴 Crítica | **Tiempo estimado:** 1 día

### Cambios de Estructura

- [ ] Migrar a `src/` layout (PyPA recommended)
  - `wredis/` → `src/wredis/`
  - Zero breaking changes: `from wredis.bitmap import RedisBitmapManager` sigue funcionando
- [ ] Renombrar `examples/sorted_set.py/` → `examples/sorted_set/`
- [ ] Eliminar `setup.py` (duplicado con hatchling)
- [ ] Limpiar `requirements.txt` (quitar `toml` innecesario)
- [ ] Mover `installer.sh` → `scripts/install.sh`
- [ ] Mover `publish.sh` → `scripts/publish.sh`

### Actualizar `pyproject.toml`

- [ ] `requires-python = ">=3.10"` (3.8/3.9 son EOL)
- [ ] Añadir dev dependencies: `pytest`, `pytest-asyncio`, `pytest-cov`, `fakeredis`, `mypy`
- [ ] Configurar `[tool.pytest.ini_options]` con coverage mínimo 95%
- [ ] Configurar `[tool.coverage.run]` con source = `wredis`
- [ ] Unificar classifiers y metadata

### Verificación

- [ ] `pip install -e .` funciona
- [ ] Todos los imports existentes funcionan sin cambios
- [ ] `python -c "from wredis.bitmap import RedisBitmapManager; print('OK')"`

---

## FASE 2: Core Infrastructure

> **Prioridad:** 🟠 Alta | **Tiempo estimado:** 2 días

### `src/wredis/_types.py`

- [ ] Type aliases: `RedisValue`, `Callback`, `AsyncCallback`, `TTL`
- [ ] TypeVars genéricos para métodos reutilizables

### `src/wredis/_exceptions.py`

- [ ] `WRedisError(Exception)` — Base exception
- [ ] `ConnectionError(WRedisError)` — Fallos de conexión
- [ ] `SerializationError(WRedisError)` — Fallos de JSON
- [ ] `CacheError(WRedisError)` — Fallos de caché
- [ ] `SentinelError(WRedisError)` — Fallos de Sentinel
- [ ] `ClusterError(WRedisError)` — Fallos de Cluster

### `src/wredis/_connection.py`

- [ ] `create_sync_client()` — Factory para conexiones síncronas
- [ ] `create_async_client()` — Factory para conexiones asíncronas
- [ ] `create_sentinel_client()` — Factory para Sentinel
- [ ] `create_cluster_client()` — Factory para Cluster
- [ ] Soporte para: `password`, `ssl`, `socket_timeout`, `retry_on_timeout`
- [ ] Connection pooling reutilizable

### Tests

- [ ] `tests/test_exceptions.py` — Cada excepción
- [ ] `tests/test_connection.py` — Cada factory

---

## FASE 3: AsyncRedis (`src/wredis/async/`)

> **Prioridad:** 🟠 Alta | **Tiempo estimado:** 4 días

### Managers Asíncronos (usando `redis.asyncio`)

| Archivo | Clase | Métodos |
|---------|-------|---------|
| `async/bitmap.py` | `AsyncRedisBitmapManager` | `set_bit`, `get_bit`, `count_bits`, `get_ttl`, `extend_ttl` |
| `async/hash.py` | `AsyncRedisHashManager` | `create_hash`, `read_hash`, `update_hash`, `delete_hash_field`, `read_all_hash`, `get_ttl`, `extend_ttl` |
| `async/pubsub.py` | `AsyncRedisPubSubManager` | `publish_message`, `on_message`, `stop_listeners` |
| `async/queue.py` | `AsyncRedisQueueManager` | `publish`, `on_message`, `start`, `stop`, `wait`, `get_queue_length` |
| `async/sets.py` | `AsyncRedisSetManager` | `add_to_set`, `get_set_members`, `is_member`, `remove_from_set`, `get_ttl`, `extend_ttl` |
| `async/sortedset.py` | `AsyncRedisSortedSetManager` | `add_to_sorted_set`, `get_sorted_set`, `get_sorted_set_reverse`, `remove_from_sorted_set`, `get_rank`, `get_score`, `delete_sorted_set`, `set_ttl`, `get_ttl`, `increment_score`, `get_sorted_set_by_score` |
| `async/streams.py` | `AsyncRedisStreamManager` | `add_to_stream`, `on_message`, `read_from_stream`, `wait` |
| `async/__init__.py` | Exports | `__all__` con re-exports explícitos |

### Ejemplos (14 archivos)

- [ ] `examples/async_bitmap/read.py`, `write.py`
- [ ] `examples/async_hash/read.py`, `write.py`
- [ ] `examples/async_pubsub/consumer.py`, `producer.py`
- [ ] `examples/async_queue/consumer.py`, `producer.py`
- [ ] `examples/async_sets/read.py`, `write.py`
- [ ] `examples/async_sortedset/read.py`, `write.py`
- [ ] `examples/async_streams/consume.py`, `producer.py`

### Tests

- [ ] `tests/test_async/test_async_bitmap.py`
- [ ] `tests/test_async/test_async_hash.py`
- [ ] `tests/test_async/test_async_queue.py`
- [ ] `tests/test_async/test_async_streams.py`
- [ ] Todos con `pytest-asyncio`
- [ ] Coverage 95%+ por módulo

---

## FASE 4: Decoradores de Caché (`src/wredis/decorators.py`)

> **Prioridad:** 🟠 Alta | **Tiempo estimado:** 2 días

### Decoradores

- [ ] `@cache(ttl=300, prefix="wredis", key_builder=None, redis_client=None)`
  - Cache-Aside para funciones síncronas
  - Si el resultado está en Redis → lo devuelve
  - Si no → ejecuta la función, guarda en Redis, devuelve
- [ ] `@async_cache(ttl=300, prefix="wredis", redis_client=None)`
  - Versión asíncrona para FastAPI / agentes IA
- [ ] `@invalidate_cache(pattern, redis_client=None)`
  - Invalidación selectiva por patrón glob
- [ ] `clear_cache(pattern, redis_client=None)` — Función utilitaria

### Features

- [ ] Key builder automático a partir de argumentos de la función
- [ ] Soporte para Pydantic models como parte de la key
- [ ] Serialización automática de resultados (dict, list, str, int, float)
- [ ] TTL configurable por decorador
- [ ] Logging de cache hit/miss

### Ejemplos (4 archivos)

- [ ] `examples/decorators/cache_basic.py` — Uso simple
- [ ] `examples/decorators/cache_with_ttl.py` — Con expiración
- [ ] `examples/decorators/cache_invalidation.py` — Invalidación manual
- [ ] `examples/decorators/async_cache.py` — Con FastAPI

### Tests

- [ ] `tests/test_decorators.py` — Todos los decoradores
- [ ] Tests de cache hit/miss
- [ ] Tests de invalidación
- [ ] Tests async

---

## FASE 5: Funciones de Conveniencia (`src/wredis/__init__.py`)

> **Prioridad:** 🟡 Media | **Tiempo estimado:** 1 día

### API Simplificada (Top-Level)

- [ ] `publish(channel, message, host="localhost", port=6379)` — Pub/Sub sin boilerplate
- [ ] `subscribe(channel, callback, host="localhost", port=6379)` — Listener simplificado
- [ ] `enqueue(queue_name, data, host="localhost", port=6379, ttl=-1)` — Queue simplificado
- [ ] `xadd(stream_name, data, host="localhost", port=6379)` — Stream simplificado

### Internamente

- Cada función instancia el manager correspondiente
- Cero duplicación de código
- Zero breaking changes

### Ejemplos (4 archivos)

- [ ] `examples/simple_pubsub/publisher.py`
- [ ] `examples/simple_pubsub/subscriber.py`
- [ ] `examples/simple_streams/producer.py`
- [ ] `examples/simple_streams/consumer.py`

### Tests

- [ ] Tests para cada función de conveniencia

---

## FASE 6: Sentinel/Cluster (`src/wredis/ha/`)

> **Prioridad:** 🟡 Media | **Tiempo estimado:** 3 días

### `src/wredis/ha/sentinel.py`

- [ ] `SentinelRedisManager` — Manager con failover automático
- [ ] Constructor: `sentinel_nodes`, `service_name`, `password`, `socket_timeout`
- [ ] Detección automática de master
- [ ] Reconexión automática tras failover
- [ ] Mismos métodos que los managers base (para consistencia de API)

### `src/wredis/ha/cluster.py`

- [ ] `ClusterRedisManager` — Manager para Redis Cluster
- [ ] Constructor: `startup_nodes`, `password`, `ssl`
- [ ] Hash slot routing automático
- [ ] Redirección MOVED/ASK automática
- [ ] Mismos métodos que los managers base

### `src/wredis/ha/__init__.py`

- [ ] Re-exports explícitos con `__all__`

### Docker Compose (ya creados)

- [x] `enviroment/docker-compose.cluster.yml` — 6 nodos (3M + 3R)
- [x] `enviroment/docker-compose.sentinel.yml` — 1M + 2R + 3S
- [x] Configs de Redis para todos los nodos
- [x] Makefile con comandos: `cluster-start`, `sentinel-start`, etc.

### Ejemplos (4 archivos)

- [ ] `examples/sentinel/basic.py` — Conexión básica
- [ ] `examples/sentinel/failover_demo.py` — Demo de failover
- [ ] `examples/cluster/basic.py` — Conexión básica
- [ ] `examples/cluster/multi_node.py` — Operaciones multi-nodo

### Tests

- [ ] `tests/test_ha/test_sentinel.py`
- [ ] `tests/test_ha/test_cluster.py`

---

## FASE 7: Serialización Automática

> **Prioridad:** 🟡 Media | **Tiempo estimado:** 2 días

### Métodos Nuevos en Cada Manager (sin modificar existentes)

| Método | Descripción |
|--------|-------------|
| `set_json(key, value, ttl=-1)` | Serializa dict/list a JSON y guarda |
| `get_json(key)` | Lee de Redis y deserializa desde JSON |
| `delete_key(key)` | Elimina cualquier key (faltaba en varios managers) |

### Managers a Actualizar

- [ ] `bitmap/bitmap.py`
- [ ] `hash/hash.py`
- [ ] `pubsub/pupsub.py`
- [ ] `queue/queue.py`
- [ ] `sets/sets.py`
- [ ] `sortedset/sortedset.py`
- [ ] `streams/streams.py`
- [ ] Todos los managers async también

### Ejemplos (3 archivos)

- [ ] `examples/serialization/json_basic.py`
- [ ] `examples/serialization/pydantic_integration.py`
- [ ] `examples/serialization/nested_objects.py`

### Tests

- [ ] `tests/test_serialization.py` — Todos los métodos nuevos
- [ ] Tests con objetos anidados
- [ ] Tests con Pydantic models
- [ ] Tests de edge cases (None, empty dict, etc.)

---

## FASE 8: Tests — 95%+ Coverage

> **Prioridad:** 🔴 Crítica | **Tiempo estimado:** 5 días

### Estructura de Tests

```
tests/
├── conftest.py                  # Fixtures: redis_client, fakeredis_client, async_redis_client
├── __init__.py
├── test_bitmap.py
├── test_hash.py
├── test_pubsub.py
├── test_queue.py
├── test_sets.py
├── test_sortedset.py
├── test_streams.py
├── test_decorators.py
├── test_serialization.py
├── test_async/
│   ├── __init__.py
│   ├── test_async_bitmap.py
│   ├── test_async_hash.py
│   ├── test_async_queue.py
│   └── test_async_streams.py
├── test_ha/
│   ├── __init__.py
│   ├── test_sentinel.py
│   └── test_cluster.py
└── test_integration/
    ├── __init__.py
    └── test_end_to_end.py
```

### Estrategia

- [ ] `conftest.py` con fixtures parametrizados:
  - `redis_client` → Redis real via Docker
  - `fakeredis_client` → fakeredis fallback (para CI sin Docker)
  - `async_redis_client` → Async Redis real
- [ ] Tests de regresión para cada método existente
- [ ] Tests de integración contra Redis Docker
- [ ] Tests async con `pytest-asyncio`
- [ ] Configurar `pytest.ini`: `--cov=wredis --cov-fail-under=95 --cov-report=term-missing`

### Matriz de Cobertura

| Módulo | Unitarios | Integración | Async | Meta Coverage |
|--------|-----------|-------------|-------|---------------|
| bitmap | ✅ | ✅ | ✅ | 95%+ |
| hash | ✅ | ✅ | ✅ | 95%+ |
| pubsub | ✅ | ✅ | ✅ | 95%+ |
| queue | ✅ | ✅ | ✅ | 95%+ |
| sets | ✅ | ✅ | ✅ | 95%+ |
| sortedset | ✅ | ✅ | ✅ | 95%+ |
| streams | ✅ | ✅ | ✅ | 95%+ |
| decorators | ✅ | ✅ | ✅ | 95%+ |
| serialization | ✅ | ✅ | ✅ | 95%+ |
| sentinel | ✅ | ✅ | — | 95%+ |
| cluster | ✅ | ✅ | — | 95%+ |

---

## FASE 9: Documentación Markdown

> **Prioridad:** 🟠 Alta | **Tiempo estimado:** 2 días

### Archivos a Crear/Actualizar

- [ ] `README.md` — Documentación principal completa (EN)
- [ ] `README_ES.md` — Documentación principal completa (ES)
- [ ] `CHANGELOG.md` — Historial de cambios con formato Keep a Changelog
- [ ] `CONTRIBUTING.md` — Guía para colaboradores
- [ ] `CODE_OF_CONDUCT.md` — Contributor Covenant v2.1
- [ ] `SECURITY.md` — Política de seguridad y reporte de vulnerabilidades
- [ ] `CITATION.cff` — Citación académica
- [ ] `examples/README.md` — Todos los ejemplos documentados

### Contenido de Cada Archivo

**CHANGELOG.md:**
```
# Changelog
All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.0.0] - 2026-XX-XX

### Added
- AsyncRedis support for all 7 modules
- @cache, @async_cache, @invalidate_cache decorators
- Sentinel and Cluster high availability managers
- Auto-serialization with set_json/get_json methods
- Simplified top-level API: publish(), subscribe(), enqueue(), xadd()
- 95%+ test coverage with pytest
- GitHub Pages marketing site
- CI/CD pipelines (test, publish, pages)

### Changed
- Migrated to src/ layout (PyPA recommended)
- Minimum Python version: 3.10
- Build system: hatchling only (removed setup.py)
- All __init__.py files use explicit re-exports

### Fixed
- Export consistency across all __init__.py files
- Queue consumer example duplicate function names
- Directory naming (sorted_set.py → sorted_set)
- Ruff linting: 0 errors
```

**CONTRIBUTING.md:**
- Setup del entorno de desarrollo
- Cómo correr tests
- Cómo pasar ruff
- Cómo añadir un nuevo módulo
- Convenciones de código
- Proceso de Pull Request
- Código de conducta

---

## FASE 10: Sitio Web Marketing (`site/`)

> **Prioridad:** 🟡 Media | **Tiempo estimado:** 3 días

### Estructura

```
site/
├── index.html
├── css/
│   └── style.css
└── js/
    └── main.js
```

### Secciones del `index.html`

1. **Hero Section**
   - Logo + tagline: "Redis control, simplified"
   - CTA buttons: `pip install wredis` (copy) + GitHub
   - Animated background gradient

2. **Stats Bar**
   - 32,000+ downloads
   - 7 modules sync + 7 async
   - 95%+ test coverage
   - MIT License

3. **Features Grid** (6 cards con iconos)
   - AsyncRedis nativo
   - Decoradores de caché
   - Sentinel/Cluster HA
   - Serialización automática
   - API simplificada
   - 95%+ coverage

4. **Code Showcase** (tabs interactivos)
   - Tab 1: Sync example
   - Tab 2: Async example
   - Tab 3: Decorator example
   - Tab 4: Sentinel example

5. **Modules Section**
   - Los 7 módulos originales con iconos
   - Los nuevos módulos (async, ha, decorators)

6. **Installation**
   - Commands copy-paste
   - Docker compose example

7. **Community**
   - GitHub stars
   - Contributors
   - Link a issues

8. **Footer**
   - Links, license, author

### Diseño (`style.css`)

- [ ] Dark theme con acentos coral/rojo Redis (#DC382D)
- [ ] Gradientes sutiles
- [ ] Animaciones CSS (fade-in, slide-up)
- [ ] Responsive (mobile-first)
- [ ] Code blocks con syntax highlighting
- [ ] CSS Grid + Flexbox
- [ ] Google Fonts (Inter + JetBrains Mono)

### Funcionalidad (`main.js`)

- [ ] Smooth scroll
- [ ] Tab switching para code examples
- [ ] Copy-to-clipboard en code blocks
- [ ] Intersection Observer para animaciones al scroll
- [ ] Mobile menu toggle

---

## FASE 11: CI/CD

> **Prioridad:** 🟠 Alta | **Tiempo estimado:** 2 días

### `.github/workflows/test.yml`

- [ ] Trigger: push a main + pull_request
- [ ] Matrix: Python 3.10, 3.11, 3.12, 3.13
- [ ] Services: Redis container
- [ ] Steps:
  1. Checkout
  2. Setup Python
  3. Install dependencies
  4. `ruff check .` (fail on any error)
  5. `ruff format --check .`
  6. `pytest --cov=wredis --cov-fail-under=95 --cov-report=term-missing`
  7. `mypy src/wredis`
  8. Upload coverage to Codecov

### `.github/workflows/publish.yml`

- [ ] Trigger: release publicado
- [ ] Steps:
  1. Checkout
  2. Setup Python
  3. Install build + twine
  4. Build con hatchling
  5. Publish a PyPI
  6. Upload artifacts

### `.github/workflows/pages.yml`

- [ ] Trigger: push a main
- [ ] Steps:
  1. Checkout
  2. Deploy `site/` a GitHub Pages
  3. Custom domain si existe

### GitHub Templates

- [ ] `.github/ISSUE_TEMPLATE/bug_report.md`
- [ ] `.github/ISSUE_TEMPLATE/feature_request.md`
- [ ] `.github/ISSUE_TEMPLATE/docs_improvement.md`
- [ ] `.github/PULL_REQUEST_TEMPLATE.md`

---

## 📅 Timeline Estimado

| Fase | Duración | Dependencias |
|------|----------|--------------|
| FASE 0: Calidad de código | 1 día | — |
| FASE 1: Restructuración | 1 día | FASE 0 |
| FASE 2: Core Infrastructure | 2 días | FASE 1 |
| FASE 3: AsyncRedis | 4 días | FASE 2 |
| FASE 4: Decoradores | 2 días | FASE 2 |
| FASE 5: Funciones de conveniencia | 1 día | FASE 2 |
| FASE 6: Sentinel/Cluster | 3 días | FASE 2 |
| FASE 7: Serialización | 2 días | FASE 2 |
| FASE 8: Tests 95%+ | 5 días | FASES 3-7 |
| FASE 9: Documentación | 2 días | FASES 3-7 |
| FASE 10: Sitio Web | 3 días | — (paralelo) |
| FASE 11: CI/CD | 2 días | FASE 8 |
| **TOTAL** | **~28 días** | |

---

## ✅ Criterios de Aceptación para LTS v1.0.0

- [ ] `ruff check .` → 0 errores
- [ ] `ruff format --check .` → 0 errores
- [ ] `pytest --cov=wredis --cov-fail-under=95` → PASS
- [ ] `mypy src/wredis` → 0 errores
- [ ] Todos los imports existentes funcionan sin cambios (backward compatibility)
- [ ] 7 módulos sync + 7 módulos async + HA + decorators
- [ ] `pip install wredis` funciona en Python 3.10, 3.11, 3.12, 3.13
- [ ] CI/CD pipelines passing
- [ ] Documentación completa (README, CHANGELOG, CONTRIBUTING, SECURITY)
- [ ] Sitio web deployado en GitHub Pages
- [ ] ~29 ejemplos nuevos funcionando
- [ ] Docker Compose para Redis standalone, Cluster y Sentinel

---

## 🔒 Reglas de Backward Compatibility

1. **Nunca cambiar la firma de un método existente** — solo añadir parámetros con default al final
2. **Nunca cambiar el tipo de retorno de un método existente**
3. **Nunca cambiar el comportamiento por defecto** de ningún método
4. **Todo feature nuevo vive en su propio namespace** (`wredis.async`, `wredis.decorators`, `wredis.ha`)
5. **Tests de regresión obligatorios** — cada método existente debe tener un test que verifique que su output no cambió

---

## 📦 Dependencias Nuevas

| Paquete | Versión | Uso |
|---------|---------|-----|
| `redis` | `>=5.0.0` | Ya existe — añade soporte asyncio |
| `loguru` | `>=0.7.0` | Ya existe |
| `pytest` | `>=8.0` | Tests |
| `pytest-asyncio` | `>=0.24` | Tests async |
| `pytest-cov` | `>=5.0` | Coverage |
| `fakeredis` | `>=2.21` | Tests sin Redis real |
| `mypy` | `>=1.8` | Type checking |
| `ruff` | `>=0.15` | Linting + formatting |

---

> **Nota:** Este roadmap es un documento vivo. Se actualizará conforme avance la implementación.
