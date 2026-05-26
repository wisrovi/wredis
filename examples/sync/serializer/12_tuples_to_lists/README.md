# 12 Tuples to Lists

## Description

Demonstrates how Python tuples are converted to JSON lists during serialization, since JSON doesn't support tuple type.

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