from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
import jwt

from app.projects.layout_example.config.settings import settings

security = HTTPBearer()


def get_current_user(token=Depends(security)):

    try:
        payload = jwt.decode(
            token.credentials, settings.SECRET_KEY, algorithms=["HS256"]
        )

        return {"user_id": payload["sub"], "email": payload["email"]}

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
