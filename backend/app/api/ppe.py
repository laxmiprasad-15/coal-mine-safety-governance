import os
import shutil
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.models.models import PPEDetection, Zone, Camera, ComplianceCase, Notification, User
from app.schemas.schemas import PPEDetectionResponse, PPEConfirmationRequest
from app.ml.ppe_detector import ppe_detector
from app.services.audit_service import create_audit_log

router = APIRouter(prefix="/ppe", tags=["AI PPE Detection"])

@router.get("/detections", response_model=List[PPEDetectionResponse])
def get_ppe_detections(
    zone_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(PPEDetection).order_by(PPEDetection.created_at.desc())
    if zone_id:
        query = query.filter(PPEDetection.zone_id == zone_id)
    if status_filter:
        query = query.filter(PPEDetection.status == status_filter)

    detections = query.limit(limit).all()
    results = []
    for d in detections:
        results.append(PPEDetectionResponse(
            id=d.id,
            camera_id=d.camera_id,
            zone_id=d.zone_id,
            zone_name=d.camera.zone.name if d.camera and d.camera.zone else "Monitored Zone",
            image_path=d.image_path,
            annotated_image_path=d.annotated_image_path,
            detections=d.detections_json,
            violation_type=d.violation_type,
            confidence=d.confidence,
            status=d.status,
            created_at=d.created_at
        ))
    return results

@router.post("/detect", response_model=PPEDetectionResponse)
async def detect_ppe_upload(
    file: UploadFile = File(...),
    zone_id: int = Form(1),
    camera_id: Optional[int] = Form(None),
    auto_create_case: bool = Form(False),
    db: Session = Depends(get_db)
):
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    # Save original image
    timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    orig_filename = f"ppe_upload_{timestamp_str}_{file.filename}"
    orig_disk_path = os.path.join(settings.PPE_UPLOAD_DIR, orig_filename)
    annotated_filename = f"annotated_{orig_filename}"
    annotated_disk_path = os.path.join(settings.PPE_UPLOAD_DIR, annotated_filename)

    with open(orig_disk_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run AI Detection Engine
    try:
        det_boxes, violation_type, conf, annot_path = ppe_detector.detect(
            orig_disk_path,
            annotated_disk_path
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PPE detection inference error: {str(e)}")

    rel_orig_path = f"/uploads/ppe/{orig_filename}"
    rel_annot_path = f"/uploads/ppe/{annotated_filename}"
    is_compliant = "Compliant" in violation_type
    initial_status = "Compliant" if is_compliant else "Pending Confirmation"

    detection_record = PPEDetection(
        camera_id=camera_id,
        zone_id=zone_id,
        image_path=rel_orig_path,
        annotated_image_path=rel_annot_path,
        detections_json=det_boxes,
        violation_type=violation_type,
        confidence=conf,
        status=initial_status,
        created_at=datetime.utcnow()
    )
    db.add(detection_record)
    db.flush()

    # If auto-create case enabled and non-compliant
    if auto_create_case and not is_compliant:
        detection_record.status = "Case Created"
        safety_user = db.query(User).filter(User.role.has(name="Safety Officer")).first()
        case = ComplianceCase(
            case_number=f"CASE-PPE-{int(datetime.utcnow().timestamp())}",
            title=f"PPE Violation: {violation_type} at {zone.name}",
            category="PPE",
            source="YOLOv8",
            risk_level="High" if "Hardhat" in violation_type else "Medium",
            risk_score=75.0 if "Hardhat" in violation_type else 55.0,
            zone_id=zone_id,
            evidence_path=rel_annot_path,
            responsible_user_id=safety_user.id if safety_user else None,
            deadline=datetime.utcnow() + timedelta(hours=8),
            status="Open",
            corrective_action_summary=f"Mandatory PPE reprimand and verification of safety gear compliance for crew in {zone.name}."
        )
        db.add(case)
        db.add(Notification(
            title=f"PPE NON-COMPLIANCE: {zone.name}",
            message=f"Detection: {violation_type}. Traceable compliance case automatically initiated.",
            type="warning",
            link_url="/compliance-cases"
        ))

    create_audit_log(
        db,
        action="PPE_DETECTION_RUN",
        entity_type="PPEDetection",
        entity_id=str(detection_record.id),
        new_state=f"Analyzed frame: {violation_type} (Confidence: {conf})"
    )

    db.commit()
    db.refresh(detection_record)

    return PPEDetectionResponse(
        id=detection_record.id,
        camera_id=detection_record.camera_id,
        zone_id=detection_record.zone_id,
        zone_name=zone.name,
        image_path=detection_record.image_path,
        annotated_image_path=detection_record.annotated_image_path,
        detections=detection_record.detections_json,
        violation_type=detection_record.violation_type,
        confidence=detection_record.confidence,
        status=detection_record.status,
        created_at=detection_record.created_at
    )

@router.post("/confirm/{detection_id}")
def confirm_ppe_detection(
    detection_id: int,
    req: PPEConfirmationRequest,
    db: Session = Depends(get_db)
):
    """Safety Officer manual confirmation or rejection workflow before final case creation"""
    detection = db.query(PPEDetection).filter(PPEDetection.id == detection_id).first()
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")

    zone = db.query(Zone).filter(Zone.id == detection.zone_id).first()

    if not req.confirmed:
        detection.status = "Rejected by Officer"
        create_audit_log(
            db,
            action="PPE_DETECTION_REJECTED",
            entity_type="PPEDetection",
            entity_id=str(detection.id),
            new_state=f"Detection rejected as false positive: {req.notes or 'No reason provided'}"
        )
        db.commit()
        return {"message": "Detection rejected. No compliance case created."}

    # If confirmed
    detection.status = "Confirmed"
    created_case_id = None
    if req.create_compliance_case:
        detection.status = "Case Created"
        safety_user = db.query(User).filter(User.role.has(name="Safety Officer")).first()
        responsible_id = req.assigned_user_id or (safety_user.id if safety_user else None)

        case = ComplianceCase(
            case_number=f"CASE-PPE-{int(datetime.utcnow().timestamp())}",
            title=f"Confirmed PPE Violation: {detection.violation_type} in {zone.name}",
            category="PPE",
            source="YOLOv8",
            risk_level="High" if "Hardhat" in detection.violation_type else "Medium",
            risk_score=75.0 if "Hardhat" in detection.violation_type else 55.0,
            zone_id=detection.zone_id,
            evidence_path=detection.annotated_image_path or detection.image_path,
            responsible_user_id=responsible_id,
            deadline=datetime.utcnow() + timedelta(hours=12),
            status="Open",
            corrective_action_summary=req.notes or f"Immediate on-site PPE compliance verification required in {zone.name}."
        )
        db.add(case)
        db.flush()
        created_case_id = case.id

        db.add(Notification(
            title=f"NEW COMPLIANCE CASE: {case.case_number}",
            message=f"Confirmed violation: {case.title}",
            type="warning",
            link_url=f"/compliance-cases"
        ))

    create_audit_log(
        db,
        action="PPE_DETECTION_CONFIRMED",
        entity_type="PPEDetection",
        entity_id=str(detection.id),
        new_state=f"Officer confirmed detection. Compliance Case ID: {created_case_id}"
    )

    db.commit()
    return {
        "message": "Detection confirmed successfully",
        "case_id": created_case_id,
        "status": detection.status
    }

