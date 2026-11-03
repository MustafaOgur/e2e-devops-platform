import os

# app.config import edilmeden önce ayarlanmalı. Testler bu adrese hiç bağlanmaz;
# yereldeki .env dosyası yerine bu değerin kullanılmasını sağlar.
os.environ["DATABASE_URL"] = "postgresql+psycopg://test:test@localhost:5432/test"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def client():
    # Her test kendi boş, bellek içi SQLite veritabanıyla çalışır
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    testing_session = sessionmaker(bind=engine, expire_on_commit=False)

    def override_get_db():
        with testing_session() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    engine.dispose()
