from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import CorrectiveAction, ComplianceCase, User
from app.schemas.schemas import CorrectiveActionResponse, CorrectiveActionCreate, CorrectiveActionUpdate
from app.services.audit_service import create_audit_log

router = APIRouter(prefix="/actions", tags=["Corrective Actions"])

@router.get("/", response_model=List[CorrectiveActionResponse])
def get_corrective_actions(
    status_filter: Optional[str] = None,
    assigned_to_user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(CorrectiveAction).order_by(CorrectiveAction.due_date.asc())
    if status_filter and status_filter != "All":
        query = query.filter(CorrectiveAction.status == status_filter)
    if assigned_to_user_id:
        query = query.filter(CorrectiveAction.assigned_to_user_id == assigned_to_user_id)

    actions = query.all()
    results = []
    for a in actions:
        results.append(CorrectiveActionResponse(
            id=a.id,
            case_id=a.case_id,
            case_title=a.case.title if a.case else "Case",
            assigned_to_user_id=a.assigned_to_user_id,
            assigned_to_name=a.assigned_to_user.full_name if a.assigned_to_user else "Supervisor",
            title=a.title,
            description=a.description,
            status=a.status,
            due_date=a.due_date,
            completed_at=a.completed_at,
            verification_notes=a.verification_notes,
            created_at=a.created_at
        ))
    return results

@router.post("/", response_model=CorrectiveActionResponse)
def create_action(data: CorrectiveActionCreate, db: Session = Depends(get_db)):
    case = db.query(ComplianceCase).filter(ComplianceCase.id == data.case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Compliance Case not found")

    action = CorrectiveAction(
        case_id=data.case_id,
        assigned_to_user_id=data.assigned_to_user_id,
        title=data.title,
        description=data.description,
        due_date=data.due_date,
        status="Assigned",
        created_at=datetime.utcnow()
    )
    db.add(action)
    db.commit()
    db.refresh(action)

    create_audit_log(
        db,
        action="CORRECTIVE_ACTION_CREATED",
        entity_type="CorrectiveAction",
        entity_id=str(action.id),
        new_state=f"Created action for Case #{case.case_number}: {action.title}"
    )

    return CorrectiveActionResponse(
        id=action.id,
        case_id=action.case_id,
        case_title=case.title,
        assigned_to_user_id=action.assigned_to_user_id,
        assigned_to_name=action.assigned_to_user.full_name if action.assigned_to_user else "Supervisor",
        title=action.title,
        description=action.description,
        status=action.status,
        due_date=action.due_date,
        completed_at=action.completed_at,
        verification_notes=action.verification_notes,
        created_at=action.created_at
    )

@router.patch("/{action_id}")
def update_action_status(action_id: int, update: CorrectiveActionUpdate, db: Session = Depends(get_db)):
    act = db.query(CorrectiveAction).filter(CorrectiveAction.id == action_id).first()
    if not act:
        raise HTTPException(status_code=404, detail="Action not found")

    old_status = act.status
    if update.status:
        act.status = update.status
        if update.status in ["Verified", "Closed"]:
            act.completed_at = datetime.utcnow()
            # If all actions for case verified/closed, update case to Pending Verification or Closed
            case = act.case
            if case:
                open_acts = db.query(CorrectiveAction).filter(
                    CorrectiveAction.case_id == case.id,
                    CorrectiveAction.status.notin_(["Verified", "Closed"])
                ).count()
                if open_acts == 0:
                    case.status = "Pending Verification"
    if update.verification_notes:
        act.verification_notes = update.verification_notes

    create_audit_log(
        db,
        action="CORRECTIVE_ACTION_STATUS_CHANGED",
        entity_type="CorrectiveAction",
        entity_id=str(act.id),
        previous_state=f"Status: {old_status}",
        new_state=f"Status: {act.status}, Notes: {act.verification_notes}"
    )

    db.commit()
    return {"message": "Action updated successfully", "status": act.status}

