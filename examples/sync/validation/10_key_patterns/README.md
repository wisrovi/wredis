# 10 Key Patterns

## Description

Demonstrates validation of various common Redis key naming patterns including entity:id, hierarchical, cache, queue, counters, locks, and configurations.

```mermaid
graph LR
    A[Key Pattern] --> B[Validator]
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
