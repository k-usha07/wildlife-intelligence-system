from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

from app.core.config import settings
from app.routers import auth, users, monitoring_sites, surveys

# Safe imports for new routers
species_router = None
image_analysis_router = None
audio_analysis_router = None
intelligence_router = None
notifications_router = None
reports_router = None

try:
    from app.routers.species import router as species_router
except Exception as e:
    logger.warning(f"Species router not loaded: {e}")

try:
    from app.routers.image_analysis import router as image_analysis_router
except Exception as e:
    logger.warning(f"Image analysis router not loaded: {e}")

try:
    from app.routers.audio_analysis import router as audio_analysis_router
except Exception as e:
    logger.warning(f"Audio analysis router not loaded: {e}")

try:
    from app.routers.intelligence import router as intelligence_router
except Exception as e:
    logger.warning(f"Intelligence router not loaded: {e}")

try:
    from app.routers.notifications import router as notifications_router
except Exception as e:
    logger.warning(f"Notifications router not loaded: {e}")

try:
    from app.routers.reports import router as reports_router
except Exception as e:
    logger.warning(f"Reports router not loaded: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🦁 {settings.app_name} v{settings.version} starting...")
    yield
    print("🦁 Shutting down...")


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(monitoring_sites.router)
app.include_router(monitoring_sites.devices_router)
app.include_router(surveys.router)

if species_router: app.include_router(species_router)
if image_analysis_router: app.include_router(image_analysis_router)
if audio_analysis_router: app.include_router(audio_analysis_router)
if intelligence_router: app.include_router(intelligence_router)
if notifications_router: app.include_router(notifications_router)
if reports_router: app.include_router(reports_router)


@app.get("/")
def read_root():
    return {"message": "Wildlife Intelligence API is live!", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "ok", "service": settings.app_name, "version": settings.version}