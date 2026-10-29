from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import (
    Zone, Camera, Sensor, SensorReading, Worker, WorkerHealthReading,
    Equipment, EquipmentReading, PPEDetection, ComplianceCase
)
from app.ml.xai_explainer import xai_explainer

router = APIRouter(prefix="/digital-twin", tags=["2D Mine Digital Twin"])

@router.get("/overview")
def get_digital_twin_overview(
    replay_offset_minutes: int = Query(0, description="Offset in minutes for historical replay"),
    db: Session = Depends(get_db)
):
    target_time = datetime.utcnow() - timedelta(minutes=replay_offset_minutes)
    zones = db.query(Zone).filter(Zone.is_active == True).all()

    zone_payloads = []
    for z in zones:
        # Determine risk color based on zone risk level
        risk_color = {
            "Low": "#16A34A",       # Safe Green
            "Medium": "#EAB308",    # Yellow
            "High": "#EA580C",      # Orange
            "Critical": "#DC2626"   # Red
        }.get(z.risk_level, "#16A34A")

        # Fetch active sensors in zone with historical or latest reading
        sensors = db.query(Sensor).filter(Sensor.zone_id == z.id).all()
        sensor_list = []
        for s in sensors:
            r = db.query(SensorReading).filter(
                SensorReading.sensor_id == s.id,
                SensorReading.timestamp <= target_time
            ).order_by(SensorReading.timestamp.desc()).first()

            is_alert = False
            if r:
                if s.type in ["O2", "AIRFLOW"]:
                    is_alert = r.value <= s.warning_threshold
                else:
                    is_alert = r.value >= s.warning_threshold

            sensor_list.append({
                "id": s.id,
                "name": s.name,
                "type": s.type,
                "unit": s.unit,
                "value": r.value if r else 0.0,
                "is_alert": is_alert,
                "map_x": s.map_x,
                "map_y": s.map_y
            })

        # Fetch workers in zone
        workers = db.query(Worker).filter(Worker.zone_id == z.id).all()
        worker_list = []
        for w in workers:
            hr = db.query(WorkerHealthReading).filter(
                WorkerHealthReading.worker_id == w.id,
                WorkerHealthReading.timestamp <= target_time
            ).order_by(WorkerHealthReading.timestamp.desc()).first()
            worker_list.append({
                "id": w.id,
                "code": w.worker_code,
                "name": w.full_name,
                "role": w.role_title,
                "heart_rate": hr.heart_rate if hr else 72.0,
                "fatigue": hr.fatigue_score if hr else 15.0,
                "is_alert": hr.is_alert if hr else False,
                "map_x": w.map_x,
                "map_y": w.map_y
            })

        # Fetch cameras in zone
        cameras = db.query(Camera).filter(Camera.zone_id == z.id).all()
        camera_list = [{
            "id": c.id,
            "code": c.camera_code,
            "name": c.name,
            "status": c.status,
            "map_x": c.map_x,
            "map_y": c.map_y
        } for c in cameras]

        # Fetch equipment in zone
        equipment = db.query(Equipment).filter(Equipment.zone_id == z.id).all()
        equip_list = [{
            "id": eq.id,
            "code": eq.equipment_code,
            "name": eq.name,
            "type": eq.type,
            "status": eq.status,
            "health_score": eq.health_score,
            "map_x": eq.map_x,
            "map_y": eq.map_y
        } for eq in equipment]

        # Fetch open compliance cases in zone
        cases = db.query(ComplianceCase).filter(
            ComplianceCase.zone_id == z.id,
            ComplianceCase.status.in_(["Open", "In Progress", "Pending Verification"])
        ).all()

        zone_payloads.append({
            "id": z.id,
            "code": z.zone_code,
            "name": z.name,
            "type": z.type,
            "risk_level": z.risk_level,
            "risk_score": z.risk_score,
            "risk_color": risk_color,
            "map_x": z.map_x,
            "map_y": z.map_y,
            "map_width": z.map_width,
            "map_height": z.map_height,
            "sensors": sensor_list,
            "workers": worker_list,
            "cameras": camera_list,
            "equipment": equip_list,
            "active_cases": [{
                "id": c.id,
                "case_number": c.case_number,
                "title": c.title,
                "risk_level": c.risk_level,
                "status": c.status
            } for c in cases]
        })

    return {
        "timestamp": target_time,
        "is_replay": replay_offset_minutes > 0,
        "replay_offset_minutes": replay_offset_minutes,
        "mine_name": "Dhanbad Colliery No. 7 (Underground)",
        "zones": zone_payloads
    }

@router.get("/zone-panel/{zone_id}")
def get_zone_panel_details(zone_id: int, db: Session = Depends(get_db)):
    """Detailed telemetry and XAI root-cause breakdown when a zone is selected on the 2D map"""
    z = db.query(Zone).filter(Zone.id == zone_id).first()
    if not z:
        raise HTTPException(status_code=404, detail="Zone not found")

    # Get recent readings
    sensors = db.query(Sensor).filter(Sensor.zone_id == zone_id).all()
    latest_readings = []
    for s in sensors:
        lr = db.query(SensorReading).filter(SensorReading.sensor_id == s.id).order_by(SensorReading.timestamp.desc()).first()
        latest_readings.append({
            "sensor_id": s.id,
            "name": s.name,
            "type": s.type,
            "unit": s.unit,
            "value": lr.value if lr else None,
            "warning_threshold": s.warning_threshold,
            "danger_threshold": s.danger_threshold,
            "is_anomaly": lr.is_anomaly if lr else False
        })

    # Recent PPE detections in zone
    ppe = db.query(PPEDetection).filter(PPEDetection.zone_id == zone_id).order_by(PPEDetection.created_at.desc()).limit(5).all()

    # Active cases in zone
    cases = db.query(ComplianceCase).filter(
        ComplianceCase.zone_id == zone_id,
        ComplianceCase.status.in_(["Open", "In Progress", "Pending Verification"])
    ).all()

    # Generate synthetic XAI insight for this zone
    pred_mock = {
        "predicted_risk": z.risk_level,
        "risk_score": z.risk_score,
        "confidence": 0.93,
        "top_factors": [
            {"feature": "methane_pct", "value": 1.42 if z.risk_level == "Critical" else 0.42, "contribution_score": 35.0},
            {"feature": "ppe_violations_24h", "value": len(ppe), "contribution_score": 20.0},
            {"feature": "vibration_mms", "value": 7.8 if z.risk_level in ["High", "Critical"] else 2.1, "contribution_score": 15.0}
        ]
    }
    xai_text = xai_explainer.generate_explanation(pred_mock, z.name)
    actions_rec = xai_explainer.get_actionable_recommendations(pred_mock)

    return {
        "zone": {
            "id": z.id,
            "code": z.zone_code,
            "name": z.name,
            "type": z.type,
            "floor_level": z.floor_level,
            "risk_level": z.risk_level,
            "risk_score": z.risk_score,
            "description": z.description
        },
        "latest_telemetry": latest_readings,
        "recent_ppe_events": [{
            "id": p.id,
            "violation_type": p.violation_type,
            "confidence": p.confidence,
            "status": p.status,
            "timestamp": p.created_at,
            "annotated_image": p.annotated_image_path
        } for p in ppe],
        "active_cases": [{
            "id": c.id,
            "case_number": c.case_number,
            "title": c.title,
            "risk_level": c.risk_level,
            "status": c.status,
            "deadline": c.deadline
        } for c in cases],
        "xai_explanation": xai_text,
        "prescriptive_actions": actions_rec
    }

