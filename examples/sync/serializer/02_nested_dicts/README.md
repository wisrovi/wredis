# 02 Nested Dicts

## Description

Demonstrates serialization of nested dictionaries, commonly used for storing complex configurations or user records in Redis.

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