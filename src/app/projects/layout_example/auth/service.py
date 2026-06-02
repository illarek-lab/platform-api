from app.projects.layout_example.auth.repository import user_repo
from app.projects.layout_example.auth.security import (
    hash_password,
    verify_password,
    create_token,
)

import httpx
from app.projects.layout_example.config.settings import settings


class AuthService:

    # ─────────────────────────────
    # Email / Password Login
    # ─────────────────────────────
    async def login(self, email: str, password: str):

        user = await user_repo.find_by_email(email)

        if not user:
            return None

        if not verify_password(password, user["password"]):
            return None

        token = create_token(str(user["_id"]), email)

        return {"access_token": token, "token_type": "bearer"}

    # ─────────────────────────────
    # Register (simple)
    # ─────────────────────────────
    async def register(self, email: str, password: str):

        existing = await user_repo.find_by_email(email)

        if existing:
            return None

        user = {
            "email": email,
            "password": hash_password(password),
            "auth_provider": "local",
        }

        result = await user_repo.create_user(user)

        return str(result.inserted_id)

    # ─────────────────────────────
    # Google Login
    # ─────────────────────────────
    async def google_login(self, id_token: str):

        async with httpx.AsyncClient() as client:

            res = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
            )

        if res.status_code != 200:
            return None

        data = res.json()

        email = data["email"]
        google_id = data["sub"]

        user = await user_repo.find_by_email(email)

        if not user:
            user = {"email": email, "google_id": google_id, "auth_provider": "google"}

            await user_repo.create_user(user)

        token = create_token(google_id, email)

        return {"access_token": token, "token_type": "bearer"}


auth_service = AuthService()
