# CLAUDE.md

Este fichero proporciona orientación a Claude Code (claude.ai/code) al trabajar con el código de este repositorio.

## Configuración

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Estándares
- Python 3.11+
- Comentarios en español
- Funciones con docstrings siempre

## Comandos

```bash
export PYTHONPATH=/home/alvaro/workspace-claude/ejem1-project/src

# Ejecutar todos los tests
pytest

# Ejecutar un test concreto
pytest tests/test_main.py::test_main++

# Ejecutar el comando CLI
ejem1
```

## Arquitectura

El paquete usa un layout `src/`. El código de la aplicación está en `src/ejem1/`; los tests están en `tests/` en la raíz del proyecto e importan desde el paquete instalado.

- `src/ejem1/main.py` — punto de entrada; `main()` está conectado al comando CLI `ejem1` mediante `pyproject.toml`
- `tests/` — tests de pytest; usar `capsys` para capturar stdout al testear `main()`

<!-- CONTROL DE VERSIONES -->
## Ramas
- Features: feature/TICKET-123-descripcion-corta
- Bugfixes: bugfix/TICKET-456-descripcion
- Hotfixes: hotfix/descripcion

## Commits (Conventional Commits)
- feat: nueva funcionalidad
- fix: corrección de bug
- docs: cambios en documentación
- refactor: refactorización sin cambios funcionales
- test: añadir o modificar tests