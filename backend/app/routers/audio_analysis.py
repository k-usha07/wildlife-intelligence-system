from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from typing import List
import tempfile
import os

from app.core.security import get_current_user
from app.models.user import User
from app.ml.audio_engine.recognizer import BioacousticRecognizer

router = APIRouter(prefix="/audio-analysis", tags=["Audio Analysis"])

audio_recognizer = BioacousticRecognizer()


@router.post("/analyze")
async def analyze_audio(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Upload and analyze a wildlife audio recording."""
    if file.content_type not in ["audio/wav", "audio/mp3", "audio/ogg", "audio/flac", "audio/x-wav"]:
        raise HTTPException(status_code=400, detail="Invalid audio format. Use WAV, MP3, OGG, or FLAC.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        result = audio_recognizer.process_audio_recording(tmp_path)
        species_class = result["species_classification"]["species_identified"]

        return {
            "filename": file.filename,
            "duration_seconds": result["duration_seconds"],
            "species_identified": [
                {
                    "species": s["species"],
                    "confidence": s["confidence"],
                    "call_type": s.get("call_type", "unknown"),
                }
                for s in species_class
            ],
            "total_calls_detected": result["species_classification"]["total_calls_detected"],
            "acoustic_events": result["acoustic_events"]["event_types"],
            "call_details": result["acoustic_events"]["events"][:20],
            "noise_level": result["audio_features"].get("rms_energy", 0.0),
            "audio_features": result["audio_features"],
            "noise_filtered": result.get("noise_filtered", True),
        }
    finally:
        os.unlink(tmp_path)


@router.post("/batch-analyze")
async def batch_analyze_audio(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
):
    """Batch analyze multiple audio recordings."""
    results = []
    for file in files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name
        try:
            result = audio_recognizer.process_audio_recording(tmp_path)
            results.append({
                "filename": file.filename,
                "species_identified": [
                    s["species"] for s in result["species_classification"]["species_identified"]
                ],
                "total_calls": result["species_classification"]["total_calls_detected"],
                "duration": result["duration_seconds"],
                "status": "success",
            })
        except Exception as e:
            results.append({"filename": file.filename, "status": "error", "error": str(e)})
        finally:
            os.unlink(tmp_path)

    return {"results": results, "total_processed": len(results)}