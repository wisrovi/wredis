# 01 TTL Validation

## Description

Demonstrates basic TTL validation with acceptable values (positive, zero, and -1 for no expiration).

```mermaid
graph LR
    A[TTL Value] --> B[Validator]
    B --> C{Valid?}
    C -->|Yes| D[Accept]
    C -->|No| E[ValidationError]
```

## Code

See `example.py`

## Run

```bash
python example.py
```
