from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import health, events

# Create the FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Local event discovery platform",
    version="0.1.0"
)

# CORS — allows the React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router)
app.include_router(events.router, prefix="/events")

@app.get("/")
def root():
    return {"message": "ChiPulse API is running"}