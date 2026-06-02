from fastapi import APIRouter

from app.projects.layout_example.api.auth import router as auth_router

router = APIRouter()


@router.get("/health")
async def health():
    return {"project": "layout_example", "status": "ok"}


router.include_router(auth_router)
