from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Equipment, EquipmentReading, ComplianceCase, Notification, Zone
from app.schemas.schemas import EquipmentResponse, EquipmentReadingCreate, EquipmentReadingResponse

router = APIRouter(prefix="/equipment", tags=["Equipment Health & Predictive Maintenance"])

@router.get("/", response_model=List[EquipmentResponse])
def get_equipment_list(zone_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Equipment)
    if zone_id:
        query = query.filter(Equipment.zone_id == zone_id)

    equipment = query.all()
    results = []
    for eq in equipment:
        last_r = db.query(EquipmentReading).filter(EquipmentReading.equipment_id == eq.id).order_by(EquipmentReading.timestamp.desc()).first()
        results.append(EquipmentResponse(
            id=eq.id,
            zone_id=eq.zone_id,
            zone_name=eq.zone.name if eq.zone else "Zone",
            name=eq.name,
            equipment_code=eq.equipment_code,
            type=eq.type,
            status=eq.status,
            health_score=eq.health_score,
            rul_days=eq.rul_days,
            map_x=eq.map_x,
            map_y=eq.map_y,
            last_vibration=last_r.vibration if last_r else None,
            last_temp=last_r.temperature if last_r else None,
            last_maintenance=eq.last_maintenance
        ))
    return results

@router.post("/reading", response_model=EquipmentReadingResponse)
def submit_equipment_telemetry(data: EquipmentReadingCreate, db: Session = Depends(get_db)):
    eq = db.query(Equipment).filter(Equipment.id == data.equipment_id).first()
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")

    is_alert = False
    reasons = []

    if data.vibration >= 7.5:
        is_alert = True
        reasons.append(f"Severe mechanical vibration ({data.vibration:.2f} mm/s)")
    if data.temperature >= 65.0:
        is_alert = True
        reasons.append(f"Bearing over-temperature ({data.temperature:.1f}°C)")

    # Dynamically update equipment condition score and remaining useful life (RUL)
    if is_alert:
        eq.health_score = max(20.0, eq.health_score - 12.0)
        eq.rul_days = max(5, int(eq.rul_days * 0.7))
        eq.status = "Warning" if eq.health_score > 40 else "Critical"
    else:
        eq.health_score = min(98.0, eq.health_score + 1.0)
        eq.status = "Operational"

    alert_reason_str = "; ".join(reasons) if is_alert else None
    
    reading = EquipmentReading(
        equipment_id=eq.id,
        vibration=data.vibration,
        temperature=data.temperature,
        oil_pressure=data.oil_pressure,
        current_draw=data.current_draw,
        rpm=data.rpm,
        is_alert=is_alert,
        alert_reason=alert_reason_str,
        timestamp=datetime.utcnow()
    )
    db.add(reading)

    if is_alert and eq.health_score <= 50:
        db.add(ComplianceCase(
            case_number=f"CASE-MAINT-{int(datetime.utcnow().timestamp())}",
            title=f"Predictive Maintenance Work-Order: {eq.name} ({alert_reason_str})",
            category="Equipment",
            source="Predictive Model",
            risk_level="High" if eq.health_score > 35 else "Critical",
            risk_score=round(100.0 - eq.health_score, 1),
            zone_id=eq.zone_id,
            deadline=datetime.utcnow() + timedelta(hours=6),
            status="Open",
            corrective_action_summary=f"Inspect bearings, lubricate drive coupling, test motor insulation resistance on {eq.equipment_code}."
        ))
        db.add(Notification(
            title="EQUIPMENT BREAKDOWN RISK",
            message=f"{eq.name} health degraded to {eq.health_score:.0f}%. RUL estimate: {eq.rul_days} days.",
            type="warning",
            link_url="/equipment"
        ))

    db.commit()
    db.refresh(reading)
    return reading

