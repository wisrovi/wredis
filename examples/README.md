# Ejemplos de WRedis

## 📁 Estructura de Ejemplos

```
examples/
├── sync/                    # Ejemplos síncronos
│   ├── basic/              # Operacion basica con Redis
│   │   ├── hash/          # Operaciones con hashes
│   │   ├── pubsub/        # Publicacion y suscripcion
│   │   ├── streams/       # Redis Streams
│   │   ├── queue/        # Colas de mensajes
│   │   ├── sorted_set/  # Conjuntos ordenados
│   │   ├── sets/        # Conjuntos
│   │   ├── bitmap/      # Bitmaps
│   │   ├── cache/       # Decoradores de cache
│   │   ├── geo/         # Operaciones geograficas
│   │   └── hyperloglog/ # HyperLogLog
│   ├── sentinel/         # Alta disponibilidad con Sentinel
│   │   ├── hash/
│   │   ├── pubsub/
│   │   ├── streams/
│   │   ├── queue/
│   │   └── connection/
│   └── cluster/          # Redis Cluster
│       ├── hash/
│       ├── pubsub/
│       ├── streams/
│       ├── queue/
│       └── pipeline/
│
├── async/                  # Ejemplos asíncronos
│   ├── basic/            # Operacion basica async
│   ├── sentinel/         # Sentinel async
│   └── cluster/         # Cluster async
│
└── test/                 # Tests de ejemplos (coverage 100%)
    ├── conftest.py
    ├── test_sync_*.py
    └── test_async_*.py
```

## 🎯 Cómo Usar Esta Guía

### 1. Encuentra tu caso de uso

| Necesidad | Carpeta |
|----------|---------|
| Operaciones básicas con Redis | `sync/basic/` |
| Alta disponibilidad (Sentinel) | `sync/sentinel/` |
| Redis Cluster | `sync/cluster/` |
| Código async (FastAPI, AI) | `async/` |

### 2. Selecciona la funcionalidad

| Funcionalidad | Descripción |
|--------------|-------------|
| `hash/` | Almacenamiento key-value |
| `pubsub/` | Mensajería pub/sub |
| `streams/` | Streams de Redis |
| `queue/` | Colas de mensajes |
| `sorted_set/` | Conjuntos ordenados |
| `sets/` | Conjuntos |
| `bitmap/` | Bitmaps |
| `cache/` | Decoradores de caché |

### 3. Ejecuta el ejemplo

```bash
# Ejecutar un ejemplo
cd examples/sync/basic/hash
python 01_create.py

# Ejecutar todos los ejemplos de una carpeta
for f in *.py; do python "$f"; done
```

## 📋 Ejemplos por Nivel

### Nivel 1: Básico (01-05)
- `01_*.py` - Crear/Insertar
- `02_*.py` - Leer
- `03_*.py` - Actualizar
- `04_*.py` - Eliminar
- `05_*.py` - TTL/Expiracion

### Nivel 2: Intermedio (06-10)
- `06_*.py` - JSON/Serializacion
- `07_*.py` - Operaciones batch
- `08_*.py` - Patrones
- `09_*.py` - Migracion
- `10_*.py` - Mejores practicas

### Nivel 3: Avanzado (11-20)
- `11_*.py` - Transacciones
- `12_*.py` - Pipelines
- `13_*.py` - Rendimiento
- `14_*.py` - Debugging
- `15-20_*.py` - Casos especiales

## 🧪 Tests

```bash
# Ejecutar todos los tests
cd examples/test
pytest -v --cov=../../wredis --cov-report=html

# Coverage 100%
pytest --cov=../../wredis --cov-fail-under=100
```

## 📚 Documentación

Cada carpeta contiene un `README.md` con:
- Descripcion de la funcionalidad
- Diagrama de arquitectura (Mermaid)
- Requisitos previos
- Explicacion de cada ejemplo

## 🚀 Inicio Rapido

```python
# Ejemplo basico - Crear un hash
from wredis.hash import RedisHashManager

manager = RedisHashManager(host="localhost")
manager.create_hash("mi_hash", "mi_clave", {"dato": "valor"})

# Leer el dato
resultado = manager.read_hash("mi_hash", "mi_clave")
print(resultado)  # {'dato': 'valor'}
```

## ⚠️ Requisitos

- Python 3.10+
- Redis ejecutandose en localhost:6379
- `pip install wredis`

## 📞 Soporte

- GitHub Issues: https://github.com/wisrovi/wredis/issues
- Documentacion: https://wisrovi.github.io/wredis/
