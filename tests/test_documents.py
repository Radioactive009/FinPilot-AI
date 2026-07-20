import io
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Mock structlog module
structlog_mock = MagicMock()
structlog_mock.get_logger.return_value = MagicMock()
sys.modules["structlog"] = structlog_mock

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.base import Base
from app.database.session import get_db
from app.core.config import settings
from app.models.user import User, UserRole
from app.core.security import get_password_hash

# Create test database (SQLite in-memory)
settings.SQLALCHEMY_DATABASE_URI = "sqlite:///./test_docs.db"

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Use dynamic storage directory inside tests folder to avoid contaminating real storage
TEST_STORAGE_DIR = Path(__file__).resolve().parent / "test_storage"
settings.STORAGE_DIR = TEST_STORAGE_DIR
settings.UPLOADS_DIR = TEST_STORAGE_DIR / "uploads"
settings.LOGS_DIR = TEST_STORAGE_DIR / "logs"


@pytest.fixture(scope="function", autouse=True)
def setup_db_and_storage():
    Base.metadata.create_all(bind=engine)
    settings.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    yield
    Base.metadata.drop_all(bind=engine)
    # Cleanup test storage files
    if TEST_STORAGE_DIR.exists():
        import shutil
        shutil.rmtree(TEST_STORAGE_DIR)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# Reusable headers
auth_headers = {}


@pytest.fixture(autouse=True)
def mock_current_user(setup_db_and_storage):
    # Setup a dummy employee user and get authentication credentials
    db = TestingSessionLocal()
    user = User(
        full_name="Employee User",
        email="employee@example.com",
        hashed_password=get_password_hash("securepassword123"),
        role=UserRole.EMPLOYEE,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()

    # Login to retrieve token
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "employee@example.com",
            "password": "securepassword123"  # password verify is mocked to return True in test environment
        }
    )
    token = response.json()["access_token"]
    global auth_headers
    auth_headers = {"Authorization": f"Bearer {token}"}


def test_upload_document_success():
    file_content = b"PDF dummy content"
    response = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        data={"document_type": "Invoice"},
        files={"file": ("invoice.pdf", io.BytesIO(file_content), "application/pdf")}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["original_filename"] == "invoice.pdf"
    assert data["document_type"] == "Invoice"
    assert data["mime_type"] == "application/pdf"
    assert data["file_size"] == len(file_content)
    assert data["upload_status"] == "Uploaded"


def test_upload_document_invalid_extension():
    response = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        data={"document_type": "Invoice"},
        files={"file": ("malicious.exe", io.BytesIO(b"binary"), "application/octet-stream")}
    )
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]


def test_upload_document_oversized():
    # Simulate oversized file by exceeding MAX_FILE_SIZE limit (20MB)
    file_content = b"0" * (21 * 1024 * 1024)
    response = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        data={"document_type": "Invoice"},
        files={"file": ("huge.pdf", io.BytesIO(file_content), "application/pdf")}
    )
    assert response.status_code == 413
    assert "exceeds" in response.json()["detail"]


def test_upload_document_unauthorized():
    response = client.post(
        "/api/v1/documents/upload",
        data={"document_type": "Invoice"},
        files={"file": ("invoice.pdf", io.BytesIO(b"pdf"), "application/pdf")}
    )
    assert response.status_code == 401


def test_delete_document():
    # 1. Upload a document
    file_content = b"PDF dummy content"
    upload_res = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        data={"document_type": "Invoice"},
        files={"file": ("invoice.pdf", io.BytesIO(file_content), "application/pdf")}
    )
    doc_id = upload_res.json()["id"]

    # 2. Delete the document
    delete_res = client.delete(
        f"/api/v1/documents/{doc_id}",
        headers=auth_headers
    )
    assert delete_res.status_code == 204

    # 3. Try to get it again
    get_res = client.get(
        f"/api/v1/documents/{doc_id}",
        headers=auth_headers
    )
    assert get_res.status_code == 404
