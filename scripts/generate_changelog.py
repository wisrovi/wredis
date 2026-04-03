#!/usr/bin/env python3
"""
Generador de changelog para WRedis.

Lee el historial de git desde la última etiqueta (o desde una etiqueta específica)
y genera un changelog formateado en Markdown, categorizando los commits por tipo.

Uso:
    python scripts/generate_changelog.py              # Desde la última etiqueta
    python scripts/generate_changelog.py v0.9.0       # Desde la etiqueta v0.9.0
    python scripts/generate_changelog.py --output CHANGELOG.md  # Guardar en archivo

Categorías de commits:
    feat:     Nuevas funcionalidades
    fix:      Correcciones de errores
    docs:     Cambios en documentación
    refactor: Refactorización de código
    test:     Cambios en pruebas
    chore:    Tareas de mantenimiento
    perf:     Mejoras de rendimiento
    ci:       Cambios en integración continua
    build:    Cambios en el sistema de compilación
"""

import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime


# ---------------------------------------------------------------------------
# Mapeo de tipos de commit a secciones del changelog
# ---------------------------------------------------------------------------

CATEGORY_MAP = {
    "feat": "🚀 Nuevas funcionalidades",
    "fix": "🐛 Correcciones de errores",
    "docs": "📚 Documentación",
    "refactor": "♻️ Refactorización",
    "test": "✅ Pruebas",
    "chore": "🔧 Mantenimiento",
    "perf": "⚡ Rendimiento",
    "ci": "🏗️ Integración continua",
    "build": "📦 Compilación",
}

# Orden en que aparecen las secciones
CATEGORY_ORDER = ["feat", "fix", "docs", "refactor", "perf", "test", "ci", "build", "chore"]

# Expresión regular para parsear commits tipo Conventional Commits
# Ejemplos: "feat: add async support", "fix(hash): resolve serialization bug"
COMMIT_PATTERN = re.compile(
    r"^(?P<type>[a-z]+)"  # Tipo del commit
    r"(?:\((?P<scope>[^)]+)\))?"  # Alcance opcional entre paréntesis
    r"(?:\!)?:\s*"  # ! opcional para breaking changes
    r"(?P<message>.+)$"  # Mensaje del commit
)


def run_git(args: list[str]) -> str:
    """Ejecuta un comando de git y devuelve su salida.

    Args:
        args: Lista de argumentos para el comando git.

    Returns:
        Salida estándar del comando.

    Raises:
        RuntimeError: Si el comando git falla.
    """
    result = subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error ejecutando git {' '.join(args)}: {result.stderr}")
    return result.stdout


def get_last_tag() -> str | None:
    """Obtiene la última etiqueta del repositorio.

    Returns:
        Nombre de la última etiqueta, o None si no hay etiquetas.
    """
    try:
        tags = run_git(["tag", "--sort=-v:refname"])
        if tags.strip():
            return tags.strip().split("\n")[0]
    except RuntimeError:
        pass
    return None


def get_commits_since(tag: str | None) -> list[dict]:
    """Obtiene los commits desde una etiqueta específica.

    Si no se proporciona etiqueta, obtiene todos los commits.

    Args:
        tag: Nombre de la etiqueta desde la cual obtener commits.

    Returns:
        Lista de diccionarios con información de cada commit.
    """
    if tag:
        log_format = "%H|%s|%aI"  # hash|mensaje|fecha ISO
        raw_log = run_git(["log", f"{tag}..HEAD", f"--format={log_format}"])
    else:
        log_format = "%H|%s|%aI"
        raw_log = run_git(["log", f"--format={log_format}"])

    commits = []
    for line in raw_log.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.split("|", 2)
        if len(parts) == 3:
            commits.append(
                {
                    "hash": parts[0][:8],  # Hash corto
                    "message": parts[1],
                    "date": parts[2],
                }
            )
    return commits


def categorize_commit(message: str) -> dict:
    """Categoriza un commit según el formato Conventional Commits.

    Args:
        message: Mensaje del commit.

    Returns:
        Diccionario con tipo, alcance, mensaje y si es breaking change.
    """
    # Detectar breaking changes (sufijo ! o BREAKING CHANGE en el cuerpo)
    is_breaking = "!" in message[:10] or "BREAKING CHANGE" in message

    match = COMMIT_PATTERN.match(message.strip())
    if match:
        commit_type = match.group("type")
        scope = match.group("scope")
        commit_message = match.group("message").strip()
    else:
        # Si no coincide con el patrón, se clasifica como "chore"
        commit_type = "chore"
        scope = None
        commit_message = message.strip()

    return {
        "type": commit_type,
        "scope": scope,
        "message": commit_message,
        "is_breaking": is_breaking,
    }


def format_changelog(commits: list[dict], version: str | None = None, date: str | None = None) -> str:
    """Genera el changelog formateado en Markdown.

    Args:
        commits: Lista de commits categorizados.
        version: Versión para el encabezado (opcional).
        date: Fecha para el encabezado (opcional).

    Returns:
        Changelog formateado como string Markdown.
    """
    # Agrupar commits por categoría
    categorized: dict[str, list[dict]] = defaultdict(list)
    breaking_changes: list[dict] = []

    for commit in commits:
        info = categorize_commit(commit["message"])
        if info["is_breaking"]:
            breaking_changes.append({**info, "hash": commit["hash"]})
        categorized[info["type"]].append({**info, "hash": commit["hash"]})

    # Construir el changelog
    lines = []

    # Encabezado
    if version:
        display_date = date or datetime.now().strftime("%Y-%m-%d")
        lines.append(f"## [{version}] - {display_date}")
    else:
        lines.append("## [Unreleased]")

    lines.append("")

    # Cambios importantes (breaking changes) primero
    if breaking_changes:
        lines.append("### ⚠️ Breaking Changes")
        lines.append("")
        for change in breaking_changes:
            scope_prefix = f"**{change['scope']}**: " if change["scope"] else ""
            lines.append(f"- {scope_prefix}{change['message']} (`{change['hash']}`)")
        lines.append("")

    # Resto de categorías en orden definido
    for category in CATEGORY_ORDER:
        if category in categorized:
            section_title = CATEGORY_MAP.get(category, category.capitalize())
            lines.append(f"### {section_title}")
            lines.append("")

            for commit in categorized[category]:
                scope_prefix = f"**{commit['scope']}**: " if commit["scope"] else ""
                lines.append(f"- {scope_prefix}{commit['message']} (`{commit['hash']}`)")

            lines.append("")

    # Si no hay commits reconocidos
    if not categorized and not breaking_changes:
        lines.append("No hay cambios significativos desde la última versión.")
        lines.append("")

    return "\n".join(lines)


def main():
    """Función principal del generador de changelog."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Genera un changelog a partir del historial de git de WRedis.",
    )
    parser.add_argument(
        "since_tag",
        nargs="?",
        default=None,
        help="Etiqueta desde la cual generar el changelog (por defecto: última etiqueta)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Archivo de salida (por defecto: imprimir en consola)",
    )
    parser.add_argument(
        "--version",
        "-v",
        default=None,
        help="Versión para el encabezado del changelog",
    )
    parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="Incluir todos los commits (ignora etiquetas)",
    )

    args = parser.parse_args()

    # Determinar desde dónde obtener los commits
    if args.all:
        tag = None
    elif args.since_tag:
        tag = args.since_tag
    else:
        tag = get_last_tag()
        if tag:
            print(f"Usando última etiqueta: {tag}", file=sys.stderr)
        else:
            print("No se encontraron etiquetas. Obteniendo todos los commits.", file=sys.stderr)

    # Obtener y procesar commits
    try:
        commits = get_commits_since(tag)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not commits:
        print("No hay commits nuevos desde la última etiqueta.", file=sys.stderr)
        sys.exit(0)

    print(f"Procesando {len(commits)} commits...", file=sys.stderr)

    # Generar changelog
    changelog = format_changelog(commits, version=args.version)

    # Mostrar o guardar resultado
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(changelog)
        print(f"Changelog guardado en: {args.output}", file=sys.stderr)
    else:
        print(changelog)


if __name__ == "__main__":
    main()
