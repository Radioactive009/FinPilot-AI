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
settings.SQLALCHEMY_DATABASE_URI = "sqlite:///./test_proc.db"

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Use dynamic storage directory inside tests folder
TEST_STORAGE_DIR = Path(__file__).resolve().parent / "test_storage_proc"
settings.STORAGE_DIR = TEST_STORAGE_DIR
settings.UPLOADS_DIR = TEST_STORAGE_DIR / "uploads"
settings.LOGS_DIR = TEST_STORAGE_DIR / "logs"


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function", autouse=True)
def setup_db_and_storage():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    settings.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()
    # Cleanup test storage files
    if TEST_STORAGE_DIR.exists():
        import shutil
        shutil.rmtree(TEST_STORAGE_DIR, ignore_errors=True)


client = TestClient(app)

auth_headers = {}


@pytest.fixture(autouse=True)
def mock_current_user(setup_db_and_storage):
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
            "password": "securepassword123"
        }
    )
    token = response.json()["access_token"]
    global auth_headers
    auth_headers = {"Authorization": f"Bearer {token}"}


def test_processing_pipeline_success():
    # 1. Upload a document
    file_content = b"PDF dummy content"
    upload_res = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        data={"document_type": "Invoice"},
        files={"file": ("invoice.pdf", io.BytesIO(file_content), "application/pdf")}
    )
    doc_id = upload_res.json()["id"]

    # Verify status is UPLOADED
    status_res = client.get(f"/api/v1/documents/{doc_id}/status", headers=auth_headers)
    assert status_res.json()["processing_status"] == "UPLOADED"

    # 2. Trigger processing pipeline
    process_res = client.post(f"/api/v1/documents/{doc_id}/process", headers=auth_headers)
    assert process_res.status_code == 200
    assert process_res.json()["status"] == "Queued & Processed"

    # 3. Check status transitions to PARSED
    status_res_2 = client.get(f"/api/v1/documents/{doc_id}/status", headers=auth_headers)
    assert status_res_2.json()["processing_status"] == "PARSED"
    assert status_res_2.json()["processed_at"] is not None
    assert status_res_2.json()["processing_error"] is None


def test_processing_unauthorized():
    # Attempt to process without headers
    response = client.post("/api/v1/documents/a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11/process")
    assert response.status_code == 401


def test_processing_failure_handling():
    # 1. Manually insert document metadata record but don't write the physical file to storage
    # This simulates a file system processing failure case
    db = TestingSessionLocal()
    # Find user
    user = db.query(User).filter(User.email == "employee@example.com").first()
    from app.models.document import Document, DocumentType
    doc = Document(
        user_id=user.id,
        original_filename="missing.pdf",
        stored_filename="missing_uuid.pdf",
        document_type=DocumentType.INVOICE,
        mime_type="application/pdf",
        file_size=100,
        storage_path=str(settings.UPLOADS_DIR / "invoices/missing_uuid.pdf"),
        upload_status="Uploaded",
        processing_status="UPLOADED"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    doc_id = doc.id
    db.close()

    # 2. Process the document
    process_res = client.post(f"/api/v1/documents/{doc_id}/process", headers=auth_headers)
    assert process_res.status_code == 200

    # 3. Verify status transitions to FAILED
    status_res = client.get(f"/api/v1/documents/{doc_id}/status", headers=auth_headers)
    assert status_res.json()["processing_status"] == "FAILED"
    assert "not found" in status_res.json()["processing_error"]
