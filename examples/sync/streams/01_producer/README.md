# Streams Producer Example

## Description

This example demonstrates producing messages to Redis streams using `RedisStreamManager`.

## Diagram

```mermaid
flowchart TD
    A[Start] --> B[Create Stream manager]
    B --> C[Add to my_stream]
    C --> D[Add to my_stream_2]
    D --> E[End]
```

## Code

```python
from wredis.streams import RedisStreamManager

stream_manager = RedisStreamManager(host="localhost")

stream_manager.add_to_stream("my_stream", {"field1": "value1"})
stream_manager.add_to_stream("my_stream", {"field2": "value3", "field4": "value4"})


stream_manager.add_to_stream("my_stream_2", {"field1": "value1"})
```

## Run Instructions

```bash
python example.py
```
