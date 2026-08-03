from fastapi import APIRouter, Depends, HTTPException
from geoalchemy2 import Geometry
from geoalchemy2.functions import ST_X, ST_Y
from geoalchemy2.elements import WKTElement
from sqlalchemy import cast, func
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_roles
from app.core.database import get_db
from app.models.monitoring_site import Device, MonitoringSite
from app.models.user import User
from app.schemas.monitoring_site import (
    DeviceCreate,
    DeviceOut,
    HABITAT_CHOICES,
    MonitoringSiteCreate,
    MonitoringSiteOut,
)

router = APIRouter(prefix="/monitoring-sites", tags=["monitoring-sites"])

# Roles allowed to register/manage sites and devices
MANAGE_ROLES = ("admin", "forest_department", "conservation_officer", "researcher")


def _site_to_out(site: MonitoringSite, lon: float, lat: float, device_count: int = 0) -> MonitoringSiteOut:
    return MonitoringSiteOut(
        id=site.id,
        name=site.name,
        habitat_type=site.habitat_type,
        protected_area=site.protected_area,
        latitude=lat,
        longitude=lon,
        elevation_m=float(site.elevation_m) if site.elevation_m is not None else None,
        description=site.description,
        created_at=site.created_at,
        device_count=device_count,
    )


@router.post("", response_model=MonitoringSiteOut, status_code=201)
def create_site(
    payload: MonitoringSiteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*MANAGE_ROLES)),
):
    if payload.habitat_type not in HABITAT_CHOICES:
        raise HTTPException(status_code=400, detail=f"Invalid habitat_type. Choose one of {HABITAT_CHOICES}")

    point = WKTElement(f"POINT({payload.longitude} {payload.latitude})", srid=4326)
    site = MonitoringSite(
        name=payload.name,
        habitat_type=payload.habitat_type,
        protected_area=payload.protected_area,
        location=point,
        elevation_m=payload.elevation_m,
        description=payload.description,
        created_by=current_user.id,
    )
    db.add(site)
    db.commit()
    db.refresh(site)
    return _site_to_out(site, payload.longitude, payload.latitude)


@router.get("", response_model=list[MonitoringSiteOut])
def list_sites(db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    rows = (
        db.query(
            MonitoringSite,
            ST_X(cast(MonitoringSite.location, Geometry)).label("lon"),
            ST_Y(cast(MonitoringSite.location, Geometry)).label("lat"),
            func.count(Device.id).label("device_count"),
        )
        .outerjoin(Device, Device.monitoring_site_id == MonitoringSite.id)
        .group_by(MonitoringSite.id)
        .all()
    )
    return [_site_to_out(site, lon, lat, device_count) for site, lon, lat, device_count in rows]


@router.get("/{site_id}", response_model=MonitoringSiteOut)
def get_site(site_id: str, db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    row = (
        db.query(
            MonitoringSite,
            ST_X(cast(MonitoringSite.location, Geometry)).label("lon"),
            ST_Y(cast(MonitoringSite.location, Geometry)).label("lat"),
            func.count(Device.id).label("device_count"),
        )
        .outerjoin(Device, Device.monitoring_site_id == MonitoringSite.id)
        .filter(MonitoringSite.id == site_id)
        .group_by(MonitoringSite.id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Monitoring site not found")
    site, lon, lat, device_count = row
    return _site_to_out(site, lon, lat, device_count)


# ---- Devices -----------------------------------------------------------

devices_router = APIRouter(prefix="/devices", tags=["devices"])


@devices_router.post("", response_model=DeviceOut, status_code=201)
def create_device(
    payload: DeviceCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(require_roles(*MANAGE_ROLES)),
):
    site = db.query(MonitoringSite).filter(MonitoringSite.id == payload.monitoring_site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Monitoring site not found")

    existing = db.query(Device).filter(Device.device_code == payload.device_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Device code already registered")

    device = Device(**payload.model_dump())
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


@devices_router.get("", response_model=list[DeviceOut])
def list_devices(db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    return db.query(Device).order_by(Device.created_at.desc()).all()
