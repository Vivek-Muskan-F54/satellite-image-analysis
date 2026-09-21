from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import health, auth, images, analyses
import logging

# Configure production logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting application in {settings.ENVIRONMENT} environment...")
    logger.info(f"CORS origins configured: {settings.CORS_ORIGINS}")
    from app.services.analysis_service import check_model_ready
    if check_model_ready():
        logger.info("ML model successfully loaded and ready.")
    else:
        logger.error("ML model failed to load at startup. Readiness check will fail.")
        if settings.ENVIRONMENT == "production":
            raise RuntimeError("Failed to load ML model in production environment.")
    yield
    logger.info("Shutting down application...")

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(images.router, prefix="/api/images", tags=["Images"])
app.include_router(analyses.router, prefix="/api/analyses", tags=["Analyses"])
