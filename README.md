<img width="1452" height="826" alt="image" src="https://github.com/user-attachments/assets/ec5277c7-ec3d-4df2-88a3-37937a318133" />

<p align="center">
  <a href="https://pypi.org/project/wredis/"><img src="https://img.shields.io/pypi/v/wredis?style=for-the-badge&logo=pypi&color=3b82f6" alt="PyPI version" /></a>
  <a href="https://pypi.org/project/wredis/"><img src="https://img.shields.io/pypi/dm/wredis?style=for-the-badge&color=10b981" alt="PyPI Downloads" /></a>
  <a href="https://pypi.org/project/wredis/"><img src="https://img.shields.io/pypi/pyversions/wredis?style=for-the-badge&logo=python&color=ffd343&logoColor=black" alt="Python Versions" /></a>
  <a href="https://linkedin.com/in/wisrovi-rodriguez"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" /></a>
  <a href="https://wisrovi.dev"><img src="https://img.shields.io/badge/Author-wisrovi.dev-111827?style=for-the-badge&logo=google-chrome&logoColor=white" alt="Portal" /></a>
  <a href="https://orcid.org/0009-0005-0710-1861"><img src="https://img.shields.io/badge/ORCID-0009--0005--0710--1861-A6CE39?style=for-the-badge&logo=orcid&logoColor=white" alt="ORCID" /></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge" alt="License" /></a>
</p>

# WRedis 🚀

**Production-Grade, High-Availability Python Client Suite for Redis with Dual Sync/Async APIs, Transparent Claim-Check RAM Offloading, and Enterprise Forensic Auditing.**

---

## 📑 Table of Contents

- [🏛️ Architectural Overview](#️-architectural-overview)
- [🌟 Why WRedis?](#-why-wredis)
- [📦 Installation](#-installation)
- [🛠️ Key Technologies and Libraries](#️-key-technologies-and-libraries)
- [🚀 Quick Start](#-quick-start)
- [🔍 Enterprise Forensic Audit Trail](#-enterprise-forensic-audit-trail)
- [🧩 Supported Data Structures & Managers](#-supported-data-structures--managers)
  - [1. Key-Value & Ephemeral Binary Storage](#1-key-value--ephemeral-binary-storage)
  - [2. Cache Decorators (`@cache` / `@async_cache`)](#2-cache-decorators-cache--async_cache)
  - [3. Hashes](#3-hashes)
  - [4. Queues with Gzip Compression](#4-queues-with-gzip-compression)
  - [5. Pub/Sub Engine](#5-pubsub-engine)
  - [6. Streams & Consumer Groups](#6-streams--consumer-groups)
  - [7. Bitmaps](#7-bitmaps)
  - [8. Sets & Sorted Sets](#8-sets--sorted-sets)
  - [9. Geospatial Indices](#9-geospatial-indices)
  - [10. HyperLogLog Cardinality](#10-hyperloglog-cardinality)
  - [11. Pipelines & Atomic Transactions](#11-pipelines--atomic-transactions)
- [🛡️ High Availability (Sentinel & Cluster)](#️-high-availability-sentinel--cluster)
- [⚙️ Connection & Configuration Reference](#️-connection--configuration-reference)
- [🧪 Unit Testing & Quality Assurance](#-unit-testing--quality-assurance)
- [👤 Author & Official Affiliation](#-author--official-affiliation)
- [📜 License](#-license)

---

## 🏛️ Architectural Overview

```
+========================================================================================+
|                                    WREDIS ECOSYSTEM                                    |
+========================================================================================+
|                                                                                        |
|   🔌 UNIFIED CLIENT INTERFACE (Dual Sync / Async APIs)                                 |
|   +--------------------------------------------------------------------------------+   |
|   |  • Auto-Reconnection & Connection Pooling with intelligent backoff            |   |
|   |  • Dual Sync / Asynchronous (`asyncio` / `await`) runtime parity               |   |
|   |  • Forensic Audit Trail (`forensic=True` appends pre/post mutation snapshots)  |   |
|   |  • Type-Safety: 100% strict PEP-484 type annotations and runtime validation    |   |
|   +--------------------------------------------------------------------------------+   |
|                                          |                                             |
|                                          v                                             |
|   🗂️ 13 SPECIALIZED DATA STRUCTURE MANAGERS                                            |
|   +--------------------------------------------------------------------------------+   |
|   |  • KeyValue: Ephemeral RAM offload, raw byte DMA, auto-JSON serialization       |   |
|   |  • Cache Decorators: `@cache` / `@async_cache` with hit/miss telemetry & TTL   |   |
|   |  • Streams & Queues: Consumer groups, ACK management, Gzip payload compression  |   |
|   |  • Pub/Sub: Thread-safe listener registries and topic routing                  |   |
|   |  • Sets / SortedSets: Leaderboards, rank queries, and set algebra operations   |   |
|   |  • Geo / Bitmaps / HyperLogLog: Spatial radii, bitfields, probabilistic stats  |   |
|   |  • Pipelines & Transactions: Batch pipelining and atomic MULTI/EXEC locks      |   |
|   +--------------------------------------------------------------------------------+   |
|                                          |                                             |
|                                          v                                             |
|   🛡️ HIGH AVAILABILITY & INFRASTRUCTURE TOPOLOGIES                                    |
|   +--------------------------------------------------------------------------------+   |
|   |  • Standalone Redis: Single-node high-throughput cache & Claim-Check RAM       |   |
|   |  • Redis Sentinel: Automatic master failover & replica topology sync           |   |
|   |  • Redis Cluster: Transparent 16,384 hash slot partitioning and sharding       |   |
|   +--------------------------------------------------------------------------------+   |
+========================================================================================+
```

---

## 🌟 Why WRedis?

Direct usage of low-level `redis-py` requires substantial boilerplate for production applications: manual connection teardown, connection pool exhaustion debugging, type casting, JSON parsing/serializing, manual retry backoff, and ad-hoc clustering configs.

**WRedis delivers an enterprise-grade developer experience:**

* 🚀 **Zero Boilerplate**: Specialized manager classes for each Redis capability with intuitive CRUD semantics.
* ⚡ **Claim-Check RAM Offload Engine**: Native `setex` and `get_bytes` optimized for ultra-high-throughput multimedia offloading in event-driven systems (e.g., `wkafka`).
* 🔍 **Forensic Auditing**: Built-in mutation audit trail stream (`forensic=True`) recording before-and-after snapshots with zero performance penalty.
* 🎯 **Dual Sync & Async APIs**: Seamlessly switch between synchronous workers and high-concurrency `asyncio` services.
* 🛡️ **Enterprise Resilience**: Native Sentinel failover detection and Redis Cluster sharding out of the box.
* 📦 **Production Ready**: 100% test coverage with `fakeredis` and live integration test suites.

---

## 📦 Installation

```bash
# Standard installation from PyPI
pip install wredis

# Using poetry
poetry add wredis
```

---

## 🛠️ Key Technologies and Libraries

WRedis is engineered on top of modern, battle-tested Python and Redis database standards:

- **Python (3.9 - 3.14)**: Modern typed runtime with PEP-561 compliance (`py.typed`).
- **redis-py (`redis>=5.0.0`)**: High-performance core Redis client supporting Standalone, Sentinel, Cluster, and AsyncIO.
- **Loguru**: Structured, thread-safe asynchronous logging and operational telemetry.
- **Fakeredis**: Deterministic in-memory Redis mocking for hermetic unit testing without external daemon dependencies.
- **Pytest & Pytest-Cov**: Automated unit, integration, and high-availability test suites (>95% coverage).

---

## 🚀 Quick Start

### Cache Decorator with Metrics & TTL
```python
from wredis.cache import RedisCacheManager

cache = RedisCacheManager(host="localhost", port=6379)

@cache(ttl=60)
def fetch_user_profile(user_id: str) -> dict:
    # Heavy database query or remote API call
    return {"id": user_id, "name": "Alice", "role": "admin"}

# First call executes function; subsequent calls within 60s return cached RAM result instantly
profile = fetch_user_profile("user-42")
```

---

## 🔍 Enterprise Forensic Audit Trail

WRedis provides an automated, stream-based audit trail (`_forensic_audit_log`) for monitoring data mutations across sensitive key-spaces.

- **Disabled by default**: Enable by setting `forensic=True` when instantiating any manager:
  ```python
  from wredis.hash import RedisHashManager

  hm = RedisHashManager(host="localhost", forensic=True)
  hm.create_hash("accounts", "acc:100", {"balance": 5000})
  ```
- **Stream-Based Immutable Ledger**: Records the action (`create`, `update`, `delete`), target key, pre-state, post-state, and high-precision UTC timestamp.
- **Zero Overhead**: Fully isolated logging stream that does not block primary database commands.

---

## 🧩 Supported Data Structures & Managers

### 1. Key-Value & Ephemeral Binary Storage
Direct ephemeral RAM storage for raw binary streams, strings, and auto-serialized dictionaries.

```python
from wredis.keyvalue import RedisKeyValueManager

kv = RedisKeyValueManager(host="localhost", port=6379)

# 1. Store raw binary bytes with 5-second TTL (ideal for high-throughput multimedia offload & claim-check)
kv.setex("frame:camera_1", ttl=5, value=raw_bytes)

# 2. Retrieve raw bytes directly without string encoding overhead
payload = kv.get_bytes("frame:camera_1")

# 3. Store and retrieve structured dictionaries (auto-serialized to JSON)
kv.set("metadata:101", {"status": "active", "tags": ["cv", "edge"]})
meta = kv.get("metadata:101")  # Returns dict directly
```

### 2. Cache Decorators (`@cache` / `@async_cache`)
High-performance memoization with configurable TTL and key hashing:

```python
# Synchronous function caching
@cache("product_cache", ttl=300)
def get_product(product_id: int) -> dict:
    return {"id": product_id, "price": 49.99}

# Asynchronous coroutine caching
@async_cache("async_orders", ttl=120)
async def get_order_async(order_id: str) -> dict:
    return await db.orders.find_one({"_id": order_id})
```

### 3. Hashes
Manage structured object maps with field-level mutations:

```python
from wredis.hash import RedisHashManager

hm = RedisHashManager(host="localhost")
hm.create_hash("users", "user:1", {"name": "Alice", "age": 30}, ttl=3600)

user = hm.read_hash("users", "user:1")
hm.update_hash("users", "user:1", {"age": 31})
hm.delete_hash_field("users", "user:1")
```

### 4. Queues with Gzip Compression
Reliable FIFO worker queues with optional compression for heavy task payloads:

```python
from wredis.queue import RedisQueueManager

# Producer
qm = RedisQueueManager(host="localhost", compress=True)
qm.publish("heavy_tasks", {"action": "render_video", "clip_id": 992}, ttl=60)

# Consumer / Worker
@qm.on_message("heavy_tasks")
def task_worker(task):
    print(f"Processing task: {task['action']}")

qm.start()
```

### 5. Pub/Sub Engine
Thread-safe topic broadcasting and event subscriptions:

```python
from wredis.pubsub import RedisPubSubManager

pbm = RedisPubSubManager(host="localhost")

# Subscribe listener
@pbm.on_message("system.alerts")
def on_alert(msg):
    print(f"Alert received: {msg}")

# Publish message
pbm.publish_message("system.alerts", {"level": "CRITICAL", "node": "gpu-01"})
```

### 6. Streams & Consumer Groups
Production event streaming with consumer group checkpointing and message acks:

```python
from wredis.streams import RedisStreamManager

sm = RedisStreamManager(host="localhost")

# Publish event
sm.add_to_stream("order_events", {"order_id": "ORD-55", "total": 99.0})

# Consumer group subscriber
@sm.on_message("order_events", group_name="billing_workers", consumer_name="worker_a")
def handle_event(event):
    print(f"Processing order event: {event}")

sm.wait()
```

### 7. Bitmaps
Compact bitfields for daily active user tracking and boolean flag registries:

```python
from wredis.bitmap import RedisBitmapManager

bm = RedisBitmapManager(host="localhost")
bm.set_bit("dau:2026-11-16", offset=402, value=1)

is_active = bm.get_bit("dau:2026-11-16", 402)  # 1
total_active = bm.count_bits("dau:2026-11-16")
```

### 8. Sets & Sorted Sets
Unordered unique sets and scored leaderboards:

```python
from wredis.sortedset import RedisSortedSetManager

ssm = RedisSortedSetManager(host="localhost")
ssm.add_to_sorted_set("leaderboard", 1500, "player_alpha")
ssm.add_to_sorted_set("leaderboard", 2300, "player_beta")

# Retrieve top 10 players
top_players = ssm.get_sorted_set_reverse("leaderboard", start=0, end=9, with_scores=True)
```

### 9. Geospatial Indices
Coordinate storage and radius-based geographic queries:

```python
from wredis.geo import RedisGeoManager

gm = RedisGeoManager(host="localhost")
gm.add_location("charging_stations", "Station A", 40.785091, -73.968285)
gm.add_location("charging_stations", "Station B", 40.758896, -73.985130)

distance_km = gm.distance("charging_stations", "Station A", "Station B", unit="km")
```

### 10. HyperLogLog Cardinality
Probabilistic distinct count tracking with negligible memory footprint:

```python
from wredis.hyperloglog import RedisHyperLogLogManager

hll = RedisHyperLogLogManager(host="localhost")
hll.add("unique_visitors", "ip_1", "ip_2", "ip_3")
unique_count = hll.count("unique_visitors")
```

### 11. Pipelines & Atomic Transactions
Batch command execution and atomic `MULTI`/`EXEC` operations:

```python
from wredis.pipeline import RedisPipelineManager

pm = RedisPipelineManager(host="localhost")
results = pm.mget_pipeline("key1", "key2", "key3")
```

---

## 🛡️ High Availability (Sentinel & Cluster)

### Redis Sentinel
Automatic master failover orchestration with Sentinel service discovery:

```python
from wredis.ha.sentinel import RedisSentinelManager

sm = RedisSentinelManager(
    sentinel_hosts=[("sentinel-node-1", 26379), ("sentinel-node-2", 26379)],
    service_name="mymaster",
    password="<your_password>",
    db=0
)
```

### Redis Cluster
Automatic client-side sharding across 16,384 hash slots:

```python
from wredis.ha.cluster import RedisClusterManager

cm = RedisClusterManager(
    startup_nodes=[{"host": "cluster-node-1", "port": 6379}, {"host": "cluster-node-2", "port": 6379}],
    password="<your_password>",
)
```

---

## ⚙️ Connection & Configuration Reference

All WRedis managers accept standard unified connection arguments:

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `host` | `str` | `"localhost"` | Redis server hostname or IP address. |
| `port` | `int` | `6379` | Redis server TCP port. |
| `db` | `int` | `0` | Target Redis database index (0-15). |
| `password` | `Optional[str]` | `None` | Authentication password. |
| `verbose` | `bool` | `True` | Structured Loguru diagnostic telemetry. |
| `decode_responses` | `bool` | `False` | Decode binary responses to UTF-8 strings automatically. |
| `forensic` | `bool` | `False` | Enable automatic stream-based mutation auditing (`_forensic_audit_log`). |

Queue-specific parameters:

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `poll_interval` | `float` | `1.0` | Seconds to wait between consumer poll intervals. |
| `max_retries` | `int` | `3` | Maximum retry attempts upon task failure. |
| `compress` | `bool` | `False` | Automatically compress queue payloads using Gzip. |

---

## 🧪 Unit Testing & Quality Assurance

WRedis enforces rigorous quality assurance with comprehensive mocked and live integration test suites:

```bash
# 1. Run unit test suite with in-memory fakeredis
pytest tests/unit/ -v

# 2. Run test coverage verification
pytest --cov=wredis tests/unit/
```

---

## 👤 Author & Official Affiliation

* **William Steve Rodriguez Villamizar (Wisrovi)**
* **Role:** AI Leader & Solutions Architect at eCaptureDtech | Principal AI Engineer
* 📧 **Email:** [wisrovi.rodriguez@gmail.com](mailto:wisrovi.rodriguez@gmail.com)
* 🌐 **Official Portal:** [wisrovi.dev](https://wisrovi.dev)
* 💼 **LinkedIn:** [wisrovi-rodriguez](https://www.linkedin.com/in/wisrovi-rodriguez/)
* 🆔 **ORCID:** [0009-0005-0710-1861](https://orcid.org/0009-0005-0710-1861)
* 📦 **PyPI:** [pypi.org/user/wisrovi/](https://pypi.org/user/wisrovi/)
* 🐙 **GitHub:** [@wisrovi](https://github.com/wisrovi)

---

## 📜 License

Distributed under the **MIT License**. Free for commercial, enterprise, and research applications.
