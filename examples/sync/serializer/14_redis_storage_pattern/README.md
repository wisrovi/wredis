# 14 Redis Storage Pattern

## Description

Demonstrates a common pattern where data is serialized before storing in Redis and deserialized when retrieving, simulating real Redis usage.

```mermaid
graph LR
    A[Data] --> B[serialize]
    B --> C[Redis]
    C --> D[deserialize]
    D --> E[Data]
```

## Code

See `example.py`

## Run

```bash
python example.py
```