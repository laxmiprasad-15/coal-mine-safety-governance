from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import ComplianceCase, CorrectiveAction, CaseComment, User, Zone, Notification
from app.schemas.schemas import (
    ComplianceCaseResponse, ComplianceCaseCreate, ComplianceCaseUpdate,
    CaseCommentCreate, CaseCommentResponse
)
from app.services.audit_service import create_audit_log
from app.api.deps import get_current_user

router = APIRouter(prefix="/compliance", tags=["Compliance Case Governance"])

@router.get("/cases", response_model=List[ComplianceCaseResponse])
def get_cases(
    category: Optional[str] = None,
    status: Optional[str] = None,
    risk_level: Optional[str] = None,
    zone_id: Optional[int] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(ComplianceCase).order_by(ComplianceCase.created_at.desc())

    if category and category != "All":
        query = query.filter(ComplianceCase.category == category)
    if status and status != "All":
        query = query.filter(ComplianceCase.status == status)
    if risk_level and risk_level != "All":
        query = query.filter(ComplianceCase.risk_level == risk_level)
    if zone_id:
        query = query.filter(ComplianceCase.zone_id == zone_id)
    if search:
        query = query.filter(
            (ComplianceCase.case_number.ilike(f"%{search}%")) |
            (ComplianceCase.title.ilike(f"%{search}%")) |
            (ComplianceCase.category.ilike(f"%{search}%"))
        )

    cases = query.offset(skip).limit(limit).all()
    results = []
    now = datetime.utcnow()

    for c in cases:
        # Check if overdue
        curr_status = c.status
        if curr_status in ["Open", "In Progress"] and c.deadline < now:
            curr_status = "Overdue"

        results.append(ComplianceCaseResponse(
            id=c.id,
            case_number=c.case_number,
            title=c.title,
            category=c.category,
            source=c.source,
            risk_level=c.risk_level,
            risk_score=c.risk_score,
            zone_id=c.zone_id,
            zone_name=c.zone.name if c.zone else "Zone",
            evidence_path=c.evidence_path,
            responsible_user_id=c.responsible_user_id,
            responsible_user_name=c.responsible_user.full_name if c.responsible_user else "Unassigned",
            deadline=c.deadline,
            status=curr_status,
            corrective_action_summary=c.corrective_action_summary,
            verification_remarks=c.verification_remarks,
            closed_at=c.closed_at,
            created_at=c.created_at,
            updated_at=c.updated_at,
            actions_count=len(c.corrective_actions)
        ))
    return results

@router.get("/cases/{case_id}")
def get_case_details(case_id: int, db: Session = Depends(get_db)):
    c = db.query(ComplianceCase).filter(ComplianceCase.id == case_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Case not found")

    actions = db.query(CorrectiveAction).filter(CorrectiveAction.case_id == c.id).all()
    comments = db.query(CaseComment).filter(CaseComment.case_id == c.id).order_by(CaseComment.created_at.asc()).all()

    return {
        "case": {
            "id": c.id,
            "case_number": c.case_number,
            "title": c.title,
            "category": c.category,
            "source": c.source,
            "risk_level": c.risk_level,
            "risk_score": c.risk_score,
            "zone_id": c.zone_id,
            "zone_name": c.zone.name if c.zone else "Zone",
            "evidence_path": c.evidence_path,
            "responsible_user_id": c.responsible_user_id,
            "responsible_user_name": c.responsible_user.full_name if c.responsible_user else "Unassigned",
            "deadline": c.deadline,
            "status": c.status,
            "corrective_action_summary": c.corrective_action_summary,
            "verification_remarks": c.verification_remarks,
            "closed_at": c.closed_at,
            "created_at": c.created_at,
            "updated_at": c.updated_at
        },
        "actions": [{
            "id": a.id,
            "title": a.title,
            "description": a.description,
            "status": a.status,
            "due_date": a.due_date,
            "assigned_to": a.assigned_to_user.full_name if a.assigned_to_user else "Supervisor",
            "verification_notes": a.verification_notes
        } for a in actions],
        "comments": [{
            "id": cm.id,
            "user_id": cm.user_id,
            "user_name": cm.user.full_name if cm.user else "User",
            "comment": cm.comment,
            "created_at": cm.created_at
        } for cm in comments],
        "timeline": [
            {"event": "Case Created", "timestamp": c.created_at, "actor": c.source},
            {"event": f"Action Initiated ({len(actions)} tasks assigned)", "timestamp": c.created_at, "actor": "Safety Directorate"},
            *([{"event": f"Closure & Statutory Sign-off: {c.verification_remarks}", "timestamp": c.closed_at, "actor": "Auditor"}] if c.closed_at else [])
        ]
    }

@router.post("/cases", response_model=ComplianceCaseResponse)
def create_case(data: ComplianceCaseCreate, db: Session = Depends(get_db)):
    case_num = f"CASE-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    new_case = ComplianceCase(
        case_number=case_num,
        title=data.title,
        category=data.category,
        source=data.source,
        risk_level=data.risk_level,
        risk_score=data.risk_score,
        zone_id=data.zone_id,
        evidence_path=data.evidence_path,
        responsible_user_id=data.responsible_user_id,
        deadline=data.deadline,
        status="Open",
        corrective_action_summary=data.corrective_action_summary,
        created_at=datetime.utcnow()
    )
    db.add(new_case)
    db.commit()
    db.refresh(new_case)

    create_audit_log(
        db,
        action="CASE_CREATED",
        entity_type="ComplianceCase",
        entity_id=new_case.case_number,
        user_id=data.responsible_user_id,
        new_state=f"Created compliance case {new_case.case_number}: {new_case.title}"
    )

    return ComplianceCaseResponse(
        id=new_case.id,
        case_number=new_case.case_number,
        title=new_case.title,
        category=new_case.category,
        source=new_case.source,
        risk_level=new_case.risk_level,
        risk_score=new_case.risk_score,
        zone_id=new_case.zone_id,
        zone_name=new_case.zone.name if new_case.zone else "Zone",
        evidence_path=new_case.evidence_path,
        responsible_user_id=new_case.responsible_user_id,
        responsible_user_name=new_case.responsible_user.full_name if new_case.responsible_user else "Unassigned",
        deadline=new_case.deadline,
        status=new_case.status,
        corrective_action_summary=new_case.corrective_action_summary,
        verification_remarks=new_case.verification_remarks,
        closed_at=new_case.closed_at,
        created_at=new_case.created_at,
        updated_at=new_case.updated_at,
        actions_count=0
    )

@router.patch("/cases/{case_id}")
def update_case(case_id: int, update_data: ComplianceCaseUpdate, db: Session = Depends(get_db)):
    c = db.query(ComplianceCase).filter(ComplianceCase.id == case_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Case not found")

    old_status = c.status
    if update_data.status:
        c.status = update_data.status
        if update_data.status == "Closed":
            c.closed_at = datetime.utcnow()
    if update_data.responsible_user_id:
        c.responsible_user_id = update_data.responsible_user_id
    if update_data.deadline:
        c.deadline = update_data.deadline
    if update_data.corrective_action_summary:
        c.corrective_action_summary = update_data.corrective_action_summary
    if update_data.verification_remarks:
        c.verification_remarks = update_data.verification_remarks

    c.updated_at = datetime.utcnow()

    create_audit_log(
        db,
        action="CASE_UPDATED",
        entity_type="ComplianceCase",
        entity_id=c.case_number,
        previous_state=f"Status: {old_status}",
        new_state=f"Status: {c.status}, Remarks: {c.verification_remarks}"
    )

    db.commit()
    db.refresh(c)
    return {"message": "Case updated successfully", "status": c.status}

@router.post("/cases/{case_id}/comments")
def add_case_comment(
    case_id: int,
    data: CaseCommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    c = db.query(ComplianceCase).filter(ComplianceCase.id == case_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Case not found")

    cm = CaseComment(
        case_id=c.id,
        user_id=current_user.id,
        comment=data.comment,
        created_at=datetime.utcnow()
    )
    db.add(cm)
    db.commit()
    db.refresh(cm)

    return {
        "id": cm.id,
        "case_id": cm.case_id,
        "user_name": current_user.full_name,
        "comment": cm.comment,
        "created_at": cm.created_at
    }

