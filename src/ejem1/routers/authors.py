"""Endpoints REST para el recurso /v1/authors."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from ejem1.database import get_db
from ejem1.schemas import (
    AuthorCreate,
    AuthorListResponse,
    AuthorResponse,
    AuthorUpdate,
    Pagination,
)
from ejem1.services import author_service

router = APIRouter(prefix="/v1/authors", tags=["authors"])


@router.get("", response_model=AuthorListResponse)
def list_authors(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    country: str | None = None,
    db: Session = Depends(get_db),
) -> AuthorListResponse:
    """Lista paginada de autores, ordenada por apellido."""
    authors, total = author_service.list_authors(db, page, page_size, country)
    return AuthorListResponse(
        data=[AuthorResponse.model_validate(a) for a in authors],
        pagination=Pagination(page=page, page_size=page_size, total=total),
    )


@router.get("/{author_id}", response_model=AuthorResponse)
def get_author(author_id: int, db: Session = Depends(get_db)) -> AuthorResponse:
    """Devuelve un autor por id."""
    author = author_service.get_author(db, author_id)
    if author is None:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": f"Author {author_id} not found", "details": []})
    return AuthorResponse.model_validate(author)


@router.post("", response_model=AuthorResponse, status_code=201)
def create_author(
    data: AuthorCreate,
    response: Response,
    db: Session = Depends(get_db),
) -> AuthorResponse:
    """Crea un nuevo autor."""
    author = author_service.create_author(db, data)
    response.headers["Location"] = f"/v1/authors/{author.id}"
    return AuthorResponse.model_validate(author)


@router.patch("/{author_id}", response_model=AuthorResponse)
def update_author(
    author_id: int,
    data: AuthorUpdate,
    db: Session = Depends(get_db),
) -> AuthorResponse:
    """Actualización parcial de un autor."""
    author = author_service.update_author(db, author_id, data)
    if author is None:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": f"Author {author_id} not found", "details": []})
    return AuthorResponse.model_validate(author)


@router.delete("/{author_id}", status_code=204)
def delete_author(author_id: int, db: Session = Depends(get_db)) -> None:
    """Elimina un autor; falla con 409 si tiene libros asociados."""
    found, book_count = author_service.delete_author(db, author_id)
    if not found:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": f"Author {author_id} not found", "details": []})
    if book_count:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "AUTHOR_HAS_BOOKS",
                "message": "Cannot delete author with associated books. Remove or reassign books first.",
                "details": [
                    {"field": "author_id", "issue": f"author has {book_count} associated book(s)"}
                ],
            },
        )
