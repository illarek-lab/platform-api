import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

from app.projects.layout_example.domain.auth_service import AuthService
from app.projects.layout_example.infra.clients.google import GoogleOAuthClient
from app.projects.layout_example.infra.settings import settings
from app.projects.layout_example.infra.repositories.user_repo import UserRepository

security = HTTPBearer()

_user_repo = UserRepository()
_google_client = GoogleOAuthClient()
_auth_service = AuthService(_user_repo, _google_client)


def get_auth_service() -> AuthService:
    return _auth_service


def get_current_user(token=Depends(security)):
    try:
        payload = jwt.decode(
            token.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return {"user_id": payload["sub"], "email": payload["email"]}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token") from None
