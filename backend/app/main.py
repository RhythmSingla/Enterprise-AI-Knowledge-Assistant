import psycopg
from fastapi import FastAPI, HTTPException

from app.api.v1 import auth, documents
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered enterprise document knowledge platform",
    version=settings.VERSION,
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "application": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }


@app.get("/health/db", tags=["Health"])
def database_health_check():
    try:
        with psycopg.connect(
            settings.RAW_DATABASE_URL,
            connect_timeout=3,
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()

        return {
            "status": "healthy",
            "database": "PostgreSQL",
            "connection": result[0] == 1,
        }

    except psycopg.Error:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed",
        )