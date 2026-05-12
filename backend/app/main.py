from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.database import AsyncSessionLocal, db_is_configured
from app.routers import auth as auth_router
from app.routers import events as events_router
from app.routers import export as export_router
from app.routers import saves as saves_router

app = FastAPI(title="ChiPulse API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events_router.router)
app.include_router(export_router.router)
app.include_router(auth_router.router)
app.include_router(saves_router.router)


@app.get("/health")
async def health():
    if not db_is_configured():
        return {"status": "healthy", "database": "not configured (using adapters)"}
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": "disconnected"},
        )


@app.get("/")
async def root():
    return {"service": "ChiPulse API", "version": "0.1.0"}
