from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleLoginRequest(BaseModel):
    token: str  # Google ID token


class UserResponse(BaseModel):
    id: str
    email: EmailStr
