# Platform API

A multi-tenant FastAPI backend platform that hosts independent projects under a single application. Each project exposes its own endpoints, maintains isolated infrastructure, and follows a clean layered architecture.

---

## Overview

```
POST /layout_example/auth/login
POST /grupo1/auth/login
POST /grupo2/customers
```

Projects are **automatically discovered** at startup — no manual registration required. Adding a new project is as simple as creating a folder under `src/app/projects/`.

---

## Architecture

Each project follows a strict three-layer architecture:

```
api/          HTTP layer — routers, schemas, dependency wiring
domain/       Business logic — services, models, ports (interfaces)
infra/        Infrastructure — databases, external clients, repositories
```

Dependencies flow in one direction: `api → domain ← infra`. The domain layer never imports from infrastructure — concrete implementations are injected via constructor and FastAPI `Depends`.

```
platform-api/
├── pyproject.toml
├── uv.lock
├── credentials/
│   └── {project_slug}.env
└── src/
    └── app/
        ├── main.py
        ├── core/
        │   └── discovery.py        # auto-loads projects at startup
        └── projects/
            └── layout_example/
                ├── api/
                │   ├── router.py   # project entry point
                │   ├── auth.py
                │   ├── geo_events.py
                │   ├── geo_events_orm.py
                │   ├── storage.py
                │   ├── schemas.py
                │   ├── deps.py
                │   └── graphql/
                │       ├── router.py
                │       ├── types.py
                │       └── resolvers/
                ├── domain/
                │   ├── models/
                │   │   ├── user.py
                │   │   ├── geo_event.py
                │   │   └── file.py
                │   ├── ports.py            # interfaces (Protocol)
                │   ├── auth_service.py
                │   ├── storage_service.py
                │   ├── security.py
                │   └── exceptions.py
                └── infra/
                    ├── db/
                    │   ├── mongo.py
                    │   ├── postgres.py
                    │   └── redis.py
                    ├── clients/
                    │   ├── google.py
                    │   ├── storage.py
                    │   └── llm.py
                    ├── repositories/
                    │   ├── user_repo.py
                    │   ├── geo_event_repo.py
                    │   ├── geo_event_orm_repo.py
                    │   └── file_orm_repo.py
                    ├── orm/
                    │   ├── base.py
                    │   ├── geo_event.py
                    │   └── file.py
                    ├── settings.py
                    └── token.py
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI + Uvicorn |
| Package manager | uv |
| Validation | Pydantic v2 |
| PostgreSQL | SQLAlchemy 2.0 async + asyncpg |
| MongoDB | Motor (async) |
| Redis | redis-py async |
| Migrations | Alembic |
| Object storage | Cloudflare R2 / AWS S3 (aioboto3) |
| Authentication | JWT (PyJWT) + Google OAuth |
| GraphQL | Strawberry |
| HTTP client | HTTPX |
| Python | 3.12+ |

---

## Endpoints — `layout_example`

### Health

```http
GET /layout_example/health
```

### Auth

```http
POST /layout_example/auth/register
POST /layout_example/auth/login
POST /layout_example/auth/google
GET  /layout_example/auth/me
```

### Geo Events — Raw SQL

```http
POST   /layout_example/geo-events/
GET    /layout_example/geo-events/{id}
GET    /layout_example/geo-events/?user_id=&event_type=&limit=&offset=
DELETE /layout_example/geo-events/{id}
```

### Geo Events — ORM

```http
POST   /layout_example/geo-events-orm/
GET    /layout_example/geo-events-orm/{id}
GET    /layout_example/geo-events-orm/?user_id=&event_type=&limit=&offset=
DELETE /layout_example/geo-events-orm/{id}
```

### Geo Events — GraphQL

```http
GET  /layout_example/graphql        # GraphiQL playground
POST /layout_example/graphql        # queries & mutations
```

```graphql
query  { geoEvent(id: 1) { ... } }
query  { geoEvents(eventType: "gps_ping", limit: 20) { ... } }
mutation { createGeoEvent(input: { latitude: 19.4326, longitude: -99.1332, ... }) { id } }
mutation { deleteGeoEvent(id: 1) }
```

### Storage

```http
POST   /layout_example/storage/upload-url     # generate presigned PUT URL
POST   /layout_example/storage/confirm        # register file metadata
GET    /layout_example/storage/files          # list files (active only)
DELETE /layout_example/storage/file/{id}      # soft delete
```

**Upload flow:**

```
1. POST /storage/upload-url  →  { upload_url, object_key }
2. PUT  {upload_url}         →  upload file directly to R2/S3 (client-side)
3. POST /storage/confirm     →  register metadata in PostgreSQL
```

> `user_id` is always extracted from the JWT — the client never sends it. `object_key` is validated to match `{project_slug}/{user_id}/...` to prevent cross-tenant access.

---

## Local Development

### Prerequisites

Install [uv](https://docs.astral.sh/uv/):

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Setup

```bash
# Install dependencies
uv sync

# Copy and fill environment variables
cp credentials/layout_example.env.example credentials/layout_example.env

# Run the server
uv run uvicorn app.main:app --reload
```

Server available at `http://localhost:8000` · Swagger UI at `http://localhost:8000/docs`

### Environment Variables

Each project reads from `credentials/{project_slug}.env`:

```env
# App
APP_NAME=layout_example
APP_ENV=development
DEBUG=true

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=platform
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secret

# MongoDB
MONGO_URI=mongodb://localhost:27017
MONGO_DATABASE=platform

# Redis
REDIS_URL=redis://localhost:6379

# Storage (Cloudflare R2 / AWS S3)
OBJECT_STORAGE_PROVIDER=r2
OBJECT_STORAGE_BUCKET=my-bucket
OBJECT_STORAGE_ENDPOINT=https://<account-id>.r2.cloudflarestorage.com
OBJECT_STORAGE_ACCESS_KEY=...
OBJECT_STORAGE_SECRET_KEY=...
OBJECT_STORAGE_REGION=auto

# Auth
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=...

# LLM
LLM_URL=http://localhost:11434
```

---

## Adding a New Project

1. **Create the folder** under `src/app/projects/`:

```
src/app/projects/my_project/
├── api/
│   ├── router.py       ← required — discovery looks for this file
│   ├── deps.py
│   └── schemas.py
├── domain/
│   ├── models/
│   ├── ports.py
│   └── exceptions.py
└── infra/
    ├── db/
    ├── clients/
    ├── repositories/
    └── settings.py
```

2. **Export a `router` object** from `api/router.py`:

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health():
    return {"project": "my_project", "status": "ok"}
```

3. **Add credentials** file at `credentials/my_project.env`.

The platform will **automatically mount** the project at `/my_project/*` on the next startup — no changes to `main.py` required.

---

## Design Principles

- **Per-project isolation** — each project owns its configuration, databases, and clients
- **Dependency inversion** — domain defines interfaces (`Protocol`); infrastructure implements them
- **Constructor injection** — services receive dependencies as arguments, enabling testability
- **Soft deletes** — file records are never physically removed; `deleted_at` is set instead
- **Presigned uploads** — files go directly from client to object storage; the API only handles metadata
- **JWT-bound ownership** — `user_id` is always derived from the token, never trusted from the request body

---

## Roadmap

- [x] Multi-project auto-discovery
- [x] JWT authentication (local + Google OAuth)
- [x] PostgreSQL async (raw SQL + ORM)
- [x] MongoDB async (Motor)
- [x] Cloudflare R2 / S3 presigned uploads
- [x] GraphQL (Strawberry)
- [x] Soft deletes
- [ ] Alembic migrations
- [ ] Redis caching
- [ ] Rate limiting
- [ ] Background jobs
- [ ] Observability (structured logging + tracing)
- [ ] Admin seed
