import io
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

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
from app.ocr.extractor_factory import ExtractorFactory
from app.ocr.pdf_text_extractor import PDFTextExtractor
from app.ocr.paddle_ocr_extractor import PaddleOCRExtractor

# Create test database (SQLite in-memory)
settings.SQLALCHEMY_DATABASE_URI = "sqlite:///./test_ocr.db"

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Use dynamic storage directory inside tests folder
TEST_STORAGE_DIR = Path(__file__).resolve().parent / "test_storage_ocr"
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


@patch("fitz.open")
def test_extractor_factory_searchable_pdf(mock_fitz_open):
    # Mock searchable PDF check returning text
    mock_doc = MagicMock()
    mock_page = MagicMock()
    mock_page.get_text.return_value = "This is searchable text contents"
    mock_doc.__len__.return_value = 1
    mock_doc.load_page.return_value = mock_page
    mock_doc.__iter__.return_value = [mock_page]
    mock_fitz_open.return_value = mock_doc

    extractor = ExtractorFactory.get_extractor("invoice.pdf")
    assert isinstance(extractor, PDFTextExtractor)


@patch("fitz.open")
def test_extractor_factory_scanned_pdf(mock_fitz_open):
    # Mock scanned PDF check returning empty text
    mock_doc = MagicMock()
    mock_page = MagicMock()
    mock_page.get_text.return_value = "   \n "
    mock_doc.__len__.return_value = 1
    mock_doc.load_page.return_value = mock_page
    mock_doc.__iter__.return_value = [mock_page]
    mock_fitz_open.return_value = mock_doc

    extractor = ExtractorFactory.get_extractor("invoice.pdf")
    assert isinstance(extractor, PaddleOCRExtractor)


def test_extractor_factory_image():
    extractor = ExtractorFactory.get_extractor("scanned_receipt.png")
    assert isinstance(extractor, PaddleOCRExtractor)


@patch("fitz.open")
def test_extract_digital_pdf_route_success(mock_fitz_open):
    # 1. Upload searchable PDF document
    file_content = b"PDF content"
    upload_res = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        data={"document_type": "Invoice"},
        files={"file": ("searchable.pdf", io.BytesIO(file_content), "application/pdf")}
    )
    doc_id = upload_res.json()["id"]

    # Mock PyMuPDF extraction output
    mock_doc = MagicMock()
    mock_page = MagicMock()
    mock_page.get_text.return_value = "Acme Corp Invoice INV-100"
    mock_page.rect.x0 = 0
    mock_page.rect.y0 = 0
    mock_page.rect.x1 = 600
    mock_page.rect.y1 = 800
    mock_doc.__len__.return_value = 1
    mock_doc.load_page.return_value = mock_page
    mock_doc.__iter__.return_value = [mock_page]
    mock_fitz_open.return_value = mock_doc

    # 2. Call extraction endpoint
    extract_res = client.post(
        f"/api/v1/documents/{doc_id}/extract-text",
        headers=auth_headers
    )
    assert extract_res.status_code == 200
    data = extract_res.json()
    assert data["extractor_used"] == "PDFTextExtractor"
    assert data["total_pages"] == 1
    assert "Acme Corp" in data["pages"][0]["raw_text"]

    # 3. Retrieve parsed JSON text from storage
    parsed_res = client.get(
        f"/api/v1/documents/{doc_id}/parsed-text",
        headers=auth_headers
    )
    assert parsed_res.status_code == 200
    assert parsed_res.json()["extractor_used"] == "PDFTextExtractor"


@patch("fitz.open")
def test_extract_scanned_document_route_success(mock_fitz_open):
    # 1. Upload scanned image
    file_content = b"image content"
    upload_res = client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        data={"document_type": "Invoice"},
        files={"file": ("receipt.png", io.BytesIO(file_content), "image/png")}
    )
    doc_id = upload_res.json()["id"]

    # 2. Call extraction endpoint (routes to PaddleOCRExtractor fallback simulation)
    extract_res = client.post(
        f"/api/v1/documents/{doc_id}/extract-text",
        headers=auth_headers
    )
    assert extract_res.status_code == 200
    data = extract_res.json()
    assert data["extractor_used"] == "PaddleOCRExtractor"
    assert "Simulated PaddleOCR" in data["pages"][0]["raw_text"]
