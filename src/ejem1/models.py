"""Modelos SQLAlchemy para Author, Book y la relación M:N AuthorBook."""
from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ejem1.database import Base


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    last_name1 = Column(String(100), nullable=False)
    last_name2 = Column(String(100), nullable=True)
    country = Column(String(2), nullable=False)

    book_associations = relationship(
        "AuthorBook", back_populates="author", cascade="all, delete-orphan"
    )


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(300), nullable=False)
    publisher = Column(String(200), nullable=False)
    year = Column(Integer, nullable=False)

    author_associations = relationship(
        "AuthorBook", back_populates="book", cascade="all, delete-orphan"
    )


class AuthorBook(Base):
    __tablename__ = "author_books"

    author_id = Column(Integer, ForeignKey("authors.id"), primary_key=True)
    book_id = Column(Integer, ForeignKey("books.id"), primary_key=True)
    contribution_date = Column(Date, nullable=False)

    author = relationship("Author", back_populates="book_associations")
    book = relationship("Book", back_populates="author_associations")
