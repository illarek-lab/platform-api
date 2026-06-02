from passlib.context import CryptContext
import jwt
import datetime

from app.projects.layout_example.config.settings import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_token(user_id: str, email: str):
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2),
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
