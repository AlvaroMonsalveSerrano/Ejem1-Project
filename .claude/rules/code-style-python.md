# Reglas de estilo Python — ejem1-project

## Estructura del proyecto
- Layout `src/`: el código de la aplicación vive en `src/ejem1/`; nunca coloques módulos en la raíz.
- Los tests van en `tests/` en la raíz, importando desde el paquete instalado (`from ejem1.xxx import yyy`).
- El punto de entrada CLI es `src/ejem1/main.py`; la función `main()` está registrada en `pyproject.toml`.

## Tests
- Framework: pytest.
- Para capturar stdout usa el fixture `capsys` de pytest; no redirijas `sys.stdout` manualmente.
- Cada test debe ser independiente y no depender del orden de ejecución.

## Commits (Conventional Commits)
- `feat:` nueva funcionalidad
- `fix:` corrección de bug
- `docs:` cambios en documentación
- `refactor:` refactorización sin cambios funcionales
- `test:` añadir o modificar tests

## Estilo de código
- Sigue PEP 8 estrictamente: 4 espacios de indentación, máximo 88 caracteres por línea (compatible con Black).
- Nombres descriptivos y en inglés: `snake_case` para variables y funciones, `PascalCase` para clases, `UPPER_SNAKE_CASE` para constantes.
- Anota los tipos en todas las funciones públicas (`def main() -> None`, `def parse(text: str) -> list[str]`).
- Sin comentarios salvo que el motivo no sea obvio por el nombre del símbolo; nunca describas lo que hace el código, solo el porqué.
- Sin docstrings multilínea en funciones privadas o triviales; una línea concisa si el contrato no es evidente.
- Importaciones ordenadas: stdlib → third-party → proyecto; usa `isort` o el orden de `ruff`.
- Prefiere expresiones idiomáticas de Python: comprensiones de lista, `pathlib` sobre `os.path`, f-strings sobre `.format()`.
- No añadas manejo de errores para escenarios imposibles; confía en las garantías del framework y lanza excepciones concretas (`ValueError`, `TypeError`) en los límites del sistema.
- Sin código muerto, variables no usadas ni imports superfluos; el linter es la referencia final.
