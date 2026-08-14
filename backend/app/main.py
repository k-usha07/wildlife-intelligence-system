"""
Wildlife Population Intelligence System — Backend Entry Point
Safe-import version: will NOT crash if new modules are missing
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

# ── Config (required — will fail here if config is broken) ────────────────
from app.core.config import settings

# ── Milestone 1 routers (these MUST exist) ────────────────────────────────
from app.routers import auth, users, monitoring_sites, surveys

# ── Milestone 2-4 routers (safe — skip/0 if missing) ─────────────────────
species_router = None
image_analysis_router = None
audio_analysis_router = None
intelligence_router = None
notifications_router = None
reports_router = None

try:
    from app.routers.species import router as species_router
except Exception as e:
    logger.warning(f"⚠️  species router not loaded: {e}")

try:
    from app.routers.image_analysis import router as image_analysis_router
except Exception as e:
    logger.warning(f"⚠️  image_analysis router not loaded: {e}")

try:
    from app.routers.audio_analysis import router as audio_analysis_router
except Exception as e:
    logger.warning(f"⚠️  audio_analysis router not loaded: {e}")

try:
    from app.routers.intelligence import router as intelligence_router
except Exception as e:
    logger.warning(f"⚠️  intelligence router not loaded: {e}")

try:
    from app.routers.notifications import router as notifications_router
except Exception as e:
    logger.warning(f"⚠️  notifications router not loaded: {e}")

try:
    from app.routers.reports import router as reports_router
except Exception as e:
    logger.warning(f"⚠️  reports router not loaded: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🦁 {settings.app_name} v1.0.0 starting...")

    # Try loading ML models (non-fatal if they fail)
    try:
        from app.ml.image_engine.detector import image_detector
        image_detector.load_model()
        print("  ✅ YOLOv8 image detector loaded")
    except Exception as exc:
        print(f"  ⚠️  Image detector not loaded: {exc}")

    try:
        from app.ml.species_engine.classifier import species_classifier
        species_classifier.load_model()
        print("  ✅ Species classifier loaded")
    except Exception as exc:
        print(f"  ⚠️  Species classifier not loaded: {exc}")

    print(f"🦁 {settings.app_name} is LIVE")
    yield
    print("🦁 Shutting down...")


app = FastAPI(
    title=settings.app_name,
    description="AI-powered Wildlife Population Intelligence System",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Milestone 1 routers (always present) ────────────────────────
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(monitoring_sites.router)
app.include_router(monitoring_sites.devices_router)
app.include_router(surveys.router)

# ── Register Milestone 2-4 routers (only if loaded) ──────────────────────
if species_router:
    app.include_router(species_router)
if image_analysis_router:
    app.include_router(image_analysis_router)
if audio_analysis_router:
    app.include_router(audio_analysis_router)
if intelligence_router:
    app.include_router(intelligence_router)
if notifications_router:
    app.include_router(notifications_router)
if reports_router:
    app.include_router(reports_router)


@app.get("/", tags=["root"])
def read_root():
    return {"message": "Wildlife Intelligence API is live!", "docs": "/docs"}


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "service": settings.app_name, "version": "1.0.0"}