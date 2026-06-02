from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # App
    APP_NAME: str
    APP_ENV: str
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # PostgreSQL
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    # Mongo
    MONGO_URI: str
    MONGO_DATABASE: str

    # Redis
    REDIS_URL: str

    # Storage
    OBJECT_STORAGE_BUCKET: str
    OBJECT_STORAGE_ENDPOINT: str
    OBJECT_STORAGE_ACCESS_KEY: str
    OBJECT_STORAGE_SECRET_KEY: str
    OBJECT_STORAGE_REGION: str

    # Auth
    OIDC_ISSUER: str
    OIDC_AUDIENCE: str

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    # AI
    LLM_URL: str

    # Seed
    SEED_ADMIN_EMAIL: str
    SEED_ADMIN_PASSWORD: str
    SEED_ADMIN_DOCUMENT_ID: str

    model_config = SettingsConfigDict(
        env_file="credentials/layout_example.env", extra="ignore"
    )


settings = Settings()
