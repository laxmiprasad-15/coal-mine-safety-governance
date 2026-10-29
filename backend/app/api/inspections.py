from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import FieldInspection, ComplianceCase, Notification, User
from app.schemas.schemas import FieldInspectionCreate, FieldInspectionResponse
from app.services.audit_service import create_audit_log

router = APIRouter(prefix="/inspections", tags=["Mobile Field Inspections & Geo-Reporting"])

DEMO_INSPECTIONS = [
    {
        "location_name": "Haul Road No. 4 Junction (BCCL Jharia)",
        "latitude": 23.7957,
        "longitude": 86.4304,
        "inspection_type": "Dust Suppression & Haul Road",
        "hazard_level": "Medium",
        "observation_notes": "Water spraying tanker delayed by 45 mins. Airborne dust concentration elevated near dumper passing zone.",
        "corrective_recommendation": "Deploy auxiliary 20kL bowser immediately and log operator attendance.",
        "is_offline_synced": False
    },
    {
        "location_name": "Working Face 4A Support Line (Moonidih)",
        "latitude": 23.7412,
        "longitude": 86.3521,
        "inspection_type": "Roof & Strata Control",
        "hazard_level": "High",
        "observation_notes": "Hydraulic roof support choke observed on Chock No. 22. Pressure dropped below 280 bar operating threshold.",
        "corrective_recommendation": "Halt shearer traversal until hydraulic seal replaced and re-pressurized to 320 bar.",
        "is_offline_synced": True
    },
    {
        "location_name": "Explosive Magazine Approach Road",
        "latitude": 23.8105,
        "longitude": 86.4189,
        "inspection_type": "Statutory CMR Blasting Safety",
        "hazard_level": "Low",
        "observation_notes": "Double-lock verification completed. Static discharge grounding grid tested at 1.8 ohms. All compliant.",
        "corrective_recommendation": "Routine biometric log confirmed.",
        "is_offline_synced": False
    }
]

@router.get("/", response_model=List[FieldInspectionResponse])
def get_all_inspections(hazard_level: Optional[str] = None, db: Session = Depends(get_db)):
    if db.query(FieldInspection).count() == 0:
        for item in DEMO_INSPECTIONS:
            fi = FieldInspection(
                location_name=item["location_name"],
                latitude=item["latitude"],
                longitude=item["longitude"],
                inspection_type=item["inspection_type"],
                hazard_level=item["hazard_level"],
                observation_notes=item["observation_notes"],
                corrective_recommendation=item["corrective_recommendation"],
                is_offline_synced=item["is_offline_synced"],
                timestamp=datetime.utcnow()
            )
            db.add(fi)
        db.commit()

    query = db.query(FieldInspection).order_by(FieldInspection.timestamp.desc())
    if hazard_level and hazard_level.lower() != "all":
        query = query.filter(FieldInspection.hazard_level == hazard_level.capitalize())
    return query.all()

@router.post("/", response_model=FieldInspectionResponse)
def submit_field_inspection(data: FieldInspectionCreate, db: Session = Depends(get_db)):
    inspection = FieldInspection(
        zone_id=data.zone_id,
        latitude=data.latitude,
        longitude=data.longitude,
        location_name=data.location_name,
        inspection_type=data.inspection_type,
        hazard_level=data.hazard_level,
        observation_notes=data.observation_notes,
        corrective_recommendation=data.corrective_recommendation,
        photo_url=data.photo_url,
        is_offline_synced=data.is_offline_synced or False,
        timestamp=datetime.utcnow()
    )
    db.add(inspection)
    db.flush()

    # Automatically create a Compliance Case if hazard is High or Critical
    if data.hazard_level in ["High", "Critical"]:
        safety_officer = db.query(User).filter(User.role.has(name="Safety Officer")).first()
        case = ComplianceCase(
            case_number=f"CASE-FLD-{int(datetime.utcnow().timestamp())}",
            title=f"Field Inspection Violation: {data.location_name}",
            category="Operational",
            source="Mobile Field App",
            risk_level=data.hazard_level,
            risk_score=85.0 if data.hazard_level == "High" else 96.0,
            zone_id=data.zone_id or 1,
            responsible_user_id=safety_officer.id if safety_officer else None,
            status="Open",
            corrective_action_summary=data.corrective_recommendation or "Perform immediate site remediation as identified during field inspection."
        )
        db.add(case)

        db.add(Notification(
            title=f"FIELD HAZARD REPORTED: {data.location_name}",
            message=f"Geo-tagged inspection reported {data.hazard_level} hazard: {data.observation_notes[:100]}...",
            type="critical" if data.hazard_level == "Critical" else "warning",
            link_url="/compliance-cases"
        ))

    create_audit_log(
        db,
        action="MOBILE_FIELD_INSPECTION_SUBMITTED",
        entity_type="FieldInspection",
        entity_id=str(inspection.id),
        new_state=f"Location: {inspection.location_name} | Geo: ({inspection.latitude}, {inspection.longitude}) | Hazard: {inspection.hazard_level}"
    )

    db.commit()
    db.refresh(inspection)
    return inspection

@router.post("/sync-offline")
def sync_offline_inspections(records: List[FieldInspectionCreate], db: Session = Depends(get_db)):
    synced_count = 0
    for r in records:
        r.is_offline_synced = True
        submit_field_inspection(r, db)
        synced_count += 1
    return {"message": f"Successfully synchronized {synced_count} offline field records."}
