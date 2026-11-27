# Enterprise AI Knowledge Assistant

A multi-tenant backend system for ingesting, validating, and indexing enterprise PDF documents for Retrieval-Augmented Generation (RAG) and semantic search.

## Tech Stack

- **Backend:** Python, FastAPI, Pydantic
- **Database & ORM:** PostgreSQL (`pgvector`), SQLAlchemy, Alembic
- **Document Processing:** PyMuPDF (`pymupdf`)
- **Authentication & Security:** JWT, Argon2 password hashing
- **Infrastructure:** Docker, Docker Compose

## Implemented Features

- **Multi-Tenant PDF Ingestion:** Tenant-isolated file handling and storage service for uploaded documents.
- **Validation & Text Extraction:** Strict PDF header/structure validation and page-level text extraction via `pymupdf` into immutable domain models (`ExtractedPage`, `ExtractedDocument`).
- **Database & Migrations:** Relational schema managed through SQLAlchemy models and Alembic migrations (`documents` table).
- **Authentication Foundation:** Secure password hashing with Argon2 and JWT-based access control[cite: 8].

## Repository Structure

```text
Enterprise-AI-Knowledge-Assistant/
├── backend/
│   ├── alembic/             # Database schema migrations
│   └── app/
│       └── services/        # Storage & PyMuPDF extraction services
├── infrastructure/          # Docker & PostgreSQL (pgvector) configuration
├── .env.example             # Environment variable template
└── .gitignore
```

## Local Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/RhythmSingla/Enterprise-AI-Knowledge-Assistant.git](https://github.com/RhythmSingla/Enterprise-AI-Knowledge-Assistant.git)
   cd Enterprise-AI-Knowledge-Assistant
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   Update `.env` with your PostgreSQL credentials and JWT secret key.

3. **Start PostgreSQL (`pgvector`):**
   ```bash
   cd infrastructure
   docker compose up -d
   ```

4. **Install dependencies and run migrations:**
   ```bash
   cd ../backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   alembic upgrade head
   ```

5. **Start the FastAPI server:**
   ```bash
   uvicorn app.main:app --reload
   ```
   Interactive API docs will be available at `http://127.0.0.1:8000/docs`.

## Roadmap

- [x] FastAPI & PostgreSQL (`pgvector`) containerized setup[cite: 8]
- [x] SQLAlchemy models, Alembic migrations & Argon2/JWT auth[cite: 8]
- [x] Multi-tenant PDF upload, validation & PyMuPDF text extraction[cite: 8]
- [x] Document chunking & vector embedding generation
- [ ] Semantic similarity search with `pgvector`
- [ ] Grounded Q&A API with page-level citations & frontend interface
