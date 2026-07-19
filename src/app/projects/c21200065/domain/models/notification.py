# NOTA: implementacion por defecto copiada de layout_example para el lab de notificaciones.
# Reemplazala por tu propia implementacion cuando llegues a ese lab.

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Notification(BaseModel):
    id: str
    user_id: str
    token: str
    title: str
    body: str
    data: Optional[dict[str, str]] = None
    status: str
    error: Optional[str] = None
    created_at: datetime
    sent_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
