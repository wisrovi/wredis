# 14 Stream and PubSub Errors

## Description

Demonstrates handling of StreamError and PubSubError for Redis Streams and Pub/Sub operations, including corrupted streams, invalid data, and connection issues.

```mermaid
graph LR
    A[Operation] --> B[Manager]
    B --> C{Redis}
    C -->|Success| D[Result]
    C -->|Error| E[Exception Handler]
```

## Code

See `example.py`

## Run

```bash
python example.py
```
