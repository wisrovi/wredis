"""Error handling in serialization.

This example shows how to catch and handle SerializationError
exceptions when trying to serialize objects that are not
compatible with JSON.
"""

from wredis._exceptions import SerializationError
from wredis._serializer import deserialize, serialize

# Try to serialize a set - not serializable in JSON
try:
    my_set = {1, 2, 3}
    serialize(my_set)
except SerializationError as e:
    print(f"Error serializing set: {e}")
print()

# Try to serialize a function - not serializable
try:

    def my_function():
        pass

    serialize(my_function)
except SerializationError as e:
    print(f"Error serializing function: {e}")
print()


# Try to serialize a custom complex object
class MyClass:
    pass


try:
    obj = MyClass()
    serialize(obj)
except SerializationError as e:
    print(f"Error serializing custom object: {e}")
print()

# Deserialization with invalid JSON
try:
    deserialize("{this is not valid json}")
except SerializationError as e:
    print(f"Error deserializing invalid JSON: {e}")
print()

# Deserialization with non-string input
try:
    deserialize(12345)
except SerializationError as e:
    print(f"Error deserializing non-string: {e}")
