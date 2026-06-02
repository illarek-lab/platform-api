from fastapi import APIRouter

from app.projects.layout_example.api.auth import router as auth_router
from app.projects.layout_example.api.geo_events import router as geo_events_router
from app.projects.layout_example.api.geo_events_orm import router as geo_events_orm_router
from app.projects.layout_example.api.graphql.router import router as graphql_router

router = APIRouter()


@router.get("/health")
async def health():
    return {"project": "layout_example", "status": "ok"}


router.include_router(auth_router)
router.include_router(geo_events_router)
router.include_router(geo_events_orm_router)
router.include_router(graphql_router, prefix="/graphql")
