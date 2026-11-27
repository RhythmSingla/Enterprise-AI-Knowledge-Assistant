import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = "Enterprise AI Knowledge Assistant"
    VERSION: str = "0.4.0"

    RAW_DATABASE_URL: str = os.getenv( # Reads the environment variable if it is set; otherwise, it falls back to the second argument as a safe default.
        "DATABASE_URL",
        "postgresql://app_user:local_dev_password@localhost:5432/knowledge_assistant",
    )
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

    # Document storage & validation settings
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "storage")
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))

    # Chunking & vector embedding settings
    EMBEDDING_MODEL_NAME: str = os.getenv( # model used by the Embedding Service to convert text into meaning vectors.
        "EMBEDDING_MODEL_NAME", "BAAI/bge-small-en-v1.5" # fast, open-source model that runs locally on CPU without external API keys
    )
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "384")) # bge-small-en-v1.5 natively outputs 384 numbers per input, which directly matches the PostgreSQL vector(384) column definition.
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "800")) # 800 characters equals roughly 120–160 words (about 1–2 paragraphs)
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "150")) # How many characters from the end of one chunk are repeated at the beginning of the next chunk. Prevents semantic loss when an important rule or sentence gets split


settings = Settings()