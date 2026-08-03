from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, users, monitoring_sites, surveys

app = FastAPI(
    title=settings.app_name,
    description="Milestone 1: authentication, RBAC, and wildlife monitoring workflows.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(monitoring_sites.router)
app.include_router(monitoring_sites.devices_router)
app.include_router(surveys.router)


@app.get("/", tags=["root"])
def read_root():
    return {"message": "Wildlife Prediction API is live!"}

@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "service": settings.app_name}