import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = "Enterprise AI Knowledge Assistant"
    VERSION: str = "0.2.0"

    RAW_DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://app_user:local_dev_password@localhost:5432/knowledge_assistant",
    )
    # SQLAlchemy defaults to psycopg2 for 'postgresql://'; switch to psycopg v3 automatically
    DATABASE_URL: str = (
        RAW_DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
        if RAW_DATABASE_URL.startswith("postgresql://")
        else RAW_DATABASE_URL
    )

    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY", "change-me-in-production-super-secret-key"
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(
        os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
    )


settings = Settings()