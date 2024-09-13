from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

router = APIRouter()


# Root endpoint ("/") - Health check or welcome message
@router.get("/")
async def read_root():
    return {"message": "Welcome to the Task Tracker API!"}


# Database connection check ("/check_db")
@router.get("/check_db")
async def check_db_connection(db: AsyncSession = Depends(get_db)):
    try:
        # Run a simple query to check if the connection is working
        result = await db.execute(text("SELECT 1"))
        return {"database_status": "Connection successful"}
    except Exception as e:
        return {"database_status": "Connection failed", "error": str(e)}
