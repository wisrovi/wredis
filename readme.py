from pathlib import Path

# Cargar ejemplos desde el archivo README de la carpeta examples
examples_path = Path("examples/README.md")
main_readme_path = Path("README_template.md")

with open(examples_path, "r") as examples_file:
    examples_content = examples_file.read()

# Leer el README principal y añadir ejemplos
with open(main_readme_path, "r") as readme_file:
    main_readme = readme_file.read()

updated_readme = main_readme.replace("# Aquí se insertarán automáticamente los ejemplos", examples_content)

# Escribir el README actualizado
with open(main_readme_path, "w") as readme_file:
    readme_file.write(updated_readme)

print("README.md actualizado con los ejemplos.")
