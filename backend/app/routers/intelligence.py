from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.species import Species
from app.models.observation import Observation
from app.models.survey import Survey
from app.models.biodiversity import BiodiversityIndex, HabitatAssessment, EcosystemHealthScore
from app.models.population import PopulationEstimate
from app.schemas.biodiversity import HabitatAssessmentCreate

from app.ml.population_engine.estimator import PopulationEstimator
from app.ml.biodiversity_engine.analyzer import BiodiversityAnalyzer
from app.ml.habitat_engine.assessor import HabitatAssessor
from app.ml.conservation_engine.recommender import ConservationRecommender
from app.ml.health_engine.scorer import EcosystemHealthScorer

router = APIRouter(prefix="/intelligence", tags=["Wildlife Intelligence"])

pop_estimator = PopulationEstimator()
biodiversity_analyzer = BiodiversityAnalyzer()
habitat_assessor = HabitatAssessor()
conservation_recommender = ConservationRecommender()
health_scorer = EcosystemHealthScorer()


# ═══════════════════════════════════════════════════════════════════════════════
#  POPULATION ESTIMATION
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/population/distance-sampling")
async def estimate_population_distance(
    survey_id: UUID,
    transect_length_km: float,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Observation).where(Observation.survey_id == survey_id)
    )
    observations = result.scalars().all()
    obs_data = [{"distance": 0.01 * i, "count": o.count_estimate} for i, o in enumerate(observations)]
    return pop_estimator.estimate_population_distance_sampling(obs_data, transect_length_km)


@router.post("/population/mark-recapture")
async def estimate_population_mark_recapture(
    marked_first: int,
    captured_second: int,
    recaptured: int,
    current_user: User = Depends(get_current_user),
):
    return pop_estimator.estimate_population_mark_recapture(marked_first, captured_second, recaptured)


@router.post("/population/camera-trap")
async def estimate_population_camera_trap(
    survey_id: UUID,
    camera_days: float,
    area_km2: float,
    detection_probability: float = 0.8,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Observation).where(Observation.survey_id == survey_id)
    )
    observations = result.scalars().all()
    detections = [{"species": str(o.species_id), "count": o.count_estimate} for o in observations]
    return pop_estimator.estimate_population_camera_trap(detections, camera_days, area_km2, detection_probability)


@router.post("/population/trend-analysis")
async def analyze_population_trends(
    population_data: List[Dict[str, Any]],
    current_user: User = Depends(get_current_user),
):
    return pop_estimator.analyze_population_trends(population_data)


@router.post("/population/migration-analysis")
async def analyze_migration(
    movement_data: List[Dict[str, Any]],
    current_user: User = Depends(get_current_user),
):
    return pop_estimator.analyze_migration_patterns(movement_data)


# ═══════════════════════════════════════════════════════════════════════════════
#  BIODIVERSITY
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/biodiversity/analyze")
async def analyze_biodiversity(
    survey_id: UUID,
    area_km2: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Observation).where(Observation.survey_id == survey_id)
    )
    observations = result.scalars().all()

    obs_data = []
    for obs in observations:
        sp_name = obs.species_name or f"species_{obs.species_id}"
        obs_data.append({"species": sp_name, "count": obs.count_estimate})

    analysis = biodiversity_analyzer.comprehensive_biodiversity_analysis(obs_data, area_km2)

    bio_index = BiodiversityIndex(
        survey_id=survey_id,
        shannon_index=analysis["shannon_index"],
        simpson_index=analysis["simpson_index"],
        species_richness=analysis["species_richness"],
        evenness_index=analysis["evenness_index"],
        calculation_date=datetime.utcnow(),
        area_km2=area_km2,
    )
    db.add(bio_index)
    await db.commit()

    return analysis


@router.post("/biodiversity/compare")
async def compare_biodiversity(
    site_a_observations: List[Dict[str, Any]],
    site_b_observations: List[Dict[str, Any]],
    site_a_name: str = "Site A",
    site_b_name: str = "Site B",
    current_user: User = Depends(get_current_user),
):
    return biodiversity_analyzer.compare_biodiversity(
        site_a_observations, site_b_observations, site_a_name, site_b_name
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  HABITAT
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/habitat/assess")
async def assess_habitat(
    data: HabitatAssessmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    data_dict = data.model_dump()
    quality = habitat_assessor.assess_habitat_quality(data_dict)
    degradation = habitat_assessor.detect_degradation(data_dict)
    classification = habitat_assessor.classify_habitat(data_dict)

    record = HabitatAssessment(
        survey_id=data.survey_id,
        habitat_type=data.habitat_type,
        vegetation_cover_pct=data.vegetation_cover_pct,
        water_availability_score=data.water_availability_score,
        food_availability_score=data.food_availability_score,
        human_disturbance_score=data.human_disturbance_score,
        fragmentation_index=data_dict.get("fragmentation_index", 0.0),
        overall_quality_score=quality["overall_quality_score"],
        degradation_level=degradation["degradation_level"],
        suitability_score=quality["suitability_score"],
        assessment_date=data.assessment_date,
    )
    db.add(record)
    await db.commit()

    return {
        "quality": quality,
        "degradation": degradation,
        "classification": classification,
    }


@router.post("/habitat/suitability")
async def predict_habitat_suitability(
    habitat_data: Dict[str, Any],
    species_requirements: Dict[str, Any],
    current_user: User = Depends(get_current_user),
):
    return habitat_assessor.predict_habitat_suitability(habitat_data, species_requirements)


# ═══════════════════════════════════════════════════════════════════════════════
#  CONSERVATION
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/conservation/recommendations")
async def generate_conservation_recommendations(
    survey_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    species_result = await db.execute(select(Species))
    species_data = [
        {
            "common_name": s.common_name,
            "is_endangered": s.is_endangered,
            "conservation_status": s.conservation_status,
        }
        for s in species_result.scalars().all()
    ]

    obs_result = await db.execute(
        select(Observation).where(Observation.survey_id == survey_id)
    )
    obs_data = [{"species": o.species_name or str(o.species_id)} for o in obs_result.scalars().all()]
    biodiversity = biodiversity_analyzer.comprehensive_biodiversity_analysis(obs_data)
    habitat = {"degradation_level": "moderate_degradation", "overall_quality_score": 5.0}

    return conservation_recommender.generate_recommendations(species_data, habitat, [], biodiversity)


# ═══════════════════════════════════════════════════════════════════════════════
#  ECOSYSTEM HEALTH
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/health/score")
async def calculate_ecosystem_health(
    survey_id: UUID,
    species_diversity_data: Dict[str, Any],
    population_data: Dict[str, Any],
    habitat_data: Dict[str, Any],
    endangered_data: Dict[str, Any],
    environmental_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    health = health_scorer.calculate_ecosystem_health(
        species_diversity_data, population_data, habitat_data, endangered_data, environmental_data
    )

    record = EcosystemHealthScore(
        survey_id=survey_id,
        species_diversity_score=health["component_scores"]["species_diversity"]["score"],
        population_stability_score=health["component_scores"]["population_stability"]["score"],
        habitat_quality_score=health["component_scores"]["habitat_quality"]["score"],
        endangered_species_score=health["component_scores"]["endangered_species_status"]["score"],
        environmental_conditions_score=health["component_scores"]["environmental_conditions"]["score"],
        overall_health_score=health["overall_health_score"],
        conservation_status=health["conservation_status"],
        assessment_date=datetime.utcnow(),
    )
    db.add(record)
    await db.commit()

    return health