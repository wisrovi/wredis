"""Serialización de cadenas de texto muy largas.

Este ejemplo demuestra el comportamiento del serializador
con cadenas de texto extremadamente largas, como las que
podrían encontrarse al almacenar logs o contenido de archivos.
"""

from wredis._serializer import serialize, deserialize

# Crear una cadena larga simulando un log
lineas_log = [f"[2024-01-{i:02d} 10:{i:02d}:00] INFO: Proceso completado exitosamente" for i in range(1, 101)]
log_completo = "\n".join(lineas_log)

print(f"Longitud del log: {len(log_completo)} caracteres")
print(f"Primeras 80 chars: {log_completo[:80]}...")

# Serializar
serialized = serialize(log_completo)
print(f"\nTamaño serializado: {len(serialized)} caracteres")

# Deserializar
restored = deserialize(serialized)
print(f"Longitud deserializada: {len(restored)} caracteres")
print(f"¿Contenido intacto? {log_completo == restored}")
print()

# Cadena con caracteres de escape
texto_con_escapes = 'Ruta: C:\\Users\\admin\\docs\nNueva línea\tTabulador\n"Comillas"'
serialized = serialize(texto_con_escapes)
print(f"Texto con escapes: {texto_con_escapes!r}")
print(f"Serializado: {serialized}")
restored = deserialize(serialized)
print(f"Deserializado: {restored!r}")
print(f"¿Contenido intacto? {texto_con_escapes == restored}")
