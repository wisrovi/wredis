from wredis.pubsub import RedisPubSubManager


pubsub_manager = RedisPubSubManager(host="localhost")


pubsub_manager.publish_message("channel_1", "Hello, Redis!")


pubsub_manager.publish_message("channel_2", {"saludo": "Hola desde channel_2!"})
