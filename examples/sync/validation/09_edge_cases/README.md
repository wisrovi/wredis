# 09 Edge Cases

## Description

Demonstrates edge case validation for all validation functions, testing boundary limits for TTL, keys, offsets, bit values, and scores.

```mermaid
graph LR
    A[Value] --> B[Validator]
    B --> C{Boundary}
    C -->|In Range| D[Accept]
    C -->|Out of Range| E[ValidationError]
```

## Code

See `example.py`

## Run

```bash
python example.py
```