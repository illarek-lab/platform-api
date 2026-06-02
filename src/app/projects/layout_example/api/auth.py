from fastapi import APIRouter, Depends, HTTPException

from app.projects.layout_example.api.deps import get_auth_service, get_current_user
from app.projects.layout_example.api.schemas import (
    GoogleLoginRequest,
    LoginRequest,
    RegisterResponse,
    TokenResponse,
)
from app.projects.layout_example.domain.auth_service import AuthService
from app.projects.layout_example.domain.exceptions import (
    InvalidCredentialsError,
    InvalidGoogleTokenError,
    UserAlreadyExistsError,
)
from app.projects.layout_example.infra.token import create_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, service: AuthService = Depends(get_auth_service)):
    try:
        user_id, email = await service.login(payload.email, payload.password)
        return TokenResponse(access_token=create_token(user_id, email))
    except InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="Invalid credentials") from None


@router.post("/register", response_model=RegisterResponse)
async def register(payload: LoginRequest, service: AuthService = Depends(get_auth_service)):
    try:
        user_id = await service.register(payload.email, payload.password)
        return RegisterResponse(user_id=user_id)
    except UserAlreadyExistsError:
        raise HTTPException(status_code=400, detail="User already exists") from None


@router.post("/google", response_model=TokenResponse)
async def google_login(payload: GoogleLoginRequest, service: AuthService = Depends(get_auth_service)):
    try:
        google_id, email = await service.google_login(payload.token)
        return TokenResponse(access_token=create_token(google_id, email))
    except InvalidGoogleTokenError:
        raise HTTPException(status_code=401, detail="Invalid Google token") from None


@router.get("/me")
async def me(user=Depends(get_current_user)):
    return {"user": user}
