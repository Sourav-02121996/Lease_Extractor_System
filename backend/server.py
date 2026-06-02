"""Lease Abstraction Assistant — FastAPI entrypoint."""
import logging
import os

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

logging.basicConfig(level=logging.INFO)

from routes import documents as documents_route  # noqa: E402
from routes import export as export_route  # noqa: E402
from routes import upload as upload_route  # noqa: E402
from db import db  # noqa: E402

app = FastAPI(title="Lease Abstraction Assistant")

cors_origins = os.environ.get("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_route.router)
app.include_router(documents_route.router)
app.include_router(export_route.router)


@app.get("/api/health")
async def health():
    db_connected = False
    db_error = None
    try:
        await db.command("ping")
        db_connected = True
    except Exception as exc:
        db_error = type(exc).__name__

    return {
        "status": "ok",
        "ai_provider": os.environ.get("AI_PROVIDER", "gemini"),
        "ai_key_configured": bool(os.environ.get("GEMINI_API_KEY")),
        "db_connected": db_connected,
        "db_error": db_error,
    }
