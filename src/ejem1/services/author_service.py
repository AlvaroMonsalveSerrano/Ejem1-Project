"""Lógica de negocio para el recurso Author."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ejem1.models import Author, AuthorBook
from ejem1.schemas import AuthorCreate, AuthorUpdate


def list_authors(
    db: Session,
    page: int,
    page_size: int,
    country: str | None,
) -> tuple[list[Author], int]:
    """Retorna la página de autores y el total que coinciden con los filtros."""
    query = select(Author)
    if country:
        query = query.where(Author.country == country.upper())
    query = query.order_by(Author.last_name1)

    total = db.scalar(select(func.count()).select_from(query.subquery()))
    offset = (page - 1) * page_size
    authors = list(db.scalars(query.offset(offset).limit(page_size)))
    return authors, total or 0


def get_author(db: Session, author_id: int) -> Author | None:
    """Retorna el autor por id o None si no existe."""
    return db.get(Author, author_id)


def create_author(db: Session, data: AuthorCreate) -> Author:
    """Crea y persiste un nuevo autor."""
    author = Author(**data.model_dump())
    db.add(author)
    db.commit()
    db.refresh(author)
    return author


def update_author(db: Session, author_id: int, data: AuthorUpdate) -> Author | None:
    """Actualiza parcialmente un autor; retorna None si no existe."""
    author = db.get(Author, author_id)
    if author is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(author, field, value)
    db.commit()
    db.refresh(author)
    return author


def delete_author(db: Session, author_id: int) -> tuple[bool, int]:
    """Elimina el autor.

    Retorna (encontrado, número_de_libros_asociados).
    Si tiene libros, no elimina y retorna el conteo.
    """
    author = db.get(Author, author_id)
    if author is None:
        return False, 0

    book_count = db.scalar(
        select(func.count()).where(AuthorBook.author_id == author_id)
    )
    if book_count:
        return True, book_count

    db.delete(author)
    db.commit()
    return True, 0
