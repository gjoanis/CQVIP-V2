# CQVIP — Computerized Quality Validation Information Platform

A validation/compliance management platform for regulated (GxP) environments:
managing validation projects, requirements, risk, and documentation, backed by
an AI layer and a RAG-based regulatory/standards knowledge base.

## Structure

```
cqvip/
├── backend/    FastAPI + SQLAlchemy + Alembic + ChromaDB + Anthropic Claude
└── frontend/   React + Vite + TypeScript SPA
```

See [backend/README.md](backend/README.md) for the backend's 11-layer
architecture, and `frontend/src/` for the frontend (pages, components,
layouts, hooks, services, types).

## Getting started

You need Python 3.11+ and Node.js 18+.

**Backend** (from `backend/`):

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then fill in ANTHROPIC_API_KEY etc.
uvicorn app.main:app --reload --port 8000
```

**Frontend** (from `frontend/`, in a second terminal):

```bash
npm install
cp .env.example .env          # VITE_API_BASE_URL defaults to http://localhost:8000
npm run dev
```

Visit `http://localhost:5173`. The backend's interactive API docs are at
`http://localhost:8000/docs`.

First run: register an account from the frontend's login screen (there's no
seed user). Auth is a real JWT flow (`POST /auth/register`, `POST /auth/login`,
`GET /auth/me`) — the frontend stores the token in `localStorage` and attaches
it as a Bearer token to every request.

**Note on Python version:** `chromadb` depends on `onnxruntime`, which lags
behind new CPython releases. If `pip install` fails on `onnxruntime`, use
Python 3.11-3.13 for the backend venv, or skip it for now — everything except
RAG search (`/knowledge/search`) works without chromadb installed, since
`app/knowledge/rag/*` imports it lazily.

## How the two sides connect

- CORS is configured via `CORS_ORIGINS` in `backend/.env` (defaults include
  `http://localhost:5173`, Vite's default port).
- The frontend's project-scoped pages (Requirements, Risk Register, Documents,
  etc.) all read from a single "current project" selector in the header —
  there's no per-page project picker, and most API calls are scoped by
  `project_id`.
- Any unhandled backend exception is caught by a middleware in
  `backend/app/main.py` (`catch_unhandled_exceptions`) so it comes back as a
  normal JSON 500 with CORS headers intact, instead of an opaque browser
  network error. Keep new custom middleware registered *before*
  `app.add_middleware(CORSMiddleware, ...)` if you want it to run inside CORS
  the same way.
