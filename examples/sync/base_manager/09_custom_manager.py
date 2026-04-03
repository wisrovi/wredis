"""Ejemplo 09: Creación de un gestor personalizado extendiendo BaseManager.

Demuestra cómo crear una clase personalizada que hereda de BaseManager
para agregar funcionalidad específica de la aplicación.
"""

import fakeredis

from wredis._base import BaseManager


class MiGestorCache(BaseManager):
    """Gestor de caché personalizado que extiende BaseManager.

    Agrega métodos de conveniencia para operaciones comunes de caché
    con tiempos de expiración y prefijos de claves.
    """

    def __init__(self, prefijo: str = "cache", ttl: int = 300, **kwargs):
        """Inicializa el gestor de caché.

        Args:
            prefijo: Prefijo para todas las claves de caché.
            ttl: Tiempo de vida por defecto en segundos.
            **kwargs: Argumentos adicionales para BaseManager.
        """
        super().__init__(**kwargs)
        self.prefijo = prefijo
        self.ttl = ttl

    def _clave_completa(self, clave: str) -> str:
        """Genera la clave completa con el prefijo."""
        return f"{self.prefijo}:{clave}"

    def almacenar(self, clave: str, valor: str) -> bool:
        """Almacena un valor en caché con TTL.

        Args:
            clave: Clave del valor.
            valor: Valor a almacenar.

        Returns:
            True si se almacenó correctamente.
        """
        clave_completa = self._clave_completa(clave)
        return self._execute("setex", clave_completa, self.ttl, valor)

    def obtener(self, clave: str) -> str | None:
        """Obtiene un valor de la caché.

        Args:
            clave: Clave del valor.

        Returns:
            El valor almacenado o None si no existe.
        """
        clave_completa = self._clave_completa(clave)
        return self._execute("get", clave_completa)

    def eliminar(self, clave: str) -> bool:
        """Elimina un valor de la caché.

        Args:
            clave: Clave a eliminar.

        Returns:
            True si se eliminó correctamente.
        """
        clave_completa = self._clave_completa(clave)
        return bool(self._execute("delete", clave_completa))

    def estadisticas(self) -> dict:
        """Obtiene estadísticas del gestor de caché.

        Returns:
            Diccionario con información del gestor.
        """
        return {
            "prefijo": self.prefijo,
            "ttl": self.ttl,
            "verbose": self.verbose,
            "tipo_pool": type(self._pool).__name__,
        }


# Demostración del gestor personalizado
print("=== Gestor Personalizado Extendiendo BaseManager ===\n")

with MiGestorCache(prefijo="miapp", ttl=600, verbose=False) as cache:
    # Reemplazamos con FakeRedis para las pruebas
    cache.redis_client = fakeredis.FakeRedis(decode_responses=True)

    # Mostramos estadísticas del gestor
    stats = cache.estadisticas()
    print("Estadísticas del gestor:")
    for clave, valor in stats.items():
        print(f"  {clave}: {valor}")

    # Almacenamos valores en caché
    print("\nAlmacenando valores en caché:")
    cache.almacenar("usuario:1", '{"nombre": "Ana", "rol": "admin"}')
    print("  Usuario 1 almacenado")

    cache.almacenar("usuario:2", '{"nombre": "Carlos", "rol": "usuario"}')
    print("  Usuario 2 almacenado")

    # Recuperamos valores
    print("\nRecuperando valores de caché:")
    usuario1 = cache.obtener("usuario:1")
    print(f"  Usuario 1: {usuario1}")

    usuario2 = cache.obtener("usuario:2")
    print(f"  Usuario 2: {usuario2}")

    # Eliminamos un valor
    print("\nEliminando valor:")
    cache.eliminar("usuario:1")
    usuario1_eliminado = cache.obtener("usuario:1")
    print(f"  Usuario 1 después de eliminar: {usuario1_eliminado}")

print("\nGestor personalizado cerrado correctamente")
