import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app  # app.main já importa app.models (registra as tabelas)
from app.core.database import Base, get_db
from app.core.security import hash_password
from app.models.user import User
from app.models.enums import UserRole

engine_test = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine_test)
    db = TestingSessionLocal()
    db.add(
        User(
            name="Admin",
            email="admin@test.com",
            password_hash=hash_password("testpass123"),
            role=UserRole.ADMIN,
            email_verified=True,
        )
    )
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_headers(client):
    resp = client.post(
        "/api/auth/login", json={"email": "admin@test.com", "password": "testpass123"}
    )
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}
