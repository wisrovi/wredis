"""Serialización de objetos personalizados con default=str.

Este ejemplo muestra cómo serializar objetos de clases
personalizadas utilizando json.dumps con el parámetro
default=str para convertir objetos no serializables.
"""

import json
from dataclasses import dataclass, asdict

from wredis._serializer import serialize, deserialize


@dataclass
class Producto:
    """Clase que representa un producto."""

    nombre: str
    precio: float
    stock: int


@dataclass
class Carrito:
    """Clase que representa un carrito de compras."""

    usuario: str
    productos: list
    total: float


# Serializar un diccionario derivado de un dataclass
producto = Producto("Laptop", 999.99, 5)
datos_producto = asdict(producto)
serialized = serialize(datos_producto)
print(f"Producto original: {producto}")
print(f"Como diccionario: {datos_producto}")
print(f"Serializado: {serialized}")
restored = deserialize(serialized)
print(f"Deserializado: {restored}")
print()

# Carrito con múltiples productos
carrito = Carrito(
    usuario="maria@email.com",
    productos=[
        {"nombre": "Mouse", "precio": 25.50, "cantidad": 2},
        {"nombre": "Teclado", "precio": 75.00, "cantidad": 1},
    ],
    total=126.00,
)
serialized = serialize(asdict(carrito))
print(f"Carrito original: {carrito}")
print(f"Serializado: {serialized}")
restored = deserialize(serialized)
print(f"Deserializado: {restored}")
print(f"Total del carrito: ${restored['total']}")
