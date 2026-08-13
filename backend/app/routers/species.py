from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.species import Species, SpeciesGroup, ConservationStatusEnum
from app.models.observation import Observation
from app.schemas.species import (
    SpeciesCreate, SpeciesResponse, SpeciesDetail,
    ObservationCreate, ObservationResponse,
)

router = APIRouter(prefix="/species", tags=["Species"])


# ── CRUD ──────────────────────────────────────────────────────────────────────

@router.post("/", response_model=SpeciesResponse, status_code=status.HTTP_201_CREATED)
async def create_species(
    data: SpeciesCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    species = Species(**data.model_dump())
    species.is_endangered = species.conservation_status in ("EN", "CR", "EW")
    db.add(species)
    await db.commit()
    await db.refresh(species)
    return SpeciesResponse.model_validate(species)


@router.get("/", response_model=List[SpeciesResponse])
async def list_species(
    group: Optional[str] = None,
    conservation: Optional[str] = None,
    endangered_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    query = select(Species)
    if group:
        query = query.where(Species.species_group == group)
    if conservation:
        query = query.where(Species.conservation_status == conservation)
    if endangered_only:
        query = query.where(Species.is_endangered == True)
    query = query.offset(skip).limit(limit).order_by(Species.common_name)
    result = await db.execute(query)
    return [SpeciesResponse.model_validate(s) for s in result.scalars().all()]


@router.get("/endangered", response_model=List[SpeciesResponse])
async def get_endangered_species(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Species).where(
            Species.conservation_status.in_(["EN", "CR", "VU"])
        ).order_by(Species.conservation_status, Species.common_name)
    )
    return [SpeciesResponse.model_validate(s) for s in result.scalars().all()]


@router.get("/{species_id}", response_model=SpeciesDetail)
async def get_species(species_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Species).where(Species.id == species_id))
    species = result.scalar_one_or_none()
    if not species:
        raise HTTPException(status_code=404, detail="Species not found")
    return SpeciesDetail.model_validate(species)


@router.get("/stats/summary")
async def species_stats(db: AsyncSession = Depends(get_db)):
    total = await db.scalar(select(func.count(Species.id)))
    endangered = await db.scalar(
        select(func.count(Species.id)).where(Species.is_endangered == True)
    )
    groups = await db.execute(
        select(Species.species_group, func.count(Species.id))
        .group_by(Species.species_group)
    )
    return {
        "total_species": total,
        "endangered_count": endangered,
        "by_group": {row[0]: row[1] for row in groups.all()},
    }


# ── Observations ──────────────────────────────────────────────────────────────

@router.post("/observations", response_model=ObservationResponse, status_code=status.HTTP_201_CREATED)
async def create_observation(
    data: ObservationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    obs = Observation(**data.model_dump())
    db.add(obs)
    await db.commit()
    await db.refresh(obs)
    return ObservationResponse.model_validate(obs)


@router.get("/observations", response_model=List[ObservationResponse])
async def list_observations(
    survey_id: Optional[UUID] = None,
    species_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    query = select(Observation)
    if survey_id:
        query = query.where(Observation.survey_id == survey_id)
    if species_id:
        query = query.where(Observation.species_id == species_id)
    query = query.offset(skip).limit(limit).order_by(Observation.created_at.desc())
    result = await db.execute(query)
    return [ObservationResponse.model_validate(o) for o in result.scalars().all()]