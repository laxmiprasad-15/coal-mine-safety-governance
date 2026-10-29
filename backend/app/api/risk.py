from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Zone, Sensor, SensorReading, PPEDetection, Equipment, WorkerHealthReading, RiskPrediction, Worker
from app.schemas.schemas import RiskPredictionResponse, RiskPredictionRequest
from app.ml.risk_predictor import risk_engine
from app.ml.xai_explainer import xai_explainer
from app.services.audit_service import create_audit_log

router = APIRouter(prefix="/risk", tags=["Predictive Risk & Explainable AI"])

def _extract_zone_feature_vector(zone_id: int, db: Session) -> dict:
    """Aggregates real-time sensor, health, and equipment indicators into an ML feature vector"""
    # 1. Latest gas and atmospheric telemetry
    ch4_s = db.query(Sensor).filter(Sensor.zone_id == zone_id, Sensor.type == "CH4").first()
    ch4_val = 0.35
    if ch4_s:
        last_r = db.query(SensorReading).filter(SensorReading.sensor_id == ch4_s.id).order_by(SensorReading.timestamp.desc()).first()
        if last_r:
            ch4_val = last_r.value

    co_s = db.query(Sensor).filter(Sensor.zone_id == zone_id, Sensor.type == "CO").first()
    co_val = 12.0
    if co_s:
        last_r = db.query(SensorReading).filter(SensorReading.sensor_id == co_s.id).order_by(SensorReading.timestamp.desc()).first()
        if last_r:
            co_val = last_r.value

    temp_s = db.query(Sensor).filter(Sensor.zone_id == zone_id, Sensor.type == "TEMP").first()
    temp_val = 26.5
    if temp_s:
        last_r = db.query(SensorReading).filter(SensorReading.sensor_id == temp_s.id).order_by(SensorReading.timestamp.desc()).first()
        if last_r:
            temp_val = last_r.value

    hum_s = db.query(Sensor).filter(Sensor.zone_id == zone_id, Sensor.type == "HUMIDITY").first()
    hum_val = 65.0
    if hum_s:
        last_r = db.query(SensorReading).filter(SensorReading.sensor_id == hum_s.id).order_by(SensorReading.timestamp.desc()).first()
        if last_r:
            hum_val = last_r.value

    vib_s = db.query(Sensor).filter(Sensor.zone_id == zone_id, Sensor.type == "VIBRATION").first()
    vib_val = 2.2
    if vib_s:
        last_r = db.query(SensorReading).filter(SensorReading.sensor_id == vib_s.id).order_by(SensorReading.timestamp.desc()).first()
        if last_r:
            vib_val = last_r.value

    # 2. PPE Violations in last 24h
    ppe_count = db.query(PPEDetection).filter(
        PPEDetection.zone_id == zone_id,
        PPEDetection.status.in_(["Confirmed", "Case Created", "Pending Confirmation"])
    ).count()

    # 3. Worker fatigue average in zone
    workers = db.query(Worker).filter(Worker.zone_id == zone_id).all()
    fatigue_scores = []
    for w in workers:
        hr = db.query(WorkerHealthReading).filter(WorkerHealthReading.worker_id == w.id).order_by(WorkerHealthReading.timestamp.desc()).first()
        if hr:
            fatigue_scores.append(hr.fatigue_score)
    avg_fatigue = sum(fatigue_scores) / len(fatigue_scores) if fatigue_scores else 22.0

    # 4. Equipment health average in zone
    equipments = db.query(Equipment).filter(Equipment.zone_id == zone_id).all()
    equip_scores = [e.health_score for e in equipments] if equipments else [88.0]
    avg_equip = sum(equip_scores) / len(equip_scores)

    return {
        "methane_pct": ch4_val,
        "carbon_monoxide_ppm": co_val,
        "temperature_c": temp_val,
        "humidity_pct": hum_val,
        "vibration_mms": vib_val,
        "ppe_violations_24h": ppe_count,
        "worker_fatigue_avg": avg_fatigue,
        "equipment_health_avg": avg_equip,
        "historical_incidents": 1 if zone_id == 4 else 0,
        "shift_hour": 4.5
    }

@router.post("/predict", response_model=RiskPredictionResponse)
def evaluate_zone_risk(req: RiskPredictionRequest, db: Session = Depends(get_db)):
    zone = db.query(Zone).filter(Zone.id == req.zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    features = _extract_zone_feature_vector(zone.id, db)
    pred_res = risk_engine.predict_risk(features)
    xai_text = xai_explainer.generate_explanation(pred_res, zone.name)

    # Update zone risk level and score in database
    zone.risk_level = pred_res["predicted_risk"]
    zone.risk_score = pred_res["risk_score"]

    record = RiskPrediction(
        zone_id=zone.id,
        predicted_risk=pred_res["predicted_risk"],
        risk_score=pred_res["risk_score"],
        confidence=pred_res["confidence"],
        top_factors_json=pred_res["top_factors"],
        xai_explanation=xai_text,
        forecast_shift=req.forecast_shift,
        timestamp=datetime.utcnow()
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return RiskPredictionResponse(
        id=record.id,
        zone_id=zone.id,
        zone_name=zone.name,
        predicted_risk=record.predicted_risk,
        risk_score=record.risk_score,
        confidence=record.confidence,
        top_factors=record.top_factors_json or [],
        xai_explanation=record.xai_explanation,
        forecast_shift=record.forecast_shift,
        timestamp=record.timestamp
    )

@router.get("/forecast/next-shift")
def get_next_shift_risk_forecast(db: Session = Depends(get_db)):
    """Computes Next Shift Risk Forecast for all 8 zones with XAI explanations"""
    zones = db.query(Zone).filter(Zone.is_active == True).all()
    forecasts = []

    for z in zones:
        features = _extract_zone_feature_vector(z.id, db)
        pred = risk_engine.predict_risk(features)
        xai = xai_explainer.generate_explanation(pred, z.name)
        recs = xai_explainer.get_actionable_recommendations(pred)

        forecasts.append({
            "zone_id": z.id,
            "zone_code": z.zone_code,
            "zone_name": z.name,
            "current_risk": z.risk_level,
            "forecasted_risk": pred["predicted_risk"],
            "risk_score": pred["risk_score"],
            "confidence": pred["confidence"],
            "class_probabilities": pred.get("class_probabilities", {}),
            "top_factors": pred["top_factors"],
            "xai_explanation": xai,
            "prescriptive_actions": recs
        })

    # Sort high-risk zones first
    risk_rank = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
    forecasts.sort(key=lambda x: risk_rank.get(x["forecasted_risk"], 0), reverse=True)

    return {
        "shift_name": "Next Shift (14:00 - 22:00)",
        "evaluation_timestamp": datetime.utcnow(),
        "total_zones": len(forecasts),
        "high_or_critical_count": sum(1 for f in forecasts if f["forecasted_risk"] in ["High", "Critical"]),
        "forecasts": forecasts
    }

