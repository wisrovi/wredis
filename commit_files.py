import os
import subprocess


def run_command(command):
    if isinstance(command, str):
        import shlex

        args = shlex.split(command)
    else:
        args = command
    result = subprocess.run(args, check=False, capture_output=True, text=True)
    return result.stdout.strip()


def main():
    # Obtener el status de git
    status_output = run_command("git status --short")
    if not status_output:
        print("No hay cambios para procesar.")
        return

    lines = status_output.split("\n")
    for line in lines:
        if not line.strip():
            continue

        # git status --short devuelve algo como "M path/to/file" o "?? path/to/file"
        parts = line.split(maxsplit=1)
        if len(parts) < 2:
            continue

        status = parts[0]
        file_path = parts[1].strip('"')  # Eliminar comillas si las hay

        if status == "M":
            msg = f"Update {file_path}"
        elif status == "??":
            msg = f"Add {file_path}"
        else:
            msg = f"Modified {file_path} ({status})"

        print(f"Committing: {file_path} with message: {msg}")

        # Añadir y commitear
        subprocess.run(["git", "add", file_path], check=False)
        subprocess.run(["git", "commit", "-m", msg], check=False)


if __name__ == "__main__":
    main()
