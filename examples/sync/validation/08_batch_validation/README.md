# 08 Batch Validation

## Description

Demonstrates batch validation of multiple parameters for operations like bitmaps, validating key, offset, and bit_value together.

```mermaid
graph LR
    A[Parameters] --> B[Validator]
    B --> C{All Valid?}
    C -->|Yes| D[Accept]
    C -->|No| E[ValidationError]
```

## Code

See `example.py`

## Run

```bash
python example.py
```
