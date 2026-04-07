# 05 Offset Validation

## Description

Demonstrates offset validation for bitmap operations, showing valid offsets (0, positive numbers) and invalid negative offsets.

```mermaid
graph LR
    A[Offset] --> B[Validator]
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