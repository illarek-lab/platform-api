from fastapi import APIRouter, HTTPException, Depends
from app.projects.layout_example.auth.schemas import LoginRequest, GoogleLoginRequest
from app.projects.layout_example.auth.service import auth_service
from app.projects.layout_example.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


# ─────────────────────────────
# Login email/password
# ─────────────────────────────
@router.post("/login")
async def login(payload: LoginRequest):

    result = await auth_service.login(payload.email, payload.password)

    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return result


# ─────────────────────────────
# Register
# ─────────────────────────────
@router.post("/register")
async def register(payload: LoginRequest):

    user_id = await auth_service.register(payload.email, payload.password)

    if not user_id:
        raise HTTPException(status_code=400, detail="User already exists")

    return {"user_id": user_id}


# ─────────────────────────────
# Google login
# ─────────────────────────────
@router.post("/google")
async def google_login(payload: GoogleLoginRequest):

    result = await auth_service.google_login(payload.token)

    if not result:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    return result


# ─────────────────────────────
# ME (CURRENT USER)
# ─────────────────────────────
@router.get("/me")
async def me(user=Depends(get_current_user)):

    return {"user": user}
