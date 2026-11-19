import os

import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

load_dotenv()

app = FastAPI(
    title="Enterprise AI Knowledge Assistant",
    description="AI-powered enterprise document knowledge platform",
    version="0.1.0"
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "Enterprise AI Knowledge Assistant"
    }


@app.get("/health/db")
def database_health_check():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise HTTPException(
            status_code=500,
            detail="DATABASE_URL is not configured"
        )

    try:
        with psycopg.connect(
            database_url,
            connect_timeout=3
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()

        return {
            "status": "healthy",
            "database": "PostgreSQL",
            "connection": result[0] == 1
        }

    except psycopg.Error:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed"
        )