from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.routers import auth, users, monitoring_sites, surveys
from app.routers import species, image_analysis, audio_analysis
from app.routers import intelligence, notifications, reports


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle handler."""
    # ── Startup ──────────────────────────────────────────────────────
    print(f"🦁 {settings.app_name} v{settings.version} starting...")

    # Pre-load ML models (lazy — only if files exist on disk)
    try:
        from app.ml.image_engine.detector import image_detector
        image_detector.load_model()
        print("  ✅ YOLOv8 wildlife image detector loaded")
    except Exception as exc:
        print(f"  ⚠️  Image detector not loaded: {exc}")

    try:
        from app.ml.audio_engine.recognizer import audio_recognizer
        # No explicit load needed — librosa loads on demand
        print("  ✅ Bioacoustic recognizer ready")
    except Exception as exc:
        print(f"  ⚠️  Audio recognizer not loaded: {exc}")

    try:
        from app.ml.species_engine.classifier import species_classifier
        species_classifier.load_model()
        print("  ✅ Species classifier loaded")
    except Exception as exc:
        print(f"  ⚠️  Species classifier not loaded: {exc}")

    print(f"🦁 {settings.app_name} is LIVE")

    yield

    # ── Shutdown ─────────────────────────────────────────────────────
    print(f"🦁 {settings.app_name} shutting down...")


# ──────────────────────────────────────────────────────────────────────────────
# App creation
# ──────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    description=(
        "AI-powered Wildlife Population Intelligence System — "
        "Species recognition, bioacoustic analysis, population estimation, "
        "biodiversity analytics, habitat intelligence, conservation recommendations, "
        "ecosystem health scoring, dashboards, reports."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ──────────────────────────────────────────────────────────────────────────────
# Middleware
# ──────────────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────────────────────────────────────
# Milestone 1 routers (already existed)
# ──────────────────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(monitoring_sites.router)
app.include_router(monitoring_sites.devices_router)
app.include_router(surveys.router)


# ──────────────────────────────────────────────────────────────────────────────
# Milestone 2 routers — species recognition & biodiversity
# ──────────────────────────────────────────────────────────────────────────────
app.include_router(species.router)
app.include_router(image_analysis.router)
app.include_router(audio_analysis.router)


# ──────────────────────────────────────────────────────────────────────────────
# Milestone 3 routers — population, habitat, conservation, health
# ──────────────────────────────────────────────────────────────────────────────
app.include_router(intelligence.router)


# ──────────────────────────────────────────────────────────────────────────────
# Milestone 4 routers — notifications, reports & export
# ──────────────────────────────────────────────────────────────────────────────
app.include_router(notifications.router)
app.include_router(reports.router)


# ──────────────────────────────────────────────────────────────────────────────
# Health / root
# ──────────────────────────────────────────────────────────────────────────────
@app.get("/", tags=["root"])
def read_root():
    return {
        "message": "Wildlife Population Intelligence API is live!",
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "service": settings.app_name, "version": "1.0.0"}