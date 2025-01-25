from wredis.queue import RedisQueueManager


# Crear una instancia del productor
queue_manager = RedisQueueManager(host="localhost")

# Publicar mensajes en diferentes colas
queue_manager.publish("4090", {"id": 1, "task": "process_image", "status": "pending"})
queue_manager.publish("4060", {"id": 2, "task": "generate_report", "priority": "high"})
queue_manager.publish(
    "queue:4060", {"id": 3, "task": "process_video", "status": "pending"}
)

queue_manager.publish("tasks", {"task_id": 3, "description": "Generar reporte"}, ttl=30)
queue_manager.publish(
    "tasks", {"task_id": 4, "description": "Actualizar base de datos"}, ttl=120
)
queue_manager.publish(
    "tasks",
    {
        "task_id": 4,
        "description": {"id": 2, "task": "generate_report", "priority": "high"},
    },
    ttl=10,
)


# NOTA: ajusta un TTL modifica el tiempo de toda la cola y no de un mensaje en particular
# NOTA: el TTL se mide en segundos