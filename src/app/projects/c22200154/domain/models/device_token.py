
# domain/models/device_token.py
from datetime import datetime
from pydantic import BaseModel

=======
# NOTA: implementacion por defecto copiada de layout_example para el lab de notificaciones.
# Reemplazala por tu propia implementacion cuando llegues a ese lab.

from datetime import datetime

from pydantic import BaseModel



class DeviceToken(BaseModel):
    id: str
    user_id: str
    user_name: str
    device_id: str
    fcm_token: str
    updated_at: datetime


    model_config = {"from_attributes": True}
=======
    model_config = {"from_attributes": True}

