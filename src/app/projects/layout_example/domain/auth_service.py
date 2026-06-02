from app.projects.layout_example.domain.exceptions import (
    InvalidCredentialsError,
    InvalidGoogleTokenError,
    UserAlreadyExistsError,
)
from app.projects.layout_example.domain.ports import IGoogleOAuthClient, IUserRepository
from app.projects.layout_example.domain.security import hash_password, verify_password


class AuthService:

    def __init__(self, user_repo: IUserRepository, google_client: IGoogleOAuthClient) -> None:
        self._user_repo = user_repo
        self._google_client = google_client

    async def login(self, email: str, password: str) -> tuple[str, str]:
        user = await self._user_repo.find_by_email(email)

        if not user or not user.get("password"):
            raise InvalidCredentialsError

        if not verify_password(password, user["password"]):
            raise InvalidCredentialsError

        return str(user["_id"]), email

    async def register(self, email: str, password: str) -> str:
        if await self._user_repo.find_by_email(email):
            raise UserAlreadyExistsError

        result = await self._user_repo.create_user(
            {
                "email": email,
                "password": hash_password(password),
                "auth_provider": "local",
            }
        )
        return str(result.inserted_id)

    async def google_login(self, id_token: str) -> tuple[str, str]:
        data = await self._google_client.verify_id_token(id_token)

        if not data:
            raise InvalidGoogleTokenError

        email = data["email"]
        google_id = data["sub"]

        if not await self._user_repo.find_by_email(email):
            await self._user_repo.create_user(
                {
                    "email": email,
                    "google_id": google_id,
                    "auth_provider": "google",
                }
            )

        return google_id, email
