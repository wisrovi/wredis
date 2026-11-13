# WRedis — WHEN TO USE (Agent Decision Guide)

Decision guide for AI agents and developers: **when** to use WRedis and **which** data structure to choose.

---

## When to Use WRedis?

Use **WRedis** when you need:

- **Ultra-fast in-memory shared state** across processes/services (sub-millisecond latency).
- **Reliable FIFO task queues** with retries, dead-letter queues, and background processing.
- **Function caching** (Cache-Aside pattern) with hit/miss metrics tracking.
- **Streaming event logs** with consumer groups, ACK acknowledgments, and message replay.
- **Leaderboards, atomic counters, user flags, geolocation, sessions**.
- **Multiple services concurrently reading/writing the same real-time data source**.

> Do NOT use WRedis for data that requires strict relational persistence or long-term transaction guarantees
> (use WSQLite / WPostgreSQL), nor for long-term multi-broker event backlogs
> (use WKafka). Redis is ephemeral and volatile by design: data requires TTL or periodic snapshots.

---

## Decision Matrix: Which WRedis Data Structure to Use?

| Requirement | Data Structure | Class | Module |
|---|---|---|---|
| Entity / profile / session with fields | Hash | `RedisHashManager` | `wredis.hash` |
| Reliable FIFO queue with retries | Queue | `RedisQueueManager` | `wredis.queue` |
| Event log with consumer groups + ACK | Stream | `RedisStreamManager` | `wredis.streams` |
| Fire-and-forget notification broadcast | Pub/Sub | `RedisPubSubManager` | `wredis.pubsub` |
| Unique memberships / tags | Set | `RedisSetManager` | `wredis.sets` |
| Leaderboard / ranking / score ordering | Sorted Set | `RedisSortedSetManager` | `wredis.sortedset` |
| DAU/MAU / feature flags (bits) | Bitmap | `RedisBitmapManager` | `wredis.bitmap` |
| Scalable cardinality / unique counting | HyperLogLog | `RedisHyperLogLogManager` | `wredis.hyperloglog` |
| Geolocation / distance searches / nearby | Geo | `RedisGeoManager` | `wredis.geo` |
| Batch operations in single round-trip | Pipeline | `RedisPipelineManager` | `wredis.pipeline` |
| Atomic operations (locks, WATCH, counters) | Transaction | `RedisTransactionManager` | `wredis.transaction` |
| Function caching with metrics | Decorators | `@cache` / `@async_cache` / `CacheMetrics` | `wredis.decorators` |
| Transient offloading / raw key-value | Key/Value | `RedisKeyValueManager` | `wredis.keyvalue` |
| High availability / auto-failover | Sentinel | `SentinelRedisManager` | `wredis.ha.sentinel` |
| Distributed cluster with hash slots | Cluster | `ClusterRedisManager` | `wredis.ha.cluster` |

**Golden Rule:** For every manager, an identical asynchronous version exists in `wredis.aio`
(with `await`). Synchronous = `from wredis.sync import ...`; Asynchronous = `from wredis.aio import ...`.

---

## Architectural Patterns

```
Service / API  →  Repository (repositories/*.py)  →  WRedis Manager  →  Redis
                                              ↘  @cache (decorators)  →  Redis
```

- **Producer / Worker**: `producer.publish("tasks", {...})` → `@consumer.on_message("tasks")` + `consumer.start()`.
- **Streaming Events**: `s.add_to_stream("events", {...})` → `@s.on_message("events", group_name=...)`.
- **Function Caching**: `@cache(ttl=300, prefix="app")` wraps the target function; `CacheMetrics` reports hit rate.
- **Distributed Locks**: `t.set_if_not_exists(key, val, ttl=60)` for locks; `t.increment_atomic(k, 1)`.

---

## Installation

```bash
pip install wredis
```

---

*Authored for the WRedis ecosystem by wisrovi.*
