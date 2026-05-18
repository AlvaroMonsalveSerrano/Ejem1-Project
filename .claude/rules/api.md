# Reglas de API REST — ejem1-project

## Diseño de recursos y URLs

- Las URLs identifican recursos, no acciones; usa sustantivos en plural: `/users`, `/orders/{id}`.
- Usa jerarquía solo cuando la relación es de pertenencia real: `/users/{id}/orders`; evita más de dos niveles de anidamiento.
- Todo en minúsculas y con guiones medios para separar palabras: `/payment-methods`, no `/paymentMethods` ni `/payment_methods`.
- Los identificadores de recurso van en la ruta, no en el cuerpo ni en query params: `GET /users/42`, no `GET /users?id=42`.
- Las acciones que no encajan en CRUD se modelan como sub-recursos o con verbos acotados: `POST /orders/{id}/cancel`.

## Métodos HTTP

| Método   | Semántica                                 | Idempotente | Body en request |
|----------|-------------------------------------------|-------------|-----------------|
| `GET`    | Leer recurso o colección                  | Sí          | No              |
| `POST`   | Crear recurso o acción no idempotente     | No          | Sí              |
| `PUT`    | Reemplazar recurso completo               | Sí          | Sí              |
| `PATCH`  | Modificación parcial                      | No          | Sí              |
| `DELETE` | Eliminar recurso                          | Sí          | No              |

- Nunca uses `GET` para operaciones con efecto secundario.
- Usa `POST` para acciones (enviar email, iniciar proceso) cuando no hay un verbo HTTP semántico apropiado.

## Códigos de estado HTTP

- `200 OK` — respuesta exitosa con cuerpo.
- `201 Created` — recurso creado; incluye `Location` header apuntando al nuevo recurso.
- `204 No Content` — éxito sin cuerpo (p. ej., `DELETE`).
- `400 Bad Request` — error de validación del cliente; incluye detalle en el cuerpo.
- `401 Unauthorized` — no autenticado.
- `403 Forbidden` — autenticado pero sin permisos.
- `404 Not Found` — recurso inexistente.
- `409 Conflict` — conflicto de estado (p. ej., duplicado).
- `422 Unprocessable Entity` — datos semánticamente inválidos.
- `500 Internal Server Error` — error del servidor; nunca expongas stack traces.

## Formato de respuesta

- Usa siempre JSON (`Content-Type: application/json`).
- Las respuestas de colección incluyen paginación:
  ```json
  {
    "data": [...],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 150
    }
  }
  ```
- Los errores siguen una estructura uniforme:
  ```json
  {
    "error": {
      "code": "VALIDATION_ERROR",
      "message": "El campo 'email' no es válido.",
      "details": [
        { "field": "email", "issue": "formato inválido" }
      ]
    }
  }
  ```
- Las fechas en formato ISO 8601 con timezone UTC: `"2024-03-15T10:30:00Z"`.
- Los campos en `snake_case`; nunca mezcles convenciones en la misma API.

## Versionado

- Versiona desde el primer release público; nunca publiques una API sin versión.
- El número de versión va en la ruta base: `/v1/users`, `/v2/users`.
- Una versión nueva solo cuando hay cambios incompatibles (breaking changes); los cambios aditivos no requieren nueva versión.
- Mantén al menos una versión anterior activa durante el periodo de deprecación (mínimo 6 meses).
- Comunica la deprecación mediante el header `Deprecation: true` y `Sunset: <fecha ISO 8601>`.
- Documenta los breaking changes en un `CHANGELOG.md` con la versión y fecha.

## Seguridad

- Autenticación mediante JWT (Bearer token) en el header `Authorization`; nunca en query params.
- Usa HTTPS siempre; rechaza conexiones HTTP en producción.
- Valida y sanitiza toda entrada en el servidor, independientemente de la validación del cliente.
- Implementa rate limiting e incluye los headers `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`.
- No expongas información sensible en URLs (tokens, passwords, IDs internos de base de datos cuando sean secuenciales).

## Documentación

- Documenta la API con OpenAPI 3.x (`openapi.yaml` o `openapi.json` en la raíz del proyecto).
- Cada endpoint debe especificar: descripción, parámetros, cuerpo de request, todas las respuestas posibles y ejemplos.
- Mantén la documentación en el mismo repositorio que el código; un PR que cambia un endpoint debe actualizar el spec.
- Genera y publica la documentación interactiva (Swagger UI o Redoc) en `/docs` o `/api-docs`.
- Incluye en el spec los esquemas de error para todos los códigos de estado documentados.
- Añade ejemplos realistas (`example` o `examples`) en cada esquema; evita `string`, `123` como valores de ejemplo.
