# Platform API

Platform API es una plataforma backend construida con FastAPI que permite alojar múltiples proyectos independientes dentro de una única aplicación.

Cada proyecto expone sus propios endpoints bajo un prefijo específico y mantiene aislamiento lógico de:

- Autenticación
- Base de datos
- Cache
- Almacenamiento de archivos
- Servicios de IA

---

## Objetivo

La plataforma permite incorporar nuevos proyectos sin modificar la arquitectura principal.

Ejemplos:

```text
/layout_example/*
/grupo1/*
/grupo2/*
/proyectox/*
```

Cada proyecto puede tener:

- PostgreSQL propio
- Redis propio
- OAuth/OIDC propio
- Cloudflare R2 propio
- Servidor LLM propio

---

# Arquitectura

```text
Mobile App
     │
     ▼
Platform API
     │
     ├── /layout_example/*
     ├── /grupo1/*
     ├── /grupo2/*
     └── /proyectox/*
```

Ejemplo:

```http
POST /layout_example/auth/login
POST /layout_example/ai/chat

POST /grupo1/auth/login
POST /grupo1/customers
```

---

# Tecnologías

- Python 3.12+
- FastAPI
- Uvicorn
- uv
- PostgreSQL
- Redis
- Cloudflare R2
- OAuth 2.1 / OpenID Connect
- HTTPX
- Pydantic
- SQLAlchemy
- Alembic

---

# Estructura del proyecto

```text
platform-api/

├── pyproject.toml
├── uv.lock
├── .env
│
└── src/
    │
    └── app/
        │
        ├── main.py
        │
        ├── core/
        │
        └── projects/
            │
            ├── layout_example/
            │   ├── config/
            │   ├── database/
            │   ├── auth/
            │   ├── ai/
            │   ├── files/
            │   └── router.py
            │
            ├── grupo1/
            │
            ├── grupo2/
            │
            └── proyectox/
```

---

# Conceptos

## Proyecto

Un proyecto representa un dominio funcional independiente.

Ejemplo:

```text
layout_example
grupo1
grupo2
```

Cada proyecto registra su propio router.

---

## AI

Cada proyecto puede utilizar un servidor LLM diferente.

Ejemplo:

```text
layout_example
    └── http://10.0.0.10:8000

grupo1
    └── http://10.0.0.20:8000
```

Los endpoints de IA actúan como orquestadores y delegan el procesamiento al servidor correspondiente.

---

## Archivos

Los archivos se almacenan mediante Cloudflare R2.

La base de datos almacena únicamente metadata:

```text
id
filename
content_type
size
storage_key
created_at
```

---

## Autenticación

Cada proyecto puede implementar su propia estrategia OAuth/OIDC.

Ejemplos:

```text
/layout_example/auth/*
/grupo1/auth/*
```

Los tokens y credenciales pueden ser completamente independientes entre proyectos.

---

# Desarrollo local

## Instalar uv

### Linux / macOS

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

---

## Instalar dependencias

```bash
uv sync
```

---

## Ejecutar servidor

```bash
uv run uvicorn src.app.main:app --reload
```

Servidor disponible en:

```text
http://localhost:8000
```

---

# Endpoints

## Layout Example

### Health

```http
GET /layout_example/health
```

### Auth

```http
POST /layout_example/auth/login
POST /layout_example/auth/logout
GET  /layout_example/auth/me
```

### AI

```http
POST /layout_example/ai/chat
POST /layout_example/ai/analyze
```

### Files

```http
POST   /layout_example/files/upload
GET    /layout_example/files/{id}
DELETE /layout_example/files/{id}
```

---

# Agregar un nuevo proyecto

## 1. Crear carpeta

```text
src/app/projects/grupo3
```

## 2. Crear estructura

```text
grupo3/

├── config/
├── database/
├── auth/
├── ai/
├── files/
└── router.py
```

## 3. Registrar router

```python
app.include_router(
    grupo3_router,
    prefix="/grupo3"
)
```

## 4. Configurar infraestructura

- PostgreSQL
- Redis
- OAuth/OIDC
- Cloudflare R2
- Servidor LLM

---

# Principios

- Separación por proyecto.
- Bajo acoplamiento.
- Infraestructura configurable por proyecto.
- API-first para aplicaciones móviles.
- Integración con IA mediante servidores externos.
- Escalabilidad horizontal futura.
- Modularidad y mantenimiento simplificado.

---

# Roadmap

- [ ] OAuth 2.1
- [ ] Cloudflare R2
- [ ] Redis Cache
- [ ] PostgreSQL + SQLAlchemy
- [ ] Alembic Migrations
- [ ] Auditoría
- [ ] Rate Limiting
- [ ] Background Jobs
- [ ] Observabilidad
- [ ] Multi-project Management