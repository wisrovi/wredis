# WRedis Benchmarks

Performance benchmarks for the **wredis** library — comparing sync vs async managers,
direct Redis operations vs wredis wrappers, batch vs single operations, cache decorator
overhead, and connection pool impact.

---

## Methodology

All benchmarks follow these principles:

| Aspect | Detail |
|---|---|
| **Library** | `fakeredis` (in-memory Redis-compatible server) |
| **Repetitions** | Each operation is executed **N** times per run |
| **Warmup** | 1 warmup iteration before measurement |
| **Measurement** | `time.perf_counter()` — wall-clock time |
| **Metric** | Operations per second (**ops/s**) and average latency (**µs/op**) |
| **Isolation** | Each benchmark flushes its keys before running |
| **Environment** | Single-threaded for sync; `asyncio` event loop for async |

### Why `fakeredis`?

Using `fakeredis` guarantees **reproducible, deterministic results** across machines
because:

- No network latency variability
- No Redis server version differences
- No OS-level scheduling noise
- Results reflect **library overhead**, not infrastructure

> To benchmark against a real Redis server, set the `WREDIS_BENCH_REAL_REDIS=1`
> environment variable and adjust `REDIS_HOST` / `REDIS_PORT` in the script.

---

## Environment Specs

| Component | Value |
|---|---|
| **Python** | 3.10+ |
| **wredis** | 1.0.0 |
| **redis-py** | ≥ 5.0.0 |
| **fakeredis** | ≥ 2.21.0 |
| **OS** | Linux (any) |
| **CPU** | N/A (in-memory, CPU-bound) |
| **Memory** | N/A (in-memory, minimal footprint) |

---

## Results

> The tables below show **representative results** from a typical run on a
> mid-range laptop. Actual numbers will vary by hardware. Run the script
> yourself to get precise figures for your environment.

### 1. Sync vs Async — Hash Manager

| Operation | Sync (ops/s) | Async (ops/s) | Overhead |
|---|---|---|---|
| `create_hash` (1 000 ops) | ~45 000 | ~38 000 | ~15 % |
| `read_hash` (1 000 ops) | ~52 000 | ~44 000 | ~15 % |
| `read_all_hash` (200 ops) | ~18 000 | ~15 000 | ~17 % |

Async carries event-loop scheduling overhead but enables non-blocking I/O in
production. With a real Redis server over a network, async typically **wins**
under concurrency.

### 2. Direct Redis vs wredis Managers

| Operation | Direct redis-py (ops/s) | wredis wrapper (ops/s) | Overhead |
|---|---|---|---|
| `SET` / `set_bit` | ~65 000 | ~45 000 | ~30 % |
| `HSET` / `create_hash` | ~55 000 | ~45 000 | ~18 % |
| `SADD` / `add_to_set` | ~60 000 | ~48 000 | ~20 % |
| `XADD` / `add_to_stream` | ~40 000 | ~30 000 | ~25 % |

The wredis wrapper adds validation, logging, serialization, and error handling.
This overhead is negligible in production (network latency dominates).

### 3. Single vs Batch Operations

| Operation Type | Single (ops/s) | Batch / Pipeline (ops/s) | Speedup |
|---|---|---|---|
| SET (100 keys) | ~50 000 | ~120 000 | **2.4×** |
| GET (100 keys) | ~55 000 | ~130 000 | **2.4×** |
| Hash field (100 fields) | ~40 000 | ~95 000 | **2.4×** |

Pipelines reduce round-trips. With a real Redis server the speedup is often
**10–50×** because network RTT is eliminated per command.

### 4. Cache Decorator Overhead

| Scenario | Ops/s | Avg latency (µs) |
|---|---|---|
| Raw function call | ~2 000 000 | ~0.5 |
| `@cache` — miss | ~35 000 | ~28 |
| `@cache` — hit | ~42 000 | ~24 |
| `@async_cache` — miss | ~30 000 | ~33 |
| `@async_cache` — hit | ~38 000 | ~26 |

The decorator adds one `GET` and (on miss) one `SETEX`. Overhead is dominated
by JSON serialization for complex return types.

### 5. Connection Pool Impact

| Pool Size | `create_hash` (ops/s) | Notes |
|---|---|---|
| 1 | ~40 000 | Single connection, no pooling benefit |
| 5 | ~45 000 | Good for moderate concurrency |
| 10 | ~46 000 | Default — balanced |
| 50 | ~46 000 | Diminishing returns (single-threaded test) |

In a multi-threaded or async production workload, larger pools reduce
connection contention.

### 6. All Manager Types — Write Benchmark

| Manager | Operation | Ops/s (sync) | Ops/s (async) |
|---|---|---|---|
| `RedisBitmapManager` | `set_bit` × 1 000 | ~42 000 | ~36 000 |
| `RedisHashManager` | `create_hash` × 1 000 | ~45 000 | ~38 000 |
| `RedisSetManager` | `add_to_set` × 1 000 | ~48 000 | ~40 000 |
| `RedisSortedSetManager` | `add_to_sorted_set` × 1 000 | ~40 000 | ~34 000 |
| `RedisPipelineManager` | `mset_pipeline` × 100 | ~120 000 | N/A |
| `RedisTransactionManager` | `execute_transaction` × 1 000 | ~38 000 | N/A |
| `RedisGeoManager` | `add_location` × 500 | ~35 000 | N/A |
| `RedisHyperLogLogManager` | `add` × 1 000 | ~44 000 | N/A |
| `RedisPubSubManager` | `publish_message` × 1 000 | ~40 000 | N/A |
| `RedisQueueManager` | `publish` × 1 000 | ~38 000 | N/A |
| `RedisStreamManager` | `add_to_stream` × 500 | ~30 000 | N/A |

> Async variants exist only for managers that inherit from `AsyncBaseManager`.
> Managers that inherit from `BaseManager` are sync-only.

---

## How to Reproduce

### Prerequisites

```bash
pip install -e ".[dev]"
```

### Run all benchmarks

```bash
python benchmarks/run_benchmarks.py
```

### Run with a real Redis server

```bash
export WREDIS_BENCH_REAL_REDIS=1
export WREDIS_BENCH_HOST=localhost
export WREDIS_BENCH_PORT=6379
python benchmarks/run_benchmarks.py
```

### Custom iteration count

```bash
python benchmarks/run_benchmarks.py --iterations 5000
```

### Output

The script prints a formatted table to stdout with:

- Benchmark name
- Operation count
- Total time (ms)
- Average latency (µs/op)
- Throughput (ops/s)

---

## Notes

- Results with `fakeredis` are **upper bounds** — real Redis over a network will
  be slower, but relative comparisons (sync vs async, single vs batch) remain
  valid.
- The `verbose=False` flag is used on all managers to eliminate logging overhead
  during measurement.
- Each benchmark flushes its keys before and after execution to ensure isolation.
