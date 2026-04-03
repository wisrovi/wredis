"""09 - Manager personalizado con herencia

Este ejemplo muestra cómo crear un manager personalizado heredando
de AsyncBaseManager, agregando métodos específicos para casos de
uso particulares como gestión de sesiones de usuario.
"""

import asyncio
import json
from typing import Any

import fakeredis.aioredis
from wredis._async_base import AsyncBaseManager


class SessionManager(AsyncBaseManager):
    """Manager personalizado para gestión de sesiones de usuario."""

    def __init__(self, session_ttl: int = 3600, **kwargs: Any):
        """Inicializa el SessionManager.

        Args:
            session_ttl: Tiempo de vida de las sesiones en segundos.
            **kwargs: Argumentos para AsyncBaseManager.
        """
        super().__init__(**kwargs)
        self.session_ttl = session_ttl
        self.prefix = "sesion"

    async def crear_sesion(self, user_id: str, datos: dict) -> str:
        """Crea una nueva sesión para un usuario."""
        session_key = f"{self.prefix}:{user_id}"
        await self._execute("set", session_key, json.dumps(datos), ex=self.session_ttl)
        self.log(f"Sesión creada para usuario {user_id}")
        return session_key

    async def obtener_sesion(self, user_id: str) -> dict | None:
        """Obtiene los datos de una sesión existente."""
        session_key = f"{self.prefix}:{user_id}"
        datos = await self._execute("get", session_key)
        if datos:
            return json.loads(datos)
        return None

    async def eliminar_sesion(self, user_id: str) -> bool:
        """Elimina una sesión de usuario."""
        session_key = f"{self.prefix}:{user_id}"
        eliminado = await self._execute("delete", session_key)
        self.log(f"Sesión eliminada para usuario {user_id}")
        return bool(eliminado)

    async def renovar_sesion(self, user_id: str) -> bool:
        """Renueva el TTL de una sesión existente."""
        session_key = f"{self.prefix}:{user_id}"
        renovado = await self._execute("expire", session_key, self.session_ttl)
        return bool(renovado)


async def main():
    # Creamos un FakeRedis para simular el backend
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)

    async with SessionManager(
        decode_responses=True,
        session_ttl=1800,  # 30 minutos
        verbose=True,
    ) as session_mgr:
        # Inyectamos el FakeRedis
        session_mgr.redis_client = fake

        # Verificamos conexión
        conectado = await session_mgr.health_check()
        print(f"SessionManager conectado: {conectado}")

        # Creamos una sesión
        print("\n=== Crear sesión ===")
        datos_usuario = {
            "nombre": "Carlos",
            "rol": "admin",
            "ultima_actividad": "2026-04-03T10:00:00",
        }
        key = await session_mgr.crear_sesion("user_42", datos_usuario)
        print(f"Sesión creada: {key}")

        # Obtenemos la sesión
        print("\n=== Obtener sesión ===")
        sesion = await session_mgr.obtener_sesion("user_42")
        print(f"Datos de sesión: {sesion}")

        # Renovamos la sesión
        print("\n=== Renovar sesión ===")
        renovada = await session_mgr.renovar_sesion("user_42")
        print(f"Sesión renovada: {renovada}")

        # Eliminamos la sesión
        print("\n=== Eliminar sesión ===")
        eliminada = await session_mgr.eliminar_sesion("user_42")
        print(f"Sesión eliminada: {eliminada}")

        # Verificamos que ya no existe
        sesion = await session_mgr.obtener_sesion("user_42")
        print(f"Sesión después de eliminar: {sesion}")

    await fake.aclose()
    print("\nManager personalizado completado")


if __name__ == "__main__":
    asyncio.run(main())
