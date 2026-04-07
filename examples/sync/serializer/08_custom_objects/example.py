"""Serialization of custom objects with default=str.

This example shows how to serialize objects from custom classes
using json.dumps with the default=str parameter to convert
non-serializable objects.
"""

import json
from dataclasses import asdict, dataclass

from wredis._serializer import deserialize, serialize


@dataclass
class Product:
    """Class representing a product."""

    name: str
    price: float
    stock: int


@dataclass
class Cart:
    """Class representing a shopping cart."""

    user: str
    products: list
    total: float


# Serialize a dictionary from a dataclass
product = Product("Laptop", 999.99, 5)
product_data = asdict(product)
serialized = serialize(product_data)
print(f"Original product: {product}")
print(f"As dictionary: {product_data}")
print(f"Serialized: {serialized}")
restored = deserialize(serialized)
print(f"Deserialized: {restored}")
print()

# Cart with multiple products
cart = Cart(
    user="maria@email.com",
    products=[
        {"name": "Mouse", "price": 25.50, "quantity": 2},
        {"name": "Keyboard", "price": 75.00, "quantity": 1},
    ],
    total=126.00,
)
serialized = serialize(asdict(cart))
print(f"Original cart: {cart}")
print(f"Serialized: {serialized}")
restored = deserialize(serialized)
print(f"Deserialized: {restored}")
print(f"Cart total: ${restored['total']}")
