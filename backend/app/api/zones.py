from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.models import Zone, ComplianceCase, Worker, Sensor, Camera
from app.schemas.schemas import ZoneResponse

router = APIRouter(prefix="/zones", tags=["Zones & Infrastructure"])

@router.get("/", response_model=List[ZoneResponse])
def get_zones(db: Session = Depends(get_db)):
    zones = db.query(Zone).filter(Zone.is_active == True).all()
    results = []
    for z in zones:
        case_cnt = db.query(ComplianceCase).filter(ComplianceCase.zone_id == z.id, ComplianceCase.status.in_(["Open", "In Progress", "Pending Verification"])).count()
        wkr_cnt = db.query(Worker).filter(Worker.zone_id == z.id).count()
        sens_cnt = db.query(Sensor).filter(Sensor.zone_id == z.id).count()
        
        results.append(ZoneResponse(
            id=z.id,
            mine_id=z.mine_id,
            name=z.name,
            zone_code=z.zone_code,
            type=z.type,
            floor_level=z.floor_level,
            risk_level=z.risk_level,
            risk_score=z.risk_score,
            map_x=z.map_x,
            map_y=z.map_y,
            map_width=z.map_width,
            map_height=z.map_height,
            description=z.description,
            is_active=z.is_active,
            active_cases_count=case_cnt,
            worker_count=wkr_cnt,
            sensor_count=sens_cnt
        ))
    return results

@router.get("/{zone_id}")
def get_zone_details(zone_id: int, db: Session = Depends(get_db)):
    z = db.query(Zone).filter(Zone.id == zone_id).first()
    if not z:
        raise HTTPException(status_code=404, detail="Zone not found")
    
    cameras = db.query(Camera).filter(Camera.zone_id == zone_id).all()
    sensors = db.query(Sensor).filter(Sensor.zone_id == zone_id).all()
    workers = db.query(Worker).filter(Worker.zone_id == zone_id).all()
    active_cases = db.query(ComplianceCase).filter(
        ComplianceCase.zone_id == zone_id,
        ComplianceCase.status.in_(["Open", "In Progress", "Pending Verification"])
    ).all()

    return {
        "zone": {
            "id": z.id,
            "name": z.name,
            "zone_code": z.zone_code,
            "type": z.type,
            "risk_level": z.risk_level,
            "risk_score": z.risk_score,
            "floor_level": z.floor_level,
            "description": z.description
        },
        "cameras_count": len(cameras),
        "sensors_count": len(sensors),
        "workers_count": len(workers),
        "active_cases": [{
            "id": c.id,
            "case_number": c.case_number,
            "title": c.title,
            "category": c.category,
            "risk_level": c.risk_level,
            "status": c.status,
            "deadline": c.deadline
        } for c in active_cases]
    }

