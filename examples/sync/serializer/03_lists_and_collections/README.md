# 03 Lists and Collections

## Description

Demonstrates serialization of lists including simple lists, mixed-type lists, nested lists (matrices), and empty lists.

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