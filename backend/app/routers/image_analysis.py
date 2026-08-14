from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from typing import List
import numpy as np
import cv2
from io import BytesIO

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.ml.image_engine.detector import image_detector
from app.ml.species_engine.classifier import SpeciesClassifier

router = APIRouter(prefix="/image-analysis", tags=["Image Analysis"])

species_classifier = SpeciesClassifier()


@router.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    confidence_threshold: float = 0.25,
    current_user: User = Depends(get_current_user),
):
    """Upload and analyze a camera trap / drone image."""
    if file.content_type not in ["image/jpeg", "image/png", "image/bmp"]:
        raise HTTPException(status_code=400, detail="Invalid image format. Use JPG, PNG, or BMP.")

    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        raise HTTPException(status_code=400, detail="Could not decode image")

    # ── Wildlife detection ─────────────────────────────────────────────
    detection_result = image_detector.detect_wildlife(image, confidence_threshold)

    # ── Image quality ──────────────────────────────────────────────────
    quality_result = image_detector.assess_image_quality(image)

    # ── Behavior detection ─────────────────────────────────────────────
    behaviors = []
    if detection_result["num_detections"] > 0:
        behaviors = image_detector.detect_behavior(image, detection_result["detections"])

    # ── Endangered check ───────────────────────────────────────────────
    endangered_found = [
        d["species"]
        for d in detection_result["detections"]
        if d["species"] in SpeciesClassifier.ENDANGERED_SPECIES
    ]

    return {
        "filename": file.filename,
        "species_detected": list(detection_result["species_counts"].keys()),
        "species_counts": detection_result["species_counts"],
        "total_animals": detection_result["total_animals"],
        "bounding_boxes": detection_result["bounding_boxes"],
        "confidence_scores": detection_result["confidence_scores"],
        "image_quality": quality_result["quality"],
        "quality_details": quality_result,
        "behaviors_detected": behaviors,
        "endangered_species_found": endangered_found,
        "num_detections": detection_result["num_detections"],
    }


@router.post("/batch-analyze")
async def batch_analyze_images(
    files: List[UploadFile] = File(...),
    confidence_threshold: float = 0.25,
    current_user: User = Depends(get_current_user),
):
    """Batch analyze multiple camera trap images."""
    results = []
    for file in files:
        try:
            contents = await file.read()
            nparr = np.frombuffer(contents, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if image is not None:
                detection = image_detector.detect_wildlife(image, confidence_threshold)
                quality = image_detector.assess_image_quality(image)
                behaviors = (
                    image_detector.detect_behavior(image, detection["detections"])
                    if detection["num_detections"] > 0
                    else []
                )
                endangered = [
                    d["species"] for d in detection["detections"]
                    if d["species"] in SpeciesClassifier.ENDANGERED_SPECIES
                ]
                results.append({
                    "filename": file.filename,
                    "species_detected": list(detection["species_counts"].keys()),
                    "species_counts": detection["species_counts"],
                    "total_animals": detection["total_animals"],
                    "image_quality": quality["quality"],
                    "behaviors": behaviors,
                    "endangered_found": endangered,
                    "status": "success",
                })
            else:
                results.append({"filename": file.filename, "status": "failed", "error": "Could not decode image"})
        except Exception as e:
            results.append({"filename": file.filename, "status": "error", "error": str(e)})

    return {"results": results, "total_processed": len(results)}