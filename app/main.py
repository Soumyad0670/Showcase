import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from app.api.routes import api_router
from app.core.config import settings
from app.adapters.database import engine
from app.models.portfolio import Portfolio 

# --- YOUR SOUL INJECTION START ---
from app.chat import router as chat_router 
# --- YOUR SOUL INJECTION END ---

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    """
    logger.info("Showcase AI: Initializing Infrastructure...")
    SQLModel.metadata.create_all(engine)
    yield 
    logger.info(" Showcase AI: Shutting down safely")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="AI-Powered Portfolio Engine",
    debug=settings.DEBUG,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    # Allow all origins for development
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Team's original routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# --- YOUR SOUL INJECTION START ---
app.include_router(chat_router, prefix="/api/v1/chat")
# --- YOUR SOUL INJECTION END ---

@app.get("/health", include_in_schema=False)
async def health_check():
    return {
        "status": "online",
        "engine": "Gemini-Vision-v1",
        "auth": "Firebase-Google-Cloud"
    }
