import os
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_roles
from app.core.config import settings
from app.core.database import get_db
from app.models.monitoring_site import MonitoringSite
from app.models.survey import MediaAsset, Observation, Survey
from app.models.user import User
from app.schemas.survey import MediaAssetOut, ObservationOut, SurveyCreate, SurveyOut

router = APIRouter(prefix="/surveys", tags=["surveys"])

CREATE_ROLES = ("admin", "researcher", "conservation_officer")


def _survey_to_out(survey: Survey) -> SurveyOut:
    out = SurveyOut.model_validate(survey)
    out.site_count = len(survey.sites)
    return out


@router.post("", response_model=SurveyOut, status_code=201)
def create_survey(
    payload: SurveyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*CREATE_ROLES)),
):
    sites = []
    if payload.site_ids:
        sites = db.query(MonitoringSite).filter(MonitoringSite.id.in_(payload.site_ids)).all()
        if len(sites) != len(payload.site_ids):
            raise HTTPException(status_code=404, detail="One or more monitoring sites not found")

    survey = Survey(
        name=payload.name,
        objective=payload.objective,
        owner_id=current_user.id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        sites=sites,
    )
    db.add(survey)
    db.commit()
    db.refresh(survey)
    return _survey_to_out(survey)


@router.get("", response_model=list[SurveyOut])
def list_surveys(db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    surveys = db.query(Survey).order_by(Survey.created_at.desc()).all()
    return [_survey_to_out(s) for s in surveys]


@router.get("/me/summary")
def my_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    active_surveys = (
        db.query(func.count(Survey.id))
        .filter(Survey.owner_id == current_user.id, Survey.status == "active")
        .scalar()
    )
    site_count = db.query(func.count(MonitoringSite.id)).scalar()
    uploads_count = (
        db.query(func.count(MediaAsset.id))
        .filter(MediaAsset.uploaded_by == current_user.id)
        .scalar()
    )
    species_tagged = (
        db.query(func.count(func.distinct(Observation.species_name)))
        .filter(Observation.species_name.isnot(None))
        .scalar()
    )
    return {
        "active_surveys": active_surveys,
        "monitoring_sites": site_count,
        "my_uploads": uploads_count,
        "species_tagged": species_tagged,
    }


@router.get("/{survey_id}", response_model=SurveyOut)
def get_survey(survey_id: str, db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    return _survey_to_out(survey)


@router.post("/{survey_id}/media", response_model=MediaAssetOut, status_code=201)
def upload_media(
    survey_id: str,
    monitoring_site_id: str,
    media_type: str,
    device_id: str | None = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if media_type not in ("image", "audio", "video"):
        raise HTTPException(status_code=400, detail="media_type must be image, audio, or video")

    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    os.makedirs(settings.media_storage_path, exist_ok=True)
    ext = os.path.splitext(file.filename or "")[1]
    stored_name = f"{uuid.uuid4()}{ext}"
    stored_path = os.path.join(settings.media_storage_path, stored_name)

    content = file.file.read()
    with open(stored_path, "wb") as f:
        f.write(content)

    asset = MediaAsset(
        survey_id=survey.id,
        monitoring_site_id=monitoring_site_id,
        device_id=device_id,
        media_type=media_type,
        storage_path=stored_path,
        captured_at=datetime.now(timezone.utc),
        uploaded_by=current_user.id,
        file_size_bytes=len(content),
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@router.get("/{survey_id}/observations", response_model=list[ObservationOut])
def list_observations(survey_id: str, db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    rows = (
        db.query(Observation)
        .join(MediaAsset, MediaAsset.id == Observation.media_asset_id)
        .filter(MediaAsset.survey_id == survey_id)
        .order_by(Observation.created_at.desc())
        .all()
    )
    return rows
