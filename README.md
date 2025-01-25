# wredis


my_project/
├── .github/
│   └── workflows/
│       └── release-to-pypi.yml  # Archivo de configuración para GitHub Actions
├── my_project/                  # Carpeta con el código fuente
│   ├── __init__.py              # Marca la carpeta como módulo de Python
│   └── main.py                  # Archivo principal (puede tener otros módulos)
├── tests/                       # Carpeta con pruebas del proyecto
│   ├── __init__.py
│   └── test_main.py             # Archivo de pruebas (puedes agregar más)
├── LICENSE                      # Licencia del proyecto (ej. MIT, Apache)
├── README.md                    # Descripción del proyecto
├── setup.py                     # Configuración de empaquetado para PyPI
├── pyproject.toml               # Configuración moderna para herramientas de empaquetado
├── requirements.txt             # Dependencias del proyecto
├── .gitignore                   # Archivos y carpetas ignorados por Git
└── dist/                        # Carpeta donde se generarán los paquetes (se crea al construir el paquete)
