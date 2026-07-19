# NOTA: implementacion por defecto copiada de layout_example para el lab de notificaciones.
# Reemplazala por tu propia implementacion cuando llegues a ese lab.

from fastapi import APIRouter, Depends

from app.projects.c19200185.api.deps import get_notification_service
from app.projects.c19200185.api.schemas import NotificationCreate, NotificationResponse
from app.projects.c19200185.domain.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post("/", response_model=NotificationResponse, status_code=201)
async def send_notification(
    payload: NotificationCreate,
    service: NotificationService = Depends(get_notification_service),
):
    notification = await service.send(**payload.model_dump())
    return NotificationResponse(**notification.model_dump())
