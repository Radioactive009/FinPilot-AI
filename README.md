# FinanceAI Copilot

Enterprise-grade AI platform designed to help finance teams analyze invoices, expense reports, audit reports, vendor statements, and company policies. Built with Next.js, FastAPI, PostgreSQL, SQLAlchemy, LangGraph, and Docker.

## Project Architecture

```
finance-ai-copilot/
├── frontend/             # Next.js 16 (App Router, TS, Tailwind, shadcn/ui)
├── backend/              # Python 3.12 (FastAPI, SQLAlchemy, LangGraph, OCR/PDF tools)
├── docker/               # Docker & Compose configurations
├── docs/                 # Design documents and APIs
├── sample_data/          # Document categories for RAG testing
└── storage/              # Dedicated persistent volume for files, logs, and indices
    ├── uploads/          # Uploaded invoice/report documents
    ├── parsed/           # Parsed text and JSON structures
    ├── embeddings/       # Local cached vector embeddings
    ├── faiss/            # FAISS index files
    ├── generated_reports/# Output reports
    └── logs/             # Application structural log files (app.log)
```

### Backend Components
- **FastAPI Core**: Request handling, routing, dependency injection. Enforces secure, non-default `SECRET_KEY` env validation.
- **SQLAlchemy & Alembic**: Database models, async/sync sessions, migrations.
- **RAG & Agents**: FAISS vector database integration, PyMuPDF + PaddleOCR parser, LangGraph workflow architecture. Uses Groq LLM integration.

---

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.12+ (for local backend development)

### Environment Setup

1. **Configure Environment Variables:**
   ```bash
   cp backend/.env.example backend/.env
   ```
   Open `backend/.env` and configure:
   - `SECRET_KEY`: Must be generated securely (e.g. `openssl rand -hex 32`). The backend will fail to start if this is missing.
   - `GROQ_API_KEY`: API key for Groq Cloud.
   - `GROQ_MODEL`: LLM model target (defaults to `llama3-8b-8192`).
   - `BACKEND_CORS_ORIGINS`: Comma-separated list of allowed origins.

2. **Quick Start with Docker:**
   ```bash
   docker compose -f docker/docker-compose.yml up --build
   ```

3. **Access Services:**
   - **Frontend App**: `http://localhost:3000`
   - **Backend API**: `http://localhost:8000`
   - **API Swagger Docs**: `http://localhost:8000/docs`
