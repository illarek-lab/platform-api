import datetime
import secrets

import bcrypt


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def generate_refresh_token_value(expire_days: int) -> tuple[str, datetime.datetime]:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=expire_days)
    return token, expires_at
