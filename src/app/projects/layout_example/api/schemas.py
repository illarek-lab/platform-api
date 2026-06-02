from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleLoginRequest(BaseModel):
    token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    user_id: str


class GeoEventCreate(BaseModel):
    user_id: Optional[UUID] = None
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None
    event_type: str = "gps_ping"
    device_id: Optional[str] = None
    platform: Optional[str] = None
    app_version: Optional[str] = None
    device_model: Optional[str] = None
    recorded_at: Optional[datetime] = None


class GeoEventResponse(BaseModel):
    id: int
    user_id: Optional[UUID] = None
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None
    event_type: str
    device_id: Optional[str] = None
    platform: Optional[str] = None
    app_version: Optional[str] = None
    device_model: Optional[str] = None
    recorded_at: datetime
    created_at: datetime
