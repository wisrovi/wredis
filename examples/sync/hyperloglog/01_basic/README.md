# HyperLogLog Basic Example

## Description

This example demonstrates basic HyperLogLog operations for counting unique visitors using `RedisHyperLogLogManager`.

## Diagram

```mermaid
flowchart TD
    A[Start] --> B[Create HyperLogLog manager]
    B --> C[Add visitors (batch 1)]
    C --> D[Add more visitors (batch 2)]
    D --> E[Get unique count]
    E --> F[Display result]
    F --> G[End]
```

## Code

```python
from wredis.hyperloglog import RedisHyperLogLogManager

hll = RedisHyperLogLogManager(host="localhost")

hll.add("visitors", "user1", "user2", "user3", "user4", "user5")
hll.add("visitors", "user6", "user7")

count = hll.count("visitors")
print(f"Unique visitors: {count}")
```

## Run Instructions

```bash
python example.py
```
