
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
