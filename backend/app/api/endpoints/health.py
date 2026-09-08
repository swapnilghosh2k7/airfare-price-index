from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.core.config import settings

router = APIRouter()

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Check DB connection
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy ({str(e)})"

    return {
        "status": "online",
        "app_name": settings.name,
        "version": settings.version,
        "demo_mode": settings.demo_mode,
        "database_status": db_status,
        "methodology_version": settings.indexing.methodology_version
    }
