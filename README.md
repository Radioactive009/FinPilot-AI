# FinanceAI Copilot

Enterprise-grade AI platform designed to help finance teams analyze invoices, expense reports, audit reports, vendor statements, and company policies. Built with Next.js, FastAPI, PostgreSQL, SQLAlchemy, LangGraph, and Docker.

## Project Architecture

```
finance-ai-copilot/
├── frontend/             # Next.js 16 (App Router, TS, Tailwind, shadcn/ui)
├── backend/              # Python 3.12 (FastAPI, SQLAlchemy, LangChain/LangGraph, OCR/PDF tools)
├── docker/               # Docker & Compose configurations
├── docs/                 # Design documents and APIs
└── sample_data/          # Document categories for RAG testing
```

### Backend Components
- **FastAPI Core**: Request handling, routing, dependency injection.
- **SQLAlchemy & Alembic**: Database models, async/sync sessions, migrations.
- **RAG & Agents**: FAISS vector database integration, PyMuPDF + PaddleOCR parser, LangGraph workflow architecture.

---

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.12+ (for local backend development)

### Quick Start with Docker

1. **Clone the repository and set environment variables:**
   ```bash
   cp backend/.env.example backend/.env
   ```

2. **Spin up services:**
   ```bash
   docker compose -f docker/docker-compose.yml up --build
   ```

3. **Access Services:**
   - **Frontend App**: `http://localhost:3000`
   - **Backend API**: `http://localhost:8000`
   - **API Swagger Docs**: `http://localhost:8000/docs`
"# FinPilot-AI" 
