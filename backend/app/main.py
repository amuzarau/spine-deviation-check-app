from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from typing import Optional
import uuid
from pydantic import BaseModel
from backend.app.db import SessionLocal
from backend.app.models import Screening, User
from backend.app.analysis import analyze_back_photo, analyze_side_photo

app = FastAPI(
    title="Spine Deviation Check API",
    version="0.6.0",
)


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------
@app.get("/health")
def health_check():
    return {"status": "ok"}


# --------------------------------------------------
# ANALYZE ENDPOINT
# --------------------------------------------------
@app.post("/analyze")
async def analyze(
    back_photo: UploadFile = File(...),
    side_photo: UploadFile = File(...),  # ← ТЕПЕРЬ ОБЯЗАТЕЛЬНО
    user_id: str = Query(...),
):
    # ---------- VALIDATION ----------
    if back_photo.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(status_code=400, detail="Неверный формат фото со спины")

    if side_photo.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(status_code=400, detail="Неверный формат фото сбоку")

    back_bytes = await back_photo.read()
    side_bytes = await side_photo.read()

    # ---------- ANALYSIS ----------
    back_metrics = analyze_back_photo(back_bytes)
    side_metrics = analyze_side_photo(side_bytes)

    # ---------- FRONTAL RISK ----------
    sd = back_metrics["shoulder_diff"]
    hd = back_metrics["hip_diff"]

    if sd < 0.03 and hd < 0.03:
        frontal_risk = "low"
    elif sd < 0.06 and hd < 0.06:
        frontal_risk = "medium"
    else:
        frontal_risk = "high"

    # ---------- SAGITTAL RISK ----------
    fh = side_metrics["forward_head"]
    tl = side_metrics["trunk_lean"]

    if fh < 0.04 and tl < 0.04:
        sagittal_risk = "low"
    elif fh < 0.07 and tl < 0.07:
        sagittal_risk = "medium"
    else:
        sagittal_risk = "high"

    # ---------- OVERALL RISK ----------
    if frontal_risk == "high" or sagittal_risk == "high":
        overall_risk = "high"
    elif frontal_risk == "medium" or sagittal_risk == "medium":
        overall_risk = "medium"
    else:
        overall_risk = "low"

    explanation = []
    explanation.extend(back_metrics["explanation"])
    explanation.extend(side_metrics["explanation"])
    explanation.append(
        "Результат является предварительной оценкой и не заменяет консультацию врача."
    )

    # ---------- SAVE TO DB ----------
    db = SessionLocal()
    try:
        record = Screening(
            user_id=uuid.UUID(user_id),
            frontal_risk=frontal_risk,
            sagittal_risk=sagittal_risk,
            overall_risk=overall_risk,
            metrics={
                "back": back_metrics,
                "side": side_metrics,
            },
            explanation=explanation,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
    finally:
        db.close()

    return {
        "session_id": record.id.hex,
        "frontal_risk": frontal_risk,
        "sagittal_risk": sagittal_risk,
        "overall_risk": overall_risk,
        "explanation": explanation,
        "metrics": {
            "back": back_metrics,
            "side": side_metrics,
        },
    }


# --------------------------------------------------
# USER AUTH — ANONYMOUS
# --------------------------------------------------
class AnonymousAuthRequest(BaseModel):
    email: str


@app.post("/auth/anonymous")
def anonymous_auth(payload: AnonymousAuthRequest):
    db = SessionLocal()
    try:
        user = User(
            email=payload.email,
            role="parent",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        return {
            "user_id": user.id.hex,
            "email": user.email,
            "role": user.role,
        }
    finally:
        db.close()


# --------------------------------------------------
# USER HISTORY
# --------------------------------------------------
@app.get("/history/{user_id}")
def get_history(user_id: str):
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user_id")

    db = SessionLocal()
    try:
        records = (
            db.query(Screening)
            .filter(Screening.user_id == user_uuid)
            .order_by(Screening.created_at.desc())
            .all()
        )

        return [
            {
                "date": r.created_at.isoformat(),
                "overall_risk": r.overall_risk,
                "frontal_risk": r.frontal_risk,
                "sagittal_risk": r.sagittal_risk,
            }
            for r in records
        ]
    finally:
        db.close()


# --------------------------------------------------
# DOCTOR DASHBOARD (READ ONLY)
# --------------------------------------------------
@app.get("/doctor/screenings")
def doctor_screenings():
    db = SessionLocal()
    try:
        records = (
            db.query(Screening).order_by(Screening.created_at.desc()).limit(100).all()
        )

        return [
            {
                "date": r.created_at.isoformat(),
                "overall_risk": r.overall_risk,
                "user_id": r.user_id.hex,
            }
            for r in records
        ]
    finally:
        db.close()
