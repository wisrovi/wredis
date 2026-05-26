# 01 Basic Serialize

## Description

Demonstrates basic serialization of Python primitive types (integers, floats, strings, booleans) using the wredis serializer.

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