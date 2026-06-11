# 12 Validation Decorator

## Description

Demonstrates creating a reusable decorator that automatically validates key and TTL parameters before executing operations.

```mermaid
graph LR
    A[Parameters] --> B[Decorator]
    B --> C[Validator]
    C --> D[Operation]
    C -->|Invalid| E[ValidationError]
```

## Code

See `example.py`

## Run

```bash
python example.py
```
