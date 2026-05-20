"""Schemas Pydantic v2 para request/response de la API."""
from __future__ import annotations

import datetime
from typing import Annotated

from pydantic import BaseModel, Field, field_validator, model_validator

from ejem1.validators import is_valid_country_code


# ---------------------------------------------------------------------------
# Autores
# ---------------------------------------------------------------------------


class AuthorCreate(BaseModel):
    """Payload para crear un autor; el país debe ser un código ISO 3166-1 alpha-2."""

    first_name: Annotated[str, Field(min_length=1, max_length=100)]
    last_name1: Annotated[str, Field(min_length=1, max_length=100)]
    last_name2: Annotated[str | None, Field(default=None, max_length=100)]
    country: Annotated[str, Field(min_length=2, max_length=2)]

    @field_validator("country", mode="before")
    @classmethod
    def validate_country(cls, v: str) -> str:
        """Valida y normaliza el código de país a mayúsculas."""
        if not isinstance(v, str) or not is_valid_country_code(v):
            raise ValueError(f"código ISO 3166-1 alpha-2 inválido: '{v}'")
        return v.upper()


class AuthorUpdate(BaseModel):
    """Payload de actualización parcial; todos los campos son opcionales."""

    first_name: Annotated[str | None, Field(default=None, min_length=1, max_length=100)]
    last_name1: Annotated[str | None, Field(default=None, min_length=1, max_length=100)]
    last_name2: Annotated[str | None, Field(default=None, max_length=100)]
    country: Annotated[str | None, Field(default=None, min_length=2, max_length=2)]

    @field_validator("country", mode="before")
    @classmethod
    def validate_country(cls, v: str | None) -> str | None:
        """Valida y normaliza el código de país si se envía."""
        if v is None:
            return v
        if not isinstance(v, str) or not is_valid_country_code(v):
            raise ValueError(f"código ISO 3166-1 alpha-2 inválido: '{v}'")
        return v.upper()


class AuthorResponse(BaseModel):
    """Representación de un autor devuelta por la API."""

    id: int
    first_name: str
    last_name1: str
    last_name2: str | None
    country: str

    model_config = {"from_attributes": True}


class Pagination(BaseModel):
    """Metadatos de paginación incluidos en todas las respuestas de colección."""

    page: int
    page_size: int
    total: int


class AuthorListResponse(BaseModel):
    """Respuesta paginada del listado de autores."""

    data: list[AuthorResponse]
    pagination: Pagination


# ---------------------------------------------------------------------------
# Libros
# ---------------------------------------------------------------------------


class BookAuthorInput(BaseModel):
    """Asociación autor-libro en el request: id del autor y fecha de contribución."""

    author_id: int
    contribution_date: datetime.date


class BookCreate(BaseModel):
    """Payload para crear un libro; debe incluir al menos un autor."""

    title: Annotated[str, Field(min_length=1, max_length=300)]
    publisher: Annotated[str, Field(min_length=1, max_length=200)]
    year: Annotated[int, Field(ge=1000, le=2100)]
    authors: Annotated[list[BookAuthorInput], Field(min_length=1)]


class BookUpdate(BaseModel):
    """Payload de actualización parcial de libro; si se envía authors reemplaza la lista completa."""

    title: Annotated[str | None, Field(default=None, min_length=1, max_length=300)]
    publisher: Annotated[str | None, Field(default=None, min_length=1, max_length=200)]
    year: Annotated[int | None, Field(default=None, ge=1000, le=2100)]
    authors: list[BookAuthorInput] | None = None

    @model_validator(mode="after")
    def authors_not_empty(self) -> "BookUpdate":
        """Si se envía authors, debe tener al menos un elemento."""
        if self.authors is not None and len(self.authors) == 0:
            raise ValueError("authors must have at least one element when provided")
        return self


class BookAuthorResponse(BaseModel):
    """Autor embebido en la respuesta de un libro; incluye la fecha de contribución."""

    id: int
    first_name: str
    last_name1: str
    last_name2: str | None
    country: str
    contribution_date: datetime.date

    model_config = {"from_attributes": True}


class BookResponse(BaseModel):
    """Representación de un libro devuelta por la API, con sus autores embebidos."""

    id: int
    title: str
    publisher: str
    year: int
    authors: list[BookAuthorResponse]

    model_config = {"from_attributes": True}


class BookListResponse(BaseModel):
    """Respuesta paginada del listado de libros."""

    data: list[BookResponse]
    pagination: Pagination
