# CQVIP — Computerized Quality Validation Information Platform

A layered Python service for managing validation projects, requirements,
risk, and compliance documentation in regulated (GxP) environments.

## Stack

- **API**: FastAPI (`app/api/routes/*`)
- **Domain model**: SQLAlchemy 2.0 (`app/models/*`)
- **Migrations**: Alembic (`migrations/`)
- **RAG / knowledge base**: ChromaDB (`app/knowledge/rag/*`)
- **AI**: Anthropic Claude (`app/ai/*`, `app/integrations/cloud_ai/anthropic_client.py`)
- **Parsing**: `app/parsers/*` (PDF/DOCX/Excel/CSV/XML/JSON + validation-document
  parsers for URS/FS/DS/HDS/SDS/FAT/SAT/IQ/OQ/PQ/Commissioning/Protocol/Report)

## Layout

This mirrors an 11-layer architecture:

1. `app/api/` — Presentation layer (FastAPI routers)
2. `app/services/` — Application services (business logic, orchestrate repos)
3. `app/workflows/` — Workflow engine (lifecycle, approvals, background jobs)
4. `app/ai/` — AI layer (one class per capability, built on the Anthropic client)
5. `app/knowledge/` — Knowledge layer (regulatory/standards/client/internal + RAG)
6. `app/parsers/` — Parsing layer (`ParserFactory` dispatches by file type/doc type)
7. `app/models/` — Domain model (SQLAlchemy ORM entities)
8. `app/repositories/` — Repository layer (CRUD access, one per aggregate)
9. `app/integrations/` — Integration layer (adapters for external systems)
10. Database — SQLite for dev, Postgres for prod, via `DATABASE_URL`
11. `storage/` — File storage (uploads, generated docs, evidence, templates)

Most files in the core path (models, repositories, services for Client/Project/
Document/Requirement/Risk/ValidationActivity/User/Notification, the FastAPI app,
parsers, RAG plumbing) are working code. The long tails — the 25+ third-party
integrations and the less common AI capabilities — are stub classes with a
consistent interface (`connect`/`test_connection`/...), ready for you to fill in
against each vendor's actual SDK.

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then fill in ANTHROPIC_API_KEY etc.
alembic upgrade head           # or just run the app once in dev (auto-creates tables)
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for the interactive API.

**Note on Python version:** `chromadb` depends on `onnxruntime`, which typically
takes a few months to publish wheels for a new CPython release. If `pip install`
fails while building `onnxruntime` or `cryptography` from source, use Python
3.11-3.13 for this venv (`python3.12 -m venv .venv`). Everything except RAG
semantic search (`/knowledge/search`) works fine without chromadb installed at
all, since `app/knowledge/rag/*` imports it lazily.

## Adding a new entity

1. Add the model in `app/models/`, register it in `app/models/__init__.py`.
2. Add a repository in `app/repositories/` (subclass `BaseRepository`).
3. Add a service in `app/services/` that calls the repository.
4. Add a router in `app/api/routes/`, include it in `app/main.py`.
5. `alembic revision --autogenerate -m "add <entity>"` then `alembic upgrade head`.

## Adding a new integration

Implement the relevant adapter base in `app/integrations/base.py` (or a
category base like `QMSAdapter`) inside the matching stub file under
`app/integrations/<category>/`. Each stub already has the method signatures
the rest of the app expects to call.
