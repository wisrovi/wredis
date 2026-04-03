"""Demostración de degradación elegante ante fallos de Redis.

Muestra cómo continuar operando con funcionalidad reducida
cuando Redis no está disponible, en lugar de fallar por completo.
"""

from wredis._exceptions import (
    CacheError,
    RedisConnectionError,
    WRedisError,
)


class CacheConDegradacion:
    """Caché que se degrada elegantemente cuando Redis falla.

    Cuando Redis no está disponible, usa un diccionario en memoria
    como fallback para mantener la funcionalidad básica.
    """

    def __init__(self):
        self._redis_disponible = False
        self._cache_memoria = {}
        self._modo_degradado = False

    def simular_fallo_redis(self, disponible):
        """Cambia el estado de disponibilidad de Redis.

        Args:
            disponible: True si Redis está operativo.
        """
        self._redis_disponible = disponible

    def _simular_operacion_redis(self, operacion, *args):
        """Simula una operación en Redis.

        Raises:
            RedisConnectionError: Si Redis no está disponible.
        """
        if not self._redis_disponible:
            raise RedisConnectionError("Redis no está disponible")
        return operacion(*args)

    def obtener(self, clave):
        """Obtiene un valor del caché con degradación elegante.

        Args:
            clave: La clave a buscar.

        Returns:
            El valor almacenado o None si no existe.
        """
        try:
            return self._simular_operacion_redis(self._get_redis, clave)
        except RedisConnectionError:
            self._activar_modo_degradado()
            return self._cache_memoria.get(clave)

    def guardar(self, clave, valor):
        """Guarda un valor en el caché con degradación elegante.

        Args:
            clave: La clave.
            valor: El valor a almacenar.

        Returns:
            True si se guardó en Redis, False si fue en memoria.
        """
        try:
            self._simular_operacion_redis(self._set_redis, clave, valor)
            return True
        except RedisConnectionError:
            self._activar_modo_degradado()
            self._cache_memoria[clave] = valor
            return False

    def _get_redis(self, clave):
        return None

    def _set_redis(self, clave, valor):
        pass

    def _activar_modo_degradado(self):
        if not self._modo_degradado:
            self._modo_degradado = True
            print("  [AVISO] Modo degradado activado: usando caché en memoria")


# Demostración
cache = CacheConDegradacion()

# Escenario 1: Redis disponible
print("=== Escenario 1: Redis disponible ===")
cache.simular_fallo_redis(True)
exitoso = cache.guardar("usuario:1", {"nombre": "Ana"})
print(f"Guardado en Redis: {exitoso}")
valor = cache.obtener("usuario:1")
print(f"Valor obtenido: {valor}")

# Escenario 2: Redis cae, degradación automática
print("\n=== Escenario 2: Redis cae, degradación elegante ===")
cache.simular_fallo_redis(False)
exitoso = cache.guardar("usuario:2", {"nombre": "Bob"})
print(f"Guardado (fallback memoria): {exitoso}")
valor = cache.obtener("usuario:2")
print(f"Valor obtenido desde memoria: {valor}")

# Escenario 3: Múltiples operaciones en modo degradado
print("\n=== Escenario 3: Operaciones continuas en modo degradado ===")
for i in range(3):
    cache.guardar(f"temp:{i}", f"valor_{i}")

for i in range(3):
    valor = cache.obtener(f"temp:{i}")
    print(f"  temp:{i} = {valor}")

# Escenario 4: Clase base para servicios con degradación
print("\n=== Escenario 4: Servicio con degradación elegante ===")


class ServicioConFallback:
    """Patrón genérico para servicios con fallback."""

    def __init__(self, nombre):
        self.nombre = nombre

    def ejecutar(self, operacion, fallback=None):
        """Ejecuta una operación con fallback ante fallos de Redis.

        Args:
            operacion: Función que ejecuta la operación principal.
            fallback: Función alternativa si Redis falla.

        Returns:
            Resultado de la operación principal o del fallback.
        """
        try:
            return operacion()
        except (RedisConnectionError, CacheError) as exc:
            print(f"  [{self.nombre}] Redis falló: {exc}")
            if fallback:
                print(f"  [{self.nombre}] Usando fallback")
                return fallback()
            return None


def obtener_de_redis():
    raise RedisConnectionError("Conexión rechazada")


def obtener_de_bd():
    return {"fuente": "base_de_datos", "datos": "respuesta alternativa"}


servicio = ServicioConFallback("Usuarios")
resultado = servicio.ejecutar(obtener_de_redis, fallback=obtener_de_bd)
print(f"  Resultado: {resultado}")
