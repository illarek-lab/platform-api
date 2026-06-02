from fastapi import FastAPI

from app.projects.layout_example.router import router as layout_router

app = FastAPI(title="Platform API", version="1.0.0")

# ─────────────────────────────────────────────
# Projects (multi-tenant style)
# ─────────────────────────────────────────────

app.include_router(layout_router, prefix="/layout_example", tags=["layout_example"])
