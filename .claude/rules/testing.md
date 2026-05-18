# Reglas de testing — ejem1-project

## Estructura de los tests

- Los tests viven en `tests/` en la raíz del proyecto; nunca dentro de `src/`.
- Un módulo de test por módulo de producción: `src/ejem1/parser.py` → `tests/test_parser.py`.
- Los tests de integración van en `tests/integration/`; los unitarios directamente en `tests/`.
- Cada fichero de test importa desde el paquete instalado (`from ejem1.xxx import yyy`), nunca por ruta relativa.

## Nomenclatura

- Patrón: `test_<unidad_bajo_prueba>_<escenario>_<resultado_esperado>`.
  - Ejemplo: `test_parse_empty_string_returns_empty_list`
  - Ejemplo: `test_main_with_valid_input_prints_greeting`
- Los nombres deben ser autoexplicativos; si necesitas un comentario para entender el test, renómbralo.

## Tests unitarios

- Prueban una sola unidad (función, método o clase) en aislamiento.
- Sin dependencias externas reales (I/O, red, base de datos); usa `monkeypatch` o `unittest.mock` solo cuando sea estrictamente necesario y documenta por qué.
- Cada test tiene exactamente un `assert` lógico; varios `assert` están permitidos si verifican el mismo resultado.
- No compartas estado entre tests; cada test debe poder ejecutarse en cualquier orden.

## Tests de integración

- Prueban la colaboración entre dos o más módulos o con dependencias externas reales.
- Ubícalos en `tests/integration/`; márcalos con el marcador `@pytest.mark.integration`.
- Pueden usar fixtures de sesión (`scope="session"`) para recursos costosos (conexiones, ficheros temporales).
- Nunca mezcles lógica de test unitario e integración en el mismo fichero.

## Casos generales

- Cubre el flujo principal («happy path»): entrada válida y representativa que produce el resultado esperado.
- Un test por comportamiento observable, no por línea de código.
- Usa fixtures de pytest para datos de entrada reutilizables; evita literales duplicados.

## Casos de borde

- Cubre los límites del dominio: valor mínimo, valor máximo, colecciones vacías, cadenas vacías, `None`.
- Para numéricos: `0`, `1`, `-1`, y los valores en los extremos del rango válido.
- Para cadenas: cadena vacía `""`, un solo carácter, longitud máxima permitida, caracteres especiales y Unicode.
- Para colecciones: lista vacía `[]`, un elemento, orden inverso, duplicados.
- Cada caso de borde debe tener su propio test con nombre que describa el límite probado.

## Casos específicos (errores y excepciones)

- Verifica que se lanza la excepción correcta ante entrada inválida usando `pytest.raises`:
  ```python
  with pytest.raises(ValueError, match="mensaje esperado"):
      funcion_bajo_prueba(entrada_invalida)
  ```
- Prueba el comportamiento ante tipos incorrectos (`TypeError`) en los límites del sistema.
- Un test por tipo de excepción esperada; no uses un solo test para múltiples excepciones.

## Fixtures y datos de prueba

- Define fixtures en `conftest.py` al nivel más bajo posible (raíz o subdirectorio).
- Usa `tmp_path` de pytest para ficheros temporales; nunca crees ficheros en rutas absolutas.
- Parametriza con `@pytest.mark.parametrize` cuando el mismo comportamiento se verifica con múltiples entradas:
  ```python
  @pytest.mark.parametrize("entrada,esperado", [
      ("hola", "HOLA"),
      ("",     ""),
  ])
  def test_upper(entrada, esperado):
      assert upper(entrada) == esperado
  ```

## Cobertura y calidad

- Objetivo mínimo: 80 % de cobertura de líneas en `src/`; ejecuta con `pytest --cov=src`.
- Un test que siempre pasa no aporta valor; verifica que falla al romper la implementación.
- Sin `time.sleep` en tests; usa mocks para el tiempo o eventos síncronos.
- Los tests deben ser deterministas: no dependas de fechas actuales, orden de dicts, o valores aleatorios sin semilla fija.
