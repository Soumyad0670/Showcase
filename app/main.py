import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from app.api.routes import api_router
from app.core.config import settings
from app.adapters.database import engine
from app.models.portfolio import Portfolio 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events.
    Triggers database table creation on launch.
    """
    logger.info("🚀 Showcase AI: Initializing Infrastructure...")
    
    SQLModel.metadata.create_all(engine)
    
    yield 
    
    logger.info("🛑 Showcase AI: Shutting down safely")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="AI-Powered Portfolio Engine",
    debug=settings.DEBUG,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", include_in_schema=False)
async def health_check():
    """Hidden from Swagger docs; used by cloud monitors to verify status."""
    return {
        "status": "online",
        "engine": "Gemini-Vision-v1",
        "auth": "Firebase-Google-Cloud"
    }