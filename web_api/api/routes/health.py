"""Health check and bot status endpoints."""

import logging
import os
from datetime import datetime

import aiosqlite
from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/health",
    summary="Health check",
    description="Check if the API is healthy and database is connected",
    tags=["Public"],
)
async def health_check():
    """
    Health check endpoint - no authentication required.
    Returns the health status of the API and database connection.
    """
    db_status = "ok"
    try:
        # Simple query to verify database connection
        from database.db import get_db, close_db
        db = await get_db()
        try:
            await db.execute("SELECT 1")
            await db.commit()
        finally:
            await close_db(db)
    except Exception as e:
        db_status = "error"

    return {"status": "healthy" if db_status == "ok" else "degraded", "database": db_status}


@router.get(
    "/bot-status",
    summary="Bot status",
    description="Get the current status of the bot and its services",
    tags=["Public"],
)
async def bot_status():
    """
    Bot status endpoint - no authentication required.
    Returns the status of various bot services including AI and database.
    """
    # Check database connection
    db_connected = True
    try:
        from database.db import get_db, close_db
        db = await get_db()
        try:
            await db.execute("SELECT 1")
        except Exception:
            db_connected = False
        finally:
            await close_db(db)
    except Exception:
        db_connected = False

    # Check AI availability (based on API key presence)
    ai_api_key = os.getenv("AI_API_KEY", "")
    ai_available = bool(ai_api_key and ai_api_key != "sk-...")

    # Determine overall status
    status = "operational" if db_connected else "degraded"

    return {
        "status": status,
        "ai_available": ai_available,
        "database_connected": db_connected,
        "last_updated": datetime.utcnow().isoformat(),
    }