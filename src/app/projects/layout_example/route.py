from fastapi import APIRouter

from app.projects.layout_example.auth.router import router as auth_router

router = APIRouter()


# ─────────────────────────────
# Health (service status)
# ─────────────────────────────
@router.get("/health")
async def health():
    return {"project": "layout_example", "status": "ok"}


# ─────────────────────────────
# Include auth module
# ─────────────────────────────
router.include_router(auth_router)
