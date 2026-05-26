# 07 Datetime Serialization

## Description

Demonstrates serialization of datetime objects by converting them to ISO 8601 strings.

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