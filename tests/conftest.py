"""Fixtures compartidos para todos los tests de integración."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ejem1.database import Base, get_db
from ejem1.main import app


@pytest.fixture()
def client():
    """Cliente HTTP con BD SQLite en memoria limpia por cada test."""
    # StaticPool garantiza que todas las conexiones usan el mismo objeto
    # de BD en memoria; sin él cada nueva conexión ve una BD vacía.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
