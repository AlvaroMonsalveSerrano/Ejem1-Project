"""Configuración de SQLAlchemy: engine, sesión y base declarativa."""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependencia FastAPI que provee una sesión de BD por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
