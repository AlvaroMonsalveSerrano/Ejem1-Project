"""Endpoints REST para el recurso /v1/books."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from ejem1.database import get_db
from ejem1.schemas import (
    BookCreate,
    BookListResponse,
    BookResponse,
    BookUpdate,
    Pagination,
)
from ejem1.services import book_service

router = APIRouter(prefix="/v1/books", tags=["books"])


@router.get("", response_model=BookListResponse)
def list_books(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    title: str | None = None,
    author_id: int | None = None,
    db: Session = Depends(get_db),
) -> BookListResponse:
    """Lista paginada de libros, ordenada por título."""
    books, total = book_service.list_books(db, page, page_size, title, author_id)
    return BookListResponse(
        data=[BookResponse.model_validate(b) for b in books],
        pagination=Pagination(page=page, page_size=page_size, total=total),
    )


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)) -> BookResponse:
    """Devuelve un libro con sus autores embebidos."""
    book = book_service.get_book(db, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": f"Book {book_id} not found", "details": []})
    return BookResponse.model_validate(book)


@router.post("", response_model=BookResponse, status_code=201)
def create_book(
    data: BookCreate,
    response: Response,
    db: Session = Depends(get_db),
) -> BookResponse:
    """Crea un nuevo libro con sus autores iniciales."""
    try:
        book = book_service.create_book(db, data)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": f"Author {exc.args[0]} not found", "details": []})
    response.headers["Location"] = f"/v1/books/{book['id']}"
    return BookResponse.model_validate(book)


@router.patch("/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int,
    data: BookUpdate,
    db: Session = Depends(get_db),
) -> BookResponse:
    """Actualización parcial de un libro."""
    try:
        book = book_service.update_book(db, book_id, data)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": f"Author {exc.args[0]} not found", "details": []})
    if book is None:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": f"Book {book_id} not found", "details": []})
    return BookResponse.model_validate(book)


@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db)) -> None:
    """Elimina un libro y sus relaciones; los autores no se eliminan."""
    if not book_service.delete_book(db, book_id):
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": f"Book {book_id} not found", "details": []})
