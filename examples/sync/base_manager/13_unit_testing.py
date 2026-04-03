"""Ejemplo 13: Pruebas unitarias con BaseManager y fakeredis.

Demuestra cómo escribir pruebas unitarias para código que usa
BaseManager, utilizando fakeredis para simular Redis sin necesidad
de un servidor real.
"""

import fakeredis

from wredis._base import BaseManager


def crear_manager_prueba() -> BaseManager:
    """Crea un manager configurado para pruebas con fakeredis.

    Returns:
        BaseManager configurado con FakeRedis.
    """
    manager = BaseManager(verbose=False, decode_responses=True)
    manager.redis_client = fakeredis.FakeRedis(decode_responses=True)
    return manager


def test_health_check():
    """Prueba que health_check devuelve True con conexión activa."""
    manager = crear_manager_prueba()
    try:
        assert manager.health_check() is True
        print("  [PASS] test_health_check")
    finally:
        manager.close()


def test_set_get():
    """Prueba operaciones básicas de SET y GET."""
    manager = crear_manager_prueba()
    try:
        manager._execute("set", "test:clave", "valor_prueba")
        resultado = manager._execute("get", "test:clave")
        assert resultado == "valor_prueba"
        print("  [PASS] test_set_get")
    finally:
        manager.close()


def test_delete():
    """Prueba operación de DELETE."""
    manager = crear_manager_prueba()
    try:
        manager._execute("set", "test:eliminar", "temporal")
        assert manager._execute("get", "test:eliminar") == "temporal"
        manager._execute("delete", "test:eliminar")
        assert manager._execute("get", "test:eliminar") is None
        print("  [PASS] test_delete")
    finally:
        manager.close()


def test_list_operations():
    """Prueba operaciones con listas."""
    manager = crear_manager_prueba()
    try:
        manager._execute("lpush", "test:lista", "elem1", "elem2", "elem3")
        longitud = manager._execute("llen", "test:lista")
        assert longitud == 3
        elemento = manager._execute("rpop", "test:lista")
        assert elemento == "elem1"
        print("  [PASS] test_list_operations")
    finally:
        manager.close()


def test_hash_operations():
    """Prueba operaciones con hashes."""
    manager = crear_manager_prueba()
    try:
        manager._execute("hset", "test:hash", mapping={"campo1": "valor1", "campo2": "valor2"})
        valor = manager._execute("hget", "test:hash", "campo1")
        assert valor == "valor1"
        todos = manager._execute("hgetall", "test:hash")
        assert len(todos) == 2
        print("  [PASS] test_hash_operations")
    finally:
        manager.close()


def test_context_manager():
    """Prueba que el gestor de contexto funciona correctamente."""
    with BaseManager(verbose=False) as manager:
        manager.redis_client = fakeredis.FakeRedis(decode_responses=True)
        manager._execute("set", "test:contexto", "ok")
        assert manager._execute("get", "test:contexto") == "ok"
    print("  [PASS] test_context_manager")


def test_verbose_mode():
    """Prueba que el modo verbose controla el logging."""
    manager = BaseManager(verbose=False)
    manager.redis_client = fakeredis.FakeRedis(decode_responses=True)
    assert manager.verbose is False
    # No debería generar errores al llamar log con verbose=False
    manager.log("mensaje de prueba", level="debug")
    manager.close()
    print("  [PASS] test_verbose_mode")


# Ejecutamos todas las pruebas
print("=== Pruebas Unitarias con BaseManager ===\n")
print("Ejecutando pruebas:\n")

test_health_check()
test_set_get()
test_delete()
test_list_operations()
test_hash_operations()
test_context_manager()
test_verbose_mode()

print("\nTodas las pruebas pasaron exitosamente")
