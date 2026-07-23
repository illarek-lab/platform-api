
from fastapi import APIRouter, Depends

from app.projects.c22200002.api.deps import get_device_token_repo
from app.projects.c22200002.api.schemas import DeviceTokenCreate, DeviceTokenResponse
from app.projects.c22200002.infra.repositories.device_token_repo import DeviceTokenRepository

router = APIRouter(prefix="/device-tokens", tags=["device-tokens"])

@router.post("/", response_model=DeviceTokenResponse, status_code=201)
async def register_device_token(
    payload: DeviceTokenCreate,
    repo: DeviceTokenRepository = Depends(get_device_token_repo),
):
    return await repo.upsert(payload.model_dump())
