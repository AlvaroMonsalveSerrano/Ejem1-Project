"""Lógica de negocio para el recurso Book."""
import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ejem1.models import Author, AuthorBook, Book
from ejem1.schemas import BookAuthorInput, BookCreate, BookUpdate


def _build_book_response(book: Book) -> dict:
    """Construye el dict de respuesta con autores embebidos."""
    authors = []
    for assoc in book.author_associations:
        a = assoc.author
        authors.append(
            {
                "id": a.id,
                "first_name": a.first_name,
                "last_name1": a.last_name1,
                "last_name2": a.last_name2,
                "country": a.country,
                "contribution_date": assoc.contribution_date,
            }
        )
    return {
        "id": book.id,
        "title": book.title,
        "publisher": book.publisher,
        "year": book.year,
        "authors": authors,
    }


def list_books(
    db: Session,
    page: int,
    page_size: int,
    title: str | None,
    author_id: int | None,
) -> tuple[list[dict], int]:
    """Retorna la página de libros (con autores embebidos) y el total."""
    query = select(Book)
    if title:
        query = query.where(Book.title.ilike(f"%{title}%"))
    if author_id is not None:
        query = query.where(
            Book.id.in_(select(AuthorBook.book_id).where(AuthorBook.author_id == author_id))
        )
    query = query.order_by(Book.title)

    total = db.scalar(select(func.count()).select_from(query.subquery()))
    offset = (page - 1) * page_size
    books = list(db.scalars(query.offset(offset).limit(page_size)))
    return [_build_book_response(b) for b in books], total or 0


def get_book(db: Session, book_id: int) -> dict | None:
    """Retorna el libro con autores embebidos o None si no existe."""
    book = db.get(Book, book_id)
    if book is None:
        return None
    return _build_book_response(book)


def _resolve_authors(
    db: Session, author_inputs: list[BookAuthorInput]
) -> list[tuple[Author, datetime.date]]:
    """Resuelve author_id → Author; lanza KeyError si alguno no existe."""
    result = []
    for entry in author_inputs:
        author = db.get(Author, entry.author_id)
        if author is None:
            raise KeyError(entry.author_id)
        result.append((author, entry.contribution_date))
    return result


def create_book(db: Session, data: BookCreate) -> dict:
    """Crea y persiste un nuevo libro con sus relaciones de autores."""
    pairs = _resolve_authors(db, data.authors)
    book = Book(title=data.title, publisher=data.publisher, year=data.year)
    db.add(book)
    db.flush()
    for author, date in pairs:
        db.add(AuthorBook(author_id=author.id, book_id=book.id, contribution_date=date))
    db.commit()
    db.refresh(book)
    return _build_book_response(book)


def update_book(db: Session, book_id: int, data: BookUpdate) -> dict | None:
    """Actualiza parcialmente un libro; si se envía authors, reemplaza la lista completa."""
    book = db.get(Book, book_id)
    if book is None:
        return None

    for field in ("title", "publisher", "year"):
        if field in data.model_fields_set:
            setattr(book, field, getattr(data, field))

    if data.authors is not None:
        pairs = _resolve_authors(db, data.authors)
        for assoc in list(book.author_associations):
            db.delete(assoc)
        db.flush()
        for author, date in pairs:
            db.add(AuthorBook(author_id=author.id, book_id=book.id, contribution_date=date))

    db.commit()
    db.refresh(book)
    return _build_book_response(book)


def delete_book(db: Session, book_id: int) -> bool:
    """Elimina el libro y sus relaciones; retorna False si no existe."""
    book = db.get(Book, book_id)
    if book is None:
        return False
    db.delete(book)
    db.commit()
    return True
