
from pathlib import Path
from setuptools import setup, find_packages


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="wredis",  # Nombre del paquete en PyPI
    version="0.1.0",  # Versión inicial
    packages=find_packages(),
    install_requires=[
        "redis",
        "loguru",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Build Tools",
        "Intended Audience :: Developers",
    ],
    description="Redis easy control",
    long_description_content_type="text/markdown",
    long_description=long_description,
    url="https://github.com/wisrovi/wredis",
    author="William Steve Rodriguez Villamizar",
    author_email="wisrovi.rodriguez@gmail.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6, <3.12",  # Requiere Python >=3.6 y <3.10
)
