from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_NAME = Path(__file__).resolve().parents[1].name
BASE_DIR = Path(__file__).resolve().parents[5]

class Settings(BaseSettings):

    APP_NAME: str
    APP_ENV: str
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    MONGO_URI: str
    MONGO_DATABASE: str

    REDIS_URL: str

    OBJECT_STORAGE_PROVIDER: str = "r2"
    OBJECT_STORAGE_BUCKET: str
    OBJECT_STORAGE_ENDPOINT: str
    OBJECT_STORAGE_ACCESS_KEY: str
    OBJECT_STORAGE_SECRET_KEY: str
    OBJECT_STORAGE_REGION: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    LLM_URL: str

    SEED_ADMIN_EMAIL: str
    SEED_ADMIN_PASSWORD: str
    SEED_ADMIN_DOCUMENT_ID: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / "credentials" / f"{PROJECT_NAME}.env",
        extra="ignore",
    )

settings = Settings()
