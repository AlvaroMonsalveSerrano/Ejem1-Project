# SPEC.md — API REST de Gestión de Biblioteca

## 1. Resumen del sistema

API REST para la gestión de libros y autores de una biblioteca. Permite realizar operaciones CRUD sobre ambas entidades y gestiona la relación muchos-a-muchos entre ellas, incluyendo la fecha de contribución de cada autor a cada libro.

---

## 2. Stack tecnológico

| Componente     | Tecnología                          |
|---------------|-------------------------------------|
| Framework      | FastAPI                             |
| ORM            | SQLAlchemy 2.x                      |
| Base de datos  | SQLite en memoria (`sqlite:///:memory:`) |
| Validación     | Pydantic v2 (integrado en FastAPI)  |
| Testing        | pytest + `httpx.TestClient` de FastAPI |
| Documentación  | OpenAPI 3.x (generada automáticamente por FastAPI en `/docs`) |
| Python         | 3.11+                               |

---

## 3. Modelo de datos

### 3.1 Entidades

#### `Author` (Autor)

| Campo        | Tipo              | Restricciones                             |
|-------------|-------------------|--------------------------------------------|
| `id`         | Integer (PK)      | Autoincremental, generado por la BD        |
| `first_name` | String(100)       | Obligatorio, no vacío                      |
| `last_name1` | String(100)       | Obligatorio, no vacío                      |
| `last_name2` | String(100)       | Opcional, puede ser `null`                 |
| `country`    | String(2)         | Obligatorio, código ISO 3166-1 alpha-2 válido (ej. `ES`, `US`, `FR`) |

> No se valida unicidad de negocio: pueden existir dos autores con los mismos datos; cada uno tiene su propio `id`.

#### `Book` (Libro)

| Campo       | Tipo         | Restricciones                          |
|------------|--------------|----------------------------------------|
| `id`        | Integer (PK) | Autoincremental, generado por la BD    |
| `title`     | String(300)  | Obligatorio, no vacío                  |
| `publisher` | String(200)  | Obligatorio, texto libre, no vacío     |
| `year`      | Integer      | Obligatorio, rango válido: 1000–2100   |

#### `AuthorBook` (Relación M:N)

| Campo               | Tipo        | Restricciones                                     |
|--------------------|-------------|---------------------------------------------------|
| `author_id`         | Integer (FK) | Referencia a `Author.id`                         |
| `book_id`           | Integer (FK) | Referencia a `Book.id`                           |
| `contribution_date` | Date        | Obligatorio, formato ISO 8601 (`YYYY-MM-DD`)     |

PK compuesta: `(author_id, book_id)`.

### 3.2 Relaciones

- Un **libro** tiene **al menos un autor** (invariante de negocio obligatoria).
- Un **autor** puede tener **cero o más libros**.
- La relación es **muchos a muchos** con atributo propio (`contribution_date`).
- **Eliminar un autor con libros asociados está prohibido** (ver reglas de negocio §5).

---

## 4. Estructura del proyecto

```
src/
  ejem1/
    main.py            # Punto de entrada FastAPI (app = FastAPI())
    database.py        # Engine SQLite, SessionLocal, Base
    models.py          # Modelos SQLAlchemy (Author, Book, AuthorBook)
    schemas.py         # Modelos Pydantic (request/response)
    routers/
      authors.py       # Endpoints /authors
      books.py         # Endpoints /books
    services/
      author_service.py
      book_service.py
    validators.py      # Validación ISO 3166-1, reglas de negocio

tests/
  test_authors.py
  test_books.py
  conftest.py          # Fixtures: app, client, BD en memoria
```

---

## 5. Reglas de negocio

1. **Autor mínimo por libro**: un libro debe tener siempre al menos un autor. Intentar crear o modificar un libro con `authors=[]` devuelve `422 Unprocessable Entity`.
2. **Protección de autor con libros**: `DELETE /authors/{id}` cuando el autor tiene libros asociados devuelve `409 Conflict`. El cliente debe eliminar o reasignar los libros antes.
3. **País válido**: el campo `country` del autor debe ser un código ISO 3166-1 alpha-2 reconocido. Valores inválidos devuelven `422`.
4. **Año de publicación**: `year` debe estar en el rango `[1000, 2100]` inclusive.
5. **Autores deben existir antes de asociarse**: los `author_id` enviados en el cuerpo del libro deben corresponder a autores existentes; si alguno no existe, devuelve `404`.

---

## 6. Endpoints

### 6.1 Autores (`/v1/authors`)

#### `GET /v1/authors`

Lista paginada de autores, ordenada por `last_name1` ascendente.

**Query params:**

| Param       | Tipo    | Por defecto | Descripción                           |
|------------|---------|-------------|---------------------------------------|
| `page`      | integer | `1`         | Número de página (empieza en 1)       |
| `page_size` | integer | `20`        | Resultados por página (máx. 100)      |
| `country`   | string  | —           | Filtra por código ISO 3166-1 alpha-2  |

**Respuesta `200 OK`:**
```json
{
  "data": [
    {
      "id": 1,
      "first_name": "Miguel",
      "last_name1": "Cervantes",
      "last_name2": "Saavedra",
      "country": "ES"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 1
  }
}
```

---

#### `GET /v1/authors/{id}`

Devuelve los datos del autor. **No incluye la lista de libros** (navegar a `GET /v1/books?author_id={id}`).

**Respuesta `200 OK`:**
```json
{
  "id": 1,
  "first_name": "Miguel",
  "last_name1": "Cervantes",
  "last_name2": "Saavedra",
  "country": "ES"
}
```

**Errores:**
- `404 Not Found` si el autor no existe.

---

#### `POST /v1/authors`

Crea un nuevo autor.

**Request body:**
```json
{
  "first_name": "Miguel",
  "last_name1": "Cervantes",
  "last_name2": "Saavedra",
  "country": "ES"
}
```

**Respuesta `201 Created`** con header `Location: /v1/authors/{id}`:
```json
{
  "id": 1,
  "first_name": "Miguel",
  "last_name1": "Cervantes",
  "last_name2": "Saavedra",
  "country": "ES"
}
```

**Errores:**
- `422 Unprocessable Entity` si `country` no es un código ISO válido o faltan campos obligatorios.

---

#### `PATCH /v1/authors/{id}`

Actualización parcial. Solo se modifican los campos enviados; los omitidos no cambian.

**Request body (todos los campos opcionales):**
```json
{
  "first_name": "Miguel de",
  "country": "ES"
}
```

**Respuesta `200 OK`:** recurso completo actualizado (mismo formato que `GET /v1/authors/{id}`).

**Errores:**
- `404 Not Found` si el autor no existe.
- `422 Unprocessable Entity` si algún valor es inválido.

---

#### `DELETE /v1/authors/{id}`

Elimina el autor.

**Respuesta `204 No Content`** si el autor existe y no tiene libros.

**Errores:**
- `404 Not Found` si el autor no existe.
- `409 Conflict` si el autor tiene libros asociados:
```json
{
  "error": {
    "code": "AUTHOR_HAS_BOOKS",
    "message": "Cannot delete author with associated books. Remove or reassign books first.",
    "details": [
      { "field": "author_id", "issue": "author has 3 associated book(s)" }
    ]
  }
}
```

---

### 6.2 Libros (`/v1/books`)

#### `GET /v1/books`

Lista paginada de libros, ordenada por `title` ascendente.

**Query params:**

| Param       | Tipo    | Por defecto | Descripción                                      |
|------------|---------|-------------|--------------------------------------------------|
| `page`      | integer | `1`         | Número de página                                 |
| `page_size` | integer | `20`        | Resultados por página (máx. 100)                 |
| `title`     | string  | —           | Búsqueda parcial por título (case-insensitive)   |
| `author_id` | integer | —           | Filtra libros que tengan este autor              |

**Respuesta `200 OK`:**
```json
{
  "data": [
    {
      "id": 1,
      "title": "Don Quijote de la Mancha",
      "publisher": "Francisco de Robles",
      "year": 1605,
      "authors": [
        {
          "id": 1,
          "first_name": "Miguel",
          "last_name1": "Cervantes",
          "last_name2": "Saavedra",
          "country": "ES",
          "contribution_date": "1605-01-16"
        }
      ]
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 1
  }
}
```

---

#### `GET /v1/books/{id}`

Devuelve el libro con todos sus autores embebidos (incluyendo `contribution_date` de cada autor).

**Respuesta `200 OK`:** mismo esquema que cada elemento del listado anterior.

**Errores:**
- `404 Not Found` si el libro no existe.

---

#### `POST /v1/books`

Crea un nuevo libro con sus autores iniciales.

**Request body:**
```json
{
  "title": "Don Quijote de la Mancha",
  "publisher": "Francisco de Robles",
  "year": 1605,
  "authors": [
    { "author_id": 1, "contribution_date": "1605-01-16" }
  ]
}
```

**Reglas:**
- `authors` debe tener al menos un elemento.
- Todos los `author_id` deben existir.
- `contribution_date` es obligatorio por cada entrada de autor.

**Respuesta `201 Created`** con header `Location: /v1/books/{id}`:
```json
{
  "id": 1,
  "title": "Don Quijote de la Mancha",
  "publisher": "Francisco de Robles",
  "year": 1605,
  "authors": [
    {
      "id": 1,
      "first_name": "Miguel",
      "last_name1": "Cervantes",
      "last_name2": "Saavedra",
      "country": "ES",
      "contribution_date": "1605-01-16"
    }
  ]
}
```

**Errores:**
- `422 Unprocessable Entity` si `authors` está vacío o tiene datos inválidos.
- `404 Not Found` si algún `author_id` no existe.

---

#### `PATCH /v1/books/{id}`

Actualización parcial. Los campos omitidos no cambian.

**Request body (todos opcionales, pero `authors` si se envía debe tener al menos un elemento):**
```json
{
  "title": "Don Quijote",
  "authors": [
    { "author_id": 1, "contribution_date": "1605-01-16" },
    { "author_id": 2, "contribution_date": "1615-11-01" }
  ]
}
```

> Cuando se envía `authors`, **reemplaza completamente** la lista de autores del libro (no es aditivo). Si no se envía `authors`, la lista de autores no cambia.

**Respuesta `200 OK`:** recurso completo actualizado (mismo formato que `GET /v1/books/{id}`).

**Errores:**
- `404 Not Found` si el libro no existe.
- `404 Not Found` si algún `author_id` en la lista no existe.
- `422 Unprocessable Entity` si `authors=[]` (lista vacía viola la invariante de mínimo un autor).

---

#### `DELETE /v1/books/{id}`

Elimina el libro y todas sus relaciones con autores. Los autores **no** se eliminan.

**Respuesta `204 No Content`.**

**Errores:**
- `404 Not Found` si el libro no existe.

---

## 7. Formato de errores

Todos los errores siguen esta estructura uniforme:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Descripción legible por humanos.",
    "details": [
      { "field": "country", "issue": "código ISO 3166-1 alpha-2 inválido: 'XX'" }
    ]
  }
}
```

| Código HTTP | `error.code`            | Cuándo                                           |
|------------|-------------------------|--------------------------------------------------|
| `400`       | `BAD_REQUEST`           | Malformación genérica del request               |
| `404`       | `NOT_FOUND`             | Recurso inexistente                             |
| `409`       | `AUTHOR_HAS_BOOKS`      | Intento de borrar autor con libros              |
| `422`       | `VALIDATION_ERROR`      | Datos semánticamente inválidos                  |
| `500`       | `INTERNAL_ERROR`        | Error del servidor (sin stack trace expuesto)   |

---

## 8. Paginación

Todos los listados usan paginación basada en páginas:

```
GET /v1/books?page=2&page_size=10
```

- `page` mínimo: `1`.
- `page_size` máximo: `100`; por defecto: `20`.
- La respuesta siempre incluye el bloque `pagination` con `page`, `page_size` y `total` (total de registros que coinciden con los filtros).

---

## 9. Base de datos en memoria

El engine SQLAlchemy se crea con:

```python
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
)
```

Las tablas se crean al arrancar la aplicación (`Base.metadata.create_all(engine)`). Los datos **no persisten** entre reinicios.

Para los tests, cada test recibe una BD en memoria limpia mediante un fixture de sesión en `conftest.py`.

---

## 10. Estrategia de testing

- **Framework**: pytest + `httpx.AsyncClient` o `starlette.testclient.TestClient`.
- **BD**: SQLite en memoria, instancia por fichero de test (fixture con `scope="module"` o `scope="function"` según el caso).
- **Sin mocks**: los tests de integración usan la BD real en memoria; no se mockea SQLAlchemy.

### Casos a cubrir por recurso

#### Autores
- `test_create_author_valid_data_returns_201`
- `test_create_author_invalid_country_returns_422`
- `test_get_author_existing_returns_200`
- `test_get_author_not_found_returns_404`
- `test_list_authors_filter_by_country`
- `test_list_authors_pagination`
- `test_patch_author_partial_update_returns_200`
- `test_delete_author_no_books_returns_204`
- `test_delete_author_with_books_returns_409`

#### Libros
- `test_create_book_valid_data_returns_201`
- `test_create_book_empty_authors_returns_422`
- `test_create_book_nonexistent_author_returns_404`
- `test_get_book_includes_authors_embedded`
- `test_get_book_not_found_returns_404`
- `test_list_books_filter_by_title_contains`
- `test_list_books_filter_by_author_id`
- `test_patch_book_replace_authors`
- `test_patch_book_authors_empty_list_returns_422`
- `test_delete_book_returns_204_authors_unaffected`

---

## 11. Documentación interactiva

FastAPI genera automáticamente:
- **Swagger UI**: `GET /docs`
- **ReDoc**: `GET /redoc`
- **OpenAPI JSON**: `GET /openapi.json`

---

## 12. Decisiones de diseño registradas

| Decisión | Elección | Alternativa descartada | Motivo |
|---------|----------|------------------------|--------|
| Unicidad de autores | Solo ID interno | Nombre+apellidos únicos | Evitar falsos positivos con homónimos reales |
| Eliminar autor con libros | 409 Conflict | Borrado en cascada | Previene pérdida accidental de datos |
| Editorial | Texto libre | Entidad propia | Simplicidad para el alcance de la prueba |
| País | ISO 3166-1 alpha-2 | Texto libre | Consistencia en filtros y búsquedas |
| Autenticación | Ninguna | JWT Bearer | Prueba técnica sin requisitos de seguridad |
| Fecha en relación | ISO 8601 date completa | Solo año entero | Precisión al modelar la contribución editorial |
| PATCH authors | Reemplazo completo de la lista | Operaciones aditivas (`add`/`remove`) | Simplicidad; el cliente envía el estado final deseado |
