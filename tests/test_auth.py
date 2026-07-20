import sys
from pathlib import Path
from unittest.mock import MagicMock
import importlib.metadata

# Mock email-validator distribution version check done by Pydantic
original_version = importlib.metadata.version
def mock_version(distribution_name):
    if distribution_name == "email-validator":
        return "2.0.0"
    return original_version(distribution_name)
importlib.metadata.version = mock_version

# Mock external dependencies that are not in the local global python environment
structlog_mock = MagicMock()
structlog_mock.get_logger.return_value = MagicMock()
sys.modules["structlog"] = structlog_mock

# Mock email-validator module
email_validator_mock = MagicMock()
sys.modules["email_validator"] = email_validator_mock

# Mock jose
jose_mock = MagicMock()
jwt_mock = MagicMock()
jwt_mock.encode.return_value = "mocked_jwt_token"
jwt_mock.decode.return_value = {"sub": "test@example.com"}
jose_mock.jwt = jwt_mock
sys.modules["jose"] = jose_mock

# Mock passlib
passlib_mock = MagicMock()
pwd_context_mock = MagicMock()
pwd_context_mock.hash.return_value = "mocked_hashed_password"
pwd_context_mock.verify.return_value = True
passlib_mock.context = MagicMock()
passlib_mock.context.CryptContext.return_value = pwd_context_mock
sys.modules["passlib"] = passlib_mock
sys.modules["passlib.context"] = passlib_mock.context

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.session import Base, get_db

# Create test database (SQLite in-memory)
from app.core.config import settings
settings.SQLALCHEMY_DATABASE_URI = "sqlite:///./test.db"

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_register():
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "securepassword123",
            "role": "Employee"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_email():
    payload = {
        "full_name": "Test User",
        "email": "test@example.com",
        "password": "securepassword123",
        "role": "Employee"
    }
    client.post("/api/v1/auth/register", json=payload)
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409


def test_register_invalid_password():
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "short",
            "role": "Employee"
        }
    )
    assert response.status_code == 422


def test_login():
    # Register user
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "securepassword123",
            "role": "Employee"
        }
    )

    # Login
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "securepassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_invalid_login():
    # Force mock verification to fail for this check
    pwd_context_mock.verify.return_value = False
    try:
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
    finally:
        pwd_context_mock.verify.return_value = True
        
    response2 = client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
    )
    assert response2.status_code == 401
