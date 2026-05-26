"""01 - Inicialización básica de BaseManager

Este ejemplo muestra cómo crear una instancia de BaseManager
con los parámetros por defecto y verificar la conexión.
"""

import asyncio

from wredis.aio import BaseManager


async def main():
    manager = BaseManager(verbose=True)

    is_alive = await manager.health_check()
    print(f"Redis connected: {is_alive}")

    result = await manager._execute("set", "greeting", "hello world")
    print(f"SET result: {result}")

    value = await manager._execute("get", "greeting")
    print(f"GET result: {value}")

    await manager.close()
    print("Connection closed correctly")


if __name__ == "__main__":
    asyncio.run(main())
