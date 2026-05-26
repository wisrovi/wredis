# 09 Large Data

## Description

Demonstrates serialization of large datasets with thousands of elements, showing performance characteristics.

```mermaid
graph LR
    A[Data] --> B[Serializer]
    B --> C[Redis]
    C --> D[Deserializer]
    D --> E[Data]
```

## Code

See `example.py`

## Run

```bash
python example.py
```