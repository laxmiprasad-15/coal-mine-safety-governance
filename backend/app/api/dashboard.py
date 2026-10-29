from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import (
    ComplianceCase, PPEDetection, SensorReading, Zone,
    Equipment, WorkerHealthReading, CorrectiveAction, Sensor
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard Summary & Analytics"])

@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    today_start = now - timedelta(hours=24)

    # Compliance Cases
    total_cases = db.query(ComplianceCase).count()
    open_cases = db.query(ComplianceCase).filter(ComplianceCase.status.in_(["Open", "In Progress", "Pending Verification"])).count()
    closed_cases = db.query(ComplianceCase).filter(ComplianceCase.status == "Closed").count()
    completion_rate = round((closed_cases / total_cases * 100), 1) if total_cases > 0 else 100.0

    # Overdue Actions
    overdue_actions = db.query(CorrectiveAction).filter(
        CorrectiveAction.status.notin_(["Verified", "Closed"]),
        CorrectiveAction.due_date < now
    ).count()

    # Alerts Today
    ppe_violations_today = db.query(PPEDetection).filter(
        PPEDetection.created_at >= today_start,
        PPEDetection.violation_type != "Compliant"
    ).count()

    critical_sensor_alerts = db.query(SensorReading).filter(
        SensorReading.timestamp >= today_start,
        SensorReading.is_anomaly == True
    ).count()

    worker_alerts = db.query(WorkerHealthReading).filter(
        WorkerHealthReading.timestamp >= today_start,
        WorkerHealthReading.is_alert == True
    ).count()

    equipment_alerts = db.query(Equipment).filter(Equipment.status.in_(["Warning", "Critical"])).count()

    # Zones
    high_risk_zones = db.query(Zone).filter(Zone.risk_level.in_(["High", "Critical"])).count()
    zones = db.query(Zone).all()

    # Recent AI PPE Detections
    recent_ppe = db.query(PPEDetection).order_by(PPEDetection.created_at.desc()).limit(6).all()

    # Recent Anomalies
    recent_readings = db.query(SensorReading).filter(SensorReading.is_anomaly == True).order_by(SensorReading.timestamp.desc()).limit(6).all()

    # Zone risk forecast distribution
    risk_distribution = {
        "Low": db.query(Zone).filter(Zone.risk_level == "Low").count(),
        "Medium": db.query(Zone).filter(Zone.risk_level == "Medium").count(),
        "High": db.query(Zone).filter(Zone.risk_level == "High").count(),
        "Critical": db.query(Zone).filter(Zone.risk_level == "Critical").count()
    }

    return {
        "kpis": {
            "open_cases": open_cases,
            "total_cases": total_cases,
            "completion_rate": completion_rate,
            "critical_alerts_today": critical_sensor_alerts + worker_alerts,
            "ppe_violations_today": ppe_violations_today,
            "high_risk_zones": high_risk_zones,
            "overdue_actions": overdue_actions,
            "equipment_alerts": equipment_alerts,
            "worker_health_alerts": worker_alerts
        },
        "risk_distribution": risk_distribution,
        "recent_detections": [{
            "id": p.id,
            "violation": p.violation_type,
            "confidence": p.confidence,
            "status": p.status,
            "zone": p.camera.zone.name if p.camera and p.camera.zone else "Zone",
            "time": p.created_at,
            "image": p.annotated_image_path or p.image_path
        } for p in recent_ppe],
        "recent_anomalies": [{
            "id": r.id,
            "sensor": r.sensor.name if r.sensor else "Sensor",
            "type": r.sensor.type if r.sensor else "Metric",
            "unit": r.sensor.unit if r.sensor else "",
            "value": r.value,
            "zone": r.sensor.zone.name if r.sensor and r.sensor.zone else "Zone",
            "time": r.timestamp,
            "score": r.anomaly_score
        } for r in recent_readings],
        "zones_mini": [{
            "id": z.id,
            "name": z.name,
            "risk_level": z.risk_level,
            "risk_score": z.risk_score
        } for z in zones]
    }

