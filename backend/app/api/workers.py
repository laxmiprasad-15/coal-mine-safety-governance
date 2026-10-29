from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Worker, WorkerHealthReading, ComplianceCase, Notification, Zone
from app.schemas.schemas import WorkerResponse, WorkerHealthReadingCreate, WorkerHealthReadingResponse

router = APIRouter(prefix="/workers", tags=["Worker Health & Fatigue Monitoring"])

@router.get("/", response_model=List[WorkerResponse])
def get_all_workers(zone_id: Optional[int] = None, status_filter: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Worker)
    if zone_id:
        query = query.filter(Worker.zone_id == zone_id)
    if status_filter:
        query = query.filter(Worker.status == status_filter)

    workers = query.all()
    results = []
    for w in workers:
        last_hr = db.query(WorkerHealthReading).filter(WorkerHealthReading.worker_id == w.id).order_by(WorkerHealthReading.timestamp.desc()).first()
        results.append(WorkerResponse(
            id=w.id,
            worker_code=w.worker_code,
            full_name=w.full_name,
            role_title=w.role_title,
            zone_id=w.zone_id,
            zone_name=w.zone_id and db.query(Zone.name).filter(Zone.id == w.zone_id).scalar() or "Unassigned",
            emergency_contact=w.emergency_contact,
            blood_group=w.blood_group,
            shift=w.shift,
            status=w.status,
            map_x=w.map_x,
            map_y=w.map_y,
            last_heart_rate=last_hr.heart_rate if last_hr else None,
            last_body_temp=last_hr.body_temp if last_hr else None,
            fatigue_score=last_hr.fatigue_score if last_hr else None,
            is_alert=last_hr.is_alert if last_hr else False,
            alert_reason=last_hr.alert_reason if last_hr else None
        ))
    return results

@router.post("/health-reading", response_model=WorkerHealthReadingResponse)
def submit_wearable_reading(data: WorkerHealthReadingCreate, db: Session = Depends(get_db)):
    worker = db.query(Worker).filter(Worker.id == data.worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    is_alert = False
    reasons = []

    # Wearable fatigue and biometric rule thresholds
    if data.heart_rate > 120.0:
        is_alert = True
        reasons.append(f"Tachycardia detected ({data.heart_rate:.0f} bpm)")
    if data.body_temp >= 38.0:
        is_alert = True
        reasons.append(f"Heat stress condition ({data.body_temp:.1f}°C)")
    if data.fatigue_score >= 75.0:
        is_alert = True
        reasons.append(f"Critical crew exhaustion index ({data.fatigue_score:.0f}/100)")
    if data.shift_hours >= 8.5:
        is_alert = True
        reasons.append(f"Prolonged shift without mandatory rest ({data.shift_hours:.1f}h)")

    alert_reason_str = "; ".join(reasons) if is_alert else None
    
    reading = WorkerHealthReading(
        worker_id=worker.id,
        heart_rate=data.heart_rate,
        body_temp=data.body_temp,
        spo2=data.spo2,
        fatigue_score=data.fatigue_score,
        activity_status=data.activity_status,
        shift_hours=data.shift_hours,
        is_alert=is_alert,
        alert_reason=alert_reason_str,
        timestamp=datetime.utcnow()
    )
    db.add(reading)

    if is_alert:
        worker.status = "Medical Alert"
        # Auto-generate case if extreme
        if data.heart_rate > 125.0 or data.body_temp >= 38.5:
            db.add(ComplianceCase(
                case_number=f"CASE-WKR-{int(datetime.utcnow().timestamp())}",
                title=f"Worker Health Emergency: {worker.full_name} ({alert_reason_str})",
                category="Worker Health",
                source="Sensor Anomaly",
                risk_level="Critical",
                risk_score=92.0,
                zone_id=worker.zone_id or 1,
                deadline=datetime.utcnow() + timedelta(hours=1),
                status="Open",
                corrective_action_summary="Immediate surface evacuation, administer first-aid and medical checkup."
            ))
            db.add(Notification(
                title="WORKER HEALTH CRITICAL ALERT",
                message=f"{worker.full_name} ({worker.worker_code}): {alert_reason_str}",
                type="critical",
                link_url="/workers"
            ))

    db.commit()
    db.refresh(reading)
    return reading

