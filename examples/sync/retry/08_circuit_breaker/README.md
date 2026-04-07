# 08 Circuit Breaker

## Description

Demonstrates implementing a circuit breaker pattern that stops retrying after too many consecutive failures to prevent cascading failures.

```mermaid
graph LR
    A[Operation] --> B[Manager]
    B --> C{Redis}
    C -->|Success| D[Result]
    C -->|Error| E[Circuit Breaker]
```

## Code

See `example.py`

## Run

```bash
python example.py
```