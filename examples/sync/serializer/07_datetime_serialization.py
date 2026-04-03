"""Serialización de fechas y horas usando datetime.

Este ejemplo demuestra cómo serializar objetos datetime
convirtiéndolos a cadenas ISO 8601, ya que json.dumps no
soporta datetime nativamente. Se usa el parámetro default=str
para la conversión automática.
"""

import json
from datetime import datetime, date, time, timedelta

from wredis._serializer import serialize, deserialize

# Convertir datetime a cadena ISO antes de serializar
ahora = datetime.now()
fecha_str = ahora.isoformat()
serialized = serialize(fecha_str)
print(f"datetime original: {ahora}")
print(f"Convertido a ISO: {fecha_str}")
print(f"Serializado: {serialized}")
restored = deserialize(serialized)
print(f"Deserializado: {restored}")
print(f"Reconvertido a datetime: {datetime.fromisoformat(restored)}")
print()

# Fecha (date) como cadena
hoy = date.today()
fecha_str = hoy.isoformat()
serialized = serialize(fecha_str)
print(f"date original: {hoy}")
print(f"Convertido a ISO: {fecha_str}")
print(f"Serializado: {serialized}")
print(f"Deserializado: {deserialize(serialized)}")
print()

# Diccionario con múltiples campos de fecha
registro = {
    "evento": "conferencia",
    "fecha_inicio": date(2024, 6, 15).isoformat(),
    "fecha_fin": date(2024, 6, 17).isoformat(),
    "creado_en": datetime(2024, 1, 1, 10, 30, 0).isoformat(),
}
serialized = serialize(registro)
print(f"Registro con fechas: {registro}")
print(f"Serializado: {serialized}")
restored = deserialize(serialized)
print(f"Deserializado: {restored}")
print(f"Fecha inicio como date: {date.fromisoformat(restored['fecha_inicio'])}")
