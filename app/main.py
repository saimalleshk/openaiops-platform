
import logging
import os
from contextlib import asynccontextmanager

import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("openaiops.api")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured")


def initialize_database():
    """Create the events table if it does not exist."""
    with psycopg.connect(DATABASE_URL, connect_timeout=3) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS platform_events (
                id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                event_type VARCHAR(100) NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    logger.info("Database initialization successful")
    yield


app = FastAPI(
    title="OpenAIOps Platform API",
    description="A local platform engineering and AIOps learning project.",
    version="0.2.1",
    lifespan=lifespan,
)


class EventCreate(BaseModel):
    event_type: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=2000)


@app.get("/")
def root():
    return {
        "service": "openaiops-api",
        "version": "0.2.1",
        "message": "OpenAIOps Platform is running",
    }


@app.get("/health")
def health():
    """Liveness check: the API process can respond."""
    return {"status": "ok"}


@app.get("/ready")
def readiness():
    """Readiness check: verify database connectivity."""
    try:
        with psycopg.connect(DATABASE_URL, connect_timeout=3) as connection:
            connection.execute("SELECT 1")

        return {"status": "ready", "database": "connected"}

    except psycopg.Error:
        logger.exception("Database readiness check failed")
        raise HTTPException(
            status_code=503,
            detail={"status": "not_ready", "database": "unavailable"},
        )


@app.post("/events", status_code=201)
def create_event(event: EventCreate):
    """Store an event in PostgreSQL."""
    try:
        with psycopg.connect(DATABASE_URL, connect_timeout=3) as connection:
            row = connection.execute(
                """
                INSERT INTO platform_events (event_type, message)
                VALUES (%s, %s)
                RETURNING id, event_type, message, created_at
                """,
                (event.event_type, event.message),
            ).fetchone()

        return {
            "id": row[0],
            "event_type": row[1],
            "message": row[2],
            "created_at": row[3].isoformat(),
        }

    except psycopg.Error:
        logger.exception("Database write error")
        raise HTTPException(
            status_code=503,
            detail="Database operation failed",
        )


@app.get("/events")
def list_events():
    """Return the latest 100 events."""
    try:
        with psycopg.connect(DATABASE_URL, connect_timeout=3) as connection:
            rows = connection.execute(
                """
                SELECT id, event_type, message, created_at
                FROM platform_events
                ORDER BY id DESC
                LIMIT 100
                """
            ).fetchall()

        return [
            {
                "id": row[0],
                "event_type": row[1],
                "message": row[2],
                "created_at": row[3].isoformat(),
            }
            for row in rows
        ]

    except psycopg.Error:
        logger.exception("Database read error")
        raise HTTPException(
            status_code=503,
            detail="Database operation failed",
        )
