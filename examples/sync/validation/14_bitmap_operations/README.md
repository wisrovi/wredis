# 14 Bitmap Operations

## Description

Demonstrates complete validation of parameters (key, offset, bit_value) for bitmap operations like SETBIT/GETBIT.

```mermaid
graph LR
    A[Parameters] --> B[Validator]
    B --> C[Operation]
    C -->|Invalid| D[ValidationError]
```

## Code

See `example.py`

## Run

```bash
python example.py
```
