from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import Optional
import uuid

app = FastAPI(title="Spine Deviation Check API", version="0.1.0")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze_photo(
    back_photo: UploadFile = File(...),
    side_photo: Optional[UploadFile] = File(None),
):
    # Basic validation
    if back_photo.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(status_code=400, detail="Back photo must be JPG or PNG")

    if side_photo and side_photo.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(status_code=400, detail="Side photo must be JPG or PNG")

    # Read files into memory (NO saving to disk)
    back_bytes = await back_photo.read()
    side_bytes = await side_photo.read() if side_photo else None

    # Temporary fake analysis result (STEP 2)
    session_id = uuid.uuid4().hex

    return {
        "session_id": session_id,
        "risk_level": "low",
        "explanation": ["No significant posture asymmetry detected (temporary logic)."],
        "metrics": {"shoulder_diff": 0.01, "hip_diff": 0.02},
    }
