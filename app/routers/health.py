from fastapi import APIRouter
from app.database import check_db_connection
from app.config import settings
import datetime

router = APIRouter()

@router.get("/health")
def health_check():
    db_ok = check_db_connection()

    return {
        "status": "ok" if db_ok else "degraded",
        "app": settings.app_name,
        "environment": settings.app_env,
        "database": "connected" if db_ok else "unreachable",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }