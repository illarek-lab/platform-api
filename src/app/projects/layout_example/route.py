from fastapi import APIRouter

router = APIRouter()


# ─────────────────────────────
# Health check
# ─────────────────────────────
@router.get("/health")
async def health():
    return {"project": "layout_example", "status": "ok"}
