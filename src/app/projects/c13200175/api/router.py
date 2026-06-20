from fastapi import APIRouter

from app.projects.c13200175.api.auth import router as auth_router
from app.projects.c13200175.api.geo_events import router as geo_events_router
from app.projects.c13200175.api.geo_events_orm import router as geo_events_orm_router
from app.projects.c13200175.api.graphql.router import router as graphql_router
from app.projects.c13200175.api.storage import router as storage_router
from app.projects.c13200175.infra.settings import PROJECT_NAME

router = APIRouter()


@router.get("/health")
async def health():
    return {"project": PROJECT_NAME, "status": "ok"}


router.include_router(auth_router)
router.include_router(geo_events_router)
router.include_router(geo_events_orm_router)
router.include_router(graphql_router, prefix="/graphql")
router.include_router(storage_router)
