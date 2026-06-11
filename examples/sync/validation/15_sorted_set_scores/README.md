# 15 Sorted Set Scores

## Description

Demonstrates score validation for sorted set operations (ZADD) including valid scores (positive, negative, float, zero) and invalid scores (NaN, infinity, string).

```mermaid
graph LR
    A[Score] --> B[Validator]
    B --> C[Sorted Set]
    C -->|Invalid| D[ValidationError]
```

## Code

See `example.py`

## Run

```bash
python example.py
```
