from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db

router = APIRouter()

@router.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "message": "Service is healthy"}

@router.get("/ready", tags=["System"])
def readiness_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"

    return {
        "status": "ready" if db_status == "ok" else "not_ready",
        "database": db_status
    }

@router.get("/live", tags=["System"])
def liveness_check():
    return {"status": "alive"}
