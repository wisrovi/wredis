Pub/Sub Patterns
================

Redis Pub/Sub enables real-time messaging between applications. WRedis provides a decorator-based API for easy integration.

Basic Pub/Sub
-------------

.. code-block:: python

   from wredis.pubsub import RedisPubSubManager

   manager = RedisPubSubManager()

   # Register a handler for a channel
   @manager.on_message("notifications")
   def handle_notification(message):
       print(f"Received: {message}")

   # Publish a message
   manager.publish_message("notifications", "User logged in!")

JSON Messages
-------------

Pub/Sub automatically serializes dictionaries to JSON:

.. code-block:: python

   from wredis.pubsub import RedisPubSubManager

   manager = RedisPubSubManager()

   @manager.on_message("events")
   def handle_event(message):
       if isinstance(message, dict):
           print(f"Event type: {message.get('type')}")
           print(f"Event data: {message.get('data')}")

   # Publish structured event
   manager.publish_message("events", {
       "type": "user.created",
       "data": {"id": 1001, "name": "Alice"},
   })

Multiple Channels
-----------------

Handle different message types on separate channels:

.. code-block:: python

   from wredis.pubsub import RedisPubSubManager

   manager = RedisPubSubManager()

   @manager.on_message("orders")
   def handle_order(message):
       print(f"New order: {message}")

   @manager.on_message("inventory")
   def handle_inventory(message):
       print(f"Inventory update: {message}")

   # Publish to different channels
   manager.publish_message("orders", {"item": "Widget", "qty": 5})
   manager.publish_message("inventory", {"sku": "WDG-001", "stock": 150})

Microservices Communication
----------------------------

Pub/Sub is ideal for event-driven microservices:

.. code-block:: python

   # Service A: Order Service
   from wredis.pubsub import RedisPubSubManager

   order_pubsub = RedisPubSubManager()

   def create_order(order_data: dict):
       # Process order
       order_pubsub.publish_message("order.created", order_data)
       order_pubsub.publish_message("inventory.reserve", {
           "order_id": order_data["id"],
           "items": order_data["items"],
       })

   # Service B: Notification Service
   notification_pubsub = RedisPubSubManager()

   @notification_pubsub.on_message("order.created")
   def send_confirmation(message):
       # Send email confirmation
       print(f"Sending confirmation for order {message['id']}")

   # Service C: Inventory Service
   inventory_pubsub = RedisPubSubManager()

   @inventory_pubsub.on_message("inventory.reserve")
   def reserve_inventory(message):
       # Reserve items
       print(f"Reserving items for order {message['order_id']}")

Real-Time Dashboard
-------------------

.. code-block:: python

   from wredis.pubsub import RedisPubSubManager

   dashboard_pubsub = RedisPubSubManager()

   @dashboard_pubsub.on_message("metrics")
   def update_dashboard(message):
       """Update real-time dashboard with new metrics."""
       metric_type = message.get("type")
       value = message.get("value")
       print(f"Dashboard update - {metric_type}: {value}")

   # Publish metrics from various services
   dashboard_pubsub.publish_message("metrics", {
       "type": "requests_per_second",
       "value": 1250,
   })

   dashboard_pubsub.publish_message("metrics", {
       "type": "error_rate",
       "value": 0.02,
   })

Graceful Shutdown
-----------------

.. code-block:: python

   import signal
   import sys
   from wredis.pubsub import RedisPubSubManager

   manager = RedisPubSubManager()

   @manager.on_message("commands")
   def handle_command(message):
       print(f"Command: {message}")

   def shutdown(signum, frame):
       print("\nShutting down...")
       manager.stop_listeners()
       sys.exit(0)

   signal.signal(signal.SIGINT, shutdown)
   signal.pause()

Best Practices
--------------

1. **Use structured messages** - Prefer JSON objects over plain strings
2. **Separate channels by domain** - Use distinct channels for different event types
3. **Handle reconnection** - Implement retry logic for connection failures
4. **Monitor message rates** - Track throughput and latency
5. **Use appropriate data types** - Keep messages small and focused
6. **Consider message ordering** - Pub/Sub does not guarantee ordering
