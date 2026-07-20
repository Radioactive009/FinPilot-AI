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
settings.SQLALCHEMY_DATABASE_URI = "sqlite:///./test_inv.db"

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Use dynamic storage directory inside tests folder
TEST_STORAGE_DIR = Path(__file__).resolve().parent / "test_storage_inv"
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


def test_extract_invoice_success():
    # 1. Upload valid invoice document
    file_content = b"Invoice dummy data"
    upload_res = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        data={"document_type": "Invoice"},
        files={"file": ("invoice.pdf", io.BytesIO(file_content), "application/pdf")}
    )
    doc_id = upload_res.json()["id"]

    # 2. Extract invoice
    extract_res = client.post(
        f"/api/v1/invoices/{doc_id}/extract",
        headers=auth_headers
    )
    assert extract_res.status_code == 201
    data = extract_res.json()
    assert data["invoice_number"] == "INV-2026-0001"
    assert data["total_amount"] == 1100.0
    assert len(data["items"]) == 2
    assert data["items"][0]["description"] == "Software Subscription"


def test_extract_invoice_unsupported_type():
    # 1. Upload non-invoice document (e.g. Policy)
    file_content = b"Policy dummy data"
    upload_res = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        data={"document_type": "Policy"},
        files={"file": ("policy.pdf", io.BytesIO(file_content), "application/pdf")}
    )
    doc_id = upload_res.json()["id"]

    # 2. Extract invoice (should return 400 Bad Request)
    extract_res = client.post(
        f"/api/v1/invoices/{doc_id}/extract",
        headers=auth_headers
    )
    assert extract_res.status_code == 400
    assert "only supported for Invoice" in extract_res.json()["detail"]


def test_extract_invoice_missing_required_fields():
    # 1. Upload document with missing fields trigger name
    file_content = b"Missing fields dummy data"
    upload_res = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        data={"document_type": "Invoice"},
        files={"file": ("missing_fields.pdf", io.BytesIO(file_content), "application/pdf")}
    )
    doc_id = upload_res.json()["id"]

    # 2. Extract (should fail with 400 validation error)
    extract_res = client.post(
        f"/api/v1/invoices/{doc_id}/extract",
        headers=auth_headers
    )
    assert extract_res.status_code == 400
    assert "Validation failed" in extract_res.json()["detail"]


def test_extract_invoice_duplicate_prevention():
    # 1. Upload first duplicate invoice document
    file_content = b"Duplicate invoice dummy data"
    upload_res_1 = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        data={"document_type": "Invoice"},
        files={"file": ("duplicate_1.pdf", io.BytesIO(file_content), "application/pdf")}
    )
    doc_id_1 = upload_res_1.json()["id"]

    # Extract first invoice (succeeds)
    extract_res_1 = client.post(
        f"/api/v1/invoices/{doc_id_1}/extract",
        headers=auth_headers
    )
    assert extract_res_1.status_code == 201

    # 2. Upload second duplicate invoice document (triggers the duplicate INV-DUP-999 number)
    upload_res_2 = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        data={"document_type": "Invoice"},
        files={"file": ("duplicate_2.pdf", io.BytesIO(file_content), "application/pdf")}
    )
    doc_id_2 = upload_res_2.json()["id"]

    # Extract second invoice (should return 409 Conflict)
    extract_res_2 = client.post(
        f"/api/v1/invoices/{doc_id_2}/extract",
        headers=auth_headers
    )
    assert extract_res_2.status_code == 409
    assert "already exists" in extract_res_2.json()["detail"]
